from fastapi import APIRouter, status


health_router = APIRouter(
    tags=["healthchecks"],
)


@health_router.get("/health", status_code=status.HTTP_200_OK)
def healthcheck() -> dict:
    return {"status": "healthy"}
