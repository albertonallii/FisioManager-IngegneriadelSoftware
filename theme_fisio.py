from tkinter import ttk

PRIMARY      = "#128062"
PRIMARY_DARK = "#0F6A52"
ACCENT       = "#E7F3EF"
BG_MAIN      = "#F6F9F8"
TEXT_MAIN    = "#152524"
BORDER       = "#CFE2DC"
INPUT_BG     = "#FFFFFF"
INPUT_FG     = "#1F2D2A"
DISABLED_FG_TTK = "#000000"
DISABLED_FG_TK  = "#000000"

def apply_theme(root):
    r = root
    r.configure(bg=BG_MAIN)
    r.option_add("*Background", BG_MAIN)
    r.option_add("*Foreground", TEXT_MAIN)
    r.option_add("*Font", "{Segoe UI} 10")
    r.option_add("*LabelFrame.background", ACCENT)
    r.option_add("*LabelFrame.foreground", TEXT_MAIN)
    r.option_add("*Frame.background", BG_MAIN)
    r.option_add("*Button.background", PRIMARY)
    r.option_add("*Button.foreground", "white")
    r.option_add("*Button.activeBackground", PRIMARY_DARK)
    r.option_add("*Button.activeForeground", "white")
    r.option_add("*Button.disabledforeground", DISABLED_FG_TK)
    r.option_add("*Entry.background", INPUT_BG)
    r.option_add("*Entry.foreground", INPUT_FG)
    r.option_add("*Entry.insertBackground", TEXT_MAIN)
    r.option_add("*Text.background", INPUT_BG)
    r.option_add("*Text.foreground", INPUT_FG)
    r.option_add("*Listbox.background", INPUT_BG)
    r.option_add("*Listbox.foreground", INPUT_FG)
    r.option_add("*Listbox.selectBackground", "#C7EEE2")
    r.option_add("*Listbox.selectForeground", "#0F201C")

    style = ttk.Style(r)
    try:
        style.theme_use("default")
    except Exception:
        pass

    style.configure("TFrame", background=BG_MAIN)

    style.configure("TLabelframe", background=ACCENT, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=ACCENT, foreground=TEXT_MAIN)

    style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN)

    style.configure(
        "TButton",
        background=PRIMARY,
        foreground="white",
        bordercolor=PRIMARY,
        focusthickness=3,
        focuscolor=PRIMARY,
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("active", PRIMARY_DARK), ("pressed", PRIMARY_DARK)],
        foreground=[("disabled", DISABLED_FG_TTK)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=INPUT_BG,
        background=INPUT_BG,
        foreground=INPUT_FG,
        arrowsize=14,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", INPUT_BG)],
        foreground=[("disabled", DISABLED_FG_TTK)],
    )

    style.configure("TEntry", fieldbackground=INPUT_BG, foreground=INPUT_FG)
    style.configure("TSpinbox", fieldbackground=INPUT_BG, foreground=INPUT_FG)

    style.configure("TNotebook", background=BG_MAIN, bordercolor=BORDER)
    style.configure("TNotebook.Tab", background=ACCENT, padding=(12, 6))
    style.map("TNotebook.Tab", background=[("selected", INPUT_BG)])

    style.configure(
        "Treeview",
        background=INPUT_BG,
        fieldbackground=INPUT_BG,
        foreground=INPUT_FG,
        bordercolor=BORDER,
    )
    style.map(
        "Treeview",
        background=[("selected", "#C7EEE2")],
        foreground=[("selected", "#0F201C")],
    )

def paint(window):
    try:
        window.configure(bg=BG_MAIN)
    except Exception:
        pass

    for w in window.winfo_children():
        cls = w.winfo_class()
        try:
            if cls in ("Labelframe",):
                w.configure(bg=ACCENT)
            elif cls in ("Frame",):
                w.configure(bg=BG_MAIN)
            elif cls in ("Label",):
                w.configure(bg=BG_MAIN, fg=TEXT_MAIN)
            elif cls in ("Button",):
                w.configure(
                    bg=PRIMARY, fg="white",
                    activebackground=PRIMARY_DARK, activeforeground="white",
                    disabledforeground=DISABLED_FG_TK,
                )
            elif cls in ("Entry", "Spinbox"):
                w.configure(bg=INPUT_BG, fg=INPUT_FG, insertbackground=TEXT_MAIN)
            elif cls in ("Text",):
                w.configure(bg=INPUT_BG, fg=INPUT_FG)
            elif cls in ("Listbox",):
                w.configure(
                    bg=INPUT_BG, fg=INPUT_FG,
                    selectbackground="#C7EEE2", selectforeground="#0F201C"
                )
        except Exception:
            pass
        paint(w)
