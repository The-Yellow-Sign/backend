from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from api.routers import admin, auth, chat, indexing, repository
from src.infrastructure.di.providers import (
    CacheProvider,
    InfrastructureProvider,
    RepositoryProvider,
    SericeProvider,
)

app = FastAPI(
    title="Автономная LLM-система верифицируемого знания",
    version="0.1.0",
)

container = make_async_container(
    InfrastructureProvider(),
    RepositoryProvider(),
    SericeProvider(),
    CacheProvider()
)

setup_dishka(container, app)

app.include_router(auth.router, prefix="/v1/auth")
app.include_router(chat.router_chat, prefix="/v1/chat")
app.include_router(admin.router_admin, prefix="/v1/admin")
app.include_router(repository.router_repository, prefix="/v1/repository")
app.include_router(indexing.router_indexing, prefix="/v1/indexing")
