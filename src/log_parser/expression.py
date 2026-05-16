import re
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class ExprNode:
    """
    AST Nodes
    """
    def compile(self, ignore_case: bool) -> Callable[[str], bool]:
        raise NotImplementedError


class KeywordNode(ExprNode):
    def __init__(self, keyword: str):
        self.keyword = keyword

    def compile(self, ignore_case: bool):
        if ignore_case:
            kw = self.keyword.lower()
            return lambda line: kw in line.lower()
        else:
            return lambda line: self.keyword in line


class AndNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

    def compile(self, ignore_case: bool):
        l = self.left.compile(ignore_case)
        r = self.right.compile(ignore_case)
        return lambda line: l(line) and r(line)


class OrNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

    def compile(self, ignore_case: bool):
        l = self.left.compile(ignore_case)
        r = self.right.compile(ignore_case)
        return lambda line: l(line) or r(line)


class NotNode(ExprNode):
    def __init__(self, child: ExprNode):
        self.child = child

    def compile(self, ignore_case: bool):
        c = self.child.compile(ignore_case)
        return lambda line: not c(line)


# LEXER
TOKEN_REGEX = re.compile(
    r'"[^"]*"|&&|\|\||!|\(|\)|[^\s()]+'
)

def tokenize(expr: str) -> list[str]:
    return TOKEN_REGEX.findall(expr)


class ExpressionParser:
    """
    PARSER (recursive descent)
    precedence:
      !  highest
      && middle
      || lowest
    """
    def __init__(self, expr: str):
        self.tokens = tokenize(expr)
        self.pos = 0
        logger.debug(f"Tokens: {self.tokens}")

    def parse(self) -> ExprNode:
        node = self._parse_or()

        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos]}")

        return node

    # OR level
    def _parse_or(self) -> ExprNode:
        node = self._parse_and()
        while self._match("||"):
            node = OrNode(node, self._parse_and())
        return node

    # AND level
    def _parse_and(self) -> ExprNode:
        node = self._parse_not()
        while self._match("&&"):
            node = AndNode(node, self._parse_not())
        return node

    # NOT level
    def _parse_not(self) -> ExprNode:
        if self._match("!"):
            return NotNode(self._parse_not())
        return self._parse_primary()

    # primary (keywords / parentheses)
    def _parse_primary(self) -> ExprNode:
        if self._match("("):
            node = self._parse_or()
            if not self._match(")"):
                raise ValueError("Expected ')'")
            return node

        token = self._consume()

        # quoted string
        if token.startswith('"') and token.endswith('"'):
            return KeywordNode(token[1:-1])

        # raw CLI keyword (no quoting required)
        if token not in ("&&", "||", "!"):
            return KeywordNode(token)

        raise ValueError(f"Unexpected token: {token}")

    # helpers
    def _match(self, token: str) -> bool:
        if self.pos < len(self.tokens) and self.tokens[self.pos] == token:
            self.pos += 1
            return True
        return False

    def _consume(self) -> str:
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of expression")
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok