# ** info: fastapi imports
from fastapi import APIRouter
from fastapi import status

# ** info: fastapi imports
from src.artifacts.path.generator import generator

# ** info: health check dtos imports
from src.dtos.health_check_dtos import HealthCheckResponseDto

from src.services.health_check_service import health_check_service

__all__: list[str] = ["health_check_router"]

health_check_router: APIRouter = APIRouter(prefix=generator.build_posix_path("health-check"))


@health_check_router.get(
    path=generator.build_posix_path("is-everything-ok"),
    response_model=HealthCheckResponseDto,
    status_code=status.HTTP_200_OK,
)
async def load_configuration_file() -> HealthCheckResponseDto:
    health_check_response: HealthCheckResponseDto = await health_check_service.get_health_check_metrics()
    return health_check_response
