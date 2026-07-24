.PHONY: dev prod down clean

dev: ## Dev mode: Postgres in Docker, backend/frontend run natively
	docker compose up -d
	@echo ""
	@echo "✅ Postgres is running on :5432"
	@echo ""
	@echo "Now start in separate terminals:"
	@echo "  Terminal 2:  cd backend && uv run uvicorn app.main:app --reload --port 8000"
	@echo "  Terminal 3:  cd frontend && npm run dev"
	@echo ""

prod: ## Full Docker: everything containerized
	docker compose -f docker-compose.prod.yml up --build -d
	@echo ""
	@echo "✅ App is running at http://localhost"
	@echo ""

down: ## Stop all running containers
	docker compose down
	docker compose -f docker-compose.prod.yml down 2>/dev/null || true

clean: ## Stop containers and wipe all volumes (deletes DB data)
	docker compose down -v
	docker compose -f docker-compose.prod.yml down -v 2>/dev/null || true
	@echo "✅ All containers stopped and volumes removed"

logs-backend: ## Tail backend logs (prod mode)
	docker compose -f docker-compose.prod.yml logs -f backend

logs-db: ## Tail Postgres logs
	docker compose logs -f postgres

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
