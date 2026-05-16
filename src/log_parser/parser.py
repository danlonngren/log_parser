import logging
from pathlib import Path
import datetime
from typing import List

from log_parser.matchers import Matcher
from log_parser.io import read_lines_stream, write_stream

logger = logging.getLogger(__name__)


class LogParser:
    """
    A simple log parser that reads a log file and extracts lines containing specified patterns.
    """

    def parse(self, file_path: Path, matcher: Matcher, output_file: str | None):
        lines = read_lines_stream(file_path=file_path)
        result = self._filter_stream(lines, matcher)
        write_stream(output_file, result)

    def _filter_stream(self, lines_iter: list[str], matcher: Matcher):
        for line in lines_iter:
            if matcher.match_line(line):
                yield line.rstrip()

    def resolve_output_path(self, output_path: str | None, log_path: Path) -> Path | None:
        if not output_path:
            logger.debug("output path is None")
            return None

        o = Path(output_path)
        if o.suffix == "":
            o.mkdir(parents=True, exist_ok=True)
            # Generate a timestamped file name
            now = datetime.datetime.now()
            date_str = now.strftime("%Y%m%d")
            seconds_from_midnight = int((now - datetime.datetime.combine(now.date(), datetime.time.min)).total_seconds())
            file_name = f"parsed_{log_path.stem}_{date_str}_{seconds_from_midnight}.log"
            logger.debug(f"Create dir and file: {o / file_name}")
            return o / file_name

        # Case 2 file path
        o.parent.mkdir(parents=True, exist_ok=True)
        return o

