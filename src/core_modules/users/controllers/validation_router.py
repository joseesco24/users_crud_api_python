# Python
from datetime import timedelta
from datetime import datetime
import logging

# FastAPI
from fastapi import APIRouter, Body, status

# App Files
from src.commons.yaml_reader import yaml_reader

# Commons
from src.commons.path_manager import build_posix_path, get_file_name

# Dtos
from src.dtos.validate_response_dto import ValidateResponse
from src.dtos.validate_request_dto import ValidateRequest

# Controllers
from src.controllers.validation_controller import ValidationController


paths_metadata: dict = yaml_reader.get_paths_metadata()
script_name: str = get_file_name()

__all__: list[str] = ["validation_router"]

validation_router: APIRouter = APIRouter(
    prefix=build_posix_path("validate"), tags=["Validate"]
)


@validation_router.post(
    response_model=ValidateResponse,
    summary=paths_metadata["configuration"]["post"]["summary"],
    path=build_posix_path("configuration"),
    status_code=status.HTTP_202_ACCEPTED,
)
async def load_configuration_file(
    request: ValidateRequest = Body(...),
) -> ValidateResponse:

    """**Validate a Configuration File**


    This method is the incharge of receive, read, process, validate and mark a configuration
    file, the result of this operation is a mark in the configurations map file
    (**configurations_map.json**) if the file is valid the isValid label is added and established
    as true if not the isValid label is also added but is established as false


    **Request Body Parameters (LoadRequest)**
    - **fileName (str)**: The name of the file to load


    """

    controller: ValidationController
    execution_time: timedelta
    logg_data: dict[str, str]
    milliseconds: int
    start: datetime
    end: datetime
    seconds: int

    logg_data = {"file_name": request.fileName}
    logging.debug(yaml_reader.get_logg_message(script_name, "logg_001", logg_data))
    logging.debug(yaml_reader.get_logg_message(script_name, "logg_002"))
    start = datetime.now()

    controller = ValidationController()
    await controller.controller(file_name=request.fileName)

    end = datetime.now()
    execution_time = end - start
    logging.debug(yaml_reader.get_logg_message(script_name, "logg_003"))
    seconds = execution_time.seconds
    milliseconds = int(execution_time.microseconds / 1000)
    logg_data = {
        "file_name": request.fileName,
        "seconds": seconds,
        "milliseconds": milliseconds,
    }
    logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

    return ValidateResponse(detail=f"{request.fileName} successfully validated")
