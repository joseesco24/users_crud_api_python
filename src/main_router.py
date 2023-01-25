"""main_router.py

this module is the incharge of assemble, make executable and expose the paths of the main.schema.graphql file in a single route

"""

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
from ariadne.validation import cost_validator
from ariadne import make_executable_schema
from ariadne import load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne import MutationType
from ariadne import QueryType

# ** info: artifacts imports
from src.artifacts.graphql.custom_scalars_serializer import integer_scalar
from src.artifacts.graphql.error_formatter import error_formatter
from src.artifacts.path.generator import generator
from src.artifacts.env.configs import configs

# ** info: users dtos imports
from src.dtos.users_dtos import UserDto

# ** info: resolvers imports
from src.resolvers.users_resolvers import users_resolvers

# pylint: disable=unused-variable
__all__: list[str] = ["main_router"]

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal
# ---------------------------------------------------------------------------------------------------------------------

current_file_path: Path = Path(__file__).parent.resolve()
schema_path: Path = Path(current_file_path, "main.schema.graphql")

schema_literal: str = load_schema_from_path(schema_path)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling querie facades with resolvers
# ---------------------------------------------------------------------------------------------------------------------

mutation: MutationType = MutationType()
query: QueryType = QueryType()


@mutation.field("addUser")
async def add_user_facade(
    *_: Any,
    estatalId: int,
    firstName: str,
    lastName: str,
    phoneNumber: int,
    email: str,
    gender: str,
    birthday: str,
    password: str
) -> UserDto:
    """add_user_facade

    addUser resolver facade

    """

    logging.debug("starting addUser resolver facade")

    response: UserDto = await users_resolvers.add_user_resolver(
        estatal_id=estatalId,
        first_name=firstName,
        last_name=lastName,
        phone_number=phoneNumber,
        email=email,
        gender=gender,
        birthday=birthday,
        password=password,
    )

    logging.debug("ending addUser resolver facade")

    return response


@query.field("users")
async def users_public_data_facade(*_: Any, limit: int, offset: int) -> List[UserDto]:
    """users_facade

    users resolver facade

    """

    logging.debug("starting users resolver facade")

    response: List[UserDto] = await users_resolvers.users_resolver(
        limit=limit, offset=offset
    )

    logging.debug("ending users resolver facade")

    return response


# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal with schema executable
# ---------------------------------------------------------------------------------------------------------------------

schema_executable: GraphQLSchema = make_executable_schema(
    schema_literal, query, mutation, integer_scalar
)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema executable with graphql endpoint
# ---------------------------------------------------------------------------------------------------------------------

graphql_endpoint_definition: GraphQL = GraphQL(
    debug=False if configs.app_environment_mode == "production" else True,
    validation_rules=[cost_validator(maximum_cost=5)],
    error_formatter=error_formatter.formatter,
    schema=schema_executable,
)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling graphql endpoint with the main router
# ---------------------------------------------------------------------------------------------------------------------

main_router: Route = Route(
    path=generator.build_posix_path("graphql"),
    endpoint=graphql_endpoint_definition,
)
