"""
Auth API Router — registration, login, credential management, Google OAuth.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..config import settings
from ..crypto import decrypt, encrypt
from ..database import get_db
from ..models import User, UserCredentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str | None
    is_admin: bool


class CredentialSaveRequest(BaseModel):
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    openrouter_api_key: str = ""
    qdrant_collection_name: str = ""


class CredentialStatusResponse(BaseModel):
    configured: bool
    has_qdrant: bool
    has_openrouter: bool
    is_admin: bool


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    is_admin: bool
    created_at: datetime


# ── Auth Endpoints ────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user account and return a JWT."""
    # Check for duplicate email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    if not body.password or len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 6 characters.",
        )

    is_admin = body.email.strip().lower() in settings.admin_emails_list
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_admin=is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.email, user.is_admin)
    logger.info("New user registered: %s (id=%d, is_admin=%s)", user.email, user.id, user.is_admin)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Verify credentials and return a JWT."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Auto-promote user to admin if their email is in ADMIN_EMAILS
    if body.email.strip().lower() in settings.admin_emails_list and not user.is_admin:
        user.is_admin = True
        await db.commit()
        logger.info("User %s promoted to admin via ADMIN_EMAILS settings.", user.email)

    token = create_access_token(user.id, user.email, user.is_admin)
    logger.info("User logged in: %s (id=%d, is_admin=%s)", user.email, user.id, user.is_admin)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current user's profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )


@router.get("/credentials/status", response_model=CredentialStatusResponse)
async def credentials_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check whether the current user has API credentials configured."""
    # Admins always have credentials via .env
    if current_user.is_admin:
        return CredentialStatusResponse(
            configured=True,
            has_qdrant=bool(settings.qdrant_url),
            has_openrouter=bool(settings.openrouter_api_key),
            is_admin=True,
        )

    result = await db.execute(
        select(UserCredentials).where(UserCredentials.user_id == current_user.id)
    )
    creds = result.scalar_one_or_none()

    has_qdrant = bool(creds and creds.qdrant_url_enc and creds.qdrant_api_key_enc)
    has_openrouter = bool(creds and creds.openrouter_api_key_enc)

    return CredentialStatusResponse(
        configured=has_qdrant and has_openrouter,
        has_qdrant=has_qdrant,
        has_openrouter=has_openrouter,
        is_admin=False,
    )


@router.post("/credentials")
async def save_credentials(
    body: CredentialSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update the current user's encrypted API credentials."""
    if current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin uses .env credentials — no need to configure here.",
        )

    result = await db.execute(
        select(UserCredentials).where(UserCredentials.user_id == current_user.id)
    )
    creds = result.scalar_one_or_none()

    collection_name = body.qdrant_collection_name or f"rag_{current_user.id}"

    if creds:
        # Update existing record
        if body.qdrant_url:
            creds.qdrant_url_enc = encrypt(body.qdrant_url)
        if body.qdrant_api_key:
            creds.qdrant_api_key_enc = encrypt(body.qdrant_api_key)
        if body.openrouter_api_key:
            creds.openrouter_api_key_enc = encrypt(body.openrouter_api_key)
        creds.qdrant_collection_name = collection_name
    else:
        # Create new credentials row
        creds = UserCredentials(
            user_id=current_user.id,
            qdrant_url_enc=encrypt(body.qdrant_url) if body.qdrant_url else "",
            qdrant_api_key_enc=encrypt(body.qdrant_api_key) if body.qdrant_api_key else "",
            openrouter_api_key_enc=encrypt(body.openrouter_api_key) if body.openrouter_api_key else "",
            qdrant_collection_name=collection_name,
        )
        db.add(creds)

    await db.commit()
    logger.info("Credentials updated for user %d", current_user.id)
    return {"message": "Credentials saved successfully.", "collection_name": collection_name}


@router.delete("/credentials")
async def delete_credentials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove stored API credentials for the current user."""
    result = await db.execute(
        select(UserCredentials).where(UserCredentials.user_id == current_user.id)
    )
    creds = result.scalar_one_or_none()
    if creds:
        await db.delete(creds)
        await db.commit()
    return {"message": "Credentials removed."}


# ── Google OAuth (optional) ───────────────────────────────────────────────────

@router.get("/google")
async def google_oauth_start(request: Request):
    """Redirect to Google OAuth consent screen."""
    if not settings.google_oauth_enabled:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured on this server.")

    from authlib.integrations.starlette_client import OAuth
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    redirect_uri = str(request.url_for("google_oauth_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_oauth_callback")
async def google_oauth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback — create/fetch user and return JWT via redirect."""
    if not settings.google_oauth_enabled:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured on this server.")

    from authlib.integrations.starlette_client import OAuth
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    token_data = await oauth.google.authorize_access_token(request)
    google_user = token_data.get("userinfo") or {}

    google_id = google_user.get("sub")
    email = google_user.get("email")
    full_name = google_user.get("name")

    if not email or not google_id:
        raise HTTPException(status_code=400, detail="Google OAuth did not return user info.")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    is_admin = email.strip().lower() in settings.admin_emails_list

    if not user:
        user = User(email=email, full_name=full_name, google_id=google_id, is_admin=is_admin)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        updated = False
        if not user.google_id:
            user.google_id = google_id
            updated = True
        if is_admin and not user.is_admin:
            user.is_admin = True
            updated = True
        if updated:
            await db.commit()

    token = create_access_token(user.id, user.email, user.is_admin)
    # Redirect frontend with token in URL fragment (SPA handles it)
    return RedirectResponse(url=f"/?token={token}&type=oauth")
