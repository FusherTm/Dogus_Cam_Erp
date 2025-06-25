import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database

class KasaBankaFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = Database()
        self.selected_hesap_id = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.arayuzu_kur()
        self.hesaplari_goster()

    def arayuzu_kur(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Hesap Adı:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hesap_adi_entry = ctk.CTkEntry(form_frame, placeholder_text="Örn: Merkez Kasa veya Banka Adı")
        self.hesap_adi_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Hesap Tipi:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.hesap_tipi_menu = ctk.CTkOptionMenu(form_frame, values=["Kasa", "Banka"])
        self.hesap_tipi_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Açılış Bakiyesi:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.bakiye_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.bakiye_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.ekle_button = ctk.CTkButton(form_frame, text="Yeni Hesap Ekle", command=self.yeni_hesap_ekle)
        self.ekle_button.grid(row=3, column=1, pady=10, sticky="ew")

        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=("No", "Account Name", "Account Type", "Balance"),
            show="headings",
        )
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.heading("No", text="No")
        self.tree.column("No", width=50)
        self.tree.heading("Account Name", text="Account Name")
        self.tree.heading("Account Type", text="Account Type")
        self.tree.column("Account Type", width=100)
        self.tree.heading("Balance", text="Balance", anchor="e")
        self.tree.column("Balance", width=150, anchor="e")
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        # YENİ: Seçim olayını bağla
        self.tree.bind("<<TreeviewSelect>>", self.hesap_secildi)

        # YENİ: Ekstre butonu
        self.ekstre_button = ctk.CTkButton(self, text="Seçili Hesabın Hareketlerini Görüntüle", state="disabled", command=self.hesap_hareketleri_penceresi_ac)
        self.ekstre_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def hesaplari_goster(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for hesap in self.db.kasa_banka_getir():
            self.tree.insert("", "end", values=(hesap[0], hesap[1], hesap[2], f"{hesap[3]:.2f} ₺"), iid=hesap[0])
        self.ekstre_button.configure(state="disabled") # Liste yenilendiğinde butonu pasif yap
        self.selected_hesap_id = None

    def hesap_secildi(self, event):
        secili = self.tree.focus()
        if secili:
            self.selected_hesap_id = secili
            self.ekstre_button.configure(state="normal")
        else:
            self.selected_hesap_id = None
            self.ekstre_button.configure(state="disabled")

    def yeni_hesap_ekle(self):
        hesap_adi = self.hesap_adi_entry.get(); hesap_tipi = self.hesap_tipi_menu.get()
        bakiye_str = self.bakiye_entry.get() or "0"
        if not hesap_adi: return messagebox.showerror("Hata", "Hesap adı boş olamaz.")
        try: bakiye = float(bakiye_str.replace(',', '.'))
        except ValueError: return messagebox.showerror("Hata", "Lütfen geçerli bir bakiye girin.")
        
        if self.db.kasa_banka_ekle(hesap_adi, hesap_tipi, bakiye):
            messagebox.showinfo("Başarılı", f"'{hesap_adi}' hesabı başarıyla eklendi.")
            self.hesaplari_goster(); self.temizle()
            if hasattr(self.app, 'finans_frame'): self.app.finans_frame.yenile()
        else: messagebox.showerror("Hata", "Bu hesap adı zaten mevcut.")

    def temizle(self):
        self.hesap_adi_entry.delete(0, 'end'); self.bakiye_entry.delete(0, 'end'); self.bakiye_entry.insert(0, "0.00")

    def hesap_hareketleri_penceresi_ac(self):
        if not self.selected_hesap_id: return

        hesap_bilgisi = self.db.kasa_banka_getir_by_id(self.selected_hesap_id)
        if not hesap_bilgisi: return

        win = ctk.CTkToplevel(self)
        win.title(f"{hesap_bilgisi[1]} - Hesap Hareketleri")
        win.geometry("800x600")

        ctk.CTkLabel(win, text=f"Güncel Bakiye: {hesap_bilgisi[3]:.2f} ₺", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        tree_frame = ctk.CTkFrame(win); tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Tarih", "Açıklama", "Gelir", "Gider"), show="headings")
        tree.pack(side="left", expand=True, fill="both")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        for col in tree['columns']: tree.heading(col, text=col)
        tree.column("Gelir", anchor="e"); tree.column("Gider", anchor="e")

        hareketler = self.db.hesap_hareketlerini_getir(self.selected_hesap_id)
        for h in hareketler:
            gelir_str = f"{h[2]:.2f} ₺" if h[2] and h[2] > 0 else ""
            gider_str = f"{h[3]:.2f} ₺" if h[3] and h[3] > 0 else ""
            tree.insert("", "end", values=(h[0], h[1], gelir_str, gider_str))
            
        win.transient(self); win.grab_set()
