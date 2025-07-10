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
        self.secili_cari_id = None  # Seçilen carinin ID'si
        self.cari_tipi = "Müşteri"
        
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
        self.tip_menu = ctk.CTkOptionMenu(form_frame, values=['Gelir', 'Gider'], command=self._tip_degisti)
        self.tip_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self._tip_degisti(self.tip_menu.get())
        ctk.CTkLabel(form_frame, text="Kategori:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.kategori_menu = ctk.CTkOptionMenu(form_frame, values=["Kategori Yok"]); self.kategori_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Hesap:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.hesap_menu = ctk.CTkOptionMenu(form_frame, values=["Hesap Yok"]); self.hesap_menu.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Ödeme Yöntemi:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.odeme_menu = ctk.CTkOptionMenu(form_frame, values=[
            "Nakit",
            "Kredi Kartı",
            "Havale / EFT",
            "Çek",
            "Senet",
            "Diğer",
        ])
        self.odeme_menu.set("Nakit")
        self.odeme_menu.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="İlişkili Cari:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        cari_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cari_frame.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
        cari_frame.grid_columnconfigure(0, weight=1)
        self.cari_entry = ctk.CTkEntry(cari_frame)
        self.cari_entry.insert(0, "Seçim Yap (Opsiyonel)")
        self.cari_entry.configure(state="disabled")
        self.cari_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(cari_frame, text="...", width=40, command=self.cari_ara).grid(row=0, column=1, padx=(5,0))

        ctk.CTkButton(form_frame, text="Kaydet", command=self.yeni_finansal_hareket_ekle).grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")
        self.show_history_button = ctk.CTkButton(form_frame, text="İşlem Geçmişini Göster", command=self.toggle_history_tab)
        self.show_history_button.grid(row=10, column=0, columnspan=2, pady=(0,10), sticky="ew")
        
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

    def _tip_degisti(self, secim):
        self.cari_tipi = 'Tedarikçi' if secim == 'Gider' else 'Müşteri'
        self.secili_cari_id = None
        if hasattr(self, 'cari_entry'):
            self.cari_entry.configure(state="normal")
            self.cari_entry.delete(0, 'end')
            self.cari_entry.insert(0, "Seçim Yap (Opsiyonel)")
            self.cari_entry.configure(state="disabled")

    def cari_ara(self):
        from .cari_arama_penceresi import CariAramaPenceresi
        def callback(cid, ad):
            self.secili_cari_id = cid
            self.cari_entry.configure(state="normal")
            self.cari_entry.delete(0, "end")
            self.cari_entry.insert(0, ad)
            self.cari_entry.configure(state="disabled")
        CariAramaPenceresi(self, self.cari_tipi, callback)

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
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Treeview', background='#2a2d2e', foreground='white', fieldbackground='#343638', borderwidth=0)
            style.map('Treeview', background=[('selected', '#22559b')])
            style.configure(
                'Treeview.Heading',
                background='#1E1E2F',
                foreground='#FFFFFF',
                relief='flat',
                font=('Helvetica', 10, 'bold'),
            )
            self.tree = ttk.Treeview(tree_frame, show='headings')
            self.tree.grid(row=0, column=0, sticky='nsew')
            vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview); vsb.grid(row=0, column=1, sticky='ns')
            self.tree.configure(yscrollcommand=vsb.set)
            search_entry.bind('<KeyRelease>', lambda e: self.finansal_hareketleri_goster(search_entry.get()))
            self.finansal_hareketleri_goster()
            self.tab_view.set('Geçmiş')
            self.show_history_button.configure(text='İşlem Geçmişini Gizle')
        
    def yeni_finansal_hareket_ekle(self):
        # Formdan verileri al
        tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d')
        aciklama = self.aciklama_entry.get()
        tutar_str = self.fiyat_entry.get()
        islem_tipi = self.tip_menu.get()

        # İlişkili cari ID'sini al
        secilen_cari_id = self.secili_cari_id

        # Gerekli kontroller
        try:
            tutar = float(tutar_str)
        except (ValueError, TypeError):
            messagebox.showerror("Hata", "Lütfen geçerli bir tutar girin.")
            return

        borc = 0.0
        alacak = 0.0

        if islem_tipi == 'Gelir':
            borc = tutar
        elif islem_tipi in ['Gider', 'Tahsilat', 'Ödeme']:
            alacak = tutar

        basarili = self.db.finansal_hareket_ekle(
            tarih=tarih,
            aciklama=aciklama,
            borc=borc,
            alacak=alacak,
            tip=islem_tipi,
            cari_id=secilen_cari_id
        )

        if basarili:
            messagebox.showinfo("Başarılı", "Finansal hareket başarıyla kaydedildi.")
            self.liste_yenile()
            self.formu_temizle()
        else:
            messagebox.showerror("Hata", "Kayıt sırasında bir sorun oluştu.")
        
    def finansal_hareketleri_goster(self, filtre=""):
        if not hasattr(self, "tree"):
            return
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.tree["columns"] = ("Tarih", "Açıklama", "Borç", "Alacak", "Tip")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        for col in ["Borç", "Alacak"]:
            self.tree.column(col, anchor="e", width=80)
        self.tree.column("Tip", width=60)
        self.tree.column("#0", width=0, stretch="NO")

        if self.secilen_cari_id is None:
            messagebox.showwarning("Uyarı", "Lütfen önce bir cari hesap seçin.")
            return

        hareketler = self.db.finansal_hareketleri_getir(self.secilen_cari_id)
        for kayit in hareketler:
            row = (
                kayit[0],
                kayit[1],
                f"{kayit[2]:.2f}" if kayit[2] else "",
                f"{kayit[3]:.2f}" if kayit[3] else "",
                kayit[4],
            )
            if filtre and filtre.lower() not in " ".join(str(x).lower() for x in row):
                continue
            self.tree.insert("", "end", values=row)

    def formu_temizle(self):
        self.aciklama_entry.delete(0, "end")
        self.fiyat_entry.delete(0, "end")
        self.cari_entry.configure(state="normal")
        self.cari_entry.delete(0, "end")
        self.cari_entry.insert(0, "Seçim Yap (Opsiyonel)")
        self.cari_entry.configure(state="disabled")
        self.secili_cari_id = None

    def liste_yenile(self):
        self.yenile()
        if hasattr(self.app, "kasa_banka_frame"):
            self.app.kasa_banka_frame.hesaplari_goster()
        if self.secili_cari_id is not None:
            if self.cari_tipi == "Müşteri" and hasattr(self.app, "musteri_frame"):
                self.app.musteri_frame.musterileri_goster()
                self.app.musteri_frame.hesap_hareketlerini_goster(self.secili_cari_id)
            elif self.cari_tipi == "Tedarikçi" and hasattr(self.app, "tedarikci_frame"):
                self.app.tedarikci_frame.musterileri_goster()
                self.app.tedarikci_frame.hesap_hareketlerini_goster(self.secili_cari_id)

