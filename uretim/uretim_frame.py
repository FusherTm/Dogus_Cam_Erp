import customtkinter as ctk
from tkinter import ttk, messagebox, Menu, filedialog
import os
import shutil
import webbrowser
from tkcalendar import DateEntry
from database import Database

class UretimFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.secili_musteri_id_yeni_is_emri = None
        self.upload_dir = os.path.join(os.path.dirname(__file__), "uploaded_lists")
        os.makedirs(self.upload_dir, exist_ok=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.arayuzu_kur()
        self.is_emirlerini_goster()

    def arayuzu_kur(self):
        # Üst Kontrol Paneli
        kontrol_frame = ctk.CTkFrame(self)
        kontrol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        kontrol_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(kontrol_frame, text="Yeni İş Emri Ekle", command=self.yeni_is_emri_penceresi_ac, height=35).pack(side="left", padx=10, pady=10)
        
        arama_entry_label = ctk.CTkLabel(kontrol_frame, text="Ara (Firma/Ürün):")
        arama_entry_label.pack(side="left", padx=(10,5), pady=10)
        self.arama_entry = ctk.CTkEntry(kontrol_frame, width=300)
        self.arama_entry.pack(side="left", padx=(0,10), pady=10, fill="x")
        self.arama_entry.bind("<KeyRelease>", lambda e: self.is_emirlerini_goster(self.arama_entry.get()))

        # Ana Liste
        liste_frame = ctk.CTkFrame(self)
        liste_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        liste_frame.grid_rowconfigure(0, weight=1)
        liste_frame.grid_columnconfigure(0, weight=1)

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
        
        self.tree = ttk.Treeview(
            liste_frame,
            columns=("ID", "Tarih", "Firma Adı", "Ürün Niteliği", "Miktar", "Durum", "Liste"),
            show="headings",
        )
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
        self.tree.heading("Liste", text="Liste"); self.tree.column("Liste", width=80, anchor="center")

        self.tree.tag_configure('Bekliyor', background='#636300', foreground='white')
        self.tree.tag_configure('Üretimde', background='#005B9A', foreground='white')
        self.tree.tag_configure('Hazır', background='#006325', foreground='white')

        self.tree.bind("<Button-3>", self.durum_degistir_menu_goster)
        self.tree.bind("<Button-1>", self._liste_btn)

    def verileri_yukle(self):
        """Bu fonksiyon, ana iş listesini yeniler."""
        self.is_emirlerini_goster()

    def is_emirlerini_goster(self, arama_terimi=""):
        for i in self.tree.get_children(): self.tree.delete(i)
        for is_emri in self.db.is_emirlerini_getir(arama_terimi):
            # GÜNCELLENDİ: Firma adı yoksa "Muhtelif Müşteri" yaz
            firma_adi = is_emri[2] if is_emri[2] else "Muhtelif Müşteri"
            liste_var = self.db.cam_listesi_var_mi(is_emri[0]) or self.db.is_emri_liste_dosyasi_getir(is_emri[0])
            btn_text = "Listeyi Gör" if liste_var else ""
            gosterilecek_degerler = (
                is_emri[0],
                is_emri[1],
                firma_adi,
                is_emri[3],
                is_emri[4],
                is_emri[5],
                btn_text,
            )
            self.tree.insert("", "end", values=gosterilecek_degerler, iid=is_emri[0], tags=(is_emri[5],))

    def yeni_is_emri_penceresi_ac(self):
        self.secili_musteri_id_yeni_is_emri = None
        self.cam_listesi_temp = []
        self.yuklenen_liste_path = None

        win = ctk.CTkToplevel(self)
        win.title("Yeni İş Emri")
        win.geometry("500x450")

        ctk.CTkLabel(win, text="Tarih:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.is_emri_tarih_entry = DateEntry(win, date_pattern='y-mm-dd')
        self.is_emri_tarih_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(win, text="Firma (Cari):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        musteri_cerceve = ctk.CTkFrame(win, fg_color="transparent")
        musteri_cerceve.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        musteri_cerceve.grid_columnconfigure(0, weight=1)
        self.yeni_is_emri_musteri_entry = ctk.CTkEntry(musteri_cerceve, placeholder_text="Muhtelif (Seçim zorunlu değil)")
        # show a default value so it's clear a customer selection isn't required
        self.yeni_is_emri_musteri_entry.insert(0, "Muhtelif")
        self.yeni_is_emri_musteri_entry.configure(state="disabled")
        self.yeni_is_emri_musteri_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(musteri_cerceve, text="...", width=40, command=lambda: self.cari_sec_penceresi_ac(win)).grid(row=0, column=1, padx=(5,0))

        ctk.CTkLabel(win, text="Firmanın Müşterisi:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.is_emri_firma_musterisi_entry = ctk.CTkEntry(win)
        self.is_emri_firma_musterisi_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(win, text="Ürün Niteliği:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.yeni_is_emri_nitelik_entry = ctk.CTkEntry(win, placeholder_text="Örn: 4+16+4 Konfor Isıcam")
        self.yeni_is_emri_nitelik_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(win, text="Miktar (m²):").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.yeni_is_emri_miktar_entry = ctk.CTkEntry(win)
        self.yeni_is_emri_miktar_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(win, text="Fiyat:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.is_emri_fiyat_entry = ctk.CTkEntry(win)
        self.is_emri_fiyat_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        def dosya_sec():
            path = filedialog.askopenfilename(filetypes=[("Liste", "*.pdf *.jpg *.jpeg *.png")])
            if path:
                self.yuklenen_liste_path = path

        def cam_listesi_penceresi_ac():
            self.cam_listesi_temp = []
            p = ctk.CTkToplevel(win)
            p.title("Cam Listesi")
            p.geometry("400x400")

            count_frame = ctk.CTkFrame(p)
            count_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(count_frame, text="Kaç adet cam gireceksiniz?").pack(pady=10)
            adet_entry = ctk.CTkEntry(count_frame)
            adet_entry.pack(pady=10)

            def olustur():
                try:
                    adet = int(adet_entry.get())
                except ValueError:
                    return messagebox.showerror("Hata", "Geçerli bir sayı girin.", parent=p)
                count_frame.destroy()

                liste_frame = ctk.CTkScrollableFrame(p, width=360, height=250)
                liste_frame.pack(fill="both", expand=True, padx=10, pady=10)

                headers = ["En", "Boy", "Poz", "m²"]
                for idx, h in enumerate(headers):
                    ctk.CTkLabel(liste_frame, text=h).grid(row=0, column=idx, padx=5)

                en_entries = []
                boy_entries = []
                poz_entries = []
                m2_labels = []

                total_var = ctk.StringVar(value="Toplam m²: 0.00")

                def hesapla(*args):
                    toplam = 0
                    for i in range(adet):
                        try:
                            en = float(en_entries[i].get())
                            boy = float(boy_entries[i].get())
                            m2 = en * boy / 10000
                        except ValueError:
                            m2 = 0
                        m2_labels[i].configure(text=f"{m2:.2f}")
                        toplam += m2
                    total_var.set(f"Toplam m²: {toplam:.2f}")

                for i in range(adet):
                    en_e = ctk.CTkEntry(liste_frame, width=60)
                    en_e.grid(row=i+1, column=0, padx=5, pady=2)
                    boy_e = ctk.CTkEntry(liste_frame, width=60)
                    boy_e.grid(row=i+1, column=1, padx=5, pady=2)
                    poz_e = ctk.CTkEntry(liste_frame, width=80)
                    poz_e.grid(row=i+1, column=2, padx=5, pady=2)
                    m2_l = ctk.CTkLabel(liste_frame, text="0.00")
                    m2_l.grid(row=i+1, column=3, padx=5, pady=2)

                    en_e.bind("<KeyRelease>", lambda e, idx=i: hesapla())
                    boy_e.bind("<KeyRelease>", lambda e, idx=i: hesapla())

                    en_entries.append(en_e)
                    boy_entries.append(boy_e)
                    poz_entries.append(poz_e)
                    m2_labels.append(m2_l)

                toplam_label = ctk.CTkLabel(p, textvariable=total_var)
                toplam_label.pack(pady=5)

                def kaydet_liste():
                    self.cam_listesi_temp = []
                    toplam = 0
                    for i in range(adet):
                        try:
                            en = float(en_entries[i].get())
                            boy = float(boy_entries[i].get())
                            m2 = en * boy / 10000
                        except ValueError:
                            continue
                        poz = poz_entries[i].get()
                        self.cam_listesi_temp.append((en, boy, m2, poz))
                        toplam += m2
                    self.yeni_is_emri_miktar_entry.delete(0, 'end')
                    self.yeni_is_emri_miktar_entry.insert(0, f"{toplam:.2f}")
                    p.destroy()

                ctk.CTkButton(p, text="Kaydet", command=kaydet_liste).pack(pady=10)

            ctk.CTkButton(count_frame, text="Tamam", command=olustur).pack(pady=10)
            p.transient(win)
            p.grab_set()

        def kaydet():
            nitelik = self.yeni_is_emri_nitelik_entry.get()
            miktar_str = self.yeni_is_emri_miktar_entry.get()
            fiyat_str = self.is_emri_fiyat_entry.get()
            tarih = self.is_emri_tarih_entry.get_date().strftime('%Y-%m-%d')
            firma_must = self.is_emri_firma_musterisi_entry.get()
            if not all([nitelik, miktar_str, fiyat_str]):
                return messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır.", parent=win)
            try:
                miktar = float(miktar_str.replace(',', '.'))
                fiyat = float(fiyat_str.replace(',', '.'))
            except ValueError:
                return messagebox.showerror("Hata", "Miktar ve Fiyat sayısal olmalıdır.", parent=win)

            is_id = self.db.is_emri_ekle(self.secili_musteri_id_yeni_is_emri, firma_must, nitelik, miktar, fiyat, tarih)
            for en, boy, m2, poz in self.cam_listesi_temp:
                self.db.cam_listesi_ekle(is_id, en, boy, m2, poz)
            if self.yuklenen_liste_path:
                ext = os.path.splitext(self.yuklenen_liste_path)[1]
                dest = os.path.join(self.upload_dir, f"isemri_{is_id}_liste{ext}")
                shutil.copy(self.yuklenen_liste_path, dest)
                self.db.is_emri_liste_dosyasi_guncelle(is_id, dest)
            if self.secili_musteri_id_yeni_is_emri:
                self.db.musteri_hesap_hareketi_ekle(self.secili_musteri_id_yeni_is_emri, tarih, f"İş Emri: {nitelik}", fiyat, 0)
            messagebox.showinfo("Başarılı", "İş emri başarıyla eklendi.")
            self.is_emirlerini_goster()
            if self.secili_musteri_id_yeni_is_emri and hasattr(self.app, 'musteri_frame'):
                self.app.musteri_frame.is_gecmisini_goster(self.secili_musteri_id_yeni_is_emri)
                self.app.musteri_frame.hesap_hareketlerini_goster(self.secili_musteri_id_yeni_is_emri)
                self.app.musteri_frame.musterileri_goster()
            win.destroy()

        ctk.CTkButton(win, text="Liste Ekle", command=cam_listesi_penceresi_ac).grid(row=6, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkButton(win, text="PDF / Resim Liste Yükle", command=dosya_sec).grid(row=7, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkButton(win, text="Kaydet", command=kaydet, height=35).grid(row=8, column=1, padx=10, pady=20, sticky="e")
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
            item = tree.item(tree.focus(), 'values'); self.secili_musteri_id_yeni_is_emri = item[0]
            self.yeni_is_emri_musteri_entry.configure(state="normal"); self.yeni_is_emri_musteri_entry.delete(0, 'end'); self.yeni_is_emri_musteri_entry.insert(0, item[1]); self.yeni_is_emri_musteri_entry.configure(state="disabled")
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

    def durumu_guncelle(self, is_emri_id, yeni_durum):
        self.db.is_emri_durum_guncelle(is_emri_id, yeni_durum)
        self.is_emirlerini_goster(self.arama_entry.get())
        emri = self.db.is_emri_getir_by_id(is_emri_id)
        if emri and hasattr(self.app, 'event_bus'):
            self.app.event_bus.publish('is_emri_guncellendi', emri[1])

    def _liste_btn(self, event):
        col = self.tree.identify_column(event.x)
        if col != "#7":
            return
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        values = self.tree.item(row_id, "values")
        if len(values) < 7 or values[6] != "Listeyi Gör":
            return
        self._cam_listesi_penceresi_ac(values[0])

    def _cam_listesi_penceresi_ac(self, is_emri_id):
        liste = self.db.cam_listesini_getir(is_emri_id)
        dosya = self.db.is_emri_liste_dosyasi_getir(is_emri_id)
        if not liste and not dosya:
            messagebox.showinfo("Bilgi", "Bu iş emrine ait cam listesi bulunamadı.")
            return
        if dosya and not liste:
            if os.path.isfile(dosya):
                webbrowser.open_new_tab('file://' + os.path.abspath(dosya))
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı.")
            return

        is_emri = self.db.is_emri_getir_by_id(is_emri_id)
        musteri_adi = ""
        if is_emri[1]:
            musteri = self.db.musteri_getir_by_id(is_emri[1])
            if musteri:
                musteri_adi = musteri[1]
        firma_musterisi = is_emri[2] or ""
        toplam_m2 = sum((en * boy) / 10000 for en, boy, *_ in liste)

        win = ctk.CTkToplevel(self)
        win.title("Cam Listesi")
        win.geometry("500x400")

        info = ctk.CTkFrame(win)
        info.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(info, text=f"Cari: {musteri_adi or 'Muhtelif'}").pack(anchor="w")
        if firma_musterisi:
            ctk.CTkLabel(info, text=f"Firmanın Müşterisi: {firma_musterisi}").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Toplam Cam Sayısı: {len(liste)}").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Toplam m²: {toplam_m2:.2f}").pack(anchor="w")

        tree = ttk.Treeview(
            win,
            columns=("No", "En", "Boy", "m2", "Poz"),
            show="headings",
        )
        tree.pack(expand=True, fill="both", padx=10, pady=10)
        tree.heading("No", text="Sıra No")
        tree.column("No", width=60, anchor="center")
        tree.heading("En", text="En (cm)")
        tree.column("En", width=80, anchor="center")
        tree.heading("Boy", text="Boy (cm)")
        tree.column("Boy", width=80, anchor="center")
        tree.heading("m2", text="m²")
        tree.column("m2", width=80, anchor="center")
        tree.heading("Poz", text="Pozisyon")
        tree.column("Poz", width=100)

        for idx, (en, boy, _m2, poz) in enumerate(liste, start=1):
            m2_val = en * boy / 10000
            tree.insert("", "end", values=(idx, en, boy, f"{m2_val:.2f}", poz))

        if dosya:
            ctk.CTkButton(win, text="Yüklenen Dosyayı Aç", command=lambda: webbrowser.open_new_tab('file://' + os.path.abspath(dosya))).pack(pady=5)

        win.transient(self)
        win.grab_set()
