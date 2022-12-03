# Pydantic
from pydantic import BaseModel
from pydantic import Field

# App Files
from src.commons.yaml_reader import yaml_reader

__all__ = ["ValidateResponse"]


load_response_dto_metadata = yaml_reader.get_dtos_metadata()["validate_response_dto"]


class ValidateResponse(BaseModel):
    detail: str = Field(
        ...,
        title=load_response_dto_metadata["detail"]["title"],
        description=load_response_dto_metadata["detail"]["description"],
    )

    class Config:
        schema_extra = {
            "example": {
                "detail": load_response_dto_metadata["detail"]["example"],
            }
        }
