from .musteri_frame import MusteriFrame

class TedarikciFrame(MusteriFrame):
    """Müşteri yönetim ekranının tedarikçi için uyarlanmış hali."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.musterileri_goster()

    # Override CRUD operations to use tedarikçi fonksiyonları
    def musteri_ekle(self):
        firma_adi = self.firma_adi_entry.get()
        if not firma_adi:
            from tkinter import messagebox
            return messagebox.showerror("Hata", "Firma Adı alanı zorunludur.")
        if self.db.tedarikci_ekle(
            firma_adi,
            self.yetkili_entry.get(),
            self.tel_entry.get(),
            self.email_entry.get(),
            self.adres_entry.get("1.0", "end-1c"),
        ):
            from tkinter import messagebox
            messagebox.showinfo("Başarılı", "Tedarikçi (Cari) eklendi.")
            self.yenile_ve_entegre_et()
        else:
            from tkinter import messagebox
            messagebox.showerror("Hata", "Bu firma adı zaten mevcut.")

    def musterileri_goster(self, arama_terimi=""):
        for i in self.musteri_tree.get_children():
            self.musteri_tree.delete(i)
        for tedarikci in self.db.tedarikcileri_getir(arama_terimi):
            bakiye_str = f"{tedarikci[6]:.2f} ₺"
            self.musteri_tree.insert(
                "",
                "end",
                values=(tedarikci[0], tedarikci[1], tedarikci[2], bakiye_str),
                iid=tedarikci[0],
            )

    def musteri_guncelle(self):
        if not self.selected_musteri_id:
            from tkinter import messagebox
            return messagebox.showerror("Hata", "Güncellemek için bir tedarikçi seçin.")
        firma_adi = self.firma_adi_entry.get()
        if not firma_adi:
            from tkinter import messagebox
            return messagebox.showerror("Hata", "Firma Adı alanı zorunludur.")
        self.db.tedarikci_guncelle(
            self.selected_musteri_id,
            firma_adi,
            self.yetkili_entry.get(),
            self.tel_entry.get(),
            self.email_entry.get(),
            self.adres_entry.get("1.0", "end-1c"),
        )
        from tkinter import messagebox
        messagebox.showinfo("Başarılı", "Tedarikçi bilgileri güncellendi.")
        self.yenile_ve_entegre_et()

    def musteri_sil(self):
        if not self.selected_musteri_id:
            from tkinter import messagebox
            return messagebox.showerror("Hata", "Silmek için bir tedarikçi seçin.")
        from tkinter import messagebox
        if messagebox.askyesno("Onay", "Seçili tedarikçiyi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz."):
            self.db.tedarikci_sil(self.selected_musteri_id)
            messagebox.showinfo("Başarılı", "Tedarikçi silindi.")
            self.yenile_ve_entegre_et()
