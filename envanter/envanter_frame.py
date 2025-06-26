import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database

class EnvanterFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.selected_urun_id = None
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.urun_yonetimi_arayuzu_kur()
        self.yenile_tum_verileri()

    def urun_yonetimi_arayuzu_kur(self):
        # Sol Form Sütunu
        form_frame = ctk.CTkFrame(self, width=350)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        form_frame.grid_propagate(False)
        
        ctk.CTkLabel(form_frame, text="Ürün Bilgileri", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, padx=20)
        ctk.CTkLabel(form_frame, text="Ürün Tipi:").pack(padx=20, pady=5, anchor="w")
        # DÜZELTME: Artık maliyet alanını kilitleyen komut kaldırıldı.
        self.urun_tipi_menu = ctk.CTkOptionMenu(form_frame, values=["Hammadde", "Mamül"])
        self.urun_tipi_menu.pack(padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(form_frame, text="Ürün Adı:").pack(padx=20, pady=5, anchor="w")
        self.urun_adi_entry = ctk.CTkEntry(form_frame)
        self.urun_adi_entry.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="Stok Miktarı:").pack(padx=20, pady=5, anchor="w")
        self.stok_entry = ctk.CTkEntry(form_frame)
        self.stok_entry.pack(padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(form_frame, text="Birim (Örn: M2, KG, Adet):").pack(padx=20, pady=5, anchor="w")
        self.birim_entry = ctk.CTkEntry(form_frame)
        self.birim_entry.pack(padx=20, pady=5, fill="x")

        # DÜZELTME: Etiket metni daha genel hale getirildi.
        self.maliyet_label = ctk.CTkLabel(form_frame, text="Birim Maliyet Fiyatı:")
        self.maliyet_label.pack(padx=20, pady=5, anchor="w")
        self.maliyet_entry = ctk.CTkEntry(form_frame)
        self.maliyet_entry.pack(padx=20, pady=5, fill="x")
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkButton(button_frame, text="Ekle", command=self.urun_ekle).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Güncelle", command=self.urun_guncelle).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Sil", command=self.urun_sil, fg_color="#E54E55", hover_color="#C4424A").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Temizle", command=self.formu_temizle).pack(side="left", expand=True, padx=5)
        
        # Sağ Liste Sütunu
        list_container = ctk.CTkFrame(self)
        list_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_container.grid_rowconfigure(1, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        self.arama_entry = ctk.CTkEntry(list_container, placeholder_text="Ürün ara...")
        self.arama_entry.pack(padx=10, pady=5, fill="x")
        self.arama_entry.bind("<KeyRelease>", lambda e: self.urunleri_goster())

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map("Treeview", background=[("selected", "#22559b")])
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )
        self.urun_tree = ttk.Treeview(list_container, columns=("ID", "Ad", "Tip", "Stok", "Birim", "Maliyet"), show="headings")
        self.urun_tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.urun_tree.heading("ID", text="ID"); self.urun_tree.column("ID", width=40)
        self.urun_tree.heading("Ad", text="Ürün Adı")
        self.urun_tree.heading("Tip", text="Tipi"); self.urun_tree.column("Tip", width=80)
        self.urun_tree.heading("Stok", text="Stok", anchor="e"); self.urun_tree.column("Stok", width=80, anchor="e")
        self.urun_tree.heading("Birim", text="Birim"); self.urun_tree.column("Birim", width=80)
        self.urun_tree.heading("Maliyet", text="Maliyet Fiyatı", anchor="e"); self.urun_tree.column("Maliyet", width=100, anchor="e")
        self.urun_tree.bind("<<TreeviewSelect>>", self.urun_sec)

    def urunleri_goster(self):
        for i in self.urun_tree.get_children(): self.urun_tree.delete(i)
        arama = self.arama_entry.get()
        for urun in self.db.urunleri_getir(arama_terimi=arama):
            maliyet = f"{urun[5]:.2f} ₺" if urun[5] is not None else "N/A"
            stok = f"{urun[3]:.2f}"
            self.urun_tree.insert("", "end", values=(urun[0], urun[1], urun[2], stok, urun[4], maliyet), iid=urun[0])

    # DÜZELTME: Bu fonksiyon artık gereksiz, kaldırıldı.
    # def urun_tipi_degisti(self, secim): ...

    def urun_ekle(self):
        tip = self.urun_tipi_menu.get(); ad = self.urun_adi_entry.get(); stok = self.stok_entry.get() or "0"
        birim = self.birim_entry.get(); maliyet = self.maliyet_entry.get() or "0"
        if not all([tip, ad, birim]): return messagebox.showerror("Hata", "Ürün tipi, adı ve birimi zorunludur.")
        try:
            urun_id = self.db.urun_ekle(ad, tip, float(stok), birim, float(maliyet))
            if urun_id: messagebox.showinfo("Başarılı", "Ürün eklendi."); self.yenile_tum_verileri()
            else: messagebox.showerror("Hata", "Bu ürün adı zaten mevcut.")
        except ValueError: messagebox.showerror("Hata", "Stok ve maliyet sayısal olmalıdır.")

    def urun_guncelle(self):
        secili = self.urun_tree.focus()
        if not secili: return messagebox.showerror("Hata", "Güncellemek için bir ürün seçin.")
        tip = self.urun_tipi_menu.get(); ad = self.urun_adi_entry.get(); stok = self.stok_entry.get() or "0"
        birim = self.birim_entry.get(); maliyet = self.maliyet_entry.get() or "0"
        if not all([tip, ad, birim]): return messagebox.showerror("Hata", "Ürün tipi, adı ve birimi zorunludur.")
        try:
            self.db.urun_guncelle(secili, ad, tip, float(stok), birim, float(maliyet))
            messagebox.showinfo("Başarılı", "Ürün güncellendi."); self.yenile_tum_verileri()
        except ValueError: messagebox.showerror("Hata", "Stok ve maliyet sayısal olmalıdır.")

    def urun_sil(self):
        secili = self.urun_tree.focus()
        if not secili:
            return messagebox.showerror("Hata", "Silmek için bir ürün seçin.")
        if messagebox.askyesno("Onay", "Seçili ürünü silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."):
            self.db.urun_sil(secili)
            messagebox.showinfo("Başarılı", "Ürün silindi.")
            self.yenile_tum_verileri()

    def urun_sec(self, event):
        secili = self.urun_tree.focus();
        if not secili: return
        item = self.urun_tree.item(secili)['values']
        self.formu_temizle(clear_selection=False); self.urun_tipi_menu.set(item[2])
        self.urun_adi_entry.insert(0, item[1]); self.stok_entry.insert(0, str(item[3]))
        self.birim_entry.insert(0, item[4]); self.maliyet_entry.insert(0, str(item[5]).replace(" ₺", ""))

    def formu_temizle(self, clear_selection=True):
        self.urun_adi_entry.delete(0, 'end'); self.stok_entry.delete(0, 'end')
        self.birim_entry.delete(0, 'end'); self.maliyet_entry.delete(0, 'end')
        if clear_selection and self.urun_tree.selection(): self.urun_tree.selection_remove(self.urun_tree.selection()[0])
            
    def yenile_tum_verileri(self):
        self.urunleri_goster(); self.formu_temizle()
        if hasattr(self.app, 'uretim_frame'): self.app.uretim_frame.verileri_yukle()
        if hasattr(self.app, 'fatura_frame'): self.app.fatura_frame.verileri_yukle()
        if hasattr(self.app, 'event_bus'):
            self.app.event_bus.publish('envanter_guncellendi')
