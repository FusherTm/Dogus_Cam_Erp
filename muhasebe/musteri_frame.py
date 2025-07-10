import customtkinter as ctk
from tkinter import ttk, messagebox
import tempfile
import os
import webbrowser
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
        
        style = ttk.Style(); style.theme_use("clam"); style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )
        self.musteri_tree = ttk.Treeview(list_frame, columns=("ID", "Firma Adı", "Yetkili", "Bakiye"), show="headings"); self.musteri_tree.pack(expand=True, fill="both", padx=10, pady=10)
        # "ID" sütun başlığını kullanıcı arayüzünde "No" olarak göster
        self.musteri_tree.heading("ID", text="No"); self.musteri_tree.column("ID", width=50)
        self.musteri_tree.heading("Firma Adı", text="Firma Adı"); self.musteri_tree.heading("Yetkili", text="Yetkili")
        self.musteri_tree.heading("Bakiye", text="Bakiye", anchor="e"); self.musteri_tree.column("Bakiye", anchor="e")
        self.musteri_tree.bind("<<TreeviewSelect>>", self.musteri_sec)

        # Ekstre görüntüleme butonu
        self.ekstre_button = ctk.CTkButton(list_frame, text="Hesap Ekstresi", state="disabled", command=self.hesap_ekstresi_goruntule)
        self.ekstre_button.pack(fill="x", padx=10, pady=(0,10))

        # GÜNCELLENDİ: Alt kısma yeni sekme eklendi
        alt_tab_view = ctk.CTkTabview(self); alt_tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        alt_tab_view.add("Hesap Ekstresi"); alt_tab_view.add("İş Emirleri"); alt_tab_view.add("Temper Siparişleri"); alt_tab_view.add("Fatura Geçmişi")
        
        # --- Hesap Ekstresi Sekmesi ---
        hesap_frame = alt_tab_view.tab("Hesap Ekstresi"); hesap_frame.grid_rowconfigure(0, weight=1); hesap_frame.grid_columnconfigure(0, weight=1)
        self.hesap_tree = ttk.Treeview(hesap_frame, columns=("Tarih", "Açıklama", "Borç", "Alacak", "Bakiye"), show="headings")
        self.hesap_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for col in self.hesap_tree['columns']: self.hesap_tree.heading(col, text=col)
        for col in ["Borç", "Alacak", "Bakiye"]: self.hesap_tree.column(col, anchor="e")

        # --- İş Emirleri Sekmesi ---
        is_gecmisi_frame = alt_tab_view.tab("İş Emirleri"); is_gecmisi_frame.grid_rowconfigure(0, weight=1); is_gecmisi_frame.grid_columnconfigure(0, weight=1)
        self.is_emri_tree = ttk.Treeview(
            is_gecmisi_frame,
            columns=("ID", "Tarih", "Ürün Niteliği", "Miktar", "Durum", "Liste"),
            show="headings",
        )
        self.is_emri_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.is_emri_tree.heading("ID", text="İş Emri No"); self.is_emri_tree.column("ID", width=80)
        self.is_emri_tree.heading("Tarih", text="Tarih"); self.is_emri_tree.column("Tarih", width=100)
        self.is_emri_tree.heading("Ürün Niteliği", text="Ürün Niteliği")
        self.is_emri_tree.heading("Miktar", text="Miktar (m²)", anchor="e"); self.is_emri_tree.column("Miktar", width=100, anchor="e")
        self.is_emri_tree.heading("Durum", text="Durum", anchor="center"); self.is_emri_tree.column("Durum", width=100, anchor="center")
        self.is_emri_tree.heading("Liste", text="Liste"); self.is_emri_tree.column("Liste", width=80, anchor="center")
        self.is_emri_tree.tag_configure('Bekliyor', background='#636300', foreground='white'); self.is_emri_tree.tag_configure('Üretimde', background='#005B9A', foreground='white'); self.is_emri_tree.tag_configure('Hazır', background='#006325', foreground='white')
        self.is_emri_tree.bind("<Button-1>", self._is_emri_liste_btn)

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

        # --- Fatura Geçmişi Sekmesi ---
        invoice_frame = alt_tab_view.tab("Fatura Geçmişi"); invoice_frame.grid_rowconfigure(0, weight=1); invoice_frame.grid_columnconfigure(0, weight=1)
        self.fatura_tree = ttk.Treeview(invoice_frame, columns=("ID", "Tarih", "Fatura No", "Tutar"), show="headings")
        self.fatura_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.fatura_tree.heading("ID", text="ID"); self.fatura_tree.column("ID", width=50)
        self.fatura_tree.heading("Tarih", text="Tarih"); self.fatura_tree.column("Tarih", width=100)
        self.fatura_tree.heading("Fatura No", text="Fatura No")
        self.fatura_tree.heading("Tutar", text="Tutar", anchor="e"); self.fatura_tree.column("Tutar", anchor="e")


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
        if hasattr(self.app, 'finans_frame'):
            self.app.finans_frame.secilen_cari_id = self.selected_musteri_id
        musteri = self.db.musteri_getir_by_id(self.selected_musteri_id)
        if musteri:
            self.formu_temizle(clear_selection=False)
            self.firma_adi_entry.insert(0, musteri[1]); self.yetkili_entry.insert(0, musteri[2])
            self.tel_entry.insert(0, musteri[3]); self.email_entry.insert(0, musteri[4])
            self.adres_entry.insert("1.0", musteri[5])
            self.hesap_hareketlerini_goster(musteri[0])
            self.is_gecmisini_goster(musteri[0])
            self.temper_gecmisini_goster(musteri[0])
            self.fatura_gecmisini_goster(musteri[0])
            self.ekstre_button.configure(state="normal")

    def hesap_hareketlerini_goster(self, musteri_id):
        self.hesap_tree.delete(*self.hesap_tree.get_children())
        hareketler = self.db.finansal_hareketleri_getir(musteri_id)
        calisan_bakiye = 0.0
        for h in hareketler:
            borc = float(h[2] or 0.0)
            alacak = float(h[3] or 0.0)
            calisan_bakiye += borc - alacak
            borc_str = f"{borc:.2f} ₺"
            alacak_str = f"{alacak:.2f} ₺"
            bakiye_str = f"{calisan_bakiye:.2f} ₺"
            self.hesap_tree.insert("", "end", values=(h[0], h[1], borc_str, alacak_str, bakiye_str))
            
    def is_gecmisini_goster(self, musteri_id):
        for i in self.is_emri_tree.get_children(): self.is_emri_tree.delete(i)
        for is_emri in self.db.is_emirlerini_getir_by_musteri_id(musteri_id):
            liste_var = self.db.cam_listesi_var_mi(is_emri[0]) or self.db.is_emri_liste_dosyasi_getir(is_emri[0])
            btn_text = "Listeyi Gör" if liste_var else ""
            values = (*is_emri, btn_text)
            self.is_emri_tree.insert("", "end", values=values, tags=(is_emri[4],))

    # YENİ: Müşterinin temper geçmişini listeleyen fonksiyon
    def temper_gecmisini_goster(self, musteri_id):
        for i in self.temper_emri_tree.get_children(): self.temper_emri_tree.delete(i)
        for temper_emri in self.db.temper_emirlerini_getir_by_musteri_id(musteri_id):
            self.temper_emri_tree.insert("", "end", values=temper_emri, tags=(temper_emri[4],))

    def fatura_gecmisini_goster(self, musteri_id):
        for i in self.fatura_tree.get_children():
            self.fatura_tree.delete(i)
        for fatura in self.db.faturalari_getir_by_musteri_id(musteri_id):
            self.fatura_tree.insert(
                "", "end", values=(fatura[0], fatura[1], fatura[2], f"{fatura[3]:.2f} ₺")
            )

    def _is_emri_liste_btn(self, event):
        col = self.is_emri_tree.identify_column(event.x)
        if col != "#6":
            return
        row_id = self.is_emri_tree.identify_row(event.y)
        if not row_id:
            return
        values = self.is_emri_tree.item(row_id, "values")
        if len(values) < 6 or values[5] != "Listeyi Gör":
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
        aciklama = is_emri[3] or ""
        toplam_m2 = sum((en * boy) / 10000 for en, boy, *_ in liste)

        win = ctk.CTkToplevel(self)
        win.title("Cam Listesi")
        win.geometry("500x400")

        info = ctk.CTkFrame(win)
        info.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(info, text=f"Cari: {musteri_adi or 'Muhtelif'}").pack(anchor="w")
        if firma_musterisi:
            ctk.CTkLabel(info, text=f"Firmanın Müşterisi: {firma_musterisi}").pack(anchor="w")
        if aciklama:
            ctk.CTkLabel(info, text=f"Açıklama: {aciklama}").pack(anchor="w")
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

    # Yeni: seçili müşterinin hesap ekstresini HTML olarak görüntüle
    def hesap_ekstresi_goruntule(self):
        if not self.selected_musteri_id:
            return messagebox.showerror("Hata", "Önce bir müşteri seçin.")

        musteri = self.db.musteri_getir_by_id(self.selected_musteri_id)
        hareketler = self.db.cari_hareketlerini_getir(self.selected_musteri_id)
        html = self._ekstre_html_olustur(musteri, hareketler)

        fd, html_path = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html)

        webbrowser.open_new_tab('file://' + html_path)

        win = ctk.CTkToplevel(self)
        win.title("Hesap Ekstresi")
        win.geometry('350x120')
        msg = "Ekstre tarayıcıda açıldı. Yazdırmak için tarayıcıdan Ctrl+P kullanın."
        ctk.CTkLabel(win, text=msg, wraplength=320).pack(padx=10, pady=10)
        ctk.CTkButton(win, text="PDF İndir", command=lambda: self._ekstre_pdf_indir(html, musteri, win)).pack(pady=5)
        win.grab_set()

    def _ekstre_html_olustur(self, musteri, hareketler):
        firma = musteri[1]
        yetkili = musteri[2] or ''
        tel = musteri[3] or ''
        email = musteri[4] or ''
        rows = ''
        for h in hareketler:
            borc = f"{h[4]:.2f}" if h[4] else ''
            alacak = f"{h[5]:.2f}" if h[5] else ''
            bakiye = f"{h[6]:.2f}"
            rows += f"<tr><td>{h[2]}</td><td>{h[3]}</td><td class='num'>{borc}</td><td class='num'>{alacak}</td><td class='num'>{bakiye}</td></tr>"
        html = f"""
        <html><head><meta charset='utf-8'>
        <style>
        body{{font-family:Arial, Helvetica, sans-serif;}}
        table{{border-collapse:collapse;width:100%;}}
        th,td{{border:1px solid #ccc;padding:4px;text-align:left;}}
        th{{background:#eee;}}
        td.num{{text-align:right;}}
        </style></head>
        <body>
        <h2>{firma}</h2>
        <p>Yetkili: {yetkili}<br>Telefon: {tel}<br>Email: {email}</p>
        <table>
        <tr><th>Tarih</th><th>Açıklama</th><th>Borç</th><th>Alacak</th><th>Bakiye</th></tr>
        {rows}
        </table>
        </body></html>
        """
        return html

    def _ekstre_pdf_indir(self, html, musteri, parent_win=None):
        pdf_path = os.path.join(tempfile.gettempdir(), f"musteri_{musteri[0]}_ekstre.pdf")
        try:
            import pdfkit
            pdfkit.from_string(html, pdf_path)
        except Exception:
            try:
                from weasyprint import HTML
                HTML(string=html).write_pdf(pdf_path)
            except Exception:
                try:
                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib import colors
                    from reportlab.lib.styles import getSampleStyleSheet

                    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
                    styles = getSampleStyleSheet()
                    elems = [Paragraph(musteri[1], styles['Title']),
                             Paragraph(f"Telefon: {musteri[3]}", styles['Normal']),
                             Spacer(1,12)]
                    data = [["Tarih","Açıklama","Borç","Alacak","Bakiye"]]
                    for h in self.db.cari_hareketlerini_getir(musteri[0]):
                        data.append([h[2], h[3],
                                     f"{h[4]:.2f}" if h[4] else '',
                                     f"{h[5]:.2f}" if h[5] else '',
                                     f"{h[6]:.2f}"])
                    table = Table(data, colWidths=[60,170,50,50,50])
                    table.setStyle(TableStyle([
                        ('GRID',(0,0),(-1,-1),0.5,colors.black),
                        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
                    ]))
                    elems.append(table)
                    doc.build(elems)
                except Exception:
                    messagebox.showerror("Hata", "PDF oluşturmak için pdfkit, weasyprint veya reportlab kütüphanelerinden biri gereklidir.", parent=parent_win)
                    return
        messagebox.showinfo("PDF Kaydedildi", pdf_path, parent=parent_win)
        webbrowser.open_new_tab('file://' + pdf_path)

    def formu_temizle(self, clear_selection=True):
        self.firma_adi_entry.delete(0, "end"); self.yetkili_entry.delete(0, "end")
        self.tel_entry.delete(0, "end"); self.email_entry.delete(0, "end")
        self.adres_entry.delete("1.0", "end")
        if clear_selection:
            self.selected_musteri_id = None
            if self.musteri_tree.selection(): self.musteri_tree.selection_remove(self.musteri_tree.selection()[0])
            for tree in [self.hesap_tree, self.is_emri_tree, self.temper_emri_tree, self.fatura_tree]:
                for i in tree.get_children(): tree.delete(i)
            self.ekstre_button.configure(state="disabled")
            
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
