from pathlib import Path
from sys import exit
from jinja2 import Environment, FileSystemLoader, exceptions
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


def fill_template(template_folder, template_name, data):
    try:
        env = Environment(
            loader=FileSystemLoader(template_folder),
            block_start_string="<%",
            block_end_string="%>",
            variable_start_string="<<",
            variable_end_string=">>",
            comment_start_string="<#",
            comment_end_string="#>",
        )
        template = env.get_template(template_name)
        resume_tex = template.render(**data)
        return resume_tex
    except exceptions.TemplateNotFound:
        raise RuntimeError(f"error: {template_folder}/{template_name} not found")
    except exceptions.TemplateSyntaxError as e:
        raise RuntimeError(
            f"error: there was a syntax error in {template_folder}/{template_name}\n{e.message}"
        )


def main():
    print("TODO")


if __name__ == "__main__":
    main()
