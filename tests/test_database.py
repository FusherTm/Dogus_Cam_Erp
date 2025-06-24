import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import Database

@pytest.fixture
def db():
    db = Database(':memory:')
    # add sample customers
    db.musteri_ekle('ABC', 'Yetkili', '1', 'a@b.com', 'adres')
    db.musteri_ekle('XYZ', 'Yetkili', '2', 'x@y.com', 'adres2')
    # inventory items
    u1 = db.urun_ekle('GlassA', 'Hammadde', 100, 'Adet', 10)
    u2 = db.urun_ekle('GlassB', 'Hammadde', 50, 'Adet', 20)
    # stock movements
    db.cursor.execute(
        "INSERT INTO stok_hareketleri (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama) VALUES (?,?,?,?,?,?)",
        (u1, '2023-01-02 09:00:00', 'Giriş', 10, None, '')
    )
    db.cursor.execute(
        "INSERT INTO stok_hareketleri (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama) VALUES (?,?,?,?,?,?)",
        (u2, '2023-01-02 10:00:00', 'Giriş', 5, None, '')
    )
    db.cursor.execute(
        "INSERT INTO stok_hareketleri (urun_id, tarih, hareket_tipi, miktar, fatura_id, aciklama) VALUES (?,?,?,?,?,?)",
        (u1, '2023-01-03 11:00:00', 'Çıkış', 2, None, '')
    )
    # work orders
    db.cursor.execute(
        "INSERT INTO is_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (1, 'CustA', 'Glass1', 10, 100, 'Bekliyor', '2023-01-01'))
    db.cursor.execute(
        "INSERT INTO is_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (2, 'CustB', 'Glass2', 15, 150, 'Bekliyor', '2023-01-02'))
    db.cursor.execute(
        "INSERT INTO is_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (1, 'CustC', 'Special', 5, 50, 'Bekliyor', '2023-01-02'))
    # temper orders
    db.cursor.execute(
        "INSERT INTO temper_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (1, 'CustA', 'TemGlass1', 10, 200, 'Bekliyor', '2023-01-01'))
    db.cursor.execute(
        "INSERT INTO temper_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (2, 'CustB', 'TemGlass2', 15, 300, 'Bekliyor', '2023-01-02'))
    db.cursor.execute(
        "INSERT INTO temper_emirleri (musteri_id, firma_musterisi, urun_niteligi, miktar_m2, fiyat, durum, tarih) VALUES (?,?,?,?,?,?,?)",
        (1, 'CustC', 'TemSpecial', 5, 100, 'Bekliyor', '2023-01-02'))
    db.conn.commit()
    return db

def _is_sorted_by_date_id(rows):
    pairs = [(row[1], row[0]) for row in rows]
    return pairs == sorted(pairs, key=lambda x: (x[0], x[1]), reverse=True)

def test_is_emirlerini_getir_sorted(db):
    results = db.is_emirlerini_getir()
    assert _is_sorted_by_date_id(results)
    search_results = db.is_emirlerini_getir('ABC')
    assert _is_sorted_by_date_id(search_results)

def test_temper_emirlerini_getir_sorted(db):
    results = db.temper_emirlerini_getir()
    assert _is_sorted_by_date_id(results)
    search_results = db.temper_emirlerini_getir('ABC')
    assert _is_sorted_by_date_id(search_results)

def test_stok_hareketlerini_getir(db):
    rows = db.stok_hareketlerini_getir()
    assert _is_sorted_by_date_id(rows)
    # filter by product
    first_product_id = db.urunleri_getir()[0][0]
    filtered = db.stok_hareketlerini_getir(first_product_id)
    assert all(r[2] == 'GlassA' for r in filtered)
