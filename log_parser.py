# python3
import argparse
import re
import os
import logging
from pathlib import Path
import datetime
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the expression nodes for the parser
class ExprNode:
    def evaluate(self, line: str, ignore_case:bool) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")
    
class KeywordNode(ExprNode):
    def __init__(self, keyword: str):
        self.keyword = keyword
    
    def evaluate(self, line: str, ignore_case: bool) -> bool:
        if ignore_case:
            return self.keyword.lower() in line.lower()
        return self.keyword in line

class AndNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right
    
    def evaluate(self, line: str, ignore_case: bool) -> bool:
        return self.left.evaluate(line, ignore_case) and self.right.evaluate(line, ignore_case)

class OrNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right
    
    def evaluate(self, line: str, ignore_case: bool) -> bool:
        return self.left.evaluate(line, ignore_case) or self.right.evaluate(line, ignore_case)

class NotNode(ExprNode):
    def __init__(self, child: ExprNode):
        self.child = child
    
    def evaluate(self, line: str, ignore_case: bool) -> bool:
        return not self.child.evaluate(line, ignore_case)

# Expression parser to parse the input expression into an expression tree
class ExpressionParser:
    def __init__(self, expr: str):
        # Convert AND, OR, NOT to &&, ||, ! for easier parsing
        expr = re.sub(r'\bAND\b', '&&', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bOR\b', '||', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bNOT\b', '!', expr, flags=re.IGNORECASE)

        # Tokenize the expression
        expr = re.sub(r'([!()])', r' \1 ', expr)
        expr = re.sub(r'(\|\|)', r' \1 ', expr)
        expr = re.sub(r'(&&)', r' \1 ', expr)
        expr = re.sub(r'\s+', ' ', expr).strip()

        self.tokens = re.findall(r'!|\|\||&&|\(|\)|[^\s!()|&]+', expr)
        self.pos = 0

    def parse(self) -> ExprNode:
        return self._parse_or()

    def _parse_or(self) -> ExprNode:
        node = self._parse_and()
        while self._match('||'):
            right = self._parse_and()
            node = OrNode(node, right)
        return node

    def _parse_and(self) -> ExprNode:
        node = self._parse_not()
        while self._match('&&'):
            right = self._parse_not()
            node = AndNode(node, right)
        return node

    def _parse_not(self) -> ExprNode:
        if self._match('!'):
            child = self._parse_not()
            return NotNode(child)
        return self._parse_primary()

    def _parse_primary(self) -> ExprNode:
        if self._match('('):
            node = self._parse_or()
            if not self._expect(')'):
                raise ValueError("Expected ')'")
            return node
        else:
            return KeywordNode(self._consume())

    def _match(self, token: str) -> bool:
        if self.pos < len(self.tokens) and self.tokens[self.pos] == token:
            self.pos += 1
            return True
        return False
    
    def _consume(self) -> str:
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of expression")        
        token = self.tokens[self.pos]
        self.pos += 1
        return token

class Matcher:
    def match_line(self, line: str) -> Optional[str]:
        raise NotImplementedError("Subclasses should implement this method.")

class MatcherExpression(Matcher):
    """
    A matcher that supports logical expressions with '&&', '||', and parentheses using keyword-only matching.
    """
    def __init__(self, expressions: List[str], ignore_case=False):
        self.expressions = expressions
        self.expr_trees = [ExpressionParser(expr).parse() for expr in expressions]
        self.ignore_case = ignore_case

    def match_line(self, line: str) -> Optional[str]:
        for expr_tree in self.expr_trees:
            if expr_tree.evaluate(line, self.ignore_case):
                return line.rstrip()
        return None

    def get_expression(self) -> str:
        return self.expressions

class MatcherRegex(Matcher):
    """
    A matcher that checks if a line matches any of the specified regex patterns.
    """
    def __init__(self, patterns: List[str], ignore_case=False):
        flags = re.IGNORECASE if ignore_case else 0
        combined = '|'.join(f'({p})' for p in patterns)
        self.pattern = re.compile(combined, flags)

    def match_line(self, line: str) -> Optional[str]:
        if self.pattern.search(line):
            return line.rstrip()
        return None

    def get_expression(self) -> str:
        return self.pattern.pattern

