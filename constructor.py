from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
import frontmatter


def parse(folder):
    projects = {}
    for file in Path(folder).glob("*.md"):
        try:
            post = frontmatter.load(file)
            project = {}
            name = post["name"]
            project["start_date"] = post["start_date"]
            project["end_date"] = post["end_date"]
            project["tags"] = post["tags"]
            project["content"] = post.content
            projects[name] = project
        except KeyError as e:
            print(f"File {file} is missing required field: {e}")
        except Exception as e:
            print(f"File {file} failed to parse: {e}")
    return projects


def main():
    print("TODO")


if __name__ == "__main__":
    main()
