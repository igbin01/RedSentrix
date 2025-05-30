import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.current_theme = "dark"
        self.style = ttk.Style()

        self.themes = {
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#f0f0f0",
                "button": "#333333",
                "accent": "#0da8ff"
            },
            "light": {
                "bg": "#f5f5f5",
                "fg": "#1e1e1e",
                "button": "#e0e0e0",
                "accent": "#007acc"
            }
        }

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        for widget in self.root.winfo_children():
            self.recursively_theme(widget, theme)

    def recursively_theme(self, widget, theme):
        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.configure(bg=theme["bg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, (tk.Button, ttk.Button)):
            try:
                widget.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"])
            except:
                pass
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme["button"], fg=theme["fg"], insertbackground=theme["fg"])
        elif isinstance(widget, tk.Text):
            widget.configure(bg=theme["button"], fg=theme["fg"])

        for child in widget.winfo_children():
            self.recursively_theme(child, theme)

    def get_current_theme(self):
        return self.current_theme
