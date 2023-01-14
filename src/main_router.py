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


@query.field("getUsersFull")
async def get_users_full(*_: Any, limit: int, offset: int) -> List[Any]:
    """get_users_full

    getUsersFull resolver facade

    """

    logging.debug("starting getUsersFull resolver facade")

    response: List[Any] = await users_resolvers.get_users_full(
        limit=limit, offset=offset
    )

    logging.debug("ending getUsersFull resolver facade")

    return response


@query.field("getUsersPub")
async def get_users_pub(*_: Any, limit: int, offset: int) -> List[Any]:
    """get_users_pub

    getUsersPub resolver facade

    """

    logging.debug("starting getUsersPub resolver facade")

    response: List[Any] = await users_resolvers.get_users_pub(
        limit=limit, offset=offset
    )

    logging.debug("ending getUsersPub resolver facade")

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
