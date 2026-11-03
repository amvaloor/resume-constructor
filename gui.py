from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from constructor import build_resume
from parsers import parse

ctk.set_appearance_mode("System")


class ResumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Resume Constructor")
        self.minsize(800, 500)  ## TODO

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.folder_entries = {}
        self.scroll_frames = {}
        self.checkboxes = {"experiences": {}, "projects": {}, "activities": {}}
        self.parsed_data = {"experiences": {}, "projects": {}, "activities": {}}

        self.header_label = ctk.CTkLabel(
            self, text="Resume Constructor", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))

        self.create_frame("experiences", 0)
        self.create_frame("projects", 1)
        self.create_frame("activities", 2)

        self.create_bottom_frame()

    def create_frame(self, section, col):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=col, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)

        section_label = ctk.CTkLabel(frame, text=section)
        section_label.grid(row=0, column=0, columnspan=2)

        path_entry = ctk.CTkEntry(
            frame, placeholder_text=f"Select {section.lower()} folder..."
        )
        path_entry.grid(row=1, column=0, sticky="ew")
        self.folder_entries[section] = path_entry

        browse_button = ctk.CTkButton(
            frame,
            text="Browse",
            width=65,
            command=lambda name=section: self.browse_folder(name),
        )
        browse_button.grid(row=1, column=1)

        scroll_frame = ctk.CTkScrollableFrame(frame, label_text=f"Select {section}")
        scroll_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.scroll_frames[section] = scroll_frame

    def browse_folder(self, section):
        folder = filedialog.askdirectory(title=f"Select {section} folder")
        if not folder:
            return
        entry = self.folder_entries[section]
        entry.delete(0, ctk.END)
        entry.insert(0, folder)
        self.load_entries(section, folder)

    def load_entries(self, section, folder):
        for check in self.checkboxes[section].values():
            check.destroy()
        self.checkboxes[section].clear()

        parse_entries = parse(folder)
        if not parse_entries:
            return

        self.parsed_data[section] = parse_entries

        scroll_frame = self.scroll_frames[section]

        for entry_name in parse_entries.keys():
            check = ctk.CTkCheckBox(scroll_frame, text=entry_name)
            check.select()
            check.pack(anchor="w", padx=5, pady=4)

            self.checkboxes[section][entry_name] = check

    def create_bottom_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        self.bottom_frame = frame

        self.template = ctk.CTkEntry(
            frame, placeholder_text="Select Jinja2 template (.tex)..."
        )
        self.template.grid(row=0, column=0, padx=10, sticky="ew")

        self.template_btn = ctk.CTkButton(
            frame, text="Browse Template", width=120, command=self.browse_template
        )
        self.template_btn.grid(row=0, column=1, padx=10)

        self.output_entry = ctk.CTkEntry(
            frame, placeholder_text="Select output folder..."
        )
        self.output_entry.grid(row=1, column=0, padx=10, sticky="ew")

        self.output_btn = ctk.CTkButton(
            frame, text="Browse Output", width=120, command=self.browse_output
        )
        self.output_btn.grid(row=1, column=1, padx=10)

        self.output_name = ctk.CTkEntry(
            frame, placeholder_text="Enter output filename without extension..."
        )
        self.output_name.grid(row=2, column=0, columnspan=2, padx=10, sticky="ew")

        self.compile_btn = ctk.CTkButton(
            frame,
            text="Compile Resume",
            fg_color="green",
            hover_color="darkgreen",
            command=self.compile_resume,
        )
        self.compile_btn.grid(row=0, column=2, rowspan=3, padx=10, sticky="nsew")

        self.status_label = ctk.CTkLabel(frame, text="Ready", text_color="gray")
        self.status_label.grid(row=3, column=0, columnspan=3)

    def browse_template(self):
        file_path = filedialog.askopenfilename(
            title="Select Jinja2 Template",
            filetypes=[("TeX Files", "*.tex"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        self.template.delete(0, ctk.END)
        self.template.insert(0, file_path)

    def compile_resume(self):
        template_path = self.template.get()
        output_path = self.output_entry.get()
        output_name = self.output_name.get()

        if not template_path:
            self.status_label.configure(
                text="Please select a template first!", text_color="red"
            )
            return

        if not output_path:
            self.status_label.configure(
                text="Please select an output location first!", text_color="red"
            )
            return

        if not output_name:
            self.status_label.configure(
                text="Please enter an output filename!", text_color="red"
            )
            return

        self.status_label.configure(text="Gathering entries...", text_color="blue")
        self.update()

        selected_keys = self.get_selected_entries()
        data = {"experiences": [], "projects": [], "activities": []}
        for section, keys in selected_keys.items():
            for key in keys:
                data[section].append(self.parsed_data[section][key])

        output = Path(output_path) / f"{output_name}.pdf"
        self.status_label.configure(text="Compiling PDF...", text_color="blue")
        self.update()

        try:
            build_resume(template_path, str(output), data)
            self.status_label.configure(
                text="Compilation complete!", text_color="green"
            )
        except Exception as e:
            self.status_label.configure(
                text="Compilation failed. Check console for details.", text_color="red"
            )
            print(f"Compilation error:\n{e}")

    def get_selected_entries(self):
        selected = {"experiences": [], "projects": [], "activities": []}

        for section, entries in self.checkboxes.items():
            for entry_name, check in entries.items():
                if check.get() == 1:
                    selected[section].append(entry_name)

        return selected

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if not folder:
            return
        self.output_entry.delete(0, ctk.END)
        self.output_entry.insert(0, folder)


if __name__ == "__main__":
    app = ResumeApp()
    app.mainloop()
