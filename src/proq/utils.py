import difflib

from termcolor import cprint


def color_diff(old_text, new_text):
    """Generate a rich diff with colors using termcolor.

    Args:
        old_text (str): The original text.
        new_text (str): The modified text.
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = difflib.ndiff(old_lines, new_lines)

    for line in diff:
        if line.startswith("-"):  # Deletion
            cprint(line, "red")
        elif line.startswith("+"):  # Addition
            cprint(line, "green")
        elif line.startswith("?"):  # Changed
            cprint(line, "yellow")
        else:  # Unchanged
            print(line)
