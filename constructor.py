import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, exceptions
from parsers import parse


def choose_projects(projects):
    if not projects:
        raise RuntimeError("error: no projects found")
    selected_keys = []
    keys = list(projects.keys())
    print("The following projects were found:")
    for i, project in enumerate(projects, start=1):
        print(f"  [{i}] {project}")
    print(
        "Input the number corresponding to the project you want to add to your resume or type 'q' if you have selected enough projects. If you would like to see the projects found again, type 'info'\n"
    )
    while True:
        sel = input()
        if sel.lower() == "q":
            break
        if sel.lower() == "info":
            print("The following projects were found:")
            for i, project in enumerate(projects, start=1):
                print(f"  [{i}] {project}")
            if selected_keys:
                print("These projects have already been selected:")
                for key in selected_keys:
                    print(f"  {key}")
        elif sel.isdigit():
            idx = int(sel)
            if idx <= len(projects) and idx > 0:
                selected_key = keys[idx - 1]
                if selected_key not in selected_keys:
                    selected_keys.append(keys[idx - 1])
                    print(f"Added {selected_key}")
                else:
                    print(f"{selected_key} already selected")
            else:
                print("Input out of range; please select a number from the list")
        else:
            print(
                "Unrecognized input; please select a number from the list, 'info', or 'q'"
            )
    selected_projects = {key: projects[key] for key in selected_keys}
    return selected_projects


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
                "lualatex",
                f"-jobname={pdf_name}",
                "-interaction=nonstopmode",
                tex_path.name,
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"lualatex failed:\n{e.stdout.decode('utf-8')}")
    else:
        tex_path.unlink(missing_ok=True)
    finally:
        for extra in [".aux", ".log", ".out"]:
            Path(f"{pdf_name}{extra}").unlink(missing_ok=True)


def main():
    try:
        folder = (
            input("In which folder are the project files? Leave blank for 'projects'\n")
            or "projects"
        )
        projects = parse(folder)
        selected_projects = choose_projects(projects)
        template_folder = (
            input("What is the template folder? Leave blank for 'templates'\n")
            or "templates"
        )
        template_name = (
            input("What is the name of the template? Leave blank for 'resume.tex'\n")
            or "resume.tex"
        )
        latex_str = fill_template(
            template_folder, template_name, {"projects": selected_projects.values()}
        )
        pdf_name = (
            input(
                "What should the output PDF be called? Do not include the file extension. Leave blank for 'resume'\n"
            )
            or "resume"
        )
        compile_to_pdf(latex_str, pdf_name)
        print(f"PDF generated as {pdf_name}.pdf")
    except RuntimeError as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
