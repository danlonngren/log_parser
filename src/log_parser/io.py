from pathlib import Path


def read_lines_stream(file_path: str):
    with Path(file_path).open("r", encoding="utf-8-sig") as f:
        for line in f:
            yield line

def write_stream(output_file, lines):
    if isinstance(lines, str):
        lines = [lines]

    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
                print(line)
    else:
        for line in lines:
            print(line)