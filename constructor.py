from pathlib import Path
import subprocess
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


def compile_to_pdf(latex_string, pdf_name):
    try:
        subprocess.run(
            ["pdflatex", f"-jobname={pdf_name}", "-interaction=nonstopmode"],
            input=latex_string.encode(),
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pdflatex failed:\n{e.stdout.decode('utf-8')}")
    for extra in [".aux", ".log", ".out"]:
        Path(f"{pdf_name}{extra}").unlink(missing_ok=True)


def main():
    print("TODO")


if __name__ == "__main__":
    main()
