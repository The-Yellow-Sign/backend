import uvicorn
from fastapi import FastAPI
from src.api.routers import admin, auth, chat, repository 

app = FastAPI(
    title="Скелет",
    version="0.1.0",
)

app.include_router(auth.router, prefix="/v1/auth")
app.include_router(chat.router_chat, prefix="/v1/chat")
app.include_router(admin.router_admin, prefix="/v1/admin")
app.include_router(repository.router_repository, prefix="/v1/repository")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)