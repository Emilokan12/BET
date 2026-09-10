import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from collections import defaultdict
from datetime import datetime


def set_budget():
    amount = budget_entry.get().strip()
    if not amount:
        messagebox.showerror("Error", "Enter a budget amount")
        return
    try:
        budget_value = float(amount)
        if budget_value < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid positive budget amount")
        return

    with open("budget.txt", "w") as f:
        f.write(f"{budget_value:.2f}")
    messagebox.showinfo("Budget Set", f"₦{budget_value:,.2f} set as your budget")
    budget_entry.delete(0, tk.END)


def get_budget():
    if os.path.exists("budget.txt"):
        try:
            with open("budget.txt", "r") as f:
                val = float(f.read().strip())          
            messagebox.showinfo("Your Budget", f"₦{val:,.2f}")
        except ValueError:
            messagebox.showerror("Error", "Budget file is corrupted")
    else:
        messagebox.showwarning("No Budget", "No budget set yet")


def add_expense():
    amount_text = amount_entry.get().strip()
    category    = category_var.get()
    desc        = desc_entry.get().strip()
    date        = date_entry.get().strip()

    if not all([amount_text, desc, date]) or category == "Select a category":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        amount_value = float(amount_text)
        if amount_value <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid positive amount")
        return

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid date in YYYY-MM-DD format")
        return

    file_exists = os.path.exists("expenses.csv")
    with open("expenses.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["amount", "category", "desc", "date"])
        writer.writerow([f"{amount_value:.2f}", category, desc, date])

    messagebox.showinfo("Added", "Expense recorded successfully")
    for e in (amount_entry, desc_entry, date_entry):
        e.delete(0, tk.END)
    category_var.set("Select a category")


def view_expenses():
    if not os.path.exists("expenses.csv"):
        messagebox.showinfo("Info", "No expenses recorded yet.")
        return

    total        = 0
    invalid_rows = 0

    win = tk.Toplevel(root)
    win.title("All Expenses")
    win.geometry("580x420")
    win.resizable(False, False)

    tk.Label(win, text="Expense History",
             font=("TkDefaultFont", 12, "bold")).pack(pady=(12, 6))

    cols   = ("Category", "Description", "Amount (₦)", "Date")
    widths = {"Category": 110, "Description": 230, "Amount (₦)": 110, "Date": 120}

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))

    sb = ttk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")

    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        yscrollcommand=sb.set)
    sb.config(command=tree.yview)

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=widths[col], anchor="center")
    tree.pack(fill="both", expand=True)

    with open("expenses.csv", "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("amount", ""))
            except (ValueError, TypeError):
                invalid_rows += 1
                continue
            total += amount
            tree.insert("", tk.END,
                        values=(row.get("category", ""),
                                row.get("desc", ""),
                                f"{amount:,.2f}",
                                row.get("date", "")))

    footer = tk.Frame(win)
    footer.pack(fill="x", padx=12, pady=6)
    tk.Label(footer, text=f"Total Spent: ₦{total:,.2f}",
             font=("TkDefaultFont", 10, "bold")).pack(side="left")

    if os.path.exists("budget.txt"):
        try:
            with open("budget.txt", "r") as f:
                budget_value = float(f.read().strip())
            remaining = budget_value - total
            tk.Label(footer,
                     text=f"Remaining: ₦{remaining:,.2f}",
                     font=("TkDefaultFont", 10, "bold")).pack(side="right")
        except ValueError:
            tk.Label(footer, text="Budget file is invalid",
                     font=("TkDefaultFont", 10, "bold")).pack(side="right")

    if invalid_rows:
        messagebox.showwarning("Warning",
                               f"{invalid_rows} invalid expense row(s) were skipped.")


def monthly_summary():
    month = month_entry.get().strip()
    if not month:
        messagebox.showerror("Error", "Enter a month  e.g. 2025-11")
        return

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid month in YYYY-MM format")
        return

    if not os.path.exists("expenses.csv"):
        messagebox.showinfo("Info", "No expenses recorded yet.")
        return

    summary      = defaultdict(float)
    total        = 0
    invalid_rows = 0

    with open("expenses.csv", "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("date", "").startswith(month):
                continue
            try:
                amt = float(row.get("amount", ""))
            except (ValueError, TypeError):
                invalid_rows += 1
                continue
            summary[row.get("category", "Uncategorized")] += amt
            total += amt

    if not summary:
        messagebox.showinfo("No Data", f"No expenses found for {month}")
        return

    win = tk.Toplevel(root)
    win.title(f"Summary — {month}")
    win.geometry("340x300")
    win.resizable(False, False)

    tk.Label(win, text=f"{month} Summary",
             font=("TkDefaultFont", 12, "bold")).pack(pady=(12, 8))

    for cat, amt in sorted(summary.items(), key=lambda x: x[1], reverse=True):
        row_f = tk.Frame(win)
        row_f.pack(fill="x", padx=20, pady=3)
        tk.Label(row_f, text=cat).pack(side="left")
        tk.Label(row_f, text=f"₦{amt:,.2f}",
                 font=("TkDefaultFont", 10, "bold")).pack(side="right")

    tk.Frame(win, height=1, relief="sunken", bd=1).pack(fill="x", padx=20, pady=8)

    total_row = tk.Frame(win)
    total_row.pack(fill="x", padx=20)
    tk.Label(total_row, text="Total Spent",
             font=("TkDefaultFont", 10, "bold")).pack(side="left")
    tk.Label(total_row, text=f"₦{total:,.2f}",
             font=("TkDefaultFont", 10, "bold")).pack(side="right")

    if invalid_rows:
        messagebox.showwarning("Warning",
                               f"{invalid_rows} invalid row(s) were ignored in the summary.")


#Root window

root = tk.Tk()
root.title("BET — Budget & Expense Tracker")
root.geometry("460x480")
root.resizable(False, False)

# BUG FIX: original header label had no text= argument → invisible widget
tk.Label(root, text="Budget & Expense Tracker",
         font=("TkDefaultFont", 14, "bold")).pack(pady=(14, 4))
tk.Frame(root, height=1, relief="sunken", bd=1).pack(fill="x", padx=16, pady=(4, 0))

#Notebook

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=16, pady=10)

#Budget

f_budget = tk.Frame(notebook, padx=20, pady=20)
notebook.add(f_budget, text="  Budget  ")

tk.Label(f_budget, text="Set / View Budget",
         font=("TkDefaultFont", 11, "bold")).grid(
             row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

tk.Label(f_budget, text="Budget Amount (₦):").grid(
    row=1, column=0, sticky="w", pady=5)
budget_entry = tk.Entry(f_budget, width=28)
budget_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

btn_frame1 = tk.Frame(f_budget)
btn_frame1.grid(row=2, column=0, columnspan=2, sticky="w", pady=(14, 0))
tk.Button(btn_frame1, text="Set Budget",  command=set_budget,  width=14).pack(side="left", padx=(0, 8))
tk.Button(btn_frame1, text="View Budget", command=get_budget,  width=14).pack(side="left")

f_budget.columnconfigure(1, weight=1)

# Expenses 

f_expenses = tk.Frame(notebook, padx=20, pady=20)
notebook.add(f_expenses, text="  Expenses  ")

tk.Label(f_expenses, text="Add Expense",
         font=("TkDefaultFont", 11, "bold")).grid(
             row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

tk.Label(f_expenses, text="Amount (₦):").grid(row=1, column=0, sticky="w", pady=5)
amount_entry = tk.Entry(f_expenses, width=28)
amount_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

tk.Label(f_expenses, text="Category:").grid(row=2, column=0, sticky="w", pady=5)
CATEGORIES = [
    "Food", "Transport", "Rent", "Utilities", "Healthcare",
    "Education", "Entertainment", "Clothing", "Savings", "Miscellaneous",
]
category_var   = tk.StringVar(value="Select a category")
category_entry = ttk.Combobox(f_expenses, textvariable=category_var,
                               values=CATEGORIES, state="readonly", width=26)
category_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

tk.Label(f_expenses, text="Description:").grid(row=3, column=0, sticky="w", pady=5)
desc_entry = tk.Entry(f_expenses, width=28)
desc_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

tk.Label(f_expenses, text="Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=5)
date_entry = tk.Entry(f_expenses, width=28)
date_entry.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)

btn_frame2 = tk.Frame(f_expenses)
btn_frame2.grid(row=5, column=0, columnspan=2, sticky="w", pady=(14, 0))
tk.Button(btn_frame2, text="Add Expense", command=add_expense,   width=14).pack(side="left", padx=(0, 8))
tk.Button(btn_frame2, text="View All",    command=view_expenses, width=14).pack(side="left")

f_expenses.columnconfigure(1, weight=1)

#Summary 

f_summary = tk.Frame(notebook, padx=20, pady=20)
notebook.add(f_summary, text="  Summary  ")

tk.Label(f_summary, text="Monthly Summary",
         font=("TkDefaultFont", 11, "bold")).grid(
             row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

tk.Label(f_summary, text="Month (YYYY-MM):").grid(row=1, column=0, sticky="w", pady=5)
month_entry = tk.Entry(f_summary, width=28)
month_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

tk.Label(f_summary, text="e.g. 2025-11",
         font=("TkDefaultFont", 8)).grid(row=2, column=1, sticky="w", padx=(10, 0))

btn_frame3 = tk.Frame(f_summary)
btn_frame3.grid(row=3, column=0, columnspan=2, sticky="w", pady=(14, 0))
tk.Button(btn_frame3, text="View Summary", command=monthly_summary, width=16).pack(side="left")

f_summary.columnconfigure(1, weight=1)

#Footer 
tk.Frame(root, height=1, relief="sunken", bd=1).pack(fill="x", padx=16)
footer = tk.Frame(root)
footer.pack(fill="x", padx=16, pady=(8, 12))
tk.Button(footer, text="Exit", command=root.destroy, width=10).pack(side="right")

root.mainloop()
