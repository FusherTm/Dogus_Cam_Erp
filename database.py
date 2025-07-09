import psycopg2
import datetime


def get_db_connection():
    """PostgreSQL veritabanına yeni bir bağlantı oluşturur ve döner."""
    try:
        conn = psycopg2.connect(
            dbname="dogus_erp_db",
            user="dogus_erp_user",
            password="Dogus1234",
            host="localhost",
            port="5432",
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

class Database:
    def __init__(self, db_name="erp_database.db"):
        """Veritabanı bağlantısını başlatır ve tabloları oluşturur."""
        self.conn = get_db_connection()

        if self.conn is None:
            # Eğer bağlantı kurulamadıysa, bir hata fırlat ve programın devam etmesini engelle.
            raise ConnectionError(
                "Veritabanı bağlantısı kurulamadı. Lütfen sunucu ve ağ ayarlarını kontrol edin."
            )

        self.cursor = self.conn.cursor()
        self.tablolari_olustur()

    def tablolari_olustur(self):
        c = self.cursor
        c.execute('''CREATE TABLE IF NOT EXISTS envanter (
                        id SERIAL PRIMARY KEY, urun_adi TEXT NOT NULL UNIQUE, urun_tipi TEXT NOT NULL,
                        stok_miktari REAL NOT NULL, birim TEXT, maliyet_fiyati REAL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS stok_hareketleri (
                        id SERIAL PRIMARY KEY, urun_id INTEGER, tarih TEXT, hareket_tipi TEXT,
                        miktar REAL, fatura_id INTEGER, aciklama TEXT,
                        FOREIGN KEY (urun_id) REFERENCES envanter (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Cariler (
                        id SERIAL PRIMARY KEY,
                        firma_adi TEXT NOT NULL UNIQUE,
                        yetkili TEXT,
                        telefon TEXT,
                        email TEXT,
                        adres TEXT,
                        bakiye NUMERIC DEFAULT 0,
                        cari_tipi TEXT NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS musteri_hesap_hareketleri (
                        id SERIAL PRIMARY KEY, musteri_id INTEGER, tarih TEXT, aciklama TEXT,
                        borc REAL, alacak REAL, bakiye REAL, fatura_id INTEGER,
                        FOREIGN KEY (musteri_id) REFERENCES Cariler (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS faturalar (
                        id SERIAL PRIMARY KEY, musteri_id INTEGER, tarih TEXT,
                        fatura_no TEXT UNIQUE, fatura_tipi TEXT, toplam_tutar REAL,
                        FOREIGN KEY (musteri_id) REFERENCES Cariler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS fatura_kalemleri (
                        id SERIAL PRIMARY KEY, fatura_id INTEGER, urun_id INTEGER,
                        miktar REAL, birim_fiyat REAL, toplam REAL,
                        FOREIGN KEY (fatura_id) REFERENCES faturalar (id) ON DELETE CASCADE,
                        FOREIGN KEY (urun_id) REFERENCES envanter (id)
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS personel (
                        id SERIAL PRIMARY KEY, ad_soyad TEXT NOT NULL, pozisyon TEXT,
                        ise_baslama_tarihi TEXT, maas REAL, tc_kimlik TEXT, telefon TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS maas_odemeleri (
                        id SERIAL PRIMARY KEY, personel_id INTEGER, odeme_tarihi TEXT,
                        donem TEXT, tutar REAL, FOREIGN KEY (personel_id) REFERENCES personel (id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Izinler (
                        izin_id SERIAL PRIMARY KEY,
                        personel_id INTEGER,
                        izin_tipi TEXT,
                        baslangic_tarihi TEXT,
                        bitis_tarihi TEXT,
                        gun_sayisi INTEGER,
                        aciklama TEXT,
                        durum TEXT DEFAULT 'Beklemede',
                        talep_tarihi TEXT,
                        FOREIGN KEY (personel_id) REFERENCES personel(id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kasa_banka (
                        id SERIAL PRIMARY KEY, hesap_adi TEXT UNIQUE NOT NULL,
                        hesap_tipi TEXT, bakiye REAL DEFAULT 0
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kategoriler (
                        id SERIAL PRIMARY KEY, ad TEXT UNIQUE NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS finansal_hareketler (
                        id SERIAL PRIMARY KEY, tarih TEXT NOT NULL, aciklama TEXT,
                        gelir REAL, gider REAL, kategori_id INTEGER, hesap_id INTEGER,
                        musteri_id INTEGER, odeme_yontemi TEXT DEFAULT 'Nakit',
                        FOREIGN KEY (kategori_id) REFERENCES kategoriler (id) ON DELETE SET NULL,
                        FOREIGN KEY (hesap_id) REFERENCES kasa_banka (id) ON DELETE SET NULL,
                        FOREIGN KEY (musteri_id) REFERENCES Cariler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sabit_giderler (
                        id SERIAL PRIMARY KEY, gider_adi TEXT UNIQUE NOT NULL, tutar REAL NOT NULL,
                        kategori_id INTEGER, FOREIGN KEY (kategori_id) REFERENCES kategoriler (id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS is_emirleri (
                        id SERIAL PRIMARY KEY,
                        musteri_id INTEGER,
                        firma_musterisi TEXT,
                        urun_niteligi TEXT,
                        miktar_m2 REAL,
                        fiyat REAL,
                        durum TEXT,
                        tarih TEXT,
                        liste_dosyasi TEXT,
                        FOREIGN KEY (musteri_id) REFERENCES Cariler(id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS temper_emirleri (
                        id SERIAL PRIMARY KEY,
                        musteri_id INTEGER,
                        firma_musterisi TEXT,
                        urun_niteligi TEXT,
                        miktar_m2 REAL,
                        fiyat REAL,
                        durum TEXT,
                        tarih TEXT,
                        FOREIGN KEY (musteri_id) REFERENCES Cariler(id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS cam_listeleri (
                        id SERIAL PRIMARY KEY,
                        is_emri_id INTEGER,
                        en REAL,
                        boy REAL,
                        m2 REAL,
                        poz TEXT,
                        FOREIGN KEY (is_emri_id) REFERENCES is_emirleri(id) ON DELETE CASCADE
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS cekler (
                        id SERIAL PRIMARY KEY,
                        cek_no TEXT,
                        banka_adi TEXT,
                        sube TEXT,
                        tutar REAL,
                        vade_tarihi TEXT,
                        kesideci TEXT,
                        durum TEXT,
                        aciklama TEXT,
                        dosya_path TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS tapular (
                        id SERIAL PRIMARY KEY,
                        il TEXT,
                        ilce TEXT,
                        mahalle TEXT,
                        ada_parsel TEXT,
                        yuzolcumu REAL,
                        cinsi TEXT,
                        imar_durumu TEXT,
                        tahmini_deger REAL,
                        aciklama TEXT,
                        dosya_path TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS araclar (
                        id SERIAL PRIMARY KEY,
                        plaka TEXT,
                        marka_model TEXT,
                        tip TEXT,
                        yil INTEGER,
                        ruhsat_sahibi TEXT,
                        tahmini_deger REAL,
                        durum TEXT,
                        aciklama TEXT,
                        dosya_path TEXT
                    )''')
        self.conn.commit()

        # Ensure new columns exist when database was created with older schema
        for table, cols in {
            'is_emirleri': [('firma_musterisi', 'TEXT'), ('fiyat', 'REAL'), ('liste_dosyasi', 'TEXT')],
            'temper_emirleri': [('firma_musterisi', 'TEXT'), ('fiyat', 'REAL')],
            'finansal_hareketler': [('odeme_yontemi', "TEXT DEFAULT 'Nakit'")]
        }.items():
            self.cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
                (table,),
            )
            existing = [row[0] for row in self.cursor.fetchall()]
            for col_name, col_type in cols:
                if col_name not in existing:
                    self.cursor.execute(
                        f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    )
        self.conn.commit()

    # --- ENVANTER & REÇETE ---
    def urun_ekle(self, urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati):
        try:
            self.cursor.execute(
                "INSERT INTO envanter (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati),
            )
            new_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except psycopg2.IntegrityError: return None

    def urunleri_getir(self, arama_terimi="", urun_tipi=None):
        query, params = "SELECT * FROM envanter", []
        conditions = []
        if arama_terimi: conditions.append("urun_adi LIKE %s"); params.append(f'%{arama_terimi}%')
        if urun_tipi: conditions.append("urun_tipi = %s"); params.append(urun_tipi)
        if conditions: query += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(query, tuple(params)); return self.cursor.fetchall()

    def urun_guncelle(self, id, urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati):
        self.cursor.execute("UPDATE envanter SET urun_adi=%s, urun_tipi=%s, stok_miktari=%s, birim=%s, maliyet_fiyati=%s WHERE id=%s", (urun_adi, urun_tipi, stok_miktari, birim, maliyet_fiyati, id)); self.conn.commit()

    def urun_getir_by_id(self, urun_id):
        self.cursor.execute("SELECT * FROM envanter WHERE id=%s", (urun_id,)); return self.cursor.fetchone()

    def urun_sil(self, id): self.cursor.execute("DELETE FROM envanter WHERE id=%s", (id,)); self.conn.commit()

    # --- STOK HAREKETLERİ ---
    def stok_guncelle(self, urun_id, miktar, hareket_tipi):
        if hareket_tipi == 'Giriş': self.cursor.execute("UPDATE envanter SET stok_miktari = stok_miktari + %s WHERE id = %s", (miktar, urun_id))
        elif hareket_tipi == 'Çıkış': self.cursor.execute("UPDATE envanter SET stok_miktari = stok_miktari - %s WHERE id = %s", (miktar, urun_id))
        self.conn.commit()
        
    def stok_hareketi_ekle(self, urun_id, hareket_tipi, miktar, fatura_id=None, aciklama=""):
        tarih = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO stok_hareketleri (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama) VALUES (%s, %s, %s, %s, %s, %s)", (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama)); self.conn.commit()

    def stok_hareketlerini_getir(self, urun_id=None):
        query = (
            "SELECT sh.id, sh.tarih, e.urun_adi, sh.hareket_tipi, sh.miktar, sh.aciklama "
            "FROM stok_hareketleri sh JOIN envanter e ON sh.urun_id = e.id"
        )
        params = []
        if urun_id is not None:
            query += " WHERE sh.urun_id = %s"
            params.append(urun_id)
        query += " ORDER BY sh.tarih DESC, sh.id DESC"
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    # --- CARİ (MÜŞTERİ & TEDARİKÇİ) ---
    def cari_ekle(self, firma_adi, yetkili, telefon, email, adres, cari_tipi):
        try:
            self.cursor.execute(
                "INSERT INTO Cariler (firma_adi, yetkili, telefon, email, adres, bakiye, cari_tipi) VALUES (%s, %s, %s, %s, %s, 0, %s)",
                (firma_adi, yetkili, telefon, email, adres, cari_tipi),
            )
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            return False

    def musteri_ekle(self, firma_adi, yetkili, telefon, email, adres):
        return self.cari_ekle(firma_adi, yetkili, telefon, email, adres, "Müşteri")

    def tedarikci_ekle(self, firma_adi, yetkili, telefon, email, adres):
        return self.cari_ekle(firma_adi, yetkili, telefon, email, adres, "Tedarikçi")

    def carileri_getir(self, arama_terimi="", cari_tipi=None):
        query = "SELECT * FROM Cariler"
        params = []
        conditions = []
        if arama_terimi:
            conditions.append("firma_adi LIKE %s"); params.append(f'%{arama_terimi}%')
        if cari_tipi:
            conditions.append("cari_tipi = %s"); params.append(cari_tipi)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY firma_adi ASC"
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def musterileri_getir(self, arama_terimi=""):
        return self.carileri_getir(arama_terimi, "Müşteri")

    def tedarikcileri_getir(self, arama_terimi=""):
        return self.carileri_getir(arama_terimi, "Tedarikçi")

    def cari_guncelle(self, id, firma_adi, yetkili, telefon, email, adres):
        self.cursor.execute(
            "UPDATE Cariler SET firma_adi=%s, yetkili=%s, telefon=%s, email=%s, adres=%s WHERE id=%s",
            (firma_adi, yetkili, telefon, email, adres, id),
        )
        self.conn.commit()

    def musteri_guncelle(self, id, firma_adi, yetkili, telefon, email, adres):
        self.cari_guncelle(id, firma_adi, yetkili, telefon, email, adres)

    def tedarikci_guncelle(self, id, firma_adi, yetkili, telefon, email, adres):
        self.cari_guncelle(id, firma_adi, yetkili, telefon, email, adres)

    def cari_sil(self, id):
        self.cursor.execute("DELETE FROM Cariler WHERE id=%s", (id,))
        self.conn.commit()

    def musteri_sil(self, id):
        self.cari_sil(id)

    def tedarikci_sil(self, id):
        self.cari_sil(id)

    def cari_getir_by_id(self, cari_id):
        self.cursor.execute("SELECT * FROM Cariler WHERE id=%s", (cari_id,))
        return self.cursor.fetchone()

    def musteri_getir_by_id(self, musteri_id):
        return self.cari_getir_by_id(musteri_id)

    def tedarikci_getir_by_id(self, tedarikci_id):
        return self.cari_getir_by_id(tedarikci_id)

    def musteri_hesap_hareketi_ekle(self, musteri_id, tarih, aciklama, borc, alacak, fatura_id=None):
        self.cursor.execute("SELECT bakiye FROM Cariler WHERE id=%s", (musteri_id,))
        son_bakiye_tuple = self.cursor.fetchone()
        son_bakiye = son_bakiye_tuple[0] if son_bakiye_tuple else 0
        yeni_bakiye = son_bakiye + borc - alacak
        self.cursor.execute(
            '''INSERT INTO musteri_hesap_hareketleri (musteri_id, tarih, aciklama, borc, alacak, bakiye, fatura_id) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (musteri_id, tarih, aciklama, borc, alacak, yeni_bakiye, fatura_id),
        )
        self.cursor.execute("UPDATE Cariler SET bakiye = %s WHERE id = %s", (yeni_bakiye, musteri_id))
        self.conn.commit()
    def musteri_hesap_hareketlerini_getir(self, musteri_id):
        self.cursor.execute("SELECT * FROM musteri_hesap_hareketleri WHERE musteri_id = %s ORDER BY tarih ASC, id ASC", (musteri_id,)); return self.cursor.fetchall()

    # --- FATURA ---
    def fatura_ekle(self, musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar):
        try:
            self.cursor.execute(
                "INSERT INTO faturalar (musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (musteri_id, tarih, fatura_no, fatura_tipi, toplam_tutar),
            )
            new_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return new_id
        except psycopg2.IntegrityError: return None

    def fatura_kalemi_ekle(self, fatura_id, urun_id, miktar, birim_fiyat, toplam):
        self.cursor.execute("INSERT INTO fatura_kalemleri (fatura_id, urun_id, miktar, birim_fiyat, toplam) VALUES (%s, %s, %s, %s, %s)", (fatura_id, urun_id, miktar, birim_fiyat, toplam)); self.conn.commit()
    
    def faturalari_getir(self, arama_terimi=""):
        query = "SELECT f.id, f.fatura_no, f.tarih, m.firma_adi, f.fatura_tipi, f.toplam_tutar FROM faturalar f LEFT JOIN Cariler m ON f.musteri_id = m.id"
        params = []
        if arama_terimi: query += " WHERE f.fatura_no LIKE %s OR m.firma_adi LIKE %s"; params.extend([f'%{arama_terimi}%', f'%{arama_terimi}%'])
        query += " ORDER BY f.tarih DESC, f.id DESC"
        self.cursor.execute(query, tuple(params)); return self.cursor.fetchall()

    def fatura_detaylarini_getir(self, fatura_id):
        query = "SELECT e.urun_adi, fk.miktar, fk.birim_fiyat, fk.toplam FROM fatura_kalemleri fk JOIN envanter e ON fk.urun_id = e.id WHERE fk.fatura_id = %s"
        self.cursor.execute(query, (fatura_id,)); return self.cursor.fetchall()

    def faturalari_getir_by_musteri_id(self, musteri_id):
        self.cursor.execute(
            "SELECT id, tarih, fatura_no, toplam_tutar FROM faturalar WHERE musteri_id = %s ORDER BY tarih DESC, id DESC",
            (musteri_id,)
        )
        return self.cursor.fetchall()

    # --- PERSONEL ---
    def personel_ekle(self, ad_soyad, pozisyon, ise_baslama, maas, tc, tel): self.cursor.execute("INSERT INTO personel (ad_soyad, pozisyon, ise_baslama_tarihi, maas, tc_kimlik, telefon) VALUES (%s, %s, %s, %s, %s, %s)", (ad_soyad, pozisyon, ise_baslama, maas, tc, tel)); self.conn.commit()
    def personelleri_getir(self): self.cursor.execute("SELECT * FROM personel"); return self.cursor.fetchall()
    def personel_guncelle(self, id, ad_soyad, pozisyon, ise_baslama, maas, tc, tel): self.cursor.execute("UPDATE personel SET ad_soyad=%s, pozisyon=%s, ise_baslama_tarihi=%s, maas=%s, tc_kimlik=%s, telefon=%s WHERE id=%s", (ad_soyad, pozisyon, ise_baslama, maas, tc, tel, id)); self.conn.commit()
    def personel_sil(self, id): self.cursor.execute("DELETE FROM personel WHERE id=%s", (id,)); self.conn.commit()
    def personel_getir_by_id(self, personel_id): self.cursor.execute("SELECT * FROM personel WHERE id=%s", (personel_id,)); return self.cursor.fetchone()
    def tum_maas_toplamini_getir(self): self.cursor.execute("SELECT SUM(maas) FROM personel"); result = self.cursor.fetchone()[0]; return result if result is not None else 0

    # --- İZİNLER ---
    def izin_ekle(
        self,
        personel_id,
        izin_tipi,
        baslangic_tarihi,
        bitis_tarihi,
        gun_sayisi,
        aciklama,
        durum="Beklemede",
        talep_tarihi=None,
    ):
        if talep_tarihi is None:
            talep_tarihi = datetime.datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """INSERT INTO Izinler (personel_id, izin_tipi, baslangic_tarihi, bitis_tarihi, gun_sayisi, aciklama, durum, talep_tarihi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                personel_id,
                izin_tipi,
                baslangic_tarihi,
                bitis_tarihi,
                gun_sayisi,
                aciklama,
                durum,
                talep_tarihi,
            ),
        )
        self.conn.commit()

    def izinleri_getir(self):
        self.cursor.execute(
            """SELECT i.izin_id, p.ad_soyad, i.izin_tipi, i.baslangic_tarihi, i.bitis_tarihi, i.gun_sayisi, i.durum FROM Izinler i JOIN personel p ON i.personel_id = p.id ORDER BY i.izin_id DESC"""
        )
        return self.cursor.fetchall()

    def izin_durum_guncelle(self, izin_id, yeni_durum):
        self.cursor.execute(
            "UPDATE Izinler SET durum = %s WHERE izin_id = %s",
            (yeni_durum, izin_id),
        )
        self.conn.commit()

    def izin_ozetini_getir(self, personel_id, hak_edilen=14):
        self.cursor.execute(
            """
            SELECT SUM(gun_sayisi) FROM Izinler
            WHERE personel_id = %s
              AND durum = 'Onaylandı'
              AND izin_tipi = 'Yıllık İzin'
              AND EXTRACT(YEAR FROM baslangic_tarihi::date) = EXTRACT(YEAR FROM CURRENT_DATE)
            """,
            (personel_id,),
        )
        used = self.cursor.fetchone()[0]
        kullanilan = used if used is not None else 0
        kalan = hak_edilen - kullanilan
        return hak_edilen, kullanilan, kalan

    # --- KASA & BANKA & KATEGORİ ---
    def kasa_banka_ekle(self, hesap_adi, hesap_tipi, bakiye):
        try:
            self.cursor.execute("INSERT INTO kasa_banka (hesap_adi, hesap_tipi, bakiye) VALUES (%s, %s, %s)", (hesap_adi, hesap_tipi, bakiye)); self.conn.commit()
            return True
        except psycopg2.IntegrityError: return False
    def kasa_banka_getir(self): self.cursor.execute("SELECT * FROM kasa_banka"); return self.cursor.fetchall()
    def kasa_banka_getir_by_id(self, hesap_id): self.cursor.execute("SELECT * FROM kasa_banka WHERE id = %s", (hesap_id,)); return self.cursor.fetchone()
    def kategori_ekle(self, ad):
        try:
            self.cursor.execute("INSERT INTO kategoriler (ad) VALUES (%s)", (ad,)); self.conn.commit()
            return True
        except psycopg2.IntegrityError: return False
    def kategorileri_getir(self): self.cursor.execute("SELECT * FROM kategoriler"); return self.cursor.fetchall()
    def kategori_sil(self, id): self.cursor.execute("DELETE FROM kategoriler WHERE id=%s", (id,)); self.conn.commit()

    # --- SABİT GİDERLER ---
    def sabit_gider_ekle(self, gider_adi, tutar, kategori_id):
        try:
            self.cursor.execute("INSERT INTO sabit_giderler (gider_adi, tutar, kategori_id) VALUES (%s, %s, %s)", (gider_adi, tutar, kategori_id)); self.conn.commit()
            return True
        except psycopg2.IntegrityError: return False
    def sabit_giderleri_getir(self):
        self.cursor.execute("SELECT sg.id, sg.gider_adi, sg.tutar, k.ad FROM sabit_giderler sg LEFT JOIN kategoriler k ON sg.kategori_id = k.id"); return self.cursor.fetchall()
    def sabit_gider_sil(self, id): self.cursor.execute("DELETE FROM sabit_giderler WHERE id=%s", (id,)); self.conn.commit()
    def sabit_gider_ekle_veya_guncelle(self, gider_adi, tutar, kategori_adi="Personel Giderleri"):
        self.cursor.execute("SELECT id FROM kategoriler WHERE ad = %s", (kategori_adi,)); kategori = self.cursor.fetchone()
        if not kategori: self.kategori_ekle(kategori_adi); self.cursor.execute("SELECT id FROM kategoriler WHERE ad = %s", (kategori_adi,)); kategori_id = self.cursor.fetchone()[0]
        else: kategori_id = kategori[0]
        self.cursor.execute("SELECT id FROM sabit_giderler WHERE gider_adi = %s", (gider_adi,)); gider = self.cursor.fetchone()
        if gider: self.cursor.execute("UPDATE sabit_giderler SET tutar = %s, kategori_id = %s WHERE gider_adi = %s", (tutar, kategori_id, gider_adi))
        else: self.cursor.execute("INSERT INTO sabit_giderler (gider_adi, tutar, kategori_id) VALUES (%s, %s, %s)", (gider_adi, tutar, kategori_id))
        self.conn.commit()

    # --- FİNANSAL HAREKETLER ---
    def finansal_hareket_ekle(self, tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id=None, odeme_yontemi="Nakit"):
        self.cursor.execute('''INSERT INTO finansal_hareketler (tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id, odeme_yontemi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (tarih, aciklama, gelir, gider, kategori_id, hesap_id, musteri_id, odeme_yontemi)); self.conn.commit()
        if gelir > 0: self.cursor.execute("UPDATE kasa_banka SET bakiye = bakiye + %s WHERE id = %s", (gelir, hesap_id))
        elif gider > 0: self.cursor.execute("UPDATE kasa_banka SET bakiye = bakiye - %s WHERE id = %s", (gider, hesap_id))
        self.conn.commit()
        if gelir > 0 and musteri_id is not None: self.musteri_hesap_hareketi_ekle(musteri_id=musteri_id, tarih=tarih, aciklama=f"Tahsilat: {aciklama}", borc=0, alacak=gelir)
        
    def finansal_hareketleri_getir(self):
        self.cursor.execute("SELECT f.id, f.tarih, f.aciklama, f.gelir, f.gider, k.ad, kb.hesap_adi, m.firma_adi, f.odeme_yontemi FROM finansal_hareketler f LEFT JOIN kategoriler k ON f.kategori_id = k.id LEFT JOIN kasa_banka kb ON f.hesap_id = kb.id LEFT JOIN Cariler m ON f.musteri_id = m.id ORDER BY f.tarih DESC, f.id DESC"); return self.cursor.fetchall()
        
    def hesap_hareketlerini_getir(self, hesap_id):
        self.cursor.execute("SELECT tarih, aciklama, gelir, gider FROM finansal_hareketler WHERE hesap_id = %s ORDER BY tarih DESC, id DESC", (hesap_id,)); return self.cursor.fetchall()
        
    # --- İŞ EMİRLERİ ---
    def is_emri_ekle(self, musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, tarih=None, durum="Bekliyor"):
        if tarih is None:
            tarih = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            "INSERT INTO is_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih)
        )
        new_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return new_id
    def is_emirlerini_getir(self, arama_terimi=""):
        query = (
            "SELECT i.id, i.tarih, m.firma_adi, i.urun_niteligi, i.miktar_m2, i.durum "
            "FROM is_emirleri i LEFT JOIN Cariler m ON i.musteri_id = m.id"
        )
        params = ()
        if arama_terimi:
            query += " WHERE m.firma_adi LIKE %s OR i.urun_niteligi LIKE %s"
            params = (f"%{arama_terimi}%", f"%{arama_terimi}%")
        query += " ORDER BY i.tarih DESC, i.id DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    def is_emri_durum_guncelle(self, is_emri_id, yeni_durum): self.cursor.execute("UPDATE is_emirleri SET durum = %s WHERE id = %s", (yeni_durum, is_emri_id)); self.conn.commit()
    def is_emri_getir_by_id(self, is_emri_id):
        self.cursor.execute(
            "SELECT id, musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih, liste_dosyasi "
            "FROM is_emirleri WHERE id = %s",
            (is_emri_id,),
        )
        return self.cursor.fetchone()
    def is_emirlerini_getir_by_musteri_id(self, musteri_id): self.cursor.execute("SELECT id, tarih, urun_niteligi, miktar_m2, durum FROM is_emirleri WHERE musteri_id = %s ORDER BY tarih DESC, id DESC", (musteri_id,)); return self.cursor.fetchall()

    def cam_listesi_ekle(self, is_emri_id, en, boy, m2, poz):
        self.cursor.execute(
            "INSERT INTO cam_listeleri (is_emri_id, en, boy, m2, poz) VALUES (%s, %s, %s, %s, %s)",
            (is_emri_id, en, boy, m2, poz)
        )
        self.conn.commit()

    def cam_listesini_getir(self, is_emri_id):
        self.cursor.execute(
            "SELECT en, boy, m2, poz FROM cam_listeleri WHERE is_emri_id = %s",
            (is_emri_id,)
        )
        return self.cursor.fetchall()

    def cam_listesi_var_mi(self, is_emri_id):
        """Belirtilen iş emri için cam listesi olup olmadığını kontrol et"""
        self.cursor.execute(
            "SELECT 1 FROM cam_listeleri WHERE is_emri_id = %s LIMIT 1",
            (is_emri_id,),
        )
        return self.cursor.fetchone() is not None

    def is_emri_liste_dosyasi_getir(self, is_emri_id):
        self.cursor.execute(
            "SELECT liste_dosyasi FROM is_emirleri WHERE id = %s",
            (is_emri_id,),
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def is_emri_liste_dosyasi_guncelle(self, is_emri_id, path):
        self.cursor.execute(
            "UPDATE is_emirleri SET liste_dosyasi = %s WHERE id = %s",
            (path, is_emri_id),
        )
        self.conn.commit()

    # --- VARLIKLAR ---
    def cek_ekle(self, cek_no, banka_adi, sube, tutar, vade_tarihi, kesideci, durum, aciklama, dosya_path):
        self.cursor.execute(
            """INSERT INTO cekler (cek_no, banka_adi, sube, tutar, vade_tarihi, kesideci, durum, aciklama, dosya_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (cek_no, banka_adi, sube, tutar, vade_tarihi, kesideci, durum, aciklama, dosya_path),
        )
        self.conn.commit()

    def cekleri_getir(self):
        self.cursor.execute("SELECT * FROM cekler ORDER BY vade_tarihi DESC, id DESC")
        return self.cursor.fetchall()

    def tapu_ekle(self, il, ilce, mahalle, ada_parsel, yuzolcumu, cinsi, imar_durumu, tahmini_deger, aciklama, dosya_path):
        self.cursor.execute(
            """INSERT INTO tapular (il, ilce, mahalle, ada_parsel, yuzolcumu, cinsi, imar_durumu, tahmini_deger, aciklama, dosya_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (il, ilce, mahalle, ada_parsel, yuzolcumu, cinsi, imar_durumu, tahmini_deger, aciklama, dosya_path),
        )
        self.conn.commit()

    def tapulari_getir(self):
        self.cursor.execute("SELECT * FROM tapular ORDER BY id DESC")
        return self.cursor.fetchall()

    def arac_ekle(self, plaka, marka_model, tip, yil, ruhsat_sahibi, tahmini_deger, durum, aciklama, dosya_path):
        self.cursor.execute(
            """INSERT INTO araclar (plaka, marka_model, tip, yil, ruhsat_sahibi, tahmini_deger, durum, aciklama, dosya_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (plaka, marka_model, tip, yil, ruhsat_sahibi, tahmini_deger, durum, aciklama, dosya_path),
        )
        self.conn.commit()

    def araclari_getir(self):
        self.cursor.execute("SELECT * FROM araclar ORDER BY id DESC")
        return self.cursor.fetchall()

    # --- TEMPER SİPARİŞ FONKSİYONLARI ---
    def temper_emri_ekle(self, musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, tarih=None, durum="Bekliyor"):
        if tarih is None:
            tarih = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            "INSERT INTO temper_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih)
        )
        self.conn.commit()
    def temper_emirlerini_getir(self, arama_terimi=""):
        query = (
            "SELECT t.id, t.tarih, m.firma_adi, t.urun_niteligi, t.miktar_m2, t.durum "
            "FROM temper_emirleri t LEFT JOIN Cariler m ON t.musteri_id = m.id"
        )
        params = ()
        if arama_terimi:
            query += " WHERE m.firma_adi LIKE %s OR t.urun_niteligi LIKE %s"
            params = (f"%{arama_terimi}%", f"%{arama_terimi}%")
        query += " ORDER BY t.tarih DESC, t.id DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    def temper_emri_durum_guncelle(self, temper_emri_id, yeni_durum): self.cursor.execute("UPDATE temper_emirleri SET durum = %s WHERE id = %s", (yeni_durum, temper_emri_id)); self.conn.commit()
    def temper_emri_getir_by_id(self, temper_emri_id):
        self.cursor.execute("SELECT * FROM temper_emirleri WHERE id = %s", (temper_emri_id,))
        return self.cursor.fetchone()
    def temper_emirlerini_getir_by_musteri_id(self, musteri_id): self.cursor.execute("SELECT id, tarih, urun_niteligi, miktar_m2, durum FROM temper_emirleri WHERE musteri_id = %s ORDER BY tarih DESC, id DESC", (musteri_id,)); return self.cursor.fetchall()
    
    # --- RAPORLAMA ---
    def rapor_verilerini_getir(self, yil, ay):
        baslangic_tarih = f"{yil}-{ay:02d}-01"
        try: son_gun = (datetime.date(yil, ay + 1, 1) - datetime.timedelta(days=1)).day if ay < 12 else 31
        except ValueError: son_gun = 28
        bitis_tarih = f"{yil}-{ay:02d}-{son_gun}"
        self.cursor.execute("SELECT SUM(gelir), SUM(gider) FROM finansal_hareketler WHERE tarih BETWEEN %s AND %s", (baslangic_tarih, bitis_tarih)); aylik_gelir, aylik_gider = self.cursor.fetchone()
        self.cursor.execute("SELECT SUM(tutar) FROM sabit_giderler"); sabit_giderler_toplami = self.cursor.fetchone()[0]
        return {"aylik_gelir": aylik_gelir or 0, "aylik_degisken_gider": aylik_gider or 0, "toplam_sabit_gider": sabit_giderler_toplami or 0}

    def __del__(self):
        self.conn.close()
