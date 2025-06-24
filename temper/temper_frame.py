import customtkinter as ctk
from tkinter import ttk, messagebox, Menu
from database import Database

class TemperFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.secili_musteri_id_yeni_siparis = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.arayuzu_kur()
        self.temper_emirlerini_goster()

    def arayuzu_kur(self):
        # Üst Kontrol Paneli
        kontrol_frame = ctk.CTkFrame(self)
        kontrol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        kontrol_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(kontrol_frame, text="Yeni Temper Siparişi Ekle", command=self.yeni_siparis_penceresi_ac, height=35).pack(side="left", padx=10, pady=10)
        
        arama_entry_label = ctk.CTkLabel(kontrol_frame, text="Ara (Firma/Ürün):")
        arama_entry_label.pack(side="left", padx=(10,5), pady=10)
        self.arama_entry = ctk.CTkEntry(kontrol_frame, width=300)
        self.arama_entry.pack(side="left", padx=(0,10), pady=10, fill="x")
        self.arama_entry.bind("<KeyRelease>", lambda e: self.temper_emirlerini_goster(self.arama_entry.get()))

        # Ana Liste
        liste_frame = ctk.CTkFrame(self)
        liste_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        liste_frame.grid_rowconfigure(0, weight=1)
        liste_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        self.tree = ttk.Treeview(liste_frame, columns=("ID", "Tarih", "Firma Adı", "Ürün Niteliği", "Miktar", "Durum"), show="headings")
        self.tree.pack(side="left", expand=True, fill="both")
        
        vsb = ttk.Scrollbar(liste_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50)
        self.tree.heading("Tarih", text="Tarih"); self.tree.column("Tarih", width=100)
        self.tree.heading("Firma Adı", text="Firma Adı")
        self.tree.heading("Ürün Niteliği", text="Ürün Niteliği"); self.tree.column("Ürün Niteliği", width=300)
        self.tree.heading("Miktar", text="Miktar (m²)"); self.tree.column("Miktar", width=100, anchor="e")
        self.tree.heading("Durum", text="Durum"); self.tree.column("Durum", width=100, anchor="center")

        self.tree.tag_configure('Bekliyor', background='#636300', foreground='white')
        self.tree.tag_configure('Üretimde', background='#005B9A', foreground='white')
        self.tree.tag_configure('Hazır', background='#006325', foreground='white')

        self.tree.bind("<Button-3>", self.durum_degistir_menu_goster)

    def temper_emirlerini_goster(self, arama_terimi=""):
        for i in self.tree.get_children(): self.tree.delete(i)
        for siparis in self.db.temper_emirlerini_getir(arama_terimi):
            firma_adi = siparis[2] if siparis[2] else "Muhtelif Müşteri"
            gosterilecek_degerler = (siparis[0], siparis[1], firma_adi, siparis[3], siparis[4], siparis[5])
            self.tree.insert("", "end", values=gosterilecek_degerler, iid=siparis[0], tags=(siparis[5],))

    def yeni_siparis_penceresi_ac(self):
        self.secili_musteri_id_yeni_siparis = None

        win = ctk.CTkToplevel(self)
        win.title("Yeni Temper Siparişi")
        win.geometry("500x350")
        
        ctk.CTkLabel(win, text="Firma (Cari):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        musteri_cerceve = ctk.CTkFrame(win, fg_color="transparent")
        musteri_cerceve.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        musteri_cerceve.grid_columnconfigure(0, weight=1)
        self.yeni_siparis_musteri_entry = ctk.CTkEntry(musteri_cerceve, placeholder_text="Muhtelif (Seçim zorunlu değil)")
        self.yeni_siparis_musteri_entry.configure(state="disabled")
        self.yeni_siparis_musteri_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(musteri_cerceve, text="...", width=40, command=lambda: self.cari_sec_penceresi_ac(win)).grid(row=0, column=1, padx=(5,0))

        ctk.CTkLabel(win, text="Ürün Niteliği:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.yeni_siparis_nitelik_entry = ctk.CTkEntry(win, placeholder_text="Örn: 8mm Temperli Şeffaf Cam")
        self.yeni_siparis_nitelik_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(win, text="Miktar (m²):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.yeni_siparis_miktar_entry = ctk.CTkEntry(win)
        self.yeni_siparis_miktar_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        def kaydet():
            nitelik = self.yeni_siparis_nitelik_entry.get(); miktar_str = self.yeni_siparis_miktar_entry.get()
            if not all([nitelik, miktar_str]): return messagebox.showerror("Hata", "Ürün Niteliği ve Miktar alanları doldurulmalıdır.", parent=win)
            try: miktar = float(miktar_str.replace(',', '.'))
            except ValueError: return messagebox.showerror("Hata", "Miktar sayısal olmalıdır.", parent=win)
            
            self.db.temper_emri_ekle(self.secili_musteri_id_yeni_siparis, nitelik, miktar)
            messagebox.showinfo("Başarılı", "Temper siparişi başarıyla eklendi.")
            self.temper_emirlerini_goster()
            win.destroy()

        ctk.CTkButton(win, text="Kaydet", command=kaydet, height=35).grid(row=3, column=1, padx=10, pady=20, sticky="e")
        win.grid_columnconfigure(1, weight=1)
        win.transient(self); win.grab_set()

    def cari_sec_penceresi_ac(self, parent_win):
        win = ctk.CTkToplevel(parent_win)
        win.title("Cari Hesap Seç"); win.geometry("700x500")
        arama_entry = ctk.CTkEntry(win, placeholder_text="Aramak için firma adı yazın..."); arama_entry.pack(fill="x", padx=10, pady=10)
        tree = ttk.Treeview(win, columns=("ID", "Firma Adı", "Yetkili", "Bakiye"), show="headings"); tree.pack(expand=True, fill="both", padx=10, pady=10)
        for col in tree['columns']: tree.heading(col, text=col)
        
        def listeyi_doldur(arama=""):
            for i in tree.get_children(): tree.delete(i)
            for musteri in self.db.musterileri_getir(arama): tree.insert("", "end", values=(musteri[0], musteri[1], musteri[2], f"{musteri[6]:.2f} ₺"), iid=musteri[0])
        def secim_yap(event=None):
            if not tree.focus(): return
            item = tree.item(tree.focus(), 'values'); self.secili_musteri_id_yeni_siparis = item[0]
            self.yeni_siparis_musteri_entry.configure(state="normal"); self.yeni_siparis_musteri_entry.delete(0, 'end'); self.yeni_siparis_musteri_entry.insert(0, item[1]); self.yeni_siparis_musteri_entry.configure(state="disabled")
            win.destroy()
        
        arama_entry.bind("<KeyRelease>", lambda e: listeyi_doldur(arama_entry.get())); tree.bind("<Double-1>", secim_yap)
        listeyi_doldur(); win.grab_set()

    def durum_degistir_menu_goster(self, event):
        secili_id = self.tree.focus()
        if not secili_id: return
        
        menu = Menu(self.tree, tearoff=0)
        menu.add_command(label="Durumu 'Bekliyor' Yap", command=lambda: self.durumu_guncelle(secili_id, "Bekliyor"))
        menu.add_command(label="Durumu 'Üretimde' Yap", command=lambda: self.durumu_guncelle(secili_id, "Üretimde"))
        menu.add_command(label="Durumu 'Hazır' Yap", command=lambda: self.durumu_guncelle(secili_id, "Hazır"))
        menu.tk_popup(event.x_root, event.y_root)

    def durumu_guncelle(self, siparis_id, yeni_durum):
        self.db.temper_emri_durum_guncelle(siparis_id, yeni_durum)
        self.temper_emirlerini_goster(self.arama_entry.get())
