import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
import datetime

class MusteriFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.selected_musteri_id = None

        self.arayuzu_kur()
        self.musterileri_goster()

        if hasattr(self.app, 'event_bus'):
            self.app.event_bus.subscribe('is_emri_guncellendi', self._on_is_emri_guncellendi)
            self.app.event_bus.subscribe('temper_emri_guncellendi', self._on_temper_emri_guncellendi)

    def arayuzu_kur(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        form_frame = ctk.CTkFrame(top_frame)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ns")
        ctk.CTkLabel(form_frame, text="Firma Adı:").pack(padx=10, pady=5, anchor="w")
        self.firma_adi_entry = ctk.CTkEntry(form_frame, width=250); self.firma_adi_entry.pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Firma Yetkilisi:").pack(padx=10, pady=5, anchor="w")
        self.yetkili_entry = ctk.CTkEntry(form_frame); self.yetkili_entry.pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Telefon:").pack(padx=10, pady=5, anchor="w")
        self.tel_entry = ctk.CTkEntry(form_frame); self.tel_entry.pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Email:").pack(padx=10, pady=5, anchor="w")
        self.email_entry = ctk.CTkEntry(form_frame); self.email_entry.pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Adres:").pack(padx=10, pady=5, anchor="w")
        self.adres_entry = ctk.CTkTextbox(form_frame, height=80); self.adres_entry.pack(padx=10, pady=5, fill="x")

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent"); button_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkButton(button_frame, text="Ekle", command=self.musteri_ekle).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Güncelle", command=self.musteri_guncelle).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Sil", command=self.musteri_sil, fg_color="#E54E55", hover_color="#C4424A").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Temizle", command=self.formu_temizle).pack(side="left", expand=True, padx=5)

        list_frame = ctk.CTkFrame(top_frame); list_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1); list_frame.grid_columnconfigure(0, weight=1)
        self.arama_entry = ctk.CTkEntry(list_frame, placeholder_text="Firma ara..."); self.arama_entry.pack(fill="x", padx=10, pady=5)
        self.arama_entry.bind("<KeyRelease>", self.arama_yap)
        
        style = ttk.Style(); style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        self.musteri_tree = ttk.Treeview(list_frame, columns=("ID", "Firma Adı", "Yetkili", "Bakiye"), show="headings"); self.musteri_tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.musteri_tree.heading("ID", text="ID"); self.musteri_tree.column("ID", width=50)
        self.musteri_tree.heading("Firma Adı", text="Firma Adı"); self.musteri_tree.heading("Yetkili", text="Yetkili")
        self.musteri_tree.heading("Bakiye", text="Bakiye", anchor="e"); self.musteri_tree.column("Bakiye", anchor="e")
        self.musteri_tree.bind("<<TreeviewSelect>>", self.musteri_sec)

        # GÜNCELLENDİ: Alt kısma üçüncü sekme eklendi
        alt_tab_view = ctk.CTkTabview(self); alt_tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        alt_tab_view.add("Hesap Ekstresi"); alt_tab_view.add("İş Emirleri"); alt_tab_view.add("Temper Siparişleri")
        
        # --- Hesap Ekstresi Sekmesi ---
        hesap_frame = alt_tab_view.tab("Hesap Ekstresi"); hesap_frame.grid_rowconfigure(0, weight=1); hesap_frame.grid_columnconfigure(0, weight=1)
        self.hesap_tree = ttk.Treeview(hesap_frame, columns=("Tarih", "Açıklama", "Borç", "Alacak", "Bakiye"), show="headings")
        self.hesap_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for col in self.hesap_tree['columns']: self.hesap_tree.heading(col, text=col)
        for col in ["Borç", "Alacak", "Bakiye"]: self.hesap_tree.column(col, anchor="e")

        # --- İş Emirleri Sekmesi ---
        is_gecmisi_frame = alt_tab_view.tab("İş Emirleri"); is_gecmisi_frame.grid_rowconfigure(0, weight=1); is_gecmisi_frame.grid_columnconfigure(0, weight=1)
        self.is_emri_tree = ttk.Treeview(is_gecmisi_frame, columns=("ID", "Tarih", "Ürün Niteliği", "Miktar", "Durum"), show="headings")
        self.is_emri_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.is_emri_tree.heading("ID", text="İş Emri No"); self.is_emri_tree.column("ID", width=80)
        self.is_emri_tree.heading("Tarih", text="Tarih"); self.is_emri_tree.column("Tarih", width=100)
        self.is_emri_tree.heading("Ürün Niteliği", text="Ürün Niteliği")
        self.is_emri_tree.heading("Miktar", text="Miktar (m²)", anchor="e"); self.is_emri_tree.column("Miktar", width=100, anchor="e")
        self.is_emri_tree.heading("Durum", text="Durum", anchor="center"); self.is_emri_tree.column("Durum", width=100, anchor="center")
        self.is_emri_tree.tag_configure('Bekliyor', background='#636300', foreground='white'); self.is_emri_tree.tag_configure('Üretimde', background='#005B9A', foreground='white'); self.is_emri_tree.tag_configure('Hazır', background='#006325', foreground='white')

        # --- Temper Siparişleri Sekmesi (YENİ) ---
        temper_gecmisi_frame = alt_tab_view.tab("Temper Siparişleri"); temper_gecmisi_frame.grid_rowconfigure(0, weight=1); temper_gecmisi_frame.grid_columnconfigure(0, weight=1)
        self.temper_emri_tree = ttk.Treeview(temper_gecmisi_frame, columns=("ID", "Tarih", "Ürün Niteliği", "Miktar", "Durum"), show="headings")
        self.temper_emri_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.temper_emri_tree.heading("ID", text="Sipariş No"); self.temper_emri_tree.column("ID", width=80)
        self.temper_emri_tree.heading("Tarih", text="Tarih"); self.temper_emri_tree.column("Tarih", width=100)
        self.temper_emri_tree.heading("Ürün Niteliği", text="Ürün Niteliği")
        self.temper_emri_tree.heading("Miktar", text="Miktar (m²)", anchor="e"); self.temper_emri_tree.column("Miktar", width=100, anchor="e")
        self.temper_emri_tree.heading("Durum", text="Durum", anchor="center"); self.temper_emri_tree.column("Durum", width=100, anchor="center")
        self.temper_emri_tree.tag_configure('Bekliyor', background='#636300', foreground='white'); self.temper_emri_tree.tag_configure('Üretimde', background='#005B9A', foreground='white'); self.temper_emri_tree.tag_configure('Hazır', background='#006325', foreground='white')


    def musterileri_goster(self, arama_terimi=""):
        for i in self.musteri_tree.get_children(): self.musteri_tree.delete(i)
        for musteri in self.db.musterileri_getir(arama_terimi):
            bakiye_str = f"{musteri[6]:.2f} ₺"; self.musteri_tree.insert("", "end", values=(musteri[0], musteri[1], musteri[2], bakiye_str), iid=musteri[0])

    def arama_yap(self, event=None): self.musterileri_goster(self.arama_entry.get())

    def musteri_ekle(self):
        firma_adi = self.firma_adi_entry.get();
        if not firma_adi: return messagebox.showerror("Hata", "Firma Adı alanı zorunludur.")
        if self.db.musteri_ekle(firma_adi, self.yetkili_entry.get(), self.tel_entry.get(), self.email_entry.get(), self.adres_entry.get("1.0", "end-1c")):
            messagebox.showinfo("Başarılı", "Müşteri (Cari) eklendi."); self.yenile_ve_entegre_et()
        else: messagebox.showerror("Hata", "Bu firma adı zaten mevcut.")

    def musteri_guncelle(self):
        if not self.selected_musteri_id: return messagebox.showerror("Hata", "Güncellemek için bir müşteri seçin.")
        firma_adi = self.firma_adi_entry.get();
        if not firma_adi: return messagebox.showerror("Hata", "Firma Adı alanı zorunludur.")
        self.db.musteri_guncelle(self.selected_musteri_id, firma_adi, self.yetkili_entry.get(), self.tel_entry.get(), self.email_entry.get(), self.adres_entry.get("1.0", "end-1c"))
        messagebox.showinfo("Başarılı", "Müşteri bilgileri güncellendi."); self.yenile_ve_entegre_et()

    def musteri_sil(self):
        if not self.selected_musteri_id:
            return messagebox.showerror("Hata", "Silmek için bir müşteri seçin.")
        if messagebox.askyesno("Onay", "Seçili müşteriyi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."):
            self.db.musteri_sil(self.selected_musteri_id)
            messagebox.showinfo("Başarılı", "Müşteri silindi.")
            self.yenile_ve_entegre_et()

    def musteri_sec(self, event=None):
        selected_item = self.musteri_tree.focus();
        if not selected_item: return
        self.selected_musteri_id = selected_item
        musteri = self.db.musteri_getir_by_id(self.selected_musteri_id)
        if musteri:
            self.formu_temizle(clear_selection=False)
            self.firma_adi_entry.insert(0, musteri[1]); self.yetkili_entry.insert(0, musteri[2])
            self.tel_entry.insert(0, musteri[3]); self.email_entry.insert(0, musteri[4])
            self.adres_entry.insert("1.0", musteri[5])
            self.hesap_hareketlerini_goster(musteri[0])
            self.is_gecmisini_goster(musteri[0])
            self.temper_gecmisini_goster(musteri[0]) # YENİ

    def hesap_hareketlerini_goster(self, musteri_id):
        for i in self.hesap_tree.get_children(): self.hesap_tree.delete(i)
        for h in self.db.musteri_hesap_hareketlerini_getir(musteri_id):
            borc = f"{h[4]:.2f} ₺" if h[4] else ""; alacak = f"{h[5]:.2f} ₺" if h[5] else ""
            bakiye = f"{h[6]:.2f} ₺"; self.hesap_tree.insert("", "end", values=(h[2], h[3], borc, alacak, bakiye))
            
    def is_gecmisini_goster(self, musteri_id):
        for i in self.is_emri_tree.get_children(): self.is_emri_tree.delete(i)
        for is_emri in self.db.is_emirlerini_getir_by_musteri_id(musteri_id):
            self.is_emri_tree.insert("", "end", values=is_emri, tags=(is_emri[4],))

    # YENİ: Müşterinin temper geçmişini listeleyen fonksiyon
    def temper_gecmisini_goster(self, musteri_id):
        for i in self.temper_emri_tree.get_children(): self.temper_emri_tree.delete(i)
        for temper_emri in self.db.temper_emirlerini_getir_by_musteri_id(musteri_id):
            self.temper_emri_tree.insert("", "end", values=temper_emri, tags=(temper_emri[4],))

    def formu_temizle(self, clear_selection=True):
        self.firma_adi_entry.delete(0, "end"); self.yetkili_entry.delete(0, "end")
        self.tel_entry.delete(0, "end"); self.email_entry.delete(0, "end")
        self.adres_entry.delete("1.0", "end")
        if clear_selection:
            self.selected_musteri_id = None
            if self.musteri_tree.selection(): self.musteri_tree.selection_remove(self.musteri_tree.selection()[0])
            for tree in [self.hesap_tree, self.is_emri_tree, self.temper_emri_tree]:
                for i in tree.get_children(): tree.delete(i)
            
    def yenile_ve_entegre_et(self):
        self.musterileri_goster(); self.formu_temizle()
        if hasattr(self.app, 'fatura_frame'): self.app.fatura_frame.verileri_yukle()
        if hasattr(self.app, 'finans_frame'): self.app.finans_frame.yenile()

    def _on_is_emri_guncellendi(self, musteri_id):
        if str(musteri_id) == str(self.selected_musteri_id):
            self.is_gecmisini_goster(musteri_id)
        self.musterileri_goster()

    def _on_temper_emri_guncellendi(self, musteri_id):
        if str(musteri_id) == str(self.selected_musteri_id):
            self.temper_gecmisini_goster(musteri_id)
        self.musterileri_goster()
