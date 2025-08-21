# python3
import argparse
import re
import logging
import os
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
    def matchLine(self, line: str) -> Optional[str]:
        raise NotImplementedError("Subclasses should implement this method.")

class MatcherExpression(Matcher):
    """
    A matcher that supports logical expressions with '&&', '||', and parentheses using keyword-only matching.
    """
    def __init__(self, expressions: List[str], ignore_case=False):
        self.expr_trees = [ExpressionParser(expr).parse() for expr in expressions]
        self.ignore_case = ignore_case

    def matchLine(self, line: str) -> Optional[str]:
        for expr_tree in self.expr_trees:
            if expr_tree.evaluate(line, self.ignore_case):
                return line.rstrip()
        return None

class MatcherRegex(Matcher):
    """
    A matcher that checks if a line matches any of the specified regex patterns.
    """
    def __init__(self, patterns: List[str], ignore_case=False):
        flags = re.IGNORECASE if ignore_case else 0
        combined = '|'.join(f'({p})' for p in patterns)
        self.pattern = re.compile(combined, flags)

    def matchLine(self, line: str) -> Optional[str]:
        if self.pattern.search(line):
            return line.rstrip()
        return None

class LogParser:
    """
    A simple log parser that reads a log file and extracts lines containing specified patterns.
    """
    def parse_log_file(self, file_path: str, matcher: Matcher) -> list[str]:
        """
        Parses a log file and returns lines containing any of the specified patterns.

        :param file_path: Path to the log file.
        :param Matcher: Matcher strategy to use for matching lines.
        :return: List of matching lines.
        """
        matches = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = matcher.matchLine(line)
                if match is not None:
                    matches.append(match)
        return matches


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
        
    Log_parser = LogParser()

    if args.mode:
        matcher = MatcherRegex(patterns, ignore_case=args.ignore_case)
    else:
        matcher = MatcherExpression(patterns, ignore_case=args.ignore_case)

    # Parse the log file and print matching lines
    matching_lines = Log_parser.parse_log_file(log_file, matcher)

    if output:
        # Check if output_path is directory (or doesn't exist, treat as directory)
        if os.path.isdir(output):
            os.makedirs(output, exist_ok=True)
            base_name_without_ext = os.path.splitext(os.path.basename(log_file))[0]

            # Generate a timestamped file name
            now = datetime.datetime.now()
            date_str = now.strftime("%Y%m%d")
            midnight = datetime.datetime.combine(now.date(), datetime.time.min)
            seconds_from_midnight = int((now - midnight).total_seconds())
            file_name = f"parsed_{base_name_without_ext}_{date_str}_{seconds_from_midnight}.log"

            output_file = os.path.join(output + "/" + file_name)
        else:
            # Treat as file path
            output_file = output
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Patterns used: " + ', '.join(patterns) + '\n')
            for line in matching_lines:
                f.write(line + '\n')
        logging.info(f"Results written to {output_file}")
    else:
        for line in matching_lines:
            print(line)
