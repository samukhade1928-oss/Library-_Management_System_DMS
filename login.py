import tkinter as tk
from tkinter import messagebox
from auth import login_admin


# Main Window
root = tk.Tk()
root.title("Library Management System - Admin Login")
root.geometry("500x550")
root.resizable(False, False)
root.configure(bg="#172033")


# Center Window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width - 500) // 2
y = (screen_height - 550) // 2

root.geometry(f"500x550+{x}+{y}")


# Heading
title = tk.Label(
    root,
    text="LIBRARY MANAGEMENT",
    font=("Arial", 22, "bold"),
    bg="#172033",
    fg="white"
)
title.pack(pady=(45, 5))


subtitle = tk.Label(
    root,
    text="ADMINISTRATOR LOGIN",
    font=("Arial", 11),
    bg="#172033",
    fg="#94a3b8"
)
subtitle.pack(pady=5)


# Login Frame
frame = tk.Frame(root, bg="#243047", padx=35, pady=30)
frame.pack(pady=35, padx=40, fill="both")


# Username
tk.Label(
    frame,
    text="Username",
    font=("Arial", 11, "bold"),
    bg="#243047",
    fg="white"
).pack(anchor="w", pady=(5, 8))


username_entry = tk.Entry(
    frame,
    font=("Arial", 13),
    width=30,
    bd=0
)
username_entry.pack(ipady=10, pady=(0, 20))


# Password
tk.Label(
    frame,
    text="Password",
    font=("Arial", 11, "bold"),
    bg="#243047",
    fg="white"
).pack(anchor="w", pady=(5, 8))


password_entry = tk.Entry(
    frame,
    font=("Arial", 13),
    width=30,
    show="*",
    bd=0
)
password_entry.pack(ipady=10, pady=(0, 12))


# Show Password
show_password = tk.BooleanVar()


def toggle_password():

    if show_password.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


show_check = tk.Checkbutton(
    frame,
    text="Show Password",
    variable=show_password,
    command=toggle_password,
    bg="#243047",
    fg="white",
    selectcolor="#243047",
    activebackground="#243047",
    activeforeground="white"
)
show_check.pack(anchor="w", pady=5)


# Login Function
def login():

    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password."
        )
        return

    try:

        if login_admin(username, password):

            messagebox.showinfo(
                "Login Successful",
                "Welcome to Library Management System!"
            )

            root.destroy()

            from dashboard import open_dashboard
            open_dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# Login Button
login_button = tk.Button(
    frame,
    text="LOGIN",
    font=("Arial", 13, "bold"),
    bg="#2563eb",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    cursor="hand2",
    bd=0,
    command=login
)

login_button.pack(fill="x", ipady=10, pady=(25, 10))


# Footer
footer = tk.Label(
    root,
    text="Library Management System | Admin Portal",
    font=("Arial", 9),
    bg="#172033",
    fg="#94a3b8"
)
footer.pack(pady=10)


# Enter Key Login
root.bind("<Return>", lambda event: login())

username_entry.focus()

root.mainloop()