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
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_view.add("Yeni İşlem")
        form_frame = self.tab_view.tab("Yeni İşlem")
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Yeni Finansal Hareket", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(form_frame, text="Tarih:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tarih_entry = DateEntry(form_frame, date_pattern='y-mm-dd'); self.tarih_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Açıklama:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.aciklama_entry = ctk.CTkEntry(form_frame, placeholder_text="İşlem açıklaması"); self.aciklama_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Fiyat:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.fiyat_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: 150.00"); self.fiyat_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="İşlem Tipi:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.tip_menu = ctk.CTkOptionMenu(form_frame, values=['Gelir', 'Gider']); self.tip_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Kategori:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.kategori_menu = ctk.CTkOptionMenu(form_frame, values=["Kategori Yok"]); self.kategori_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Hesap:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.hesap_menu = ctk.CTkOptionMenu(form_frame, values=["Hesap Yok"]); self.hesap_menu.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="İlişkili Cari:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        cari_secim_frame = ctk.CTkFrame(form_frame, fg_color="transparent"); cari_secim_frame.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        cari_secim_frame.grid_columnconfigure(0, weight=1)
        self.musteri_entry = ctk.CTkEntry(cari_secim_frame, placeholder_text="Cari seçmek için butonu kullanın ->")
        self.musteri_entry.configure(state="disabled")
        self.musteri_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(cari_secim_frame, text="...", width=40, command=self.cari_sec_penceresi_ac).grid(row=0, column=1, padx=(5,0))

        ctk.CTkButton(form_frame, text="Kaydet", command=self.yeni_finansal_hareket_ekle).grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        self.show_history_button = ctk.CTkButton(form_frame, text="İşlem Geçmişini Göster", command=self.toggle_history_tab)
        self.show_history_button.grid(row=9, column=0, columnspan=2, pady=(0,10), sticky="ew")
        
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

    def toggle_history_tab(self):
        if hasattr(self, 'history_tab'):
            self.tab_view.delete('Geçmiş')
            del self.history_tab
            del self.tree
            self.show_history_button.configure(text='İşlem Geçmişini Göster')
        else:
            self.history_tab = self.tab_view.add('Geçmiş')
            self.history_tab.grid_rowconfigure(1, weight=1)
            self.history_tab.grid_columnconfigure(0, weight=1)
            search_entry = ctk.CTkEntry(self.history_tab, placeholder_text='Kategori, cari veya tarih ara...')
            search_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
            tree_frame = ctk.CTkFrame(self.history_tab, fg_color='transparent')
            tree_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
            tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
            style = ttk.Style(); style.configure('Treeview', background='#2a2d2e', foreground='white', fieldbackground='#343638', borderwidth=0); style.map('Treeview', background=[('selected', '#22559b')]); style.configure('Treeview.Heading', background='#333333', foreground='white', relief='flat')
            self.tree = ttk.Treeview(tree_frame, show='headings')
            self.tree.grid(row=0, column=0, sticky='nsew')
            vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview); vsb.grid(row=0, column=1, sticky='ns')
            self.tree.configure(yscrollcommand=vsb.set)
            search_entry.bind('<KeyRelease>', lambda e: self.finansal_hareketleri_goster(search_entry.get()))
            self.finansal_hareketleri_goster()
            self.tab_view.set('Geçmiş')
            self.show_history_button.configure(text='İşlem Geçmişini Gizle')
        
    def yeni_finansal_hareket_ekle(self):
        tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d'); aciklama = self.aciklama_entry.get()
        fiyat_str = self.fiyat_entry.get().replace(',', '.'); tip = self.tip_menu.get()
        secilen_kategori_ad = self.kategori_menu.get(); secilen_hesap_ad = self.hesap_menu.get()

        if not fiyat_str:
            return messagebox.showerror("Hata", "Fiyat alanı zorunludur.")
        try:
            miktar = float(fiyat_str)
        except ValueError:
            return messagebox.showerror("Hata", "Geçerli bir fiyat girin.")
        if secilen_kategori_ad in ["Kategori Seçin", "Kategori Yok"]: return messagebox.showerror("Hata", "Kategori seçin.")
        if secilen_hesap_ad in ["Hesap Bulunamadı", "Hesap Yok"]: return messagebox.showerror("Hata", "Hesap seçin.")
        
        kategori_id = next((k[0] for k in self.kategoriler if k[1] == secilen_kategori_ad), None)
        hesap_id = next((h[0] for h in self.hesaplar if h[1] == secilen_hesap_ad), None)
        
        gelir = miktar if tip == 'Gelir' else 0
        gider = miktar if tip == 'Gider' else 0

        self.db.finansal_hareket_ekle(tarih, aciklama, gelir, gider, kategori_id, hesap_id, self.secili_musteri_id)
        messagebox.showinfo("Başarılı", "Finansal hareket eklendi.")
        
        # Formu ve seçimi sıfırla
        self.aciklama_entry.delete(0, 'end'); self.fiyat_entry.delete(0, 'end'); self.musteri_entry.configure(state="normal"); self.musteri_entry.delete(0, 'end'); self.musteri_entry.configure(state="disabled"); self.secili_musteri_id = None
        
        self.yenile()
        if hasattr(self.app, 'kasa_banka_frame'): self.app.kasa_banka_frame.hesaplari_goster()
        if hasattr(self.app, 'musteri_frame') and self.secili_musteri_id is not None: 
            self.app.musteri_frame.musterileri_goster()
            self.app.musteri_frame.hesap_hareketlerini_goster(self.secili_musteri_id)
        
    def finansal_hareketleri_goster(self, filtre=""):
        if not hasattr(self, "tree"):
            return
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.tree['columns'] = ("Tarih", "Açıklama", "Fiyat", "Tip", "Kategori", "Hesap", "Cari")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.column("Fiyat", anchor="e", width=80)
        self.tree.column("Tip", width=60)
        self.tree.column("#0", width=0, stretch="NO")

        for kayit in self.db.finansal_hareketleri_getir():
            tip = 'Gelir' if kayit[3] and kayit[3] > 0 else 'Gider'
            fiyat = kayit[3] if tip == 'Gelir' else kayit[4]
            row = (kayit[1], kayit[2], f"{fiyat:.2f} ₺", tip, kayit[5] or "", kayit[6] or "", kayit[7] or "")
            if filtre and filtre.lower() not in ' '.join(str(x).lower() for x in row):
                continue
            self.tree.insert("", "end", values=row)

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
