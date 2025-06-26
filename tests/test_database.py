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
    # invoices
    f1 = db.fatura_ekle(1, '2023-01-05', 'F001', 'Satış', 100)
    db.fatura_kalemi_ekle(f1, u1, 10, 10, 100)
    f2 = db.fatura_ekle(2, '2023-01-10', 'F002', 'Satış', 200)
    db.fatura_kalemi_ekle(f2, u2, 5, 40, 200)
    f3 = db.fatura_ekle(1, '2023-01-01', 'F003', 'Satış', 50)
    db.fatura_kalemi_ekle(f3, u1, 5, 10, 50)
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

def test_faturalari_getir_by_musteri(db):
    rows = db.faturalari_getir_by_musteri_id(1)
    assert _is_sorted_by_date_id(rows)
    nums = [r[2] for r in rows]
    assert nums == ['F001', 'F003']

def test_cam_listesi_ekle_ve_getir(db):
    is_id = db.is_emri_ekle(1, 'CustX', 'Test', 1, 10, '2023-01-04')
    db.cam_listesi_ekle(is_id, 1000, 2000, 2.0, 'P1')
    rows = db.cam_listesini_getir(is_id)
    assert rows == [(1000, 2000, 2.0, 'P1')]

def test_is_emri_getir_by_id_order(db):
    is_id = db.is_emri_ekle(1, 'ClientZ', 'Desc', 5, 50, '2023-01-05')
    row = db.is_emri_getir_by_id(is_id)
    assert row[2] == 'ClientZ'
    assert row[3] == 'Desc'

def test_varliklar_crud(db):
    db.cek_ekle('C1', 'Bank', 'Sube', 100.0, '2023-01-10', 'Kes', 'Portföyde', '', '')
    db.tapu_ekle('İl', 'İlçe', 'Mah', '1/1', 50.0, 'Arsa', '', 1000.0, '', '')
    db.arac_ekle('34AA', 'Model', 'Otomobil', 2020, 'Firma', 200.0, 'Aktif', '', '')
    assert db.cekleri_getir()[0][1] == 'C1'
    assert db.tapulari_getir()[0][1] == 'İl'
    assert db.araclari_getir()[0][1] == '34AA'
