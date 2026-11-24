import tkinter as tk
from tkinter import messagebox
from database import connect_db


def open_dashboard():

    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("1150x720")
    root.configure(bg="#F1F5F9")
    root.resizable(False, False)

    # HEADER
    header = tk.Frame(root, bg="#172554", height=80)
    header.pack(fill="x")

    tk.Label(
        header,
        text="LIBRARY MANAGEMENT SYSTEM",
        font=("Arial", 22, "bold"),
        fg="white",
        bg="#172554"
    ).pack(side="left", padx=25, pady=20)

    tk.Label(
        header,
        text="ADMIN PANEL",
        font=("Arial", 12, "bold"),
        fg="#BFDBFE",
        bg="#172554"
    ).pack(side="right", padx=30)

    # SIDEBAR
    sidebar = tk.Frame(root, bg="#1E293B", width=240)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="MAIN MENU",
        font=("Arial", 15, "bold"),
        fg="white",
        bg="#1E293B"
    ).pack(pady=25)

    # MAIN AREA
    main_area = tk.Frame(root, bg="#F1F5F9")
    main_area.pack(side="right", fill="both", expand=True)

    tk.Label(
        main_area,
        text="Dashboard Overview",
        font=("Arial", 23, "bold"),
        bg="#F1F5F9",
        fg="#172554"
    ).pack(anchor="w", padx=30, pady=25)

    # STATISTICS
    cards_frame = tk.Frame(main_area, bg="#F1F5F9")
    cards_frame.pack(fill="x", padx=20)

    def get_statistics():

        connection = connect_db()

        if connection is None:
            return 0, 0, 0, 0

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COALESCE(SUM(available_quantity), 0) FROM books"
            )
            available_books = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM issue_records WHERE return_date IS NULL"
            )
            issued_books = cursor.fetchone()[0]

            return total_books, total_students, available_books, issued_books

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return 0, 0, 0, 0

        finally:
            if cursor:
                cursor.close()
            connection.close()

    total_books, total_students, available_books, issued_books = get_statistics()

    def create_card(parent, title, value, color):

        card = tk.Frame(
            parent,
            bg="white",
            width=195,
            height=140,
            highlightbackground="#CBD5E1",
            highlightthickness=1
        )

        card.pack(side="left", padx=10, pady=10)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#475569"
        ).pack(pady=(20, 10))

        tk.Label(
            card,
            text=str(value),
            font=("Arial", 28, "bold"),
            bg="white",
            fg=color
        ).pack()

    create_card(cards_frame, "Total Books", total_books, "#2563EB")
    create_card(cards_frame, "Total Students", total_students, "#16A34A")
    create_card(cards_frame, "Available Books", available_books, "#D97706")
    create_card(cards_frame, "Issued Books", issued_books, "#DC2626")

    # WELCOME SECTION
    welcome_frame = tk.Frame(
        main_area,
        bg="white",
        highlightbackground="#CBD5E1",
        highlightthickness=1
    )
    welcome_frame.pack(fill="x", padx=30, pady=35)

    tk.Label(
        welcome_frame,
        text="Welcome to Library Management System",
        font=("Arial", 18, "bold"),
        fg="#172554",
        bg="white"
    ).pack(anchor="w", padx=25, pady=(25, 10))

    tk.Label(
        welcome_frame,
        text="Manage books, students, issue records, returns and reports.",
        font=("Arial", 12),
        fg="#64748B",
        bg="white"
    ).pack(anchor="w", padx=25, pady=(0, 25))

    # MODULES
    def open_book_module():
        from books import open_books
        open_books()

    def open_student_module():
        from students import open_students
        open_students()

    def open_issue_module():
        from issue_return import open_issue
        open_issue()

    def open_return_module():
        from issue_return import open_return
        open_return()

    def open_reports_module():
        from reports import open_reports
        open_reports()

    # MENU BUTTONS
    def create_menu_button(text, command):

        tk.Button(
            sidebar,
            text=text,
            font=("Arial", 12, "bold"),
            bg="#1E293B",
            fg="white",
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=25,
            height=2,
            cursor="hand2",
            command=command
        ).pack(fill="x", padx=10, pady=4)

    create_menu_button("🏠  Dashboard", lambda: None)
    create_menu_button("📚  Manage Books", open_book_module)
    create_menu_button("👨‍🎓  Manage Students", open_student_module)
    create_menu_button("📖  Issue Books", open_issue_module)
    create_menu_button("↩  Return Books", open_return_module)
    create_menu_button("📊  View Reports", open_reports_module)

    tk.Frame(sidebar, bg="#475569", height=1).pack(
        fill="x", padx=15, pady=20
    )

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root.destroy()

    create_menu_button("🚪  Logout", logout)

    # FOOTER
    tk.Label(
        main_area,
        text="Library Management System | Admin Dashboard",
        font=("Arial", 9),
        bg="#F1F5F9",
        fg="#64748B"
    ).pack(side="bottom", pady=15)

    root.mainloop()


if __name__ == "__main__":
    open_dashboard()