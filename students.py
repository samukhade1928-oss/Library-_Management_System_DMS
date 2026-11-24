import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


def open_students():

    root = tk.Toplevel()
    root.title("Library Management - Student Management")
    root.geometry("1100x680")
    root.configure(bg="#f1f5f9")

    # ================= HEADER =================

    tk.Label(
        root,
        text="STUDENT MANAGEMENT",
        font=("Arial", 22, "bold"),
        bg="#172033",
        fg="white",
        pady=20
    ).pack(fill="x")

    # ================= FORM =================

    form = tk.Frame(root, bg="white", padx=25, pady=25)
    form.pack(fill="x", padx=20, pady=20)

    labels = [
        "Student Name",
        "Email",
        "Phone"
    ]

    entries = {}

    for i, label in enumerate(labels):

        tk.Label(
            form,
            text=label,
            font=("Arial", 11, "bold"),
            bg="white"
        ).grid(row=0, column=i, padx=20, pady=8)

        entry = tk.Entry(
            form,
            width=30,
            font=("Arial", 11)
        )

        entry.grid(
            row=1,
            column=i,
            padx=20,
            pady=8,
            ipady=6
        )

        entries[label] = entry

    # ================= SEARCH =================

    search_frame = tk.Frame(root, bg="#f1f5f9")
    search_frame.pack(fill="x", padx=20)

    tk.Label(
        search_frame,
        text="Search Student:",
        font=("Arial", 11, "bold"),
        bg="#f1f5f9"
    ).pack(side="left")

    search_entry = tk.Entry(
        search_frame,
        width=35,
        font=("Arial", 11)
    )

    search_entry.pack(side="left", padx=10, ipady=5)

    # ================= TABLE =================

    columns = (
        "Student ID",
        "Student Name",
        "Email",
        "Phone"
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
        table.column(col, width=220, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================= LOAD STUDENTS =================

    def load_students(keyword=""):

        for item in table.get_children():
            table.delete(item)

        db = connect_db()

        if not db:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to MySQL."
            )
            return

        cursor = db.cursor()

        try:

            query = """
                SELECT student_id, student_name, email, phone
                FROM students
                WHERE student_name LIKE %s
                OR email LIKE %s
                OR phone LIKE %s
                ORDER BY student_id
            """

            search = f"%{keyword}%"

            cursor.execute(
                query,
                (search, search, search)
            )

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            cursor.close()
            db.close()

    # ================= CLEAR FIELDS =================

    def clear_fields():

        for entry in entries.values():
            entry.delete(0, tk.END)

        table.selection_remove(table.selection())

    # ================= VALIDATION =================

    def get_form_data():

        name = entries["Student Name"].get().strip()
        email = entries["Email"].get().strip()
        phone = entries["Phone"].get().strip()

        if not name or not email or not phone:
            raise ValueError("All fields are required.")

        if "@" not in email or "." not in email:
            raise ValueError("Enter a valid email address.")

        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Enter a valid 10-digit phone number.")

        return name, email, phone

    # ================= ADD STUDENT =================

    def add_student():

        db = None
        cursor = None

        try:

            data = get_form_data()

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            cursor = db.cursor()

            query = """
                INSERT INTO students
                (student_name, email, phone)
                VALUES (%s, %s, %s)
            """

            cursor.execute(query, data)

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student registered successfully!"
            )

            clear_fields()
            load_students()

        except ValueError as e:

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

    # ================= SELECT STUDENT =================

    def select_student(event):

        selected = table.focus()

        if selected:

            values = table.item(selected, "values")

            for entry, value in zip(entries.values(), values[1:]):

                entry.delete(0, tk.END)
                entry.insert(0, value)

    table.bind("<<TreeviewSelect>>", select_student)

    # ================= UPDATE STUDENT =================

    def update_student():

        selected = table.focus()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a student first."
            )
            return

        student_id = table.item(selected, "values")[0]

        db = None
        cursor = None

        try:

            data = get_form_data()

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            cursor = db.cursor()

            query = """
                UPDATE students
                SET student_name=%s,
                    email=%s,
                    phone=%s
                WHERE student_id=%s
            """

            cursor.execute(query, (*data, student_id))

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student updated successfully!"
            )

            clear_fields()
            load_students()

        except ValueError as e:

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

    # ================= DELETE STUDENT =================

    def delete_student():

        selected = table.focus()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a student first."
            )
            return

        student_id = table.item(selected, "values")[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if not confirm:
            return

        db = None
        cursor = None

        try:

            db = connect_db()

            if not db:
                raise Exception("Database connection failed.")

            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM students WHERE student_id=%s",
                (student_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student deleted successfully!"
            )

            clear_fields()
            load_students()

        except Exception as e:

            if db:
                db.rollback()

            messagebox.showerror(
                "Delete Failed",
                "This student may have existing issue records.\n" + str(e)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # ================= SEARCH STUDENT =================

    def search_student():

        keyword = search_entry.get().strip()
        load_students(keyword)

    # ================= BUTTONS =================

    button_frame = tk.Frame(root, bg="#f1f5f9")
    button_frame.pack(pady=12)

    buttons = [

        ("ADD STUDENT", add_student, "#2563eb"),

        ("UPDATE STUDENT", update_student, "#16a34a"),

        ("DELETE STUDENT", delete_student, "#dc2626"),

        ("SEARCH", search_student, "#7c3aed"),

        ("SHOW ALL", lambda: load_students(), "#475569"),

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

    load_students()