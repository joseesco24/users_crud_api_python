from typing import Dict

# ** info: fastapi imports
from fastapi import APIRouter
from fastapi import status

# ** info: fastapi imports
from src.artifacts.path.generator import generator

# pylint: disable=unused-variable
__all__: list[str] = ["health_check_router"]

health_check_router: APIRouter = APIRouter(
    prefix=generator.build_posix_path("health-check")
)


@health_check_router.get(
    path=generator.build_posix_path("is-everything-ok"),
    status_code=status.HTTP_200_OK,
)
async def load_configuration_file() -> Dict:
    return {"ok": True}
