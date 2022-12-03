# Pydantic
from pydantic import BaseModel
from pydantic import Field

# App Files
from src.commons.yaml_reader import yaml_reader

__all__ = ["ValidateRequest"]


load_request_dto_metadata = yaml_reader.get_dtos_metadata()["validate_request_dto"]


class ValidateRequest(BaseModel):
    fileName: str = Field(
        ...,
        title=load_request_dto_metadata["file_name"]["title"],
        description=load_request_dto_metadata["file_name"]["description"],
    )

    class Config:
        schema_extra = {
            "example": {
                "fileName": load_request_dto_metadata["file_name"]["example"],
            }
        }
