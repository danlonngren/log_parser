import unittest
import os
from log_parser import LogParser
from log_parser import Matcher, MatcherExpression, MatcherRegex

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.resource_path = os.path.join(os.path.dirname(__file__), 'resources', 'example_linux.log')
        self.parser = LogParser()

    def test_parse_log_file_keywords(self):
        matcher = MatcherExpression(["Linux", "warning"], ignore_case=True)
        matches = self.parser.parse_log_file(self.resource_path, matcher)
        self.assertGreater(len(matches), 7)

    def test_parse_log_file_keywords_and(self):
        matcher = MatcherExpression(["Linux and May", "warning"], ignore_case=True)
        matches = self.parser.parse_log_file(self.resource_path, matcher)
        self.assertGreater(len(matches), 2)

    def test_parse_log_file_keywords_or(self):
        matcher = MatcherExpression(["Linux or warning"], ignore_case=True)
        matches = self.parser.parse_log_file(self.resource_path, matcher)
        self.assertGreater(len(matches), 7)

    def test_parse_log_file_keywords_and_not(self):
        matcher = MatcherExpression(["Linux and not 2.6"], ignore_case=True)
        matches = self.parser.parse_log_file(self.resource_path, matcher)
        self.assertGreater(len(matches), 4)

    def test_parse_log_file_regex(self):
        matcher = MatcherRegex(["Linux version 2.6.5-1.\d", "Jones$"], ignore_case=True)
        matches = self.parser.parse_log_file(self.resource_path, matcher)
        self.assertGreater(len(matches), 1)

if __name__ == "__main__":
    unittest.main()