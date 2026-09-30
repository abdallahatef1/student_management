# ---------------------------------------------------------
# PROJECT NAME : Student Management System (Tkinter) - Redesigned UI
# CREATED BY   : menna atef abd el hamid
# FILES USED   : marks.json (students), users.json (logins)
# ---------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

MARKS_FILE = "marks.json"
USERS_FILE = "users.json"

marks = []
users = {}

# ---------------------------------------------------------
# THEME
# ---------------------------------------------------------
BG = "#0F172A"        # window background
CARD = "#1E293B"      # cards / panels
CARD_ALT = "#243247"  # zebra rows
BORDER = "#334155"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
ACCENT = "#6366F1"
ACCENT_HOVER = "#818CF8"
GREEN = "#22C55E"
AMBER = "#F59E0B"
RED = "#EF4444"

FONT = "Segoe UI"


def f(size=10, weight="normal"):
    return (FONT, size, weight)


def make_button(parent, text, command, color=ACCENT, hover=ACCENT_HOVER, width=None):
    b = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                  activebackground=hover, activeforeground="white",
                  relief="flat", bd=0, cursor="hand2", font=f(10, "bold"),
                  padx=16, pady=8, width=width)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


def make_entry(parent, show=None, width=28):
    holder = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    e = tk.Entry(holder, bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat",
                 font=f(11), width=width, show=show)
    e.pack(ipady=6, padx=1, pady=1)
    e.bind("<FocusIn>", lambda ev: holder.config(bg=ACCENT))
    e.bind("<FocusOut>", lambda ev: holder.config(bg=BORDER))
    e.holder = holder
    return e


def center(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


def apply_styles(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure("Treeview", background=CARD, fieldbackground=CARD,
                foreground=TEXT, rowheight=34, borderwidth=0, font=f(10))
    s.configure("Treeview.Heading", background=BG, foreground=MUTED,
                font=f(9, "bold"), relief="flat", padding=8, borderwidth=0)
    s.map("Treeview", background=[("selected", ACCENT)],
          foreground=[("selected", "white")])
    s.map("Treeview.Heading", background=[("active", BG)])
    s.configure("Vertical.TScrollbar", background=BORDER, troughcolor=CARD,
                bordercolor=CARD, arrowcolor=MUTED, relief="flat")


# ---------------------------------------------------------
# FILE LOAD / SAVE
# ---------------------------------------------------------
def save_marks():
    with open(MARKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(marks, fh, indent=4)


def load_marks():
    global marks
    try:
        with open(MARKS_FILE, "r", encoding="utf-8") as fh:
            marks = json.load(fh)
    except (OSError, ValueError):
        marks = []


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as fh:
        json.dump(users, fh, indent=4)


def load_users():
    global users
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as fh:
            users = json.load(fh)
    except (OSError, ValueError):
        users = {}


def ensure_default_user():
    load_users()
    if "admin" not in users:
        users["admin"] = "1234"
        save_users()


def generate_student_id():
    nums = []
    for m in marks:
        sid = m.get("ID", "")
        if sid.startswith("STD"):
            try:
                nums.append(int(sid[3:]))
            except ValueError:
                pass
    return f"STD{(max(nums) + 1 if nums else 1):03d}"


# ---------------------------------------------------------
# STUDENT FORM (used for both Add and Update)
# ---------------------------------------------------------
def student_form(app, rec=None):
    editing = rec is not None
    win = tk.Toplevel(app.root)
    win.title("Update Student" if editing else "Add Student")
    win.configure(bg=BG)
    win.resizable(False, False)
    center(win, 420, 500)
    win.transient(app.root)
    win.grab_set()

    card = tk.Frame(win, bg=CARD, padx=28, pady=24)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="Update Student" if editing else "New Student",
             bg=CARD, fg=TEXT, font=f(16, "bold")).pack(anchor="w")
    tk.Label(card, text="Fill in the details below", bg=CARD, fg=MUTED,
             font=f(9)).pack(anchor="w", pady=(0, 14))

    entries = {}
    for key, label in [("name", "Full name"), ("grade", "Grade"),
                       ("subject", "Subject"), ("mark", "Mark (0-100)")]:
        tk.Label(card, text=label, bg=CARD, fg=MUTED, font=f(9)).pack(anchor="w", pady=(6, 2))
        e = make_entry(card)
        e.holder.pack(fill="x")
        if editing:
            e.insert(0, rec[key])
        entries[key] = e
    entries["name"].focus_set()

    def submit(event=None):
        name = entries["name"].get().strip()
        grade = entries["grade"].get().strip()
        subject = entries["subject"].get().strip()
        if not name or not grade or not subject:
            messagebox.showerror("Missing data", "All fields are required.", parent=win)
            return
        try:
            mark = int(entries["mark"].get().strip())
            if not 0 <= mark <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid mark", "Mark must be a number from 0 to 100.", parent=win)
            return

        if editing:
            rec.update(name=name, grade=grade, subject=subject, mark=mark)
            app.set_status(f"Updated {rec['ID']}", GREEN)
        else:
            sid = generate_student_id()
            marks.append({"ID": sid, "name": name, "grade": grade,
                          "subject": subject, "mark": mark})
            app.set_status(f"Added {sid} - {name}", GREEN)
        save_marks()
        app.refresh()
        win.destroy()

    win.bind("<Return>", submit)
    row = tk.Frame(card, bg=CARD)
    row.pack(fill="x", pady=(20, 0))
    make_button(row, "Save", submit).pack(side="left", expand=True, fill="x", padx=(0, 6))
    make_button(row, "Cancel", win.destroy, color=BORDER, hover="#475569").pack(
        side="left", expand=True, fill="x", padx=(6, 0))


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------
class Dashboard:
    COLS = ("ID", "name", "grade", "subject", "mark")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Management System")
        self.root.configure(bg=BG)
        self.root.minsize(820, 520)
        center(self.root, 1000, 640)
        apply_styles(self.root)
        self.build_header()
        self.build_stats()
        self.build_toolbar()
        self.build_table()
        self.build_status()
        self.refresh()
        self.root.mainloop()

    # ---- header
    def build_header(self):
        h = tk.Frame(self.root, bg=BG)
        h.pack(fill="x", padx=28, pady=(22, 6))
        tk.Label(h, text="Student Management", bg=BG, fg=TEXT,
                 font=f(20, "bold")).pack(anchor="w")
        tk.Label(h, text="Track marks, performance and records in one place",
                 bg=BG, fg=MUTED, font=f(10)).pack(anchor="w")

    # ---- stat cards
    def build_stats(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28, pady=10)
        self.stat_labels = {}
        for i, (key, title, color) in enumerate([
                ("count", "STUDENTS", ACCENT), ("avg", "AVERAGE", AMBER),
                ("max", "HIGHEST", GREEN), ("min", "LOWEST", RED)]):
            row.columnconfigure(i, weight=1, uniform="stat")
            card = tk.Frame(row, bg=CARD)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))
            tk.Frame(card, bg=color, height=3).pack(fill="x")
            tk.Label(card, text=title, bg=CARD, fg=MUTED,
                     font=f(8, "bold")).pack(anchor="w", padx=16, pady=(12, 0))
            val = tk.Label(card, text="0", bg=CARD, fg=TEXT, font=f(22, "bold"))
            val.pack(anchor="w", padx=16, pady=(0, 12))
            self.stat_labels[key] = val

    # ---- toolbar
    def build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=28, pady=(6, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        holder = tk.Frame(bar, bg=BORDER, padx=1, pady=1)
        holder.pack(side="left")
        tk.Label(holder, text=" \U0001F50D", bg=CARD, fg=MUTED, font=f(11)).pack(side="left", ipady=6)
        se = tk.Entry(holder, textvariable=self.search_var, bg=CARD, fg=TEXT,
                      insertbackground=TEXT, relief="flat", font=f(11), width=26)
        se.pack(side="left", ipady=6)
        tk.Label(bar, text="  Search by name", bg=BG, fg=MUTED, font=f(9)).pack(side="left")

        make_button(bar, "Delete", self.delete, RED, "#F87171").pack(side="right", padx=(8, 0))
        make_button(bar, "Edit", self.update, BORDER, "#475569").pack(side="right", padx=(8, 0))
        make_button(bar, "+ Add Student", lambda: student_form(self)).pack(side="right")

    # ---- table
    def build_table(self):
        wrap = tk.Frame(self.root, bg=CARD)
        wrap.pack(expand=True, fill="both", padx=28, pady=(0, 6))
        self.tree = ttk.Treeview(wrap, columns=self.COLS, show="headings", selectmode="browse")
        for c, w in zip(self.COLS, (90, 260, 100, 200, 90)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="w" if c in ("name", "subject") else "center")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both")
        self.tree.tag_configure("odd", background=CARD)
        self.tree.tag_configure("even", background=CARD_ALT)
        self.tree.tag_configure("top", foreground=GREEN)
        self.tree.tag_configure("fail", foreground=RED)
        self.tree.bind("<Double-1>", lambda e: self.update())
        self.tree.bind("<Delete>", lambda e: self.delete())

    # ---- status bar
    def build_status(self):
        self.status = tk.Label(self.root, text="Ready", bg=BG, fg=MUTED,
                               font=f(9), anchor="w")
        self.status.pack(fill="x", padx=28, pady=(0, 12))

    def set_status(self, msg, color=MUTED):
        self.status.config(text=msg, fg=color)

    # ---- data actions
    def refresh(self):
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for m in marks:
            if query and query not in m["name"].lower():
                continue
            tags = ["even" if shown % 2 else "odd"]
            if m["mark"] >= 85:
                tags.append("top")
            elif m["mark"] < 50:
                tags.append("fail")
            self.tree.insert("", "end", iid=m["ID"], tags=tags,
                             values=(m["ID"], m["name"], m["grade"], m["subject"], m["mark"]))
            shown += 1
        if query:
            self.set_status(f"{shown} result(s) for '{query}'")
        self.refresh_summary()

    def refresh_summary(self):
        n = len(marks)
        vals = [m["mark"] for m in marks]
        self.stat_labels["count"].config(text=str(n))
        self.stat_labels["avg"].config(text=f"{sum(vals) / n:.1f}" if n else "0")
        self.stat_labels["max"].config(text=str(max(vals)) if n else "0")
        self.stat_labels["min"].config(text=str(min(vals)) if n else "0")

    def selected_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select a student", "Please select a student row first.")
            return None
        return next((r for r in marks if r["ID"] == sel[0]), None)

    def update(self):
        rec = self.selected_record()
        if rec:
            student_form(self, rec)

    def delete(self):
        rec = self.selected_record()
        if rec and messagebox.askyesno("Confirm delete", f"Delete {rec['name']} ({rec['ID']})?"):
            marks.remove(rec)
            save_marks()
            self.refresh()
            self.set_status(f"Deleted {rec['ID']}", RED)


def main_app():
    Dashboard()


# ---------------------------------------------------------
# LOGIN / REGISTER
# ---------------------------------------------------------
def register_window(parent):
    win = tk.Toplevel(parent)
    win.title("Register")
    win.configure(bg=BG)
    win.resizable(False, False)
    center(win, 380, 400)
    win.transient(parent)
    win.grab_set()

    card = tk.Frame(win, bg=CARD, padx=28, pady=24)
    card.pack(fill="both", expand=True, padx=20, pady=20)
    tk.Label(card, text="Create account", bg=CARD, fg=TEXT, font=f(16, "bold")).pack(anchor="w")
    tk.Label(card, text="Choose a username and password", bg=CARD, fg=MUTED,
             font=f(9)).pack(anchor="w", pady=(0, 12))

    tk.Label(card, text="Username", bg=CARD, fg=MUTED, font=f(9)).pack(anchor="w", pady=(4, 2))
    u_entry = make_entry(card)
    u_entry.holder.pack(fill="x")
    tk.Label(card, text="Password", bg=CARD, fg=MUTED, font=f(9)).pack(anchor="w", pady=(10, 2))
    p_entry = make_entry(card, show="\u2022")
    p_entry.holder.pack(fill="x")
    u_entry.focus_set()

    def do_register(event=None):
        u, p = u_entry.get().strip(), p_entry.get().strip()
        load_users()
        if not u or not p:
            messagebox.showerror("Error", "Username and password are required.", parent=win)
        elif u in users:
            messagebox.showerror("Error", "User already exists.", parent=win)
        else:
            users[u] = p
            save_users()
            messagebox.showinfo("Success", "Account created. You can log in now.", parent=win)
            win.destroy()

    win.bind("<Return>", do_register)
    make_button(card, "Register", do_register).pack(fill="x", pady=(20, 0))


def login_window():
    load_users()
    ensure_default_user()

    win = tk.Tk()
    win.title("Login")
    win.configure(bg=BG)
    win.resizable(False, False)
    center(win, 420, 540)

    tk.Label(win, text="\U0001F393", bg=BG, fg=ACCENT, font=f(40)).pack(pady=(34, 0))
    tk.Label(win, text="Welcome back", bg=BG, fg=TEXT, font=f(20, "bold")).pack()
    tk.Label(win, text="Sign in to Student Management", bg=BG, fg=MUTED,
             font=f(10)).pack(pady=(0, 18))

    card = tk.Frame(win, bg=CARD, padx=28, pady=24)
    card.pack(fill="x", padx=36)

    tk.Label(card, text="Username", bg=CARD, fg=MUTED, font=f(9)).pack(anchor="w", pady=(0, 2))
    user_e = make_entry(card)
    user_e.holder.pack(fill="x")
    tk.Label(card, text="Password", bg=CARD, fg=MUTED, font=f(9)).pack(anchor="w", pady=(10, 2))
    pass_e = make_entry(card, show="\u2022")
    pass_e.holder.pack(fill="x")
    user_e.focus_set()

    error = tk.Label(card, text="", bg=CARD, fg=RED, font=f(9))
    error.pack(anchor="w", pady=(8, 0))

    def do_login(event=None):
        u, p = user_e.get().strip(), pass_e.get().strip()
        load_users()
        if u in users and users[u] == p:
            win.destroy()
            main_app()
        else:
            error.config(text="Invalid username or password")

    win.bind("<Return>", do_login)
    make_button(card, "Sign In", do_login).pack(fill="x", pady=(8, 8))
    make_button(card, "Create account", lambda: register_window(win),
                BORDER, "#475569").pack(fill="x")

    tk.Button(win, text="Quit", command=win.destroy, bg=BG, fg=MUTED,
              activebackground=BG, activeforeground=TEXT, relief="flat", bd=0,
              cursor="hand2", font=f(9)).pack(pady=14)

    win.mainloop()


# ---------------------------------------------------------
# START APP
# ---------------------------------------------------------
if __name__ == "__main__":
    load_marks()
    ensure_default_user()
    login_window()