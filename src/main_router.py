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
from ariadne.asgi import GraphQL
from ariadne import QueryType

from ariadne.validation import cost_validator
from ariadne import make_executable_schema
from ariadne import load_schema_from_path

# ** info: artifacts imports
from src.artifacts.graphql.error_formatter import error_formatter
from src.artifacts.path.generator import generator
from src.artifacts.env.configs import configs

# ** info: users dtos imports
from src.dtos.users_dtos import UserFullDto
from src.dtos.users_dtos import UserPubDto

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

query: QueryType = QueryType()


@query.field("usersFull")
async def users_full_facade(*_: Any, limit: int, offset: int) -> List[UserFullDto]:
    """users_full_facade

    usersFull resolver facade

    """

    logging.debug("starting usersFull resolver facade")

    response: List[UserFullDto] = await users_resolvers.users_full_resolver(
        limit=limit, offset=offset
    )

    logging.debug("ending usersFull resolver facade")

    return response


@query.field("usersPub")
async def users_pub_facade(*_: Any, limit: int, offset: int) -> List[UserPubDto]:
    """users_pub_facade

    usersPub resolver facade

    """

    logging.debug("starting usersPub resolver facade")

    response: List[UserPubDto] = await users_resolvers.users_pub_resolver(
        limit=limit, offset=offset
    )

    logging.debug("ending usersPub resolver facade")

    return response


# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema literal with schema executable
# ---------------------------------------------------------------------------------------------------------------------

schema_executable: GraphQLSchema = make_executable_schema(schema_literal, query)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: assembling schema executable with graphql endpoint
# ---------------------------------------------------------------------------------------------------------------------

graphql_endpoint_definition: GraphQL = GraphQL(
    debug=False if configs.environment_mode == "production" else True,
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
