import customtkinter as ctk
from tkinter import ttk
from database import Database

class StokHareketFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_ui()
        self.stok_hareketlerini_goster()

    def _build_ui(self):
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2d2e", foreground="white",
                        fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )

        self.tree = ttk.Treeview(container, columns=("ID", "Tarih", "Ürün", "Tip", "Miktar", "Açıklama"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=40)
        self.tree.heading("Tarih", text="Tarih")
        self.tree.column("Tarih", width=140)
        self.tree.heading("Ürün", text="Ürün")
        self.tree.heading("Tip", text="Hareket Tipi")
        self.tree.column("Tip", width=90)
        self.tree.heading("Miktar", text="Miktar")
        self.tree.column("Miktar", width=80, anchor="e")
        self.tree.heading("Açıklama", text="Açıklama")

    def stok_hareketlerini_goster(self, urun_id=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for hareket in self.db.stok_hareketlerini_getir(urun_id):
            self.tree.insert("", "end", values=hareket)
