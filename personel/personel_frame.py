import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
from database import Database

class PersonelFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.selected_personel_id = None

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        self.tabview.add("Personel Bilgileri")
        self.tabview.add("İzin Yönetimi")
        self.personel_tab = self.tabview.tab("Personel Bilgileri")
        self.izin_tab = self.tabview.tab("İzin Yönetimi")

        self.personel_tab.grid_columnconfigure(1, weight=1)
        self.personel_tab.grid_rowconfigure(0, weight=1)
        self.izin_tab.grid_columnconfigure(1, weight=1)
        self.izin_tab.grid_rowconfigure(0, weight=1)

        self.arayuzu_kur()
        self.izin_arayuzu_kur()
        self.yenile_ve_yansit()
        self.personel_combobox_doldur()
        self.izinleri_listele()

    def arayuzu_kur(self):
        # Sol Form Sütunu
        form_frame = ctk.CTkFrame(self.personel_tab, width=300)
        form_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="ns")
        form_frame.grid_propagate(False)

        ctk.CTkLabel(form_frame, text="Personel Bilgileri", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkLabel(form_frame, text="Ad Soyad:").pack(padx=20, pady=5, anchor="w")
        self.ad_entry = ctk.CTkEntry(form_frame)
        self.ad_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Pozisyon:").pack(padx=20, pady=5, anchor="w")
        self.pozisyon_entry = ctk.CTkEntry(form_frame)
        self.pozisyon_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Maaş:").pack(padx=20, pady=5, anchor="w")
        self.maas_entry = ctk.CTkEntry(form_frame)
        self.maas_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="TC Kimlik No:").pack(padx=20, pady=5, anchor="w")
        self.tc_entry = ctk.CTkEntry(form_frame)
        self.tc_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="Telefon:").pack(padx=20, pady=5, anchor="w")
        self.tel_entry = ctk.CTkEntry(form_frame)
        self.tel_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(form_frame, text="İşe Başlama Tarihi:").pack(padx=20, pady=5, anchor="w")
        self.tarih_entry = DateEntry(form_frame, date_pattern='y-mm-dd')
        self.tarih_entry.pack(padx=20, pady=5, fill="x")
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=10)
        ctk.CTkButton(button_frame, text="Ekle", command=self.personel_ekle).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="Güncelle", command=self.personel_guncelle).pack(side="left", expand=True, padx=5)
        # YENİ: Sil butonu eklendi
        ctk.CTkButton(button_frame, text="Sil", command=self.personel_sil, fg_color="#E54E55", hover_color="#C4424A").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(form_frame, text="Formu Temizle", command=self.formu_temizle).pack(side="bottom", fill="x", padx=10, pady=10)

        # Sağ Liste Sütunu
        list_frame = ctk.CTkFrame(self.personel_tab)
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Ad Soyad", "Pozisyon", "Maaş"), show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        self.tree.column("ID", width=50)
        self.tree.bind("<<TreeviewSelect>>", self.personel_sec)
        
        # YENİ: Toplam Maaş Gösterge Paneli
        toplam_maas_frame = ctk.CTkFrame(self.personel_tab)
        toplam_maas_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        ctk.CTkLabel(toplam_maas_frame, text="Aylık Toplam Maaş:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(20, 5), pady=10)
        self.toplam_maas_label = ctk.CTkLabel(toplam_maas_frame, text="0.00 ₺", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2CC985")
        self.toplam_maas_label.pack(side="left", padx=5, pady=10)

    def izin_arayuzu_kur(self):
        # Sol panel - izin talep formu
        form_frame = ctk.CTkFrame(self.izin_tab, width=300)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        form_frame.grid_propagate(False)

        ctk.CTkLabel(form_frame, text="İzin Talep Formu", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkLabel(form_frame, text="Personel:").pack(padx=20, pady=5, anchor="w")
        self.personel_cb = ctk.CTkComboBox(form_frame, values=[], command=self.personel_cb_degisti)
        self.personel_cb.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="İzin Tipi:").pack(padx=20, pady=5, anchor="w")
        self.izin_tipi_cb = ctk.CTkComboBox(form_frame, values=["Yıllık İzin", "Raporlu", "Mazeret İzni", "Ücretsiz İzin"])
        self.izin_tipi_cb.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="Başlangıç Tarihi (YYYY-MM-DD)").pack(padx=20, pady=5, anchor="w")
        self.baslangic_entry = DateEntry(form_frame, date_pattern='y-mm-dd')
        self.baslangic_entry.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="Bitiş Tarihi (YYYY-MM-DD)").pack(padx=20, pady=5, anchor="w")
        self.bitis_entry = DateEntry(form_frame, date_pattern='y-mm-dd')
        self.bitis_entry.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form_frame, text="Açıklama:").pack(padx=20, pady=5, anchor="w")
        self.aciklama_text = ctk.CTkTextbox(form_frame, height=80)
        self.aciklama_text.pack(padx=20, pady=5, fill="both", expand=True)

        self.izin_ozet_frame = ctk.CTkFrame(form_frame)
        self.izin_ozet_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(
            self.izin_ozet_frame,
            text="Yıllık İzin Özeti",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 5))
        self.hak_edilen_label = ctk.CTkLabel(
            self.izin_ozet_frame, text="Hak Edilen Yıllık İzin: -"
        )
        self.hak_edilen_label.pack(anchor="w")
        self.kullanilan_label = ctk.CTkLabel(
            self.izin_ozet_frame, text="Bu Yıl Kullanılan: -"
        )
        self.kullanilan_label.pack(anchor="w")
        self.kalan_label = ctk.CTkLabel(
            self.izin_ozet_frame,
            text="Kalan İzin: -",
            font=ctk.CTkFont(weight="bold"),
        )
        self.kalan_label.pack(anchor="w")

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(btn_frame, text="İzin Talebi Oluştur", command=self.izin_talebi_olustur).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Formu Temizle", command=self.izin_formu_temizle).pack(side="left", expand=True, padx=5)

        # Sağ panel - izin listesi
        list_frame = ctk.CTkFrame(self.izin_tab)
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.izin_tree = ttk.Treeview(list_frame, columns=("ID", "Ad", "Tip", "Başlangıç", "Bitiş", "Gün", "Durum"), show="headings")
        self.izin_tree.pack(expand=True, fill="both", padx=10, pady=10)
        for col in ("ID", "Ad", "Tip", "Başlangıç", "Bitiş", "Gün", "Durum"):
            self.izin_tree.heading(col, text=col)
        self.izin_tree.column("ID", width=50)

        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.pack(pady=(0,10))
        ctk.CTkButton(action_frame, text="Seçili İzni Onayla", command=lambda: self.izin_durum_guncelle("Onaylandı")).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Seçili İzni Reddet", command=lambda: self.izin_durum_guncelle("Reddedildi")).pack(side="left", padx=5)

    def personelleri_goster(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for personel in self.db.personelleri_getir():
            maas_str = f"{personel[4]:.2f} ₺" if personel[4] is not None else "N/A"
            self.tree.insert("", "end", values=(personel[0], personel[1], personel[2], maas_str), iid=personel[0])
    
    def personel_ekle(self):
        ad = self.ad_entry.get(); pozisyon = self.pozisyon_entry.get(); maas = self.maas_entry.get()
        tc = self.tc_entry.get(); tel = self.tel_entry.get(); tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d')
        if not all([ad, pozisyon, maas, tc, tel, tarih]): return messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır.")
        try:
            self.db.personel_ekle(ad, pozisyon, tarih, float(maas), tc, tel)
            messagebox.showinfo("Başarılı", "Personel eklendi.")
            self.yenile_ve_yansit()
        except ValueError: messagebox.showerror("Hata", "Maaş sayısal bir değer olmalıdır.")

    def personel_guncelle(self):
        if not self.selected_personel_id: return messagebox.showerror("Hata", "Güncellemek için bir personel seçiniz.")
        ad = self.ad_entry.get(); pozisyon = self.pozisyon_entry.get(); maas = self.maas_entry.get()
        tc = self.tc_entry.get(); tel = self.tel_entry.get(); tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d')
        if not all([ad, pozisyon, maas, tc, tel, tarih]): return messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır.")
        try:
            self.db.personel_guncelle(self.selected_personel_id, ad, pozisyon, tarih, float(maas), tc, tel)
            messagebox.showinfo("Başarılı", "Personel bilgileri güncellendi.")
            self.yenile_ve_yansit()
        except ValueError: messagebox.showerror("Hata", "Maaş sayısal bir değer olmalıdır.")

    # YENİ: Personel silme fonksiyonu
    def personel_sil(self):
        if not self.selected_personel_id: return messagebox.showerror("Hata", "Silmek için bir personel seçin.")
        if messagebox.askyesno("Onay", "Seçili personeli silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."):
            self.db.personel_sil(self.selected_personel_id)
            messagebox.showinfo("Başarılı", "Personel silindi.")
            self.yenile_ve_yansit()

    def personel_sec(self, event=None):
        if not self.tree.focus(): return
        self.selected_personel_id = self.tree.focus()
        item = self.tree.item(self.selected_personel_id, 'values')
        # DB'den tam veriyi al
        personel = self.db.personel_getir_by_id(self.selected_personel_id) 
        if personel:
            self.formu_temizle(clear_selection=False)
            self.ad_entry.insert(0, personel[1])
            self.pozisyon_entry.insert(0, personel[2])
            self.tarih_entry.set_date(personel[3])
            self.maas_entry.insert(0, str(personel[4]))
            self.tc_entry.insert(0, personel[5])
            self.tel_entry.insert(0, personel[6])

    def formu_temizle(self, clear_selection=True):
        self.ad_entry.delete(0, 'end'); self.pozisyon_entry.delete(0, 'end')
        self.maas_entry.delete(0, 'end'); self.tc_entry.delete(0, 'end')
        self.tel_entry.delete(0, 'end')
        if clear_selection:
            self.selected_personel_id = None
            if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])

    # YENİ: Ana yenileme ve entegrasyon fonksiyonu
    def yenile_ve_yansit(self):
        self.personelleri_goster()
        self.formu_temizle()
        toplam_maas = self.db.tum_maas_toplamini_getir()
        self.toplam_maas_label.configure(text=f"{toplam_maas:.2f} ₺")
        self.db.sabit_gider_ekle_veya_guncelle("Toplam Personel Maaşları", toplam_maas)
        if hasattr(self.app, 'sabit_gider_frame'):
            self.app.sabit_gider_frame.sabit_giderleri_goster()

    # --- İzin Yönetimi Fonksiyonları ---
    def personel_combobox_doldur(self):
        self.personel_map = {}
        adlar = []
        for p in self.db.personelleri_getir():
            adlar.append(p[1])
            self.personel_map[p[1]] = p[0]
        self.personel_cb.configure(values=adlar)
        if adlar:
            self.personel_cb.set(adlar[0])
            self.personel_cb_degisti(adlar[0])
        else:
            self.personel_cb.set("")

    def personel_cb_degisti(self, secim):
        pid = self.personel_map.get(secim)
        if not pid:
            self.hak_edilen_label.configure(text="Hak Edilen Yıllık İzin: -")
            self.kullanilan_label.configure(text="Bu Yıl Kullanılan: -")
            self.kalan_label.configure(text="Kalan İzin: -")
            return
        hak, kullanilan, kalan = self.db.izin_ozetini_getir(pid)
        self.hak_edilen_label.configure(text=f"Hak Edilen Yıllık İzin: {hak} Gün")
        self.kullanilan_label.configure(text=f"Bu Yıl Kullanılan: {kullanilan} Gün")
        self.kalan_label.configure(text=f"Kalan İzin: {kalan} Gün")

    def izin_formu_temizle(self):
        self.izin_tipi_cb.set("")
        self.aciklama_text.delete("1.0", "end")

    def izin_talebi_olustur(self):
        ad = self.personel_cb.get()
        if ad not in self.personel_map:
            return messagebox.showerror("Hata", "Geçerli bir personel seçiniz.")
        pid = self.personel_map[ad]
        izin_tipi = self.izin_tipi_cb.get()
        baslangic = self.baslangic_entry.get_date().strftime("%Y-%m-%d")
        bitis = self.bitis_entry.get_date().strftime("%Y-%m-%d")
        gun_sayisi = (
            datetime.datetime.strptime(bitis, "%Y-%m-%d")
            - datetime.datetime.strptime(baslangic, "%Y-%m-%d")
        ).days + 1
        aciklama = self.aciklama_text.get("1.0", "end").strip()
        self.db.izin_ekle(
            pid,
            izin_tipi,
            baslangic,
            bitis,
            gun_sayisi,
            aciklama,
        )
        messagebox.showinfo("Başarılı", "İzin talebi oluşturuldu.")
        self.izin_formu_temizle()
        self.izinleri_listele()

    def izinleri_listele(self):
        for i in self.izin_tree.get_children():
            self.izin_tree.delete(i)
        for row in self.db.izinleri_getir():
            self.izin_tree.insert("", "end", values=row, iid=row[0])

    def izin_durum_guncelle(self, yeni_durum):
        secili = self.izin_tree.focus()
        if not secili:
            return messagebox.showerror("Hata", "Bir izin seçin.")
        self.db.izin_durum_guncelle(secili, yeni_durum)
        self.izinleri_listele()
