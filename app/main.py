import asyncio
from fastapi import FastAPI, Request, status,Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text,select,func
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.books import router as books_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.rentals import router as rent_router
from app.models import User,Rental,Book
from app.core.dependencies import get_db
from app.core.exceptions import(
    BaseServiceException
)

app = FastAPI(
    title="BookRent API",
    description="A high-performance asynchronous REST API for managing a book catalog and user rentals.",
    version="1.0.0",
)

@app.exception_handler(BaseServiceException)
async def service_exception_handler(request: Request, exc: BaseServiceException):
    logger.warning(f"Business Rule Exception: {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code= exc.status_code,
        content={"detail": exc.message}
    )

app.include_router(books_router,prefix="/books",tags=["Books"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rent_router, prefix = "/rentals", tags = ["Rentals"])

@app.get("/", tags=["System"])
async def root():
    return {"message": "Hello World"}


@app.get("/health", tags=["System"])
async def health_check(session: AsyncSession = Depends(get_db)):
    """
    Infrastructure health check endpoint for load balancers and container orchestrators.
    Verifies that the API is running and can communicate with the database.
    """

    try:
        await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "online"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Unavailable: Database connection failed"
        )

@app.get("/metrics", tags=["System"])
async def get_metrics(session: AsyncSession = Depends(get_db)):
    """
    Application metrics for monitoring and dashboards.
    """

    users_query = select(func.count(User.id))
    books_query = select(func.count(Book.id))
    active_rentals_query = select(func.count(Rental.id)).where(Rental.status == "active")


    users_count = await session.scalar(users_query)
    books_count = await session.scalar(books_query)
    active_rentals_count = await session.scalar(active_rentals_query)

    return {
        "total_users": users_count,
        "total_books_in_catalog": books_count,
        "current_active_rentals": active_rentals_count
    }