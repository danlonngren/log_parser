import argparse
import logging

from pathlib import Path

from log_parser.parser import LogParser
from log_parser.matchers import MatcherRegex, MatcherExpression
from log_parser.logging_config import setup_logging
from log_parser.io import write_stream


logger = logging.getLogger(__name__)


def build_parser():
    p = argparse.ArgumentParser()

    mode = p.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "-k", "--keywords",
        nargs="+",
        help="Simple keyword search (implicit OR)"
    )

    mode.add_argument(
        "-e", "--expr",
        help="Boolean expression: && || ! ( )"
    )

    mode.add_argument(
        "-r", "--regex",
        help="Regex pattern"
    )

    p.add_argument("-f", "--file_path", required=True)
    p.add_argument("-o", "--output", default=None)
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("-d", "--debug", action="store_true")
    return p.parse_args()

def build_matcher(args):
    if args.keywords:
        expr = " || ".join(f'"{k}"' for k in args.keywords)
        return MatcherExpression([expr], ignore_case=args.ignore_case)

    if args.expr:
        return MatcherExpression([args.expr], ignore_case=args.ignore_case)

    if args.regex:
        return MatcherRegex([args.regex], ignore_case=args.ignore_case)

    raise ValueError("No valid mode selected")

def main():
    args = build_parser()
    setup_logging(args.debug)
    
    logger.debug(f"Patterns received from argparse: {args}")

    matcher = build_matcher(args)

    parser = LogParser()
    output_file = parser.resolve_output_path(args.output, Path(args.file_path))

    if output_file:
        logger.info(f"Output file: {output_file}")
        write_stream(output_file, f"Pattern used: {matcher.get_expression()}")

    parser.parse(Path(args.file_path), matcher, output_file)
