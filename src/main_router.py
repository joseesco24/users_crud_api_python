# ** info: python imports
from pathlib import Path
import logging

# ** info: typing imports
from typing import List
from typing import Any

# ** info: starlette imports
from starlette.routing import Route

# ** info: graphql imports
from graphql import GraphQLSchema

# ** info: ariadne imports
from ariadne.asgi import GraphQL
from ariadne import QueryType

from ariadne.validation import cost_validator
from ariadne import make_executable_schema
from ariadne import load_schema_from_path

# Commons
from src.artifacts.graphql_utils.custom_error_formatter import custom_error_formatter
from src.artifacts.path_utils.path_generator import path_generator
from src.artifacts.env_utils.env_config import env_configs


# pylint: disable=unused-variable
__all__: list[str] = ["main_router"]

current_file_path: Path = Path(__file__).parent.resolve()
schema_path: Path = Path(current_file_path, "main.schema.graphql")

schema_literal: str = load_schema_from_path(schema_path)

query: QueryType = QueryType()


users: List[Any] = [
    {
        "internalId": "34d4a2b0-6c94-4a30-ba54-2346a2ddaf59",
        "estatalId": 9192562972,
        "firstName": "Arlin",
        "lastName": "Lenham",
        "phoneNumber": 2080650944,
        "email": "alenhamrp@ca.gov",
        "gender": "Male",
        "birthday": "2012/03/08",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "01f8e301011b8a4f6aeec3afb62a22246ed8d5bd879a81a69ea414ffb38cffac",
    },
    {
        "internalId": "fbab6f6b-f58f-4453-84b4-add51c4ef3ff",
        "estatalId": 7965738053,
        "firstName": "Reynolds",
        "lastName": "Ripon",
        "phoneNumber": 1090004661,
        "email": "rriponrr@answers.com",
        "gender": "Male",
        "birthday": "1984/03/10",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "6157a2fffccf919e70513c189d24b22cfde2c06f098a336162881fda99e9298d",
    },
    {
        "internalId": "8dd93284-c27e-46bc-b251-fb1a7a432aab",
        "estatalId": 2885926469,
        "firstName": "Dulcia",
        "lastName": "Dyos",
        "phoneNumber": 1090100667,
        "email": "ddyosrq@google.cn",
        "gender": "Female",
        "birthday": "2000/09/02",
        "creation": "2004-10-19 10:23:54+02",
        "modification": "2004-10-19 10:23:54+02",
        "password": "5fa8500e0b6e6b48e388ca31ac7da22fc0efc94d4c86c09ec6de8171c3e0c6b8",
    },
]


@query.field("getUsers")
def get_users(*_):
    logging.debug("starting getUsers resolver")
    logging.debug("ending getUsers resolver")
    return users


@query.field("getUsersByinternalId")
def get_users_by_internal_id(*_, internalId: str):
    logging.debug("starting getUser resolver")
    filtered_users: List[Any] = list(
        filter(lambda user: str(user["internalId"]) == internalId, users)
    )
    logging.debug("ending getUser resolver")
    return filtered_users


schema_executable: GraphQLSchema = make_executable_schema(schema_literal, query)

graphql_endpoint_definition: GraphQL = GraphQL(
    debug=False if env_configs.environment_mode == "production" else True,
    validation_rules=[cost_validator(maximum_cost=5)],
    error_formatter=custom_error_formatter.formatter,
    schema=schema_executable,
)

main_router: Route = Route(
    path=path_generator.build_posix_path("graphql"), endpoint=graphql_endpoint_definition
)
