import os
import pytest

from log_parser.matchers import MatcherExpression, MatcherRegex
from log_parser.parser import LogParser


def num_lines_in_file(file_path: str) -> int:
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return sum(1 for _ in f)


@pytest.fixture
def setup_env(tmp_path):
    resource_path = os.path.join(
        os.path.dirname(__file__),
        "resources",
        "example_linux.log",
    )

    output_file = tmp_path / "test.log"
    parser = LogParser()

    return parser, resource_path, str(output_file)


@pytest.mark.parametrize(
    "matcher, expected",
    [
        (MatcherExpression(["Linux"], ignore_case=True), 7),
        (MatcherExpression(["Linux", "warning"], ignore_case=True), 9),
        (MatcherExpression(["Linux && May", "warning"], ignore_case=True), 3),
        (MatcherExpression(["Linux || warning"], ignore_case=True), 9),
        (MatcherExpression(["Linux && !8"], ignore_case=True), 2),
        (MatcherExpression(["(Linux || warning)"], ignore_case=True), 9),
        (MatcherRegex(["Linux version 2.6.5-1.\d", "Jones$"], ignore_case=True), 2),
    ],
)
def test_parse_log_file(setup_env, matcher, expected):
    parser, resource_path, output_file = setup_env

    parser.parse(resource_path, matcher, output_file)

    assert num_lines_in_file(output_file) == expected