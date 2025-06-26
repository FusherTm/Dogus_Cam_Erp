import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from database import Database

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class RaporFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.canvas = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.arayuzu_kur()

    def arayuzu_kur(self):
        # Üst Kontrol Paneli
        kontrol_frame = ctk.CTkFrame(self)
        kontrol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(kontrol_frame, text="Rapor Ayı:").pack(side="left", padx=10)
        self.ay_menu = ctk.CTkOptionMenu(self, values=["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
        self.ay_menu.pack(in_=kontrol_frame, side="left", padx=5)
        current_year = datetime.datetime.now().year
        self.yil_menu = ctk.CTkOptionMenu(self, values=[str(y) for y in range(current_year - 5, current_year + 2)])
        self.yil_menu.set(str(current_year)); self.yil_menu.pack(in_=kontrol_frame, side="left", padx=5)
        ctk.CTkButton(kontrol_frame, text="Rapor Oluştur", command=self.rapor_olustur).pack(side="left", padx=10)

        # Ana Rapor Alanı
        self.rapor_ana_frame = ctk.CTkFrame(self)
        self.rapor_ana_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.rapor_ana_frame.grid_columnconfigure(0, weight=2) # Grafik
        self.rapor_ana_frame.grid_columnconfigure(1, weight=3) # Detay
        self.rapor_ana_frame.grid_rowconfigure(0, weight=1)

    def rapor_olustur(self):
        # Önceki raporu temizle
        for widget in self.rapor_ana_frame.winfo_children(): widget.destroy()
        if self.canvas: self.canvas.get_tk_widget().destroy(); self.canvas = None
        
        # Verileri çek
        ay_map = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
        ay = ay_map[self.ay_menu.get()]
        yil = int(self.yil_menu.get())
        
        rapor_verileri = self.db.rapor_verilerini_getir(yil, ay)
        toplam_gelir = rapor_verileri["aylik_gelir"]
        toplam_gider = rapor_verileri["aylik_degisken_gider"] + rapor_verileri["toplam_sabit_gider"]
        net_kar_zarar = toplam_gelir - toplam_gider

        # Sol Taraf: Özet ve Grafik
        sol_frame = ctk.CTkFrame(self.rapor_ana_frame)
        sol_frame.grid(row=0, column=0, padx=(0,5), sticky="nsew")
        sol_frame.grid_rowconfigure(1, weight=1)
        
        ozet_frame = ctk.CTkFrame(sol_frame)
        ozet_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(ozet_frame, text=f"{self.ay_menu.get()} {yil} - Mali Özet", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,10))
        self.create_ozet_satiri(ozet_frame, "Aylık Toplam Gelir:", f"{toplam_gelir:.2f} ₺", "#2CC985")
        self.create_ozet_satiri(ozet_frame, "Aylık Değişken Gider:", f"{rapor_verileri['aylik_degisken_gider']:.2f} ₺", "#E54E55")
        self.create_ozet_satiri(ozet_frame, "Aylık Sabit Giderler:", f"{rapor_verileri['toplam_sabit_gider']:.2f} ₺", "#E54E55")
        self.create_ozet_satiri(ozet_frame, "AYLIK TOPLAM GİDER:", f"{toplam_gider:.2f} ₺", "#D92D2D", bold=True)
        net_renk = "#2CC985" if net_kar_zarar >= 0 else "#D92D2D"
        self.create_ozet_satiri(ozet_frame, "NET KAR/ZARAR:", f"{net_kar_zarar:.2f} ₺", net_renk, bold=True, size=14)
        
        if MATPLOTLIB_AVAILABLE:
            grafik_frame = ctk.CTkFrame(sol_frame)
            grafik_frame.pack(expand=True, fill="both", padx=10, pady=10)
            fig = Figure(figsize=(5, 4), dpi=100, facecolor='#2b2b2b'); ax = fig.add_subplot(111)
            ax.bar(['Toplam Gelir', 'Toplam Gider'], [toplam_gelir, toplam_gider], color=['#2CC985', '#E54E55'])
            ax.set_title('Gelir ve Gider Özeti', color='white'); ax.set_ylabel('Tutar (₺)', color='white')
            ax.tick_params(axis='x', colors='white'); ax.tick_params(axis='y', colors='white')
            ax.set_facecolor('#343638'); fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(fig, master=grafik_frame)
            self.canvas.draw(); self.canvas.get_tk_widget().pack(expand=True, fill="both")
        else:
            ctk.CTkLabel(sol_frame, text="Grafik için 'matplotlib' kurun.").pack(expand=True)

        # Sağ Taraf: Detaylı Döküm
        sag_frame = ctk.CTkFrame(self.rapor_ana_frame)
        sag_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")
        sag_frame.grid_rowconfigure(0, weight=1); sag_frame.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.configure(
            "Treeview.Heading",
            background="#1E1E2F",
            foreground="#FFFFFF",
            relief="flat",
            font=("Helvetica", 10, "bold"),
        )
        tree = ttk.Treeview(sag_frame, columns=("Tip", "Açıklama", "Tutar"), show="headings"); tree.pack(expand=True, fill="both", padx=10, pady=10)
        tree.heading("Tip", text="Tip"); tree.column("Tip", width=120)
        tree.heading("Açıklama", text="Açıklama")
        tree.heading("Tutar", text="Tutar", anchor="e"); tree.column("Tutar", anchor="e")

        # Hareketleri listele
        hareketler = self.db.finansal_hareketleri_getir()
        aylik_hareketler = [h for h in hareketler if datetime.datetime.strptime(h[1], '%Y-%m-%d').month == ay and datetime.datetime.strptime(h[1], '%Y-%m-%d').year == yil]
        for h in aylik_hareketler:
            if h[3] > 0: tree.insert("", "end", values=("Gelir", h[2], f"{h[3]:.2f} ₺"), tags=('gelir',))
            if h[4] > 0: tree.insert("", "end", values=("Değişken Gider", h[2], f"{h[4]:.2f} ₺"), tags=('gider',))
        
        # Sabit giderleri listele
        tree.insert("", "end", values=("", "--- Sabit Giderler ---", ""), tags=('baslik',))
        sabit_giderler = self.db.sabit_giderleri_getir()
        for sg in sabit_giderler: tree.insert("", "end", values=("Sabit Gider", sg[1], f"{sg[2]:.2f} ₺"), tags=('gider',))
        
        tree.tag_configure('gelir', foreground='#2CC985'); tree.tag_configure('gider', foreground='#E54E55'); tree.tag_configure('baslik', foreground='gray')


    def create_ozet_satiri(self, parent, label_text, value_text, color, bold=False, size=12):
        satir_frame = ctk.CTkFrame(parent, fg_color="transparent")
        satir_frame.pack(fill="x", padx=10, pady=2)
        font = ctk.CTkFont(size=size, weight="bold" if bold else "normal")
        ctk.CTkLabel(satir_frame, text=label_text, font=font).pack(side="left")
        ctk.CTkLabel(satir_frame, text=value_text, font=font, text_color=color).pack(side="right")
