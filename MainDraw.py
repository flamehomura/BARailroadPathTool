import tkinter as tk
from HexGrid import HexGridPanel

if __name__ == "__main__":
    root = tk.Tk()
    app = HexGridPanel(root)
    root.mainloop()