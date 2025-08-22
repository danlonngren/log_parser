import unittest
import os
from log_parser import LogParser, MatcherExpression, MatcherRegex

class TestLogParser(unittest.TestCase):
    def num_lines_in_file(self, file_path: str) -> int:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return sum(1 for _ in f) - 1  # Subtract 1 for the header line

    def assert_parse_log_file(self, matcher, expected_count):
        self.parser.parse_log_file(self.resource_path, matcher, self.output_file)
        self.assertEqual(self.num_lines_in_file(self.output_file), expected_count)

    def setUp(self):
        self.resource_path = os.path.join(os.path.dirname(__file__), 'resources', 'example_linux.log')
        self.parser = LogParser()
        self.output_file = "./test.log"  # No output file for testing

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_parse_log_file_keywords(self):
        self.assert_parse_log_file(MatcherExpression(["Linux"], ignore_case=True), 7)

    def test_parse_log_file_keywords_multiple(self):
        self.assert_parse_log_file(MatcherExpression(["Linux", "warning"], ignore_case=True), 9)

    def test_parse_log_file_keywords_and(self):
        self.assert_parse_log_file(MatcherExpression(["Linux && May", "warning"], ignore_case=True), 3)

    def test_parse_log_file_keywords_or(self):
        self.assert_parse_log_file(MatcherExpression(["Linux || warning"], ignore_case=True), 9)

    def test_parse_log_file_keywords_and_not(self):
        self.assert_parse_log_file(MatcherExpression(["Linux && !8"], ignore_case=True), 2)

    def test_parse_log_file_keywords_parenthesis(self):
        self.assert_parse_log_file(MatcherExpression(["(Linux || warning)"], ignore_case=True), 9)

    def test_parse_log_file_regex(self):
        self.assert_parse_log_file(MatcherRegex(["Linux version 2.6.5-1.\d", "Jones$"], ignore_case=True), 2)

if __name__ == "__main__":
    unittest.main()