import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, exceptions


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
    tex_path = Path(f"{pdf_name}.tex")
    tex_path.write_text(latex_string, encoding="utf-8")
    try:
        subprocess.run(
            [
                "pdflatex",
                f"-jobname={pdf_name}",
                "-interaction=nonstopmode",
                tex_path.name,
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pdflatex failed:\n{e.stdout.decode('utf-8')}")
    else:
        tex_path.unlink(missing_ok=True)
    finally:
        for extra in [".aux", ".log", ".out"]:
            Path(f"{pdf_name}{extra}").unlink(missing_ok=True)
