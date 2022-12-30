#!/usr/bin/env python3

# ** info: python imports
from pathlib import Path
import logging

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
from common_artifacts.path_utils.path_generator import path_generator


# pylint: disable=unused-variable
__all__: list[str] = [r"users_router"]

current_file_path: Path = Path(__file__).parent.resolve()
schema_path: Path = Path(current_file_path, r"..", r"schemas", r"users.schema.graphql")

schema_literal: str = load_schema_from_path(schema_path)

query: QueryType = QueryType()


@query.field(r"first_name")
def resolve_first_name(*_):
    logging.debug(r"resolving first_name field")
    return r"Octavio Felipe"


@query.field(r"second_name")
def resolve_second_name(*_):
    logging.debug(r"resolving second_name field")
    return r"Paz Belarcazar"


schema_executable: GraphQLSchema = make_executable_schema(schema_literal, query)

graphql_endpoint_definition: GraphQL = GraphQL(
    validation_rules=[cost_validator(maximum_cost=5)],
    schema=schema_executable,
    debug=True,
)

users_router: Route = Route(
    path=path_generator.build_posix_path(r"users"), endpoint=graphql_endpoint_definition
)
