import frontmatter
from pathlib import Path


def sanitize_latex(text):
    chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text


def sanitize_val(val):
    if isinstance(val, str):
        return sanitize_latex(val)
    if isinstance(val, list):
        return [sanitize_val(item) for item in val]
    if isinstance(val, dict):
        return {k: sanitize_val(v) for k, v in val.items()}
    return val


def parse(folder):
    entries = {}
    for file in Path(folder).glob("*.md"):
        try:
            post = frontmatter.load(file)
            entry = {k: sanitize_val(v) for k, v in post.metadata.items()}
            if "name" not in entry:
                raise KeyError
            name = post["name"]
            raw_lines = post.content.splitlines()
            bullets = [
                sanitize_latex(line.lstrip("-*+ ").strip())
                for line in raw_lines
                if line.strip()
            ]
            entry["bullets"] = bullets
            entries[name] = entry
        except KeyError as e:
            print(f"File {file} is missing required field: {e}")
        except Exception as e:
            print(f"File {file} failed to parse: {e}")
    return entries
