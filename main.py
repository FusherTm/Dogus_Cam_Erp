import customtkinter as ctk
import sys

# Modülleri içeri aktar
from muhasebe.finans_frame import FinansFrame
from muhasebe.kasa_banka_frame import KasaBankaFrame
from muhasebe.musteri_frame import MusteriFrame
from muhasebe.rapor_frame import RaporFrame
from muhasebe.sabit_gider_frame import SabitGiderFrame
from faturalar.fatura_frame import FaturaFrame
from envanter.envanter_frame import EnvanterFrame
from personel.personel_frame import PersonelFrame
from uretim.uretim_frame import UretimFrame
from temper.temper_frame import TemperFrame

# Gerekli kütüphanelerin kontrolü
try:
    from tkcalendar import DateEntry
except ImportError:
    root = ctk.CTk()
    root.withdraw() 
    from tkinter import messagebox
    messagebox.showerror("Eksik Kütüphane", "Programın çalışması için 'tkcalendar' kütüphanesi gereklidir.\n\nLütfen terminali/komut istemini açıp şu komutu çalıştırın:\n\npip install tkcalendar")
    sys.exit()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Doğuş ERP Sistemi")
        self.geometry("1440x820")
        
        # Ana Pencere Grid Yapılandırması (Başlık için üstte küçük bir alan, altta ana alan)
        self.grid_rowconfigure(0, weight=0) # Başlık satırı
        self.grid_rowconfigure(1, weight=1) # Tablo satırı
        self.grid_columnconfigure(0, weight=1)

        # YENİ: Başlık Alanı
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        title_label = ctk.CTkLabel(title_frame, text="Doğuş Cam", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3A7EBF")
        title_label.pack(anchor="center", pady=5)

        # Sekme Alanı
        self.tab_view = ctk.CTkTabview(self, corner_radius=8)
        self.tab_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # GÜNCELLENDİ: Sekme sırası isteğinize göre düzenlendi
        self.tab_view.add("Muhasebe")
        self.tab_view.add("İş Emirleri") 
        self.tab_view.add("Temper Siparişleri")
        self.tab_view.add("Envanter")
        self.tab_view.add("Personel")
        self.tab_view.add("Faturalar")
       
        # --- Modülleri (Frame'leri) Başlat ---
        # Her modüle ana uygulama referansı (self) verilir.

        # Muhasebe Sekmesi
        self.muhasebe_tab_view = ctk.CTkTabview(self.tab_view.tab("Muhasebe"), corner_radius=6)
        self.muhasebe_tab_view.pack(expand=True, fill="both", padx=5, pady=5)
        self.muhasebe_tab_view.add("Gelir/Gider"); self.muhasebe_tab_view.add("Kasa ve Banka"); self.muhasebe_tab_view.add("Müşteri Yönetimi"); self.muhasebe_tab_view.add("Sabit Giderler"); self.muhasebe_tab_view.add("Aylık Rapor")
        self.finans_frame = FinansFrame(self.muhasebe_tab_view.tab("Gelir/Gider"), self); self.finans_frame.pack(expand=True, fill="both")
        self.kasa_banka_frame = KasaBankaFrame(self.muhasebe_tab_view.tab("Kasa ve Banka"), self); self.kasa_banka_frame.pack(expand=True, fill="both")
        self.musteri_frame = MusteriFrame(self.muhasebe_tab_view.tab("Müşteri Yönetimi"), self); self.musteri_frame.pack(expand=True, fill="both")
        self.sabit_gider_frame = SabitGiderFrame(self.muhasebe_tab_view.tab("Sabit Giderler"), self); self.sabit_gider_frame.pack(expand=True, fill="both")
        self.rapor_frame = RaporFrame(self.muhasebe_tab_view.tab("Aylık Rapor"), self); self.rapor_frame.pack(expand=True, fill="both")

        # İş Emirleri Sekmesi
        self.uretim_frame = UretimFrame(self.tab_view.tab("İş Emirleri"), self)
        self.uretim_frame.pack(expand=True, fill="both")

        # Temper Siparişleri Sekmesi
        self.temper_frame = TemperFrame(self.tab_view.tab("Temper Siparişleri"), self)
        self.temper_frame.pack(expand=True, fill="both")
        
        # Envanter Sekmesi
        self.envanter_frame = EnvanterFrame(self.tab_view.tab("Envanter"), self)
        self.envanter_frame.pack(expand=True, fill="both")

        # Personel Sekmesi
        self.personel_frame = PersonelFrame(self.tab_view.tab("Personel"), self)
        self.personel_frame.pack(expand=True, fill="both")

        # Faturalar Sekmesi
        self.fatura_frame = FaturaFrame(self.tab_view.tab("Faturalar"), self)
        self.fatura_frame.pack(expand=True, fill="both")
        
        # İlk açılışta sekmeyi belirle
        self.tab_view.set("Muhasebe")


if __name__ == "__main__":
    app = App()
    app.mainloop()
