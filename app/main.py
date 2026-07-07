from fastapi import FastAPI
from app.routers.books import router as books_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI()

app.include_router(books_router,prefix="/books",tags=["Books"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
async def root():
    return {"message": "Hello World"}