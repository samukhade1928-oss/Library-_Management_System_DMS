import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import date, timedelta


FINE_PER_DAY = 5
BORROW_DAYS = 14


def open_issue():

    root = tk.Toplevel()
    root.title("Issue Books")
    root.geometry("1100x650")
    root.configure(bg="#f1f5f9")

    tk.Label(
        root,
        text="ISSUE BOOKS",
        font=("Arial", 22, "bold"),
        bg="#172033",
        fg="white",
        pady=20
    ).pack(fill="x")

    form = tk.Frame(root, bg="white", padx=30, pady=30)
    form.pack(fill="x", padx=30, pady=25)

    tk.Label(form, text="Book ID", bg="white").grid(row=0, column=0)
    book_entry = tk.Entry(form, width=25)
    book_entry.grid(row=1, column=0, padx=20, pady=10)

    tk.Label(form, text="Student ID", bg="white").grid(row=0, column=1)
    student_entry = tk.Entry(form, width=25)
    student_entry.grid(row=1, column=1, padx=20, pady=10)

    def issue_book():

        db = None
        cursor = None

        try:

            book_id = int(book_entry.get())
            student_id = int(student_entry.get())

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            db.start_transaction()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT available_quantity
                FROM books
                WHERE book_id = %s
                FOR UPDATE
                """,
                (book_id,)
            )

            book = cursor.fetchone()

            if not book:
                raise ValueError("Book not found.")

            if book[0] <= 0:
                raise ValueError("Book is not available.")

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """,
                (student_id,)
            )

            if not cursor.fetchone():
                raise ValueError("Student not found.")

            issue_date = date.today()
            due_date = issue_date + timedelta(days=BORROW_DAYS)

            cursor.execute(
                """
                INSERT INTO issue_records
                (book_id, student_id, issue_date, due_date, return_date, fine)
                VALUES (%s, %s, %s, %s, NULL, 0)
                """,
                (book_id, student_id, issue_date, due_date)
            )

            cursor.execute(
                """
                UPDATE books
                SET available_quantity = available_quantity - 1
                WHERE book_id = %s
                """,
                (book_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                f"Book issued successfully!\nDue Date: {due_date}"
            )

            book_entry.delete(0, tk.END)
            student_entry.delete(0, tk.END)

        except ValueError as e:

            if db:
                db.rollback()

            messagebox.showerror("Invalid Input", str(e))

        except Exception as e:

            if db:
                db.rollback()

            messagebox.showerror("Error", str(e))

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    tk.Button(
        form,
        text="ISSUE BOOK",
        command=issue_book,
        bg="#2563eb",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=25,
        pady=10
    ).grid(row=2, column=0, columnspan=2, pady=20)

    root.mainloop()


def open_return():

    root = tk.Toplevel()
    root.title("Return Books")
    root.geometry("1100x650")
    root.configure(bg="#f1f5f9")

    tk.Label(
        root,
        text="RETURN BOOKS",
        font=("Arial", 22, "bold"),
        bg="#172033",
        fg="white",
        pady=20
    ).pack(fill="x")

    columns = (
        "Issue ID",
        "Book ID",
        "Student ID",
        "Issue Date",
        "Due Date"
    )

    table = ttk.Treeview(
        root,
        columns=columns,
        show="headings",
        height=15
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=180, anchor="center")

    table.pack(fill="both", expand=True, padx=25, pady=25)

    def load_issued_books():

        for item in table.get_children():
            table.delete(item)

        db = connect_db()

        if not db:
            messagebox.showerror("Error", "Database connection failed.")
            return

        cursor = db.cursor()

        try:

            cursor.execute(
                """
                SELECT issue_id, book_id, student_id,
                       issue_date, due_date
                FROM issue_records
                WHERE return_date IS NULL
                ORDER BY issue_id
                """
            )

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        finally:
            cursor.close()
            db.close()

    def return_book():

        selected = table.focus()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Select an issued book first."
            )
            return

        issue_id = table.item(selected, "values")[0]

        db = None
        cursor = None

        try:

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            db.start_transaction()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT book_id, due_date, return_date
                FROM issue_records
                WHERE issue_id = %s
                FOR UPDATE
                """,
                (issue_id,)
            )

            record = cursor.fetchone()

            if not record:
                raise ValueError("Issue record not found.")

            book_id, due_date, return_date = record

            if return_date is not None:
                raise ValueError("Book has already been returned.")

            today = date.today()

            if isinstance(due_date, str):
                due_date = date.fromisoformat(due_date)

            late_days = max(0, (today - due_date).days)
            fine = late_days * FINE_PER_DAY

            cursor.execute(
                """
                UPDATE issue_records
                SET return_date = %s, fine = %s
                WHERE issue_id = %s
                """,
                (today, fine, issue_id)
            )

            cursor.execute(
                """
                UPDATE books
                SET available_quantity = available_quantity + 1
                WHERE book_id = %s
                """,
                (book_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Return Successful",
                f"Book returned successfully!\n"
                f"Late Days: {late_days}\n"
                f"Fine: Rs. {fine:.2f}"
            )

            load_issued_books()

        except Exception as e:

            if db:
                db.rollback()

            messagebox.showerror("Return Error", str(e))

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    tk.Button(
        root,
        text="RETURN SELECTED BOOK",
        command=return_book,
        bg="#16a34a",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=25,
        pady=12
    ).pack(pady=10)

    load_issued_books()
    root.mainloop()