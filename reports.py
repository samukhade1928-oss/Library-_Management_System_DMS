import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


def open_reports():

    root = tk.Toplevel()
    root.title("Library Reports")
    root.geometry("1100x650")
    root.configure(bg="#F1F5F9")

    tk.Label(
        root,
        text="LIBRARY REPORTS",
        font=("Arial", 22, "bold"),
        bg="#172554",
        fg="white",
        pady=20
    ).pack(fill="x")

    # Report selection
    control_frame = tk.Frame(root, bg="#F1F5F9")
    control_frame.pack(fill="x", padx=20, pady=20)

    tk.Label(
        control_frame,
        text="Select Report:",
        font=("Arial", 12, "bold"),
        bg="#F1F5F9"
    ).pack(side="left", padx=10)

    report_var = tk.StringVar(value="Book Inventory")

    report_options = [
        "Book Inventory",
        "Student Records",
        "Currently Issued Books",
        "Returned Books",
        "Overdue Books",
        "Fine Collection"
    ]

    report_menu = ttk.Combobox(
        control_frame,
        textvariable=report_var,
        values=report_options,
        state="readonly",
        width=30
    )
    report_menu.pack(side="left", padx=10)

    # Table
    table_frame = tk.Frame(root, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = ttk.Treeview(table_frame, show="headings")

    scrollbar_y = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    scrollbar_x = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    def load_report():

        selected = report_var.get()

        connection = connect_db()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            queries = {

                "Book Inventory": """
                    SELECT book_id, book_name, author, category,
                           total_quantity, available_quantity
                    FROM books
                    ORDER BY book_id
                """,

                "Student Records": """
                    SELECT student_id, student_name, email, phone
                    FROM students
                    ORDER BY student_id
                """,

                "Currently Issued Books": """
                    SELECT ir.issue_id, b.book_name,
                           s.student_name, ir.issue_date, ir.due_date
                    FROM issue_records ir
                    JOIN books b ON ir.book_id = b.book_id
                    JOIN students s ON ir.student_id = s.student_id
                    WHERE ir.return_date IS NULL
                    ORDER BY ir.due_date
                """,

                "Returned Books": """
                    SELECT ir.issue_id, b.book_name,
                           s.student_name, ir.issue_date,
                           ir.due_date, ir.return_date, ir.fine
                    FROM issue_records ir
                    JOIN books b ON ir.book_id = b.book_id
                    JOIN students s ON ir.student_id = s.student_id
                    WHERE ir.return_date IS NOT NULL
                    ORDER BY ir.return_date DESC
                """,

                "Overdue Books": """
                    SELECT ir.issue_id, b.book_name,
                           s.student_name, ir.issue_date,
                           ir.due_date,
                           DATEDIFF(CURDATE(), ir.due_date) AS late_days,
                           GREATEST(DATEDIFF(CURDATE(), ir.due_date), 0) * 5
                           AS estimated_fine
                    FROM issue_records ir
                    JOIN books b ON ir.book_id = b.book_id
                    JOIN students s ON ir.student_id = s.student_id
                    WHERE ir.return_date IS NULL
                    AND ir.due_date < CURDATE()
                    ORDER BY ir.due_date
                """,

                "Fine Collection": """
                    SELECT ir.issue_id, b.book_name,
                           s.student_name, ir.return_date, ir.fine
                    FROM issue_records ir
                    JOIN books b ON ir.book_id = b.book_id
                    JOIN students s ON ir.student_id = s.student_id
                    WHERE ir.return_date IS NOT NULL
                    AND ir.fine > 0
                    ORDER BY ir.return_date DESC
                """
            }

            cursor.execute(queries[selected])

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            tree.delete(*tree.get_children())
            tree["columns"] = columns

            for column in columns:
                tree.heading(column, text=column.replace("_", " ").title())
                tree.column(column, width=150, anchor="center")

            for row in rows:
                tree.insert("", "end", values=row)

            if not rows:
                messagebox.showinfo(
                    "Report",
                    "No records found for this report."
                )

        except Exception as e:
            messagebox.showerror(
                "Report Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()

            if connection.is_connected():
                connection.close()

    tk.Button(
        control_frame,
        text="Generate Report",
        font=("Arial", 11, "bold"),
        bg="#2563EB",
        fg="white",
        padx=15,
        pady=8,
        relief="flat",
        command=load_report
    ).pack(side="left", padx=15)

    load_report()