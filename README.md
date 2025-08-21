# log_parser
Python log file parser that searches for lines matching user-specified patterns, supporting both logical keyword expressions and regular expressions

## Features
- **Keyword Matching** -p with logical operators:
    - Supports `AND`, `OR`, `NOT`, `&&`, `||`, `!`, and parentheses.
    - Example: `"error && !timeout"`, `"Linux || Windows"`, `"(Linux || Windows) and bug"`
    - **Regex Mode** -r (optional)
- **Output to File** -o with timestamped names
- **Case-insensitive Search** -i (optional)

## Options
Required:
- -f, --file_path — Path to the log file
- -p, --patterns — Patterns or expressions to search
Optional:
- -i, --ignore-case — Enable case-insensitive matching
- -r, --mode — Use regex mode instead of keyword logic
- -o, --output — Output file path or directory (auto-names the file if not specified)

## Examples
...bash
python3 log_parser.py -f <log_file> -p <patterns> [options]

python3 log_parser.py -f ./tests/resources/example_linux.log -p "Linux and 2.6" -o .