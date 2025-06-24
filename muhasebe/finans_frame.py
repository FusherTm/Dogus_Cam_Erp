import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import Database

class FinansFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        
        # Veri listeleri
        self.kategoriler = []
        self.hesaplar = []
        self.musteriler = []
        self.secili_musteri_id = None # Seçilen müşterinin ID'sini tutar
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.arayuzu_kur()
        self.yenile()

    def arayuzu_kur(self):
        main_container = ctk.CTkFrame(self)
        main_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_container.grid_columnconfigure(1, weight=3); main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        sol_sutun = ctk.CTkFrame(main_container, fg_color="transparent")
        sol_sutun.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sol_sutun.grid_rowconfigure(1, weight=1)
        
        liste_container = ctk.CTkFrame(main_container)
        liste_container.grid(row=0, column=1, sticky="nsew")
        liste_container.grid_rowconfigure(1, weight=1)
        liste_container.grid_columnconfigure(0, weight=1)

        # Form
        form_frame = ctk.CTkFrame(sol_sutun); form_frame.pack(pady=0, padx=0, fill="x")
        ctk.CTkLabel(form_frame, text="Yeni Finansal Hareket", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(form_frame, text="Tarih:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tarih_entry = DateEntry(form_frame, date_pattern='y-mm-dd'); self.tarih_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Açıklama:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.aciklama_entry = ctk.CTkEntry(form_frame, placeholder_text="İşlem açıklaması"); self.aciklama_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Miktar:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.miktar_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: 150.50"); self.miktar_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="İşlem Tipi:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.tip_menu = ctk.CTkOptionMenu(form_frame, values=['Gelir', 'Gider']); self.tip_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Kategori:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.kategori_menu = ctk.CTkOptionMenu(form_frame, values=["Kategori Yok"]); self.kategori_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Hesap:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.hesap_menu = ctk.CTkOptionMenu(form_frame, values=["Hesap Yok"]); self.hesap_menu.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        
        # YENİ: İlişkili Cari Seçim Alanı
        ctk.CTkLabel(form_frame, text="İlişkili Cari:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        cari_secim_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cari_secim_frame.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        cari_secim_frame.grid_columnconfigure(0, weight=1)
        self.musteri_entry = ctk.CTkEntry(cari_secim_frame, placeholder_text="Cari seçmek için butonu kullanın ->")
        self.musteri_entry.configure(state="disabled") # Manuel girişi engelle
        self.musteri_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(cari_secim_frame, text="...", width=40, command=self.cari_sec_penceresi_ac).grid(row=0, column=1, padx=(5,0))
        
        ctk.CTkButton(form_frame, text="Kaydet", command=self.yeni_finansal_hareket_ekle).grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Liste
        ctk.CTkLabel(liste_container, text="Son Finansal Hareketler", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)
        tree_frame = ctk.CTkFrame(liste_container, fg_color="transparent"); tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
        style = ttk.Style(); style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0); style.map('Treeview', background=[('selected', '#22559b')])
        self.tree = ttk.Treeview(tree_frame, show='headings'); self.tree.grid(row=0, column=0, sticky="nsew")
        
    def verileri_yenile(self):
        self.kategoriler = self.db.kategorileri_getir()
        self.hesaplar = self.db.kasa_banka_getir()
        self.musteriler = self.db.musterileri_getir()

    def yenile(self):
        self.verileri_yenile()
        self.finansal_hareketleri_goster()
        
        kategori_degerleri = [k[1] for k in self.kategoriler] if self.kategoriler else ["Kategori Yok"]
        self.kategori_menu.configure(values=kategori_degerleri)
        self.kategori_menu.set("Kategori Seçin" if self.kategoriler else "Kategori Yok")
        
        hesap_degerleri = [h[1] for h in self.hesaplar] if self.hesaplar else ["Hesap Yok"]
        self.hesap_menu.configure(values=hesap_degerleri)
        if self.hesaplar: self.hesap_menu.set(hesap_degerleri[0])
        else: self.hesap_menu.set("Hesap Bulunamadı")
        
    def yeni_finansal_hareket_ekle(self):
        tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d'); aciklama = self.aciklama_entry.get()
        miktar_str = self.miktar_entry.get().replace(',', '.'); tip = self.tip_menu.get()
        secilen_kategori_ad = self.kategori_menu.get(); secilen_hesap_ad = self.hesap_menu.get()

        if not all([aciklama, miktar_str]): return messagebox.showerror("Hata", "Açıklama ve Miktar zorunludur.")
        try: miktar = float(miktar_str)
        except ValueError: return messagebox.showerror("Hata", "Geçerli bir miktar girin.")
        if secilen_kategori_ad in ["Kategori Seçin", "Kategori Yok"]: return messagebox.showerror("Hata", "Kategori seçin.")
        if secilen_hesap_ad in ["Hesap Bulunamadı", "Hesap Yok"]: return messagebox.showerror("Hata", "Hesap seçin.")
        
        kategori_id = next((k[0] for k in self.kategoriler if k[1] == secilen_kategori_ad), None)
        hesap_id = next((h[0] for h in self.hesaplar if h[1] == secilen_hesap_ad), None)
        
        gelir = miktar if tip == 'Gelir' else 0
        gider = miktar if tip == 'Gider' else 0

        self.db.finansal_hareket_ekle(tarih, aciklama, gelir, gider, kategori_id, hesap_id, self.secili_musteri_id)
        messagebox.showinfo("Başarılı", "Finansal hareket eklendi.")
        
        # Formu ve seçimi sıfırla
        self.aciklama_entry.delete(0, 'end'); self.miktar_entry.delete(0, 'end'); self.musteri_entry.configure(state="normal"); self.musteri_entry.delete(0, 'end'); self.musteri_entry.configure(state="disabled"); self.secili_musteri_id = None
        
        self.yenile()
        if hasattr(self.app, 'kasa_banka_frame'): self.app.kasa_banka_frame.hesaplari_goster()
        if hasattr(self.app, 'musteri_frame') and self.secili_musteri_id is not None: 
            self.app.musteri_frame.musterileri_goster()
            self.app.musteri_frame.hesap_hareketlerini_goster(self.secili_musteri_id)
        
    def finansal_hareketleri_goster(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        self.tree['columns'] = ("Tarih", "Açıklama", "Gelir", "Gider", "Kategori", "Hesap", "İlişkili Cari")
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        self.tree.column("Gelir", anchor="e"); self.tree.column("Gider", anchor="e")
        self.tree.column("#0", width=0, stretch="NO")

        for kayit in self.db.finansal_hareketleri_getir():
            gelir_str = f"{kayit[3]:.2f} ₺" if kayit[3] and kayit[3] > 0 else ""; gider_str = f"{kayit[4]:.2f} ₺" if kayit[4] and kayit[4] > 0 else ""
            self.tree.insert("", "end", values=(kayit[1], kayit[2], gelir_str, gider_str, kayit[5] or "", kayit[6] or "", kayit[7] or ""))

    def cari_sec_penceresi_ac(self):
        win = ctk.CTkToplevel(self)
        win.title("Cari Hesap Seç")
        win.geometry("700x500")
        
        arama_entry = ctk.CTkEntry(win, placeholder_text="Aramak için firma adı yazın...")
        arama_entry.pack(fill="x", padx=10, pady=10)
        
        tree_frame = ctk.CTkFrame(win); tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("ID", "Firma Adı", "Yetkili", "Bakiye"), show="headings")
        tree.pack(side="left", expand=True, fill="both")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        for col in tree['columns']: tree.heading(col, text=col)
        tree.column("ID", width=40); tree.column("Bakiye", anchor="e")

        def listeyi_doldur(arama=""):
            for i in tree.get_children(): tree.delete(i)
            for musteri in self.db.musterileri_getir(arama_terimi=arama):
                bakiye_str = f"{musteri[6]:.2f} ₺"
                tree.insert("", "end", values=(musteri[0], musteri[1], musteri[2], bakiye_str), iid=musteri[0])
        
        def secim_yap(event=None):
            secili_id = tree.focus()
            if not secili_id: return
            item = tree.item(secili_id, 'values')
            self.secili_musteri_id = item[0]
            self.musteri_entry.configure(state="normal")
            self.musteri_entry.delete(0, 'end')
            self.musteri_entry.insert(0, item[1])
            self.musteri_entry.configure(state="disabled")
            win.destroy()
            
        def secimi_temizle():
            self.secili_musteri_id = None
            self.musteri_entry.configure(state="normal")
            self.musteri_entry.delete(0, 'end')
            self.musteri_entry.configure(state="disabled")
            win.destroy()

        arama_entry.bind("<KeyRelease>", lambda e: listeyi_doldur(arama_entry.get()))
        tree.bind("<Double-1>", secim_yap)
        ctk.CTkButton(win, text="Seçimi Temizle", command=secimi_temizle, fg_color="red").pack(side="right", padx=10, pady=10)
        ctk.CTkButton(win, text="Seç ve Kapat", command=secim_yap).pack(side="right", padx=10, pady=10)
        
        listeyi_doldur()
        win.transient(self); win.grab_set()