class OutputParser:
    def __init__(self, output_file_path: str, pattern_str: List[str] = None):
        self.output_file_path = Path(output_file_path) if output_file_path else None
        self.f = None
        if self.output_file_path:
            try:
                self.f = self.output_file_path.open('a', encoding='utf-8')
                if pattern_str:
                    self.f.write("Patterns used: " + ', '.join(pattern_str) + '\n')
            except Exception as e:
                logger.error(f"Error opening output file {self.output_file_path}: {e}")
                self.f = None

    def write_to_file(self, line: str):
        if self.f:
            self.f.write(line + '\n')
        else:
            print(line)

    def close(self):
        if self.f:
            try:
                self.f.close()
            except Exception as e:
                logger.error(f"Error closing output file {self.output_file_path}: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class LogParser:
    """
    A simple log parser that reads a log file and extracts lines containing specified patterns.
    """
    def parse_log_file(self, file_path: str, matcher: Matcher, output_file: str):
        """
        Parses a log file any of the specified patterns.

        :param file_path: Path to the log file.
        :param Matcher: Matcher strategy to use for matching lines.
        :param output_file: File where output is streamed to.
        """
        out_parser = OutputParser(output_file, matcher.get_expression())

        self.linear_search(file_path, matcher, out_parser)       

    def linear_search(self, file_path: str, matcher: Matcher, output_parser: OutputParser) -> list[str]:
        """
        Parses a log file using simple lenear stratergy.

        :param file_path: Path to the log file.
        :param Matcher: Matcher strategy to use for matching lines.
        :return: List of matching lines.
        """
        input_path = Path(file_path)
        with input_path.open('r', encoding='utf-8-sig') as log_f:
            # Stream lines
            for line in log_f:
                match = matcher.match_line(line)
                if match is not None:
                    output_parser.write_to_file(match)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a log file for specific keywords.")
    parser.add_argument('-f' ,'--file_path', type=str, required=True, help='Path to the log file')
    parser.add_argument('-p','--patterns', nargs='+', required=True, help='patterns search for in the log file')
    parser.add_argument('-i','--ignore-case', action='store_true', default=False, help='Specify if case insensitive search is needed')
    parser.add_argument('-r','--mode', action='store_true', default=False, help='Specify if regex mode is needed')
    parser.add_argument('-o','--output', type=str, default=None, help='Specify output file path')
    args = parser.parse_args()

    log_file = args.file_path
    patterns = args.patterns
    output = args.output
    output_file = None
        
    log_parser = LogParser()

    if args.mode:
        matcher = MatcherRegex(patterns, ignore_case=args.ignore_case)
    else:
        matcher = MatcherExpression(patterns, ignore_case=args.ignore_case)

    log_file_path = Path(args.file_path)

    if output:
        output_path = Path(output) if output else None
        if output_path.is_dir():
            logger.info(f"Output directory {output_path} does not exist. Creating it.")
            output_path.mkdir(parents=True, exist_ok=True)

            os.makedirs(output, exist_ok=True)
            basename = log_file_path.stem

            # Generate a timestamped file name
            now = datetime.datetime.now()
            date_str = now.strftime("%Y%m%d")
            seconds_from_midnight = int((now - datetime.datetime.combine(now.date(), datetime.time.min)).total_seconds())
            file_name = f"parsed_{basename}_{date_str}_{seconds_from_midnight}.log"

            output_file = output_path / file_name
        else:
            logger.info(f"Output path {output} is not a directory. Treating it as a file path.")
            # Treat as file path
            output_file = output
    else:
        logger.info("No output file specified. Results will not be saved to a file.")

    # Parse the log file and print matching lines
    matching_lines = log_parser.parse_log_file(log_file, matcher, output_file)