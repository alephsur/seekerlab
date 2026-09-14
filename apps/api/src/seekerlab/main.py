from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from seekerlab.config import get_settings
from seekerlab.db import engine, get_session
from seekerlab.modules.campaigns.domain import Conflict, DomainError, Forbidden, NotFound
from seekerlab.modules.identity.domain import (
    ChallengeUnavailable,
    IdentityError,
    InvalidSession,
    InvalidSignIn,
)
from seekerlab.modules.identity.routes import router as identity_router
from seekerlab.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="SeekerLab API", version="0.2.0", lifespan=lifespan,
                  description="SIWS sessions are available. SGT, AI and payments are pending.")
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                       allow_credentials=False, allow_methods=["GET", "POST"],
                       allow_headers=["Authorization", "Content-Type"])
    app.include_router(router)
    app.include_router(identity_router)

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        code = 404 if isinstance(exc, NotFound) else 403 if isinstance(exc, Forbidden) else 409 if isinstance(exc, Conflict) else 422
        return JSONResponse(status_code=code, content={"detail": str(exc)})

    @app.exception_handler(IdentityError)
    async def identity_error(request: Request, exc: IdentityError):
        if isinstance(exc, ChallengeUnavailable):
            code = 409
        elif isinstance(exc, (InvalidSignIn, InvalidSession)):
            code = 401
        else:
            code = 422
        return JSONResponse(status_code=code, content={"detail": str(exc)})

    @app.get("/health/live", tags=["health"])
    def live():
        return {"status": "ok", "version": "0.2.0", "environment": settings.app_env}

    @app.get("/health/ready", tags=["health"])
    def ready(session: Annotated[Session, Depends(get_session)]):
        try:
            session.execute(text("SELECT 1 FROM campaigns LIMIT 1"))
        except SQLAlchemyError:
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        return {"status": "ready"}

    return app


app = create_app()
