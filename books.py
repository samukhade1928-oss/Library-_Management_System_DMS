import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


def open_books():

    root = tk.Toplevel()
    root.title("Library Management - Book Management")
    root.geometry("1150x700")
    root.configure(bg="#f1f5f9")

    # ================= HEADER =================

    tk.Label(
        root,
        text="BOOK MANAGEMENT",
        font=("Arial", 22, "bold"),
        bg="#172033",
        fg="white",
        pady=20
    ).pack(fill="x")

    # ================= FORM =================

    form = tk.Frame(root, bg="white", padx=20, pady=20)
    form.pack(fill="x", padx=20, pady=20)

    labels = [
        "Book Name",
        "Author",
        "Category",
        "Total Quantity",
        "Available Quantity"
    ]

    entries = {}

    for i, label in enumerate(labels):

        tk.Label(
            form,
            text=label,
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=i, padx=8, pady=8)

        entry = tk.Entry(form, width=18, font=("Arial", 11))
        entry.grid(row=1, column=i, padx=8, pady=8, ipady=5)

        entries[label] = entry

    # ================= SEARCH =================

    search_frame = tk.Frame(root, bg="#f1f5f9")
    search_frame.pack(fill="x", padx=20)

    tk.Label(
        search_frame,
        text="Search Book:",
        font=("Arial", 11, "bold"),
        bg="#f1f5f9"
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=35, font=("Arial", 11))
    search_entry.pack(side="left", padx=10, ipady=5)

    # ================= TABLE =================

    columns = (
        "ID",
        "Book Name",
        "Author",
        "Category",
        "Total Quantity",
        "Available Quantity"
    )

    table_frame = tk.Frame(root)
    table_frame.pack(fill="both", expand=True, padx=20, pady=15)

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=13
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=175, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================= DATABASE LOAD =================

    def load_books(keyword=""):

        for item in table.get_children():
            table.delete(item)

        db = connect_db()

        if not db:
            messagebox.showerror("Error", "Database connection failed.")
            return

        cursor = db.cursor()

        try:

            query = """
                SELECT * FROM books
                WHERE book_name LIKE %s
                OR author LIKE %s
                OR category LIKE %s
                ORDER BY book_id
            """

            search = f"%{keyword}%"

            cursor.execute(query, (search, search, search))

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            cursor.close()
            db.close()

    # ================= CLEAR FORM =================

    def clear_fields():

        for entry in entries.values():
            entry.delete(0, tk.END)

        table.selection_remove(table.selection())

    # ================= VALIDATION =================

    def get_form_data():

        name = entries["Book Name"].get().strip()
        author = entries["Author"].get().strip()
        category = entries["Category"].get().strip()

        if not name or not author:
            raise ValueError("Book name and author are required.")

        total = int(entries["Total Quantity"].get())
        available = int(entries["Available Quantity"].get())

        if total < 0:
            raise ValueError("Total quantity cannot be negative.")

        if available < 0 or available > total:
            raise ValueError(
                "Available quantity must be between 0 and total quantity."
            )

        return name, author, category, total, available

    # ================= ADD BOOK =================

    def add_book():

        try:

            data = get_form_data()

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            cursor = db.cursor()

            cursor.execute(
                """
                INSERT INTO books
                (book_name, author, category,
                 total_quantity, available_quantity)
                VALUES (%s, %s, %s, %s, %s)
                """,
                data
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book added successfully!"
            )

            clear_fields()
            load_books()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    # ================= SELECT BOOK =================

    def select_book(event):

        selected = table.focus()

        if selected:

            values = table.item(selected, "values")

            for entry, value in zip(entries.values(), values[1:]):
                entry.delete(0, tk.END)
                entry.insert(0, value)

    table.bind("<<TreeviewSelect>>", select_book)

    # ================= UPDATE BOOK =================

    def update_book():

        selected = table.focus()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a book first."
            )
            return

        book_id = table.item(selected, "values")[0]

        try:

            data = get_form_data()

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            cursor = db.cursor()

            cursor.execute(
                """
                UPDATE books
                SET book_name=%s,
                    author=%s,
                    category=%s,
                    total_quantity=%s,
                    available_quantity=%s
                WHERE book_id=%s
                """,
                (*data, book_id)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book updated successfully!"
            )

            clear_fields()
            load_books()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    # ================= DELETE BOOK =================

    def delete_book():

        selected = table.focus()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a book first."
            )
            return

        book_id = table.item(selected, "values")[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Do you really want to delete this book?"
        )

        if not confirm:
            return

        db = connect_db()

        if not db:
            messagebox.showerror("Error", "Database connection failed.")
            return

        cursor = db.cursor()

        try:

            cursor.execute(
                "DELETE FROM books WHERE book_id=%s",
                (book_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book deleted successfully!"
            )

            clear_fields()
            load_books()

        except Exception as e:

            db.rollback()

            messagebox.showerror(
                "Delete Failed",
                "This book may have existing issue records.\n" + str(e)
            )

        finally:
            cursor.close()
            db.close()

    # ================= SEARCH BOOK =================

    def search_book():

        keyword = search_entry.get().strip()
        load_books(keyword)

    # ================= BUTTONS =================

    button_frame = tk.Frame(root, bg="#f1f5f9")
    button_frame.pack(pady=12)

    buttons = [

        ("ADD BOOK", add_book, "#2563eb"),

        ("UPDATE BOOK", update_book, "#16a34a"),

        ("DELETE BOOK", delete_book, "#dc2626"),

        ("SEARCH", search_book, "#7c3aed"),

        ("SHOW ALL", lambda: load_books(), "#475569"),

        ("CLEAR", clear_fields, "#64748b")

    ]

    for text, command, color in buttons:

        tk.Button(
            button_frame,
            text=text,
            command=command,
            bg=color,
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            bd=0,
            padx=15,
            pady=10
        ).pack(side="left", padx=5)

    load_books()