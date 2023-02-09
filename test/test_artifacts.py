# ** info: python imports
from os.path import join
from os import path
import sys

# **info: appending src path to the system paths for absolute imports from src path
sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# ** info: artifacts imports
from src.artifacts.path.generator import generator

# ---------------------------------------------------------------------------------------------------------------------
# ** info: path.generator tests
# ---------------------------------------------------------------------------------------------------------------------


def test_build_posix_path() -> None:
    generated_path: str = generator.build_posix_path("reports", "generate")
    expected_path: str = "/reports/generate"
    assert generated_path == expected_path
