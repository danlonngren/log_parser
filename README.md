# log_parser
Python log file parser that searches for lines matching user-specified patterns, supporting regular expressions

## Features
- **Keyword Matching** with logical operators:
    - Supports `&&`, `||`, `!`, and parentheses.
    - Example: `"error && !timeout"`, `"Linux || Windows"`, `"(Linux || Windows) and bug"`
    - **Regex Mode** (optional)
- **Output to File** with timestamped names
- **Case-insensitive Search** (optional)

## Options
- Required:
    - -f, --file_path — Path to the log file
- Exclusive:
    - -k, --keyword - Simple keyword search (implicit OR)
    - -e, --expr - Boolean expression: && || ! ( )
    - -r, --regex - Regex pattern
- Optional:
    - -i, --ignore-case — Enable case-insensitive matching
    - -o, --output — Output file path or directory (auto-names the file if not specified)
    - -d, --debug — Enable debug output

## Examples
```bash
python install -e
```

```bash
log-parser -f <log_file> -e <patterns> [options] -o out
```

Run tests
```bash
ptest
```