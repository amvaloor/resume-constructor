from parsers import parse
from constructor import fill_template, compile_to_pdf


def choose_projects(entries, entry_singular, entry_plural):
    if not entries:
        return {}
    selected_keys = []
    keys = list(entries.keys())
    print(f"The following {entry_plural} were found:")
    for i, entry in enumerate(entries, start=1):
        print(f"  [{i}] {entry}")
    print(
        f"Input the number corresponding to the {entry_singular} you want to add to your resume or type 'q' if you have selected enough {entry_plural}. If you would like to see the {entry_plural} found again, type 'info'\n"
    )
    while True:
        sel = input()
        if sel.lower() == "q":
            break
        if sel.lower() == "info":
            print(f"The following {entry_plural} were found:")
            for i, entry in enumerate(entries, start=1):
                print(f"  [{i}] {entry}")
            if selected_keys:
                print(f"These {entry_plural} have already been selected:")
                for key in selected_keys:
                    print(f"  {key}")
        elif sel.isdigit():
            idx = int(sel)
            if idx <= len(entries) and idx > 0:
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
    selected_projects = {key: entries[key] for key in selected_keys}
    return selected_projects


def get_entries(entry_singular, entry_plural):
    folder = (
        input(
            f"In which folder are the {entry_singular} files? Leave blank for '{entry_plural}'\n"
        )
        or f"{entry_plural}"
    )
    entries = parse(folder)
    selected_entries = choose_projects(entries, entry_singular, entry_plural)
    return selected_entries


def main():
    try:
        template_folder = (
            input("What is the template folder? Leave blank for 'templates'\n")
            or "templates"
        )
        template_name = (
            input("What is the name of the template? Leave blank for 'resume.tex'\n")
            or "resume.tex"
        )
        experiences = get_entries("experience", "experiences")
        projects = get_entries("project", "projects")
        activities = get_entries("activity", "activities")
        latex_str = fill_template(
            template_folder,
            template_name,
            {
                "experiences": experiences.values(),
                "projects": projects.values(),
                "activities": activities.values(),
            },
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
