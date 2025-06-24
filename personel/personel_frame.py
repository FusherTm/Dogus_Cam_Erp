import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import Database

class PersonelFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.selected_personel_id = None
        
        self.grid_columnconfigure(1, weight=1) # Liste sütunu genişlesin
        self.grid_rowconfigure(0, weight=1) # Liste satırı genişlesin

        self.arayuzu_kur()
        self.yenile_ve_yansit() # Başlangıçta verileri yükle ve toplamı yansıt

    def arayuzu_kur(self):
        # Sol Form Sütunu
        form_frame = ctk.CTkFrame(self, width=300)
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
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Ad Soyad", "Pozisyon", "Maaş"), show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        self.tree.column("ID", width=50)
        self.tree.bind("<<TreeviewSelect>>", self.personel_sec)
        
        # YENİ: Toplam Maaş Gösterge Paneli
        toplam_maas_frame = ctk.CTkFrame(self)
        toplam_maas_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        ctk.CTkLabel(toplam_maas_frame, text="Aylık Toplam Maaş:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(20, 5), pady=10)
        self.toplam_maas_label = ctk.CTkLabel(toplam_maas_frame, text="0.00 ₺", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2CC985")
        self.toplam_maas_label.pack(side="left", padx=5, pady=10)

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
