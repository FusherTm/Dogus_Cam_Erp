import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import webbrowser
from database import Database


class VarliklarFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self._cekler_tab()
        self._tapular_tab()
        self._araclar_tab()

    # --- ÇEKLER ---
    def _cekler_tab(self):
        tab = self.tabview.add("Çekler")
        tab.grid_columnconfigure(0, weight=1)
        button = ctk.CTkButton(tab, text="Yeni Çek", command=self.cek_ekle_pencere)
        button.pack(pady=5)
        self.cek_tree = ttk.Treeview(tab, columns=("No", "Banka", "Vade", "Tutar", "Durum", "Not", "Belge"), show="headings")
        for col in ("No", "Banka", "Vade", "Tutar", "Durum", "Not", "Belge"):
            self.cek_tree.heading(col, text=col)
        self.cek_tree.column("Tutar", anchor="e")
        self.cek_tree.pack(expand=True, fill="both", padx=10, pady=5)
        self.cek_tree.bind("<Double-1>", lambda e: self._belge_ac(self.cek_tree))
        self.cek_toplam_label = ctk.CTkLabel(tab, text="Toplam: 0 ₺", font=ctk.CTkFont(weight="bold"))
        self.cek_toplam_label.pack(anchor="e", padx=10, pady=5)
        self.cekleri_goster()

    def cek_ekle_pencere(self):
        win = ctk.CTkToplevel(self)
        win.title("Yeni Çek")
        entries = {}
        fields = [
            ("Çek No", "cek_no"),
            ("Banka Adı", "banka"),
            ("Şube", "sube"),
            ("Tutar", "tutar"),
            ("Vade Tarihi (YYYY-MM-DD)", "vade"),
            ("Keşideci", "kesideci"),
        ]
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(win, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ent = ctk.CTkEntry(win)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[key] = ent
        ctk.CTkLabel(win, text="Durum").grid(row=len(fields), column=0, padx=5, pady=5, sticky="w")
        durum_menu = ctk.CTkOptionMenu(win, values=["Portföyde", "Ciro Edildi", "Tahsil Edildi", "Karşılıksız", "İade"])
        durum_menu.grid(row=len(fields), column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(win, text="Açıklama").grid(row=len(fields)+1, column=0, padx=5, pady=5, sticky="w")
        aciklama = ctk.CTkEntry(win)
        aciklama.grid(row=len(fields)+1, column=1, padx=5, pady=5, sticky="ew")
        file_path = ctk.StringVar(value="")
        def choose_file():
            path = filedialog.askopenfilename(filetypes=[("Document", "*.pdf *.jpg *.png *.jpeg")])
            if path:
                file_path.set(path)
        ctk.CTkButton(win, text="Belge Seç", command=choose_file).grid(row=len(fields)+2, column=0, padx=5, pady=5)
        ctk.CTkLabel(win, textvariable=file_path).grid(row=len(fields)+2, column=1, padx=5, pady=5, sticky="w")
        def save():
            data = {k: e.get() for k, e in entries.items()}
            if not data["tutar"]:
                return messagebox.showerror("Hata", "Tutar girilmeli", parent=win)
            try:
                tutar = float(data["tutar"])
            except ValueError:
                return messagebox.showerror("Hata", "Tutar sayısal olmalı", parent=win)
            dest = ""
            if file_path.get():
                dest = os.path.join(self.upload_dir, os.path.basename(file_path.get()))
                shutil.copy(file_path.get(), dest)
            self.db.cek_ekle(data["cek_no"], data["banka"], data["sube"], tutar, data["vade"], data["kesideci"], durum_menu.get(), aciklama.get(), dest)
            win.destroy()
            self.cekleri_goster()
        ctk.CTkButton(win, text="Kaydet", command=save).grid(row=len(fields)+3, column=0, columnspan=2, pady=10)
        win.grab_set()

    def cekleri_goster(self):
        for i in self.cek_tree.get_children():
            self.cek_tree.delete(i)
        toplam = 0
        for row in self.db.cekleri_getir():
            self.cek_tree.insert("", "end", values=(row[1], row[2], row[5], f"{row[4]:.2f}₺", row[7], row[8] or "", "Görüntüle" if row[9] else ""), iid=row[0])
            toplam += row[4]
        self.cek_toplam_label.configure(text=f"Toplam: {toplam:.2f} ₺")

    # --- TAPULAR ---
    def _tapular_tab(self):
        tab = self.tabview.add("Tapular")
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(tab, text="Yeni Tapu", command=self.tapu_ekle_pencere).pack(pady=5)
        self.tapu_tree = ttk.Treeview(tab, columns=("İl", "İlçe", "Parsel", "Cinsi", "Alan", "Değer", "Not", "Belge"), show="headings")
        for col in self.tapu_tree["columns"]:
            self.tapu_tree.heading(col, text=col)
        self.tapu_tree.column("Değer", anchor="e")
        self.tapu_tree.pack(expand=True, fill="both", padx=10, pady=5)
        self.tapu_tree.bind("<Double-1>", lambda e: self._belge_ac(self.tapu_tree))
        self.tapu_toplam_label = ctk.CTkLabel(tab, text="Toplam: 0 ₺", font=ctk.CTkFont(weight="bold"))
        self.tapu_toplam_label.pack(anchor="e", padx=10, pady=5)
        self.tapulari_goster()

    def tapu_ekle_pencere(self):
        win = ctk.CTkToplevel(self)
        win.title("Yeni Tapu")
        labels = [
            ("İl", "il"),
            ("İlçe", "ilce"),
            ("Mahalle/Mevki", "mahalle"),
            ("Ada/Parsel", "parsel"),
            ("Yüzölçüm (m²)", "alan"),
            ("Cinsi", "cinsi"),
            ("İmar Durumu", "imar"),
            ("Tahmini Değer", "deger"),
        ]
        entries = {}
        for i, (lab, key) in enumerate(labels):
            ctk.CTkLabel(win, text=lab).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ent = ctk.CTkEntry(win)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[key] = ent
        ctk.CTkLabel(win, text="Açıklama").grid(row=len(labels), column=0, padx=5, pady=5, sticky="w")
        aciklama = ctk.CTkEntry(win)
        aciklama.grid(row=len(labels), column=1, padx=5, pady=5, sticky="ew")
        file_path = ctk.StringVar()
        ctk.CTkButton(win, text="Belge Seç", command=lambda: file_path.set(filedialog.askopenfilename(filetypes=[("Document", "*.pdf *.jpg *.png *.jpeg")]))).grid(row=len(labels)+1, column=0, padx=5, pady=5)
        ctk.CTkLabel(win, textvariable=file_path).grid(row=len(labels)+1, column=1, padx=5, pady=5, sticky="w")
        def save():
            try:
                alan = float(entries["alan"].get() or 0)
                deger = float(entries["deger"].get() or 0)
            except ValueError:
                return messagebox.showerror("Hata", "Alan ve Değer sayısal olmalı", parent=win)
            dest = ""
            if file_path.get():
                dest = os.path.join(self.upload_dir, os.path.basename(file_path.get()))
                shutil.copy(file_path.get(), dest)
            self.db.tapu_ekle(
                entries["il"].get(),
                entries["ilce"].get(),
                entries["mahalle"].get(),
                entries["parsel"].get(),
                alan,
                entries["cinsi"].get(),
                entries["imar"].get(),
                deger,
                aciklama.get(),
                dest,
            )
            win.destroy()
            self.tapulari_goster()
        ctk.CTkButton(win, text="Kaydet", command=save).grid(row=len(labels)+2, column=0, columnspan=2, pady=10)
        win.grab_set()

    def tapulari_goster(self):
        for i in self.tapu_tree.get_children():
            self.tapu_tree.delete(i)
        toplam = 0
        for row in self.db.tapulari_getir():
            self.tapu_tree.insert("", "end", values=(row[1], row[2], row[4], row[6], f"{row[5]:.2f}", f"{row[7]:.2f}₺", row[8] or "", "Görüntüle" if row[9] else ""), iid=row[0])
            toplam += row[7] or 0
        self.tapu_toplam_label.configure(text=f"Toplam: {toplam:.2f} ₺")

    # --- ARAÇLAR ---
    def _araclar_tab(self):
        tab = self.tabview.add("Araç Ruhsatları")
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(tab, text="Yeni Araç", command=self.arac_ekle_pencere).pack(pady=5)
        self.arac_tree = ttk.Treeview(tab, columns=("Plaka", "Marka", "Tip", "Yıl", "Değer", "Durum", "Not", "Belge"), show="headings")
        for col in self.arac_tree["columns"]:
            self.arac_tree.heading(col, text=col)
        self.arac_tree.column("Değer", anchor="e")
        self.arac_tree.pack(expand=True, fill="both", padx=10, pady=5)
        self.arac_tree.bind("<Double-1>", lambda e: self._belge_ac(self.arac_tree))
        self.arac_toplam_label = ctk.CTkLabel(tab, text="Toplam: 0 ₺", font=ctk.CTkFont(weight="bold"))
        self.arac_toplam_label.pack(anchor="e", padx=10, pady=5)
        self.araclari_goster()

    def arac_ekle_pencere(self):
        win = ctk.CTkToplevel(self)
        win.title("Yeni Araç")
        labels = [
            ("Plaka", "plaka"),
            ("Marka/Model", "marka"),
            ("Tip", "tip"),
            ("Yıl", "yil"),
            ("Ruhsat Sahibi", "sahip"),
            ("Tahmini Değer", "deger"),
        ]
        entries = {}
        for i, (lab, key) in enumerate(labels):
            ctk.CTkLabel(win, text=lab).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ent = ctk.CTkEntry(win)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[key] = ent
        ctk.CTkLabel(win, text="Durum").grid(row=len(labels), column=0, padx=5, pady=5, sticky="w")
        durum_menu = ctk.CTkOptionMenu(win, values=["Aktif", "Satıldı", "Kiralık", "Hurda"])
        durum_menu.grid(row=len(labels), column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(win, text="Açıklama").grid(row=len(labels)+1, column=0, padx=5, pady=5, sticky="w")
        aciklama = ctk.CTkEntry(win)
        aciklama.grid(row=len(labels)+1, column=1, padx=5, pady=5, sticky="ew")
        file_path = ctk.StringVar()
        ctk.CTkButton(win, text="Belge Seç", command=lambda: file_path.set(filedialog.askopenfilename(filetypes=[("Document", "*.pdf *.jpg *.png *.jpeg")]))).grid(row=len(labels)+2, column=0, padx=5, pady=5)
        ctk.CTkLabel(win, textvariable=file_path).grid(row=len(labels)+2, column=1, padx=5, pady=5, sticky="w")
        def save():
            try:
                yil = int(entries["yil"].get() or 0)
                deger = float(entries["deger"].get() or 0)
            except ValueError:
                return messagebox.showerror("Hata", "Yıl tam sayı, Değer sayısal olmalı", parent=win)
            dest = ""
            if file_path.get():
                dest = os.path.join(self.upload_dir, os.path.basename(file_path.get()))
                shutil.copy(file_path.get(), dest)
            self.db.arac_ekle(
                entries["plaka"].get(),
                entries["marka"].get(),
                entries["tip"].get(),
                yil,
                entries["sahip"].get(),
                deger,
                durum_menu.get(),
                aciklama.get(),
                dest,
            )
            win.destroy()
            self.araclari_goster()
        ctk.CTkButton(win, text="Kaydet", command=save).grid(row=len(labels)+3, column=0, columnspan=2, pady=10)
        win.grab_set()

    def araclari_goster(self):
        for i in self.arac_tree.get_children():
            self.arac_tree.delete(i)
        toplam = 0
        for row in self.db.araclari_getir():
            self.arac_tree.insert("", "end", values=(row[1], row[2], row[3], row[4], f"{row[6]:.2f}₺", row[7], row[8] or "", "Görüntüle" if row[9] else ""), iid=row[0])
            toplam += row[6] or 0
        self.arac_toplam_label.configure(text=f"Toplam: {toplam:.2f} ₺")

    def _belge_ac(self, tree):
        iid = tree.focus()
        if not iid:
            return
        path = tree.item(iid)["values"][-1]
        if path and os.path.isfile(path):
            webbrowser.open_new_tab('file://' + os.path.abspath(path))
