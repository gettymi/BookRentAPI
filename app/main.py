from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.routers.books import router as books_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.rentals import router as rent_router
from app.core.exceptions import(
    BaseServiceException
)

app = FastAPI()

@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    return JSONResponse(
        status_code= exc.status_code,
        content={"detail": exc.message}
    )

app.include_router(books_router,prefix="/books",tags=["Books"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rent_router, prefix = "/rentals", tags = ["Rentals"])

@app.get("/")
async def root():
    return {"message": "Hello World"}