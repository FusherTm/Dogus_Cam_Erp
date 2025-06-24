import sqlite3
import datetime

class Database:
    def __init__(self, db_name="erp_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.tablolari_olustur()

    def tablolari_olustur(self):
        c = self.cursor
        c.execute('''CREATE TABLE IF NOT EXISTS envanter (
                        id INTEGER PRIMARY KEY, urun_adi TEXT NOT NULL UNIQUE, urun_tipi TEXT NOT NULL,
                        stok_miktari REAL NOT NULL, birim TEXT, maliyet_fiyati REAL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS receteler (
                        id INTEGER PRIMARY KEY, mamul_id INTEGER, hammadde_id INTEGER, miktar REAL NOT NULL,
                        FOREIGN KEY (mamul_id) REFERENCES envanter (id) ON DELETE CASCADE,
                        FOREIGN KEY (hammadde_id) REFERENCES envanter (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS stok_hareketleri (
                        id INTEGER PRIMARY KEY, urun_id INTEGER, tarih TEXT, hareket_tipi TEXT,
                        miktar REAL, fatura_id INTEGER, aciklama TEXT,
                        FOREIGN KEY (urun_id) REFERENCES envanter (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS musteriler (
                        id INTEGER PRIMARY KEY, firma_adi TEXT NOT NULL UNIQUE, yetkili_ad_soyad TEXT,
                        telefon TEXT, email TEXT, adres TEXT, bakiye REAL DEFAULT 0
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS musteri_hesap_hareketleri (
                        id INTEGER PRIMARY KEY, musteri_id INTEGER, tarih TEXT, aciklama TEXT,
                        borc REAL, alacak REAL, bakiye REAL, fatura_id INTEGER,
                        FOREIGN KEY (musteri_id) REFERENCES musteriler (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS faturalar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, musteri_id INTEGER, tarih TEXT,
                        fatura_no TEXT UNIQUE, fatura_tipi TEXT, toplam_tutar REAL,
                        FOREIGN KEY (musteri_id) REFERENCES musteriler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS fatura_kalemleri (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, fatura_id INTEGER, urun_id INTEGER,
                        miktar INTEGER, birim_fiyat REAL, toplam REAL,
                        FOREIGN KEY (fatura_id) REFERENCES faturalar (id) ON DELETE CASCADE,
                        FOREIGN KEY (urun_id) REFERENCES envanter (id)
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS personel (
                        id INTEGER PRIMARY KEY, ad_soyad TEXT NOT NULL, pozisyon TEXT,
                        ise_baslama_tarihi TEXT, maas REAL, tc_kimlik TEXT, telefon TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS maas_odemeleri (
                        id INTEGER PRIMARY KEY, personel_id INTEGER, odeme_tarihi TEXT,
                        donem TEXT, tutar REAL, FOREIGN KEY (personel_id) REFERENCES personel (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kasa_banka (
                        id INTEGER PRIMARY KEY, hesap_adi TEXT UNIQUE NOT NULL,
                        hesap_tipi TEXT, bakiye REAL DEFAULT 0
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kategoriler (
                        id INTEGER PRIMARY KEY, ad TEXT UNIQUE NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS finansal_hareketler (
                        id INTEGER PRIMARY KEY, tarih TEXT NOT NULL, aciklama TEXT,
                        gelir REAL, gider REAL, kategori_id INTEGER, hesap_id INTEGER,
                        musteri_id INTEGER,
                        FOREIGN KEY (kategori_id) REFERENCES kategoriler (id) ON DELETE SET NULL,
                        FOREIGN KEY (hesap_id) REFERENCES kasa_banka (id) ON DELETE SET NULL,
                        FOREIGN KEY (musteri_id) REFERENCES musteriler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sabit_giderler (
                        id INTEGER PRIMARY KEY, gider_adi TEXT UNIQUE NOT NULL, tutar REAL NOT NULL,
                        kategori_id INTEGER, FOREIGN KEY (kategori_id) REFERENCES kategoriler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS is_emirleri (
                        id INTEGER PRIMARY KEY,
                        musteri_id INTEGER,
                        firma_musterisi TEXT,
                        urun_niteligi TEXT,
                        miktar_m2 REAL,
                        fiyat REAL,
                        durum TEXT,
                        tarih TEXT,
                        FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS temper_emirleri (
                        id INTEGER PRIMARY KEY,
                        musteri_id INTEGER,
                        firma_musterisi TEXT,
                        urun_niteligi TEXT,
                        miktar_m2 REAL,
                        fiyat REAL,
                        durum TEXT,
                        tarih TEXT,
                        FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE SET NULL
                    )''')
        self.conn.commit()

        # Ensure new columns exist when database was created with older schema
        for table, cols in {
            'is_emirleri': [('firma_musterisi', 'TEXT'), ('fiyat', 'REAL')],
            'temper_emirleri': [('firma_musterisi', 'TEXT'), ('fiyat', 'REAL')]
        }.items():
            self.cursor.execute(f"PRAGMA table_info({table})")
            existing = [row[1] for row in self.cursor.fetchall()]
            for col_name, col_type in cols:
                if col_name not in existing:
                    self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
        self.conn.commit()

    # --- ENVANTER & REÇETE ---
    def urun_ekle(self, urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati):
        try:
            self.cursor.execute("INSERT INTO envanter (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati) VALUES (?, ?, ?, ?, ?)", (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati))
            self.conn.commit(); return self.cursor.lastrowid
        except sqlite3.IntegrityError: return None

    def urunleri_getir(self, arama_terimi="", urun_tipi=None):
        query, params = "SELECT * FROM envanter", []
        conditions = []
        if arama_terimi: conditions.append("urun_adi LIKE ?"); params.append(f'%{arama_terimi}%')
        if urun_tipi: conditions.append("urun_tipi = ?"); params.append(urun_tipi)
        if conditions: query += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(query, tuple(params)); return self.cursor.fetchall()

    def urun_guncelle(self, id, urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati):
        self.cursor.execute("UPDATE envanter SET urun_adi=?, urun_tipi=?, stok_miktari=?, birim=?, maliyet_fiyati=? WHERE id=?", (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati, id)); self.conn.commit()

    def urun_getir_by_id(self, urun_id):
        self.cursor.execute("SELECT * FROM envanter WHERE id=?", (urun_id,)); return self.cursor.fetchone()

    def urun_sil(self, id): self.cursor.execute("DELETE FROM envanter WHERE id=?", (id,)); self.conn.commit()
    def recete_ekle(self, mamul_id, hammadde_id, miktar): self.cursor.execute("INSERT INTO receteler (mamul_id, hammadde_id, miktar) VALUES (?, ?, ?)", (mamul_id, hammadde_id, miktar)); self.conn.commit()
    def recete_getir(self, mamul_id): self.cursor.execute("SELECT r.id, e.urun_adi, r.miktar, e.birim FROM receteler r JOIN envanter e ON r.hammadde_id = e.id WHERE r.mamul_id = ?", (mamul_id,)); return self.cursor.fetchall()
    def recete_sil(self, recete_id): self.cursor.execute("DELETE FROM receteler WHERE id = ?", (recete_id,)); self.conn.commit()
    def mamul_maliyeti_hesapla_ve_guncelle(self, mamul_id):
        recete_kalemleri, toplam_maliyet = self.recete_getir(mamul_id), 0
        for kalem in recete_kalemleri:
            hammadde_adi, gereken_miktar = kalem[1], kalem[2]
            self.cursor.execute("SELECT maliyet_fiyati FROM envanter WHERE urun_adi = ?", (hammadde_adi,)); hammadde_maliyet_fiyati = self.cursor.fetchone()
            if hammadde_maliyet_fiyati and hammadde_maliyet_fiyati[0] is not None: toplam_maliyet += gereken_miktar * hammadde_maliyet_fiyati[0]
        self.cursor.execute("UPDATE envanter SET maliyet_fiyati = ? WHERE id = ?", (toplam_maliyet, mamul_id)); self.conn.commit()
        return toplam_maliyet

    # --- STOK HAREKETLERİ ---
    def stok_guncelle(self, urun_id, miktar, hareket_tipi):
        if hareket_tipi == 'Giriş': self.cursor.execute("UPDATE envanter SET stok_miktari = stok_miktari + ? WHERE id = ?", (miktar, urun_id))
        elif hareket_tipi == 'Çıkış': self.cursor.execute("UPDATE envanter SET stok_miktari = stok_miktari - ? WHERE id = ?", (miktar, urun_id))
        self.conn.commit()
        
    def stok_hareketi_ekle(self, urun_id, hareket_tipi, miktar, fatura_id=None, aciklama=""):
        tarih = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO stok_hareketleri (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama) VALUES (?, ?, ?, ?, ?, ?)", (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama)); self.conn.commit()

    def stok_hareketlerini_getir(self, urun_id=None):
        query = (
            "SELECT sh.id, sh.tarih, e.urun_adi, sh.hareket_tipi, sh.miktar, sh.aciklama "
            "FROM stok_hareketleri sh JOIN envanter e ON sh.urun_id = e.id"
        )
        params = []
        if urun_id is not None:
            query += " WHERE sh.urun_id = ?"
            params.append(urun_id)
        query += " ORDER BY sh.tarih DESC, sh.id DESC"
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    # --- MÜŞTERİ (CARİ) ---
    def musteri_ekle(self, firma_adi, yetkili, telefon, email, adres):
        try:
            self.cursor.execute("INSERT INTO musteriler (firma_adi, yetkili_ad_soyad, telefon, email, adres, bakiye) VALUES (?, ?, ?, ?, ?, 0)", (firma_adi, yetkili, telefon, email, adres)); self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    def musterileri_getir(self, arama_terimi=""):
        if arama_terimi: self.cursor.execute("SELECT * FROM musteriler WHERE firma_adi LIKE ?", (f'%{arama_terimi}%',))
        else: self.cursor.execute("SELECT * FROM musteriler ORDER BY firma_adi ASC")
        return self.cursor.fetchall()
        
    def musteri_guncelle(self, id, firma_adi, yetkili, telefon, email, adres):
        self.cursor.execute("UPDATE musteriler SET firma_adi=?, yetkili_ad_soyad=?, telefon=?, email=?, adres=? WHERE id=?", (firma_adi, yetkili, telefon, email, adres, id)); self.conn.commit()

    def musteri_sil(self, id): self.cursor.execute("DELETE FROM musteriler WHERE id=?", (id,)); self.conn.commit()
    def musteri_getir_by_id(self, musteri_id): self.cursor.execute("SELECT * FROM musteriler WHERE id=?", (musteri_id,)); return self.cursor.fetchone()
    def musteri_hesap_hareketi_ekle(self, musteri_id, tarih, aciklama, borc, alacak, fatura_id=None):
        self.cursor.execute("SELECT bakiye FROM musteriler WHERE id=?", (musteri_id,)); son_bakiye_tuple = self.cursor.fetchone()
        son_bakiye = son_bakiye_tuple[0] if son_bakiye_tuple else 0; yeni_bakiye = son_bakiye + borc - alacak
        self.cursor.execute('''INSERT INTO musteri_hesap_hareketleri (musteri_id, tarih, aciklama, borc, alacak, bakiye, fatura_id) VALUES (?, ?, ?, ?, ?, ?, ?)''', (musteri_id, tarih, aciklama, borc, alacak, yeni_bakiye, fatura_id))
        self.cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id)); self.conn.commit()
    def musteri_hesap_hareketlerini_getir(self, musteri_id):
        self.cursor.execute("SELECT * FROM musteri_hesap_hareketleri WHERE musteri_id = ? ORDER BY tarih ASC, id ASC", (musteri_id,)); return self.cursor.fetchall()

    # --- FATURA ---
    def fatura_ekle(self, musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar):
        try:
            self.cursor.execute("INSERT INTO faturalar (musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar) VALUES (?, ?, ?, ?, ?)", (musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar)); self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError: return None

    def fatura_kalemi_ekle(self, fatura_id, urun_id, miktar, birim_fiyat, toplam):
        self.cursor.execute("INSERT INTO fatura_kalemleri (fatura_id, urun_id, miktar, birim_fiyat, toplam) VALUES (?, ?, ?, ?, ?)", (fatura_id, urun_id, miktar, birim_fiyat, toplam)); self.conn.commit()
    
    def faturalari_getir(self, arama_terimi=""):
        query = "SELECT f.id, f.fatura_no, f.tarih, m.firma_adi, f.fatura_tipi, f.toplam_tutar FROM faturalar f LEFT JOIN musteriler m ON f.musteri_id = m.id"
        params = []
        if arama_terimi: query += " WHERE f.fatura_no LIKE ? OR m.firma_adi LIKE ?"; params.extend([f'%{arama_terimi}%', f'%{arama_terimi}%'])
        query += " ORDER BY f.tarih DESC, f.id DESC"
        self.cursor.execute(query, tuple(params)); return self.cursor.fetchall()

    def fatura_detaylarini_getir(self, fatura_id):
        query = "SELECT e.urun_adi, fk.miktar, fk.birim_fiyat, fk.toplam FROM fatura_kalemleri fk JOIN envanter e ON fk.urun_id = e.id WHERE fk.fatura_id = ?"
        self.cursor.execute(query, (fatura_id,)); return self.cursor.fetchall()

    # --- PERSONEL ---
    def personel_ekle(self, ad_soyad, pozisyon, ise_baslama, maas, tc, tel): self.cursor.execute("INSERT INTO personel (ad_soyad, pozisyon, ise_baslama_tarihi, maas, tc_kimlik, telefon) VALUES (?, ?, ?, ?, ?, ?)", (ad_soyad, pozisyon, ise_baslama, maas, tc, tel)); self.conn.commit()
    def personelleri_getir(self): self.cursor.execute("SELECT * FROM personel"); return self.cursor.fetchall()
    def personel_guncelle(self, id, ad_soyad, pozisyon, ise_baslama, maas, tc, tel): self.cursor.execute("UPDATE personel SET ad_soyad=?, pozisyon=?, ise_baslama_tarihi=?, maas=?, tc_kimlik=?, telefon=? WHERE id=?", (ad_soyad, pozisyon, ise_baslama, maas, tc, tel, id)); self.conn.commit()
    def personel_sil(self, id): self.cursor.execute("DELETE FROM personel WHERE id=?", (id,)); self.conn.commit()
    def personel_getir_by_id(self, personel_id): self.cursor.execute("SELECT * FROM personel WHERE id=?", (personel_id,)); return self.cursor.fetchone()
    def tum_maas_toplamini_getir(self): self.cursor.execute("SELECT SUM(maas) FROM personel"); result = self.cursor.fetchone()[0]; return result if result is not None else 0

    # --- KASA & BANKA & KATEGORİ ---
    def kasa_banka_ekle(self, hesap_adi, hesap_tipi, bakiye):
        try:
            self.cursor.execute("INSERT INTO kasa_banka (hesap_adi, hesap_tipi, bakiye) VALUES (?, ?, ?)", (hesap_adi, hesap_tipi, bakiye)); self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False
    def kasa_banka_getir(self): self.cursor.execute("SELECT * FROM kasa_banka"); return self.cursor.fetchall()
    def kasa_banka_getir_by_id(self, hesap_id): self.cursor.execute("SELECT * FROM kasa_banka WHERE id = ?", (hesap_id,)); return self.cursor.fetchone()
    def kategori_ekle(self, ad):
        try:
            self.cursor.execute("INSERT INTO kategoriler (ad) VALUES (?)", (ad,)); self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False
    def kategorileri_getir(self): self.cursor.execute("SELECT * FROM kategoriler"); return self.cursor.fetchall()
    def kategori_sil(self, id): self.cursor.execute("DELETE FROM kategoriler WHERE id=?", (id,)); self.conn.commit()

    # --- SABİT GİDERLER ---
    def sabit_gider_ekle(self, gider_adi, tutar, kategori_id):
        try:
            self.cursor.execute("INSERT INTO sabit_giderler (gider_adi, tutar, kategori_id) VALUES (?, ?, ?)", (gider_adi, tutar, kategori_id)); self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False
    def sabit_giderleri_getir(self):
        self.cursor.execute("SELECT sg.id, sg.gider_adi, sg.tutar, k.ad FROM sabit_giderler sg LEFT JOIN kategoriler k ON sg.kategori_id = k.id"); return self.cursor.fetchall()
    def sabit_gider_sil(self, id): self.cursor.execute("DELETE FROM sabit_giderler WHERE id=?", (id,)); self.conn.commit()
    def sabit_gider_ekle_veya_guncelle(self, gider_adi, tutar, kategori_adi="Personel Giderleri"):
        self.cursor.execute("SELECT id FROM kategoriler WHERE ad = ?", (kategori_adi,)); kategori = self.cursor.fetchone()
        if not kategori: self.kategori_ekle(kategori_adi); self.cursor.execute("SELECT id FROM kategoriler WHERE ad = ?", (kategori_adi,)); kategori_id = self.cursor.fetchone()[0]
        else: kategori_id = kategori[0]
        self.cursor.execute("SELECT id FROM sabit_giderler WHERE gider_adi = ?", (gider_adi,)); gider = self.cursor.fetchone()
        if gider: self.cursor.execute("UPDATE sabit_giderler SET tutar = ?, kategori_id = ? WHERE gider_adi = ?", (tutar, kategori_id, gider_adi))
        else: self.cursor.execute("INSERT INTO sabit_giderler (gider_adi, tutar, kategori_id) VALUES (?, ?, ?)", (gider_adi, tutar, kategori_id))
        self.conn.commit()

    # --- FİNANSAL HAREKETLER ---
    def finansal_hareket_ekle(self, tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id=None):
        self.cursor.execute('''INSERT INTO finansal_hareketler (tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id) VALUES (?, ?, ?, ?, ?, ?, ?)''', (tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id)); self.conn.commit()
        if gelir > 0: self.cursor.execute("UPDATE kasa_banka SET bakiye = bakiye + ? WHERE id = ?", (gelir, hesap_id))
        elif gider > 0: self.cursor.execute("UPDATE kasa_banka SET bakiye = bakiye - ? WHERE id = ?", (gider, hesap_id))
        self.conn.commit()
        if gelir > 0 and musteri_id is not None: self.musteri_hesap_hareketi_ekle(musteri_id=musteri_id, tarih=tarih, aciklama=f"Tahsilat: {aciklama}", borc=0, alacak=gelir)
        
    def finansal_hareketleri_getir(self):
        self.cursor.execute("SELECT f.id, f.tarih, f.aciklama, f.gelir, f.gider, k.ad, kb.hesap_adi, m.firma_adi FROM finansal_hareketler f LEFT JOIN kategoriler k ON f.kategori_id = k.id LEFT JOIN kasa_banka kb ON f.hesap_id = kb.id LEFT JOIN musteriler m ON f.musteri_id = m.id ORDER BY f.tarih DESC, f.id DESC"); return self.cursor.fetchall()
        
    def hesap_hareketlerini_getir(self, hesap_id):
        self.cursor.execute("SELECT tarih, aciklama, gelir, gider FROM finansal_hareketler WHERE hesap_id = ? ORDER BY tarih DESC, id DESC", (hesap_id,)); return self.cursor.fetchall()
        
    # --- İŞ EMİRLERİ ---
    def is_emri_ekle(self, musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, tarih=None, durum="Bekliyor"):
        if tarih is None:
            tarih = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            "INSERT INTO is_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih)
        )
        self.conn.commit()
    def is_emirlerini_getir(self, arama_terimi=""):
        query = (
            "SELECT i.id, i.tarih, m.firma_adi, i.urun_niteligi, i.miktar_m2, i.durum "
            "FROM is_emirleri i LEFT JOIN musteriler m ON i.musteri_id = m.id"
        )
        params = ()
        if arama_terimi:
            query += " WHERE m.firma_adi LIKE ? OR i.urun_niteligi LIKE ?"
            params = (f"%{arama_terimi}%", f"%{arama_terimi}%")
        query += " ORDER BY i.tarih DESC, i.id DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    def is_emri_durum_guncelle(self, is_emri_id, yeni_durum): self.cursor.execute("UPDATE is_emirleri SET durum = ? WHERE id = ?", (yeni_durum, is_emri_id)); self.conn.commit()
    def is_emirlerini_getir_by_musteri_id(self, musteri_id): self.cursor.execute("SELECT id, tarih, urun_niteligi, miktar_m2, durum FROM is_emirleri WHERE musteri_id = ? ORDER BY tarih DESC, id DESC", (musteri_id,)); return self.cursor.fetchall()

    # --- TEMPER SİPARİŞ FONKSİYONLARI ---
    def temper_emri_ekle(self, musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, tarih=None, durum="Bekliyor"):
        if tarih is None:
            tarih = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            "INSERT INTO temper_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih)
        )
        self.conn.commit()
    def temper_emirlerini_getir(self, arama_terimi=""):
        query = (
            "SELECT t.id, t.tarih, m.firma_adi, t.urun_niteligi, t.miktar_m2, t.durum "
            "FROM temper_emirleri t LEFT JOIN musteriler m ON t.musteri_id = m.id"
        )
        params = ()
        if arama_terimi:
            query += " WHERE m.firma_adi LIKE ? OR t.urun_niteligi LIKE ?"
            params = (f"%{arama_terimi}%", f"%{arama_terimi}%")
        query += " ORDER BY t.tarih DESC, t.id DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    def temper_emri_durum_guncelle(self, temper_emri_id, yeni_durum): self.cursor.execute("UPDATE temper_emirleri SET durum = ? WHERE id = ?", (yeni_durum, temper_emri_id)); self.conn.commit()
    def temper_emirlerini_getir_by_musteri_id(self, musteri_id): self.cursor.execute("SELECT id, tarih, urun_niteligi, miktar_m2, durum FROM temper_emirleri WHERE musteri_id = ? ORDER BY tarih DESC, id DESC", (musteri_id,)); return self.cursor.fetchall()
    
    # --- RAPORLAMA ---
    def rapor_verilerini_getir(self, yil, ay):
        baslangic_tarih = f"{yil}-{ay:02d}-01"
        try: son_gun = (datetime.date(yil, ay + 1, 1) - datetime.timedelta(days=1)).day if ay < 12 else 31
        except ValueError: son_gun = 28
        bitis_tarih = f"{yil}-{ay:02d}-{son_gun}"
        self.cursor.execute("SELECT SUM(gelir), SUM(gider) FROM finansal_hareketler WHERE tarih BETWEEN ? AND ?", (baslangic_tarih, bitis_tarih)); aylik_gelir, aylik_gider = self.cursor.fetchone()
        self.cursor.execute("SELECT SUM(tutar) FROM sabit_giderler"); sabit_giderler_toplami = self.cursor.fetchone()[0]
        return {"aylik_gelir": aylik_gelir or 0, "aylik_degisken_gider": aylik_gider or 0, "toplam_sabit_gider": sabit_giderler_toplami or 0}

    def __del__(self):
        self.conn.close()
