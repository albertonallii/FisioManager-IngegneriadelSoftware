import tkinter as tk
from views.login_view import LoginWindow
from views.main_view import MainWindow
import theme_fisio

if __name__ == '__main__':
    root = tk.Tk()

    theme_fisio.apply_theme(root)
    login_win = LoginWindow(root)
    root.mainloop()

    user = getattr(login_win, 'logged_in_user', None)
    if user:
        MainWindow(user)
