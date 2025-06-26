import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database

class SabitGiderFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        
        # Ana layout
        self.grid_columnconfigure(1, weight=1) # Liste sütunu genişlesin
        self.grid_rowconfigure(0, weight=1)

        self.arayuzu_kur()
        self.yenile() # Başlangıçta tüm verileri yükle ve arayüzü güncelle

    def arayuzu_kur(self):
        # Sol sütun (Formlar)
        sol_sutun = ctk.CTkFrame(self, width=350)
        sol_sutun.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        sol_sutun.grid_propagate(False)

        # Sağ sütun (Liste)
        sag_sutun = ctk.CTkFrame(self)
        sag_sutun.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        sag_sutun.grid_rowconfigure(0, weight=1)
        sag_sutun.grid_columnconfigure(0, weight=1)

        # --- YENİ SABİT GİDER EKLEME FORMU ---
        gider_form_frame = ctk.CTkFrame(sol_sutun)
        gider_form_frame.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkLabel(gider_form_frame, text="Yeni Sabit Gider Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(gider_form_frame, text="Gider Adı:").pack(padx=10, pady=5, anchor="w")
        self.gider_adi_entry = ctk.CTkEntry(gider_form_frame, placeholder_text="Örn: Ofis Kirası")
        self.gider_adi_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(gider_form_frame, text="Aylık Tutar:").pack(padx=10, pady=5, anchor="w")
        self.tutar_entry = ctk.CTkEntry(gider_form_frame, placeholder_text="Örn: 5000")
        self.tutar_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(gider_form_frame, text="Kategori:").pack(padx=10, pady=5, anchor="w")
        self.kategori_menu = ctk.CTkOptionMenu(gider_form_frame, values=["Kategori Yok"])
        self.kategori_menu.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(gider_form_frame, text="Ekle", command=self.yeni_gider_ekle).pack(fill="x", padx=10, pady=10)

        # --- KATEGORİ YÖNETİMİ FORMU (YENİ) ---
        kategori_form_frame = ctk.CTkFrame(sol_sutun)
        kategori_form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(kategori_form_frame, text="Gider Kategorileri", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        kategori_ekle_cerceve = ctk.CTkFrame(kategori_form_frame, fg_color="transparent")
        kategori_ekle_cerceve.pack(fill="x", padx=5, pady=5)
        self.kategori_entry = ctk.CTkEntry(kategori_ekle_cerceve, placeholder_text="Yeni Kategori Adı")
        self.kategori_entry.pack(side="left", expand=True, fill="x", padx=(0,5))
        ctk.CTkButton(kategori_ekle_cerceve, text="Ekle", width=50, command=self.kategori_ekle).pack(side="left")
        
        self.kategori_listbox = ctk.CTkTextbox(kategori_form_frame)
        self.kategori_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(kategori_form_frame, text="Seçili Kategoriyi Sil", command=self.kategori_sil).pack(fill="x", padx=5, pady=5)

        # --- SABİT GİDERLER LİSTESİ ---
        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        self.tree = ttk.Treeview(sag_sutun, columns=("ID", "Gider Adı", "Tutar", "Kategori"), show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50)
        self.tree.heading("Gider Adı", text="Gider Adı")
        self.tree.heading("Tutar", text="Aylık Tutar", anchor="e"); self.tree.column("Tutar", anchor="e")
        self.tree.heading("Kategori", text="Kategori")
        ctk.CTkButton(sag_sutun, text="Seçili Gideri Sil", command=self.gider_sil, fg_color="#E54E55", hover_color="#C4424A").pack(fill="x", padx=10, pady=(0,10))

    def sabit_giderleri_goster(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for gider in self.db.sabit_giderleri_getir():
            self.tree.insert("", "end", values=(gider[0], gider[1], f"{gider[2]:.2f} ₺", gider[3] or "N/A"))

    def yeni_gider_ekle(self):
        gider_adi = self.gider_adi_entry.get()
        tutar_str = self.tutar_entry.get()
        kategori_adi = self.kategori_menu.get()

        if not gider_adi or not tutar_str:
            return messagebox.showerror("Hata", "Gider adı ve tutar boş olamaz.")
        if kategori_adi in ["Kategori Yok", "Önce Kategori Oluşturun"]:
            return messagebox.showerror("Hata", "Lütfen geçerli bir kategori seçin veya oluşturun.")

        try:
            tutar = float(tutar_str.replace(',', '.'))
        except ValueError:
            return messagebox.showerror("Hata", "Lütfen geçerli bir tutar girin.")

        kategoriler = self.db.kategorileri_getir()
        kategori_id = next((k[0] for k in kategoriler if k[1] == kategori_adi), None)
        if kategori_id is None:
            return messagebox.showerror("Hata", "Kategori bulunamadı. Listeyi yenileyin.")

        if self.db.sabit_gider_ekle(gider_adi, tutar, kategori_id):
            messagebox.showinfo("Başarılı", "Sabit gider başarıyla eklendi.")
            self.yenile() # Tüm arayüzü yenile
        else:
            messagebox.showerror("Hata", "Bu gider adı zaten mevcut.")

    def kategori_ekle(self):
        kategori_adi = self.kategori_entry.get()
        if not kategori_adi: return messagebox.showerror("Hata", "Kategori adı boş olamaz.")
        if self.db.kategori_ekle(kategori_adi):
            messagebox.showinfo("Başarılı", "Kategori eklendi.")
            self.kategori_entry.delete(0, 'end')
            self.yenile()
        else:
            messagebox.showerror("Hata", "Bu kategori zaten mevcut.")

    def kategori_sil(self):
        try:
            secili_metin = self.kategori_listbox.get("sel.first", "sel.last")
        except ctk.TclError:
            return messagebox.showerror("Hata", "Lütfen silmek için bir kategori seçin.")

        if not secili_metin: return messagebox.showerror("Hata", "Lütfen silmek için bir kategori seçin.")
        
        secilen_kategori_ad = secili_metin.strip()
        kategoriler = self.db.kategorileri_getir()
        kategori = next((k for k in kategoriler if k[1] == secilen_kategori_ad), None)
        
        if kategori and messagebox.askyesno("Onay", f"'{secilen_kategori_ad}' kategorisini silmek istediğinizden emin misiniz?"):
            self.db.kategori_sil(kategori[0])
            messagebox.showinfo("Başarılı", "Kategori silindi.")
            self.yenile()

    def gider_sil(self):
        secili = self.tree.focus()
        if not secili:
            return messagebox.showerror("Hata", "Silmek için bir gider seçin.")
        gider_id = self.tree.item(secili)['values'][0]
        if messagebox.askyesno("Onay", "Seçili gideri silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."):
            self.db.sabit_gider_sil(gider_id)
            messagebox.showinfo("Başarılı", "Sabit gider silindi.")
            self.yenile()

    def kategori_listesini_guncelle(self):
        kategoriler = self.db.kategorileri_getir()
        self.kategori_listbox.configure(state="normal")
        self.kategori_listbox.delete("1.0", "end")
        if kategoriler:
            self.kategori_listbox.insert("end", "\n".join([k[1] for k in kategoriler]))
        else:
            self.kategori_listbox.insert("end", "Tanımlı kategori yok.")
        self.kategori_listbox.configure(state="disabled")

        # Dropdown menüyü de güncelle
        kategori_adlari = [k[1] for k in kategoriler] if kategoriler else ["Kategori Yok"]
        self.kategori_menu.configure(values=kategori_adlari)
        self.kategori_menu.set(kategori_adlari[0] if kategoriler else "Kategori Yok")


    def yenile(self):
        """Tüm arayüzü güncel verilerle yeniden yükler."""
        self.kategori_listesini_guncelle()
        self.sabit_giderleri_goster()
        self.gider_adi_entry.delete(0, 'end')
        self.tutar_entry.delete(0, 'end')
        
        # Diğer sekmeleri de yenile (gerekirse)
        if hasattr(self.app, 'finans_frame'):
            self.app.finans_frame.yenile()
