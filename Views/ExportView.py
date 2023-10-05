import customtkinter as CTk
import tkinter as Tk

class ExportDataPopup(CTk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.geometry("400x300")
        self.label = CTk.CTkLabel(self, text="ToplevelWindow")
        print("test")
        self.label.grid(padx=20, pady=20)
