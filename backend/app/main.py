from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.router import router as agent_router
from app.approvals.router import router as approval_router
from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.customers.router import router as customer_router
from app.users.router import router as users_router

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Agentic Customer Master API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(customer_router, prefix="/api/v1")
    app.include_router(approval_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(audit_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    return app


app = create_app()
