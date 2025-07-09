import customtkinter as ctk
from tkinter import ttk
from database import Database

class CariAramaPenceresi(ctk.CTkToplevel):
    def __init__(self, parent, cari_tipi, callback):
        super().__init__(parent)
        self.db = Database()
        self.cari_tipi = cari_tipi
        self.callback = callback
        self.title("Cari Arama")
        self.geometry("700x500")

        self.arama_entry = ctk.CTkEntry(self, placeholder_text="Firma ara...")
        self.arama_entry.pack(fill="x", padx=10, pady=10)

        columns = ("ID", "Firma Adı", "Yetkili", "Bakiye")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=50)
        self.tree.column("Bakiye", anchor="e")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(0, 10))
        ctk.CTkButton(button_frame, text="Tamam", command=self._tamam).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="İptal", command=self.destroy).pack(side="left", padx=5)

        self.arama_entry.bind("<KeyRelease>", self._arama)
        self.tree.bind("<Double-1>", lambda e: self._tamam())

        self._arama()
        self.transient(parent)
        self.grab_set()

    def _arama(self, event=None):
        term = self.arama_entry.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for cari in self.db.carileri_getir(term, self.cari_tipi):
            bakiye = f"{cari[6]:.2f} ₺"
            self.tree.insert("", "end", values=(cari[0], cari[1], cari[2], bakiye), iid=cari[0])

    def _tamam(self):
        if not self.tree.focus():
            return
        item = self.tree.item(self.tree.focus(), "values")
        if item and self.callback:
            self.callback(item[0], item[1])
        self.destroy()
