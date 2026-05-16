import logging, re

from typing import List
from log_parser.expression import ExpressionParser


logger = logging.getLogger(__name__)


class Matcher:
    def match_line(self, line: str) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")

    def get_expression(self):
        raise NotImplementedError("Subclasses should implement this method.")

class MatcherExpression(Matcher):
    """
    A matcher that supports logical expressions with '&&', '||', and parentheses using keyword-only matching.
    """

    def __init__(self, expressions: List[str], ignore_case=False):
        self.ignore_case = ignore_case
        self.expr = expressions
        self.fn = self._compile(expressions, ignore_case)

    def _compile(self, expressions, ignore_case):
        compiled = [
            ExpressionParser(e).parse().compile(ignore_case)
            for e in expressions
        ]
        return lambda line: any(f(line) for f in compiled)

    def match_line(self, line: str) -> bool:
        return self.fn(line)

    def get_expression(self) -> str:
        return self.expr

class MatcherRegex(Matcher):
    """
    A matcher that checks if a line matches any of the specified regex patterns.
    """
    def __init__(self, patterns: List[str], ignore_case=False):
        flags = re.IGNORECASE if ignore_case else 0

        self.pattern = re.compile(
            "|".join(patterns),
            flags
        )

    def match_line(self, line: str) -> bool:
        return bool(self.pattern.search(line))

    def get_expression(self) -> str:
        return self.pattern.pattern