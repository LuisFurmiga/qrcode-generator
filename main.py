import tkinter as tk
from view import QRCodeView # type: ignore

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeView(root)
    root.mainloop()
