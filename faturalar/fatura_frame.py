import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import Database
import tempfile
import os
import webbrowser

class FaturaFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.musteriler, self.urunler, self.fatura_kalemleri = [], [], []
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.arayuzu_kur()
        self.verileri_yukle()
        if hasattr(self.app, 'event_bus'):
            self.app.event_bus.subscribe('envanter_guncellendi', self.verileri_yukle)

    def arayuzu_kur(self):
        main_frame = ctk.CTkFrame(self); main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=3); main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(1, weight=1)

        # Fatura Bilgileri
        fatura_bilgi_frame = ctk.CTkFrame(main_frame); fatura_bilgi_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(fatura_bilgi_frame, text="Fatura Bilgileri", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        ctk.CTkLabel(fatura_bilgi_frame, text="Müşteri (Cari):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.musteri_menu = ctk.CTkOptionMenu(fatura_bilgi_frame, values=["Müşteri Seçin"]); self.musteri_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(fatura_bilgi_frame, text="Fatura No:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.fatura_no_entry = ctk.CTkEntry(fatura_bilgi_frame); self.fatura_no_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(fatura_bilgi_frame, text="Tarih:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.tarih_entry = DateEntry(fatura_bilgi_frame, date_pattern='y-mm-dd'); self.tarih_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(fatura_bilgi_frame, text="Fatura Tipi:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.fatura_tipi_menu = ctk.CTkOptionMenu(fatura_bilgi_frame, values=["Satış", "Alış"], command=self.fatura_tipi_degisti); self.fatura_tipi_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        fatura_bilgi_frame.grid_columnconfigure(1, weight=1)

        # Ürün Ekleme
        urun_ekle_frame = ctk.CTkFrame(main_frame); urun_ekle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.urun_ekle_label = ctk.CTkLabel(urun_ekle_frame, text="Ürün Ekle (Satış)", font=ctk.CTkFont(size=14, weight="bold")); self.urun_ekle_label.grid(row=0, column=0, columnspan=2, pady=5)
        ctk.CTkLabel(urun_ekle_frame, text="Ürün:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.urun_menu = ctk.CTkOptionMenu(urun_ekle_frame, values=["Ürün Seçin"]); self.urun_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(urun_ekle_frame, text="Miktar / m²:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.miktar_entry = ctk.CTkEntry(urun_ekle_frame); self.miktar_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(urun_ekle_frame, text="Birim Fiyatı:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.birim_fiyat_entry = ctk.CTkEntry(urun_ekle_frame); self.birim_fiyat_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(urun_ekle_frame, text="Faturaya Ekle", command=self.kalem_ekle).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        urun_ekle_frame.grid_columnconfigure(1, weight=1)

        # Fatura Kalemleri Listesi
        kalemler_frame = ctk.CTkFrame(main_frame); kalemler_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        kalemler_frame.grid_rowconfigure(0, weight=1); kalemler_frame.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map("Treeview", background=[("selected", "#22559b")])
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )
        self.tree = ttk.Treeview(kalemler_frame, columns=("Ürün Adı", "Miktar / m²", "Birim Fiyatı", "Toplam"), show="headings"); self.tree.grid(row=0, column=0, sticky="nsew")
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        
        # Alt Buton ve Toplam Alanı
        alt_frame = ctk.CTkFrame(main_frame); alt_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        alt_frame.grid_columnconfigure(0, weight=1)
        self.toplam_tutar_label = ctk.CTkLabel(alt_frame, text="Toplam Tutar: 0.00 ₺", font=ctk.CTkFont(size=16, weight="bold")); self.toplam_tutar_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # YENİ: Fatura Geçmişi Butonu
        ctk.CTkButton(alt_frame, text="Fatura Geçmişi", command=self.gecmis_faturalar_penceresi).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(alt_frame, text="Seçili Ürünü Sil", command=self.kalem_sil).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(alt_frame, text="Faturayı Kaydet", command=self.faturayi_kaydet, height=35).grid(row=0, column=3, padx=5, pady=5)

    def verileri_yukle(self):
        self.musteriler = self.db.musterileri_getir(); musteri_adlari = [m[1] for m in self.musteriler] if self.musteriler else ["Müşteri Yok"]
        self.musteri_menu.configure(values=musteri_adlari); 
        if musteri_adlari: self.musteri_menu.set(musteri_adlari[0])
        self.fatura_tipi_degisti(self.fatura_tipi_menu.get())

    def fatura_tipi_degisti(self, secim):
        tip = "Mamül" if secim == "Satış" else "Hammadde"; self.urunler = self.db.urunleri_getir(urun_tipi=tip)
        self.urun_ekle_label.configure(text=f"Ürün Ekle ({secim})")
        urun_adlari = [u[1] for u in self.urunler] if self.urunler else ["Ürün Yok"]; self.urun_menu.configure(values=urun_adlari)
        if urun_adlari: self.urun_menu.set(urun_adlari[0])

    def kalem_ekle(self):
        secili_urun_adi = self.urun_menu.get(); miktar_str = self.miktar_entry.get()
        if secili_urun_adi == "Ürün Yok" or not miktar_str: return messagebox.showerror("Hata", "Lütfen bir ürün seçin ve miktar girin.")
        try: miktar = float(miktar_str); assert miktar > 0
        except(ValueError, AssertionError): return messagebox.showerror("Hata", "Miktar geçerli bir pozitif sayı olmalıdır.")
        urun = next((u for u in self.urunler if u[1] == secili_urun_adi), None)
        if not urun:
            return
        fiyat_str = self.birim_fiyat_entry.get()
        birim_fiyat = float(fiyat_str) if fiyat_str else (urun[5] if urun[5] is not None else 0)
        self.fatura_kalemleri.append({"urun_id": urun[0], "urun_adi": urun[1], "miktar": miktar, "birim_fiyat": birim_fiyat, "toplam": miktar * birim_fiyat})
        self.kalemleri_guncelle(); self.miktar_entry.delete(0, 'end'); self.birim_fiyat_entry.delete(0, 'end')

    def kalem_sil(self):
        if not self.tree.selection(): return messagebox.showerror("Hata", "Lütfen silmek için bir ürün seçin.")
        del self.fatura_kalemleri[self.tree.index(self.tree.selection()[0])]; self.kalemleri_guncelle()

    def kalemleri_guncelle(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        toplam_fatura = 0
        for item in self.fatura_kalemleri:
            self.tree.insert("", "end", values=(item["urun_adi"], f'{item["miktar"]:.2f}', f'{item["birim_fiyat"]:.2f} ₺', f'{item["toplam"]:.2f} ₺')); toplam_fatura += item["toplam"]
        self.toplam_tutar_label.configure(text=f"Toplam Tutar: {toplam_fatura:.2f} ₺")

    def faturayi_kaydet(self):
        if self.musteri_menu.get() == "Müşteri Yok" or not self.fatura_no_entry.get() or not self.fatura_kalemleri: return messagebox.showerror("Hata", "Müşteri, Fatura No ve en az bir ürün girilmelidir.")
        musteri = next((m for m in self.musteriler if m[1] == self.musteri_menu.get()), None)
        if not musteri: return
        
        toplam_tutar = sum(item['toplam'] for item in self.fatura_kalemleri); fatura_tipi = self.fatura_tipi_menu.get()
        fatura_no = self.fatura_no_entry.get(); tarih = self.tarih_entry.get_date().strftime('%Y-%m-%d')
        fatura_id = self.db.fatura_ekle(musteri[0], tarih, fatura_no, fatura_tipi, toplam_tutar)
        if fatura_id is None: return messagebox.showerror("Hata", f"'{fatura_no}' numaralı fatura zaten mevcut.")

        for item in self.fatura_kalemleri:
            self.db.fatura_kalemi_ekle(
                fatura_id, item['urun_id'], item['miktar'], item['birim_fiyat'], item['toplam']
            )
        
        messagebox.showinfo("Başarılı", "Fatura başarıyla kaydedildi.")
        html = self._fatura_html_olustur(fatura_id)
        fd, html_path = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html)
        webbrowser.open_new_tab('file://' + html_path)
        win = ctk.CTkToplevel(self)
        win.title("Fatura")
        win.geometry('350x120')
        ctk.CTkLabel(win, text="Fatura tarayıcıda açıldı. Yazdırmak için tarayıcıdan Ctrl+P kullanın.", wraplength=320).pack(padx=10, pady=10)
        ctk.CTkButton(win, text="PDF İndir", command=lambda: self._fatura_pdf_indir(html, fatura_id, win)).pack(pady=5)
        win.grab_set()
        self.fatura_kalemleri.clear(); self.kalemleri_guncelle(); self.fatura_no_entry.delete(0, 'end')

    # YENİ: Fatura Geçmişi Penceresi
    def gecmis_faturalar_penceresi(self):
        win = ctk.CTkToplevel(self)
        win.title("Fatura Geçmişi")
        win.geometry("900x600")
        
        # Arama ve Liste
        arama_frame = ctk.CTkFrame(win); arama_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(arama_frame, text="Ara (Fatura No veya Firma Adı):").pack(side="left", padx=5)
        arama_entry = ctk.CTkEntry(arama_frame, width=250); arama_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        tree_frame = ctk.CTkFrame(win); tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("ID", "Fatura No", "Tarih", "Firma", "Tip", "Tutar"), show="headings")
        tree.pack(side="left", expand=True, fill="both")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("ID", text="ID"); tree.column("ID", width=40)
        tree.heading("Fatura No", text="Fatura No"); tree.heading("Tarih", text="Tarih"); tree.heading("Firma", text="Firma Adı")
        tree.heading("Tip", text="Tipi"); tree.column("Tip", width=60)
        tree.heading("Tutar", text="Tutar", anchor="e"); tree.column("Tutar", anchor="e")

        def listeyi_doldur(arama=""):
            for i in tree.get_children(): tree.delete(i)
            for fatura in self.db.faturalari_getir(arama_terimi=arama):
                tree.insert("", "end", values=(fatura[0], fatura[1], fatura[2], fatura[3], fatura[4], f"{fatura[5]:.2f} ₺"), iid=fatura[0])
        
        def arama_yap(event): listeyi_doldur(arama_entry.get())
        arama_entry.bind("<KeyRelease>", arama_yap)

        def detay_goster(event):
            secili_id = tree.focus()
            if not secili_id: return
            fatura_no = tree.item(secili_id)['values'][1]
            detaylar = self.db.fatura_detaylarini_getir(secili_id)
            
            detay_win = ctk.CTkToplevel(win); detay_win.title(f"Fatura Detayı: {fatura_no}"); detay_win.geometry("600x400")
            detay_tree = ttk.Treeview(detay_win, columns=("Ürün", "Miktar / m²", "Birim Fiyatı", "Toplam"), show="headings"); detay_tree.pack(expand=True, fill="both", padx=10, pady=10)
            for col in detay_tree['columns']: detay_tree.heading(col, text=col)
            detay_tree.column("Birim Fiyatı", anchor="e"); detay_tree.column("Toplam", anchor="e")
            for detay in detaylar: detay_tree.insert("", "end", values=(detay[0], f"{detay[1]:.2f}", f"{detay[2]:.2f} ₺", f"{detay[3]:.2f} ₺"))
            detay_win.transient(win); detay_win.grab_set()

        tree.bind("<Double-1>", detay_goster)
        listeyi_doldur()
        win.transient(self); win.grab_set()

    def _fatura_html_olustur(self, fatura_id):
        self.db.cursor.execute(
            """SELECT f.fatura_no, f.tarih, f.fatura_tipi, m.firma_adi, m.yetkili_ad_soyad, m.telefon, m.email, m.adres
               FROM faturalar f LEFT JOIN musteriler m ON f.musteri_id = m.id WHERE f.id = ?""",
            (fatura_id,),
        )
        fatura = self.db.cursor.fetchone()
        detaylar = self.db.fatura_detaylarini_getir(fatura_id)
        rows = ""
        for d in detaylar:
            rows += f"<tr><td>{d[0]}</td><td class='num'>{d[1]:.2f}</td><td class='num'>{d[2]:.2f}</td><td class='num'>{d[3]:.2f}</td></tr>"
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
        <h2>{fatura[3]}</h2>
        <p>{fatura[4]}<br>Telefon: {fatura[5] or ''}<br>Email: {fatura[6] or ''}</p>
        <p>Fatura No: {fatura[0]}<br>Tarih: {fatura[1]}<br>Tip: {fatura[2]}</p>
        <table>
        <tr><th>Ürün</th><th>Miktar</th><th>Birim Fiyatı</th><th>Toplam</th></tr>
        {rows}
        </table>
        <p style='text-align:right;'>Toplam: {sum(d[3] for d in detaylar):.2f} ₺</p>
        </body></html>
        """
        return html

    def _fatura_pdf_indir(self, html, fatura_id, parent_win=None):
        pdf_path = os.path.join(tempfile.gettempdir(), f"fatura_{fatura_id}.pdf")
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
                    self.db.cursor.execute(
                        "SELECT urun_adi, miktar, birim_fiyat, toplam FROM fatura_kalemleri JOIN envanter ON fatura_kalemleri.urun_id = envanter.id WHERE fatura_id = ?",
                        (fatura_id,),
                    )
                    detaylar = self.db.cursor.fetchall()
                    elems = [Paragraph(f"Fatura {fatura_id}", styles['Title']), Spacer(1, 12)]
                    data = [["Ürün", "Miktar", "Birim Fiyatı", "Toplam"]]
                    for d in detaylar:
                        data.append([d[0], f"{d[1]:.2f}", f"{d[2]:.2f}", f"{d[3]:.2f}"])
                    table = Table(data, colWidths=[150, 60, 60, 60])
                    table.setStyle(TableStyle([
                        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
                    ]))
                    elems.append(table)
                    doc.build(elems)
                except Exception:
                    messagebox.showerror("Hata", "PDF oluşturmak için pdfkit, weasyprint veya reportlab kütüphanelerinden biri gereklidir.", parent=parent_win)
                    return
        messagebox.showinfo("PDF Kaydedildi", pdf_path, parent=parent_win)
        webbrowser.open_new_tab('file://' + pdf_path)
