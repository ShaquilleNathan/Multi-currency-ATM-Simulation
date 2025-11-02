# Author             : Kelompok 7 Berkom K.33

import os
import time
import random
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)
app.secret_key = os.urandom(24) 

MIN_SALDO_AWAL_IDR = 50000
MIN_SISA_SALDO_IDR = 10000
MAKS_PERCOBAAN_PIN = 3

KURS_BELI = {
    'USD': 16570, 'EUR': 19310, 'GBP': 22225, 'KRW': 11.65,
    'JPY': 109.85, 'CNY': 2325, 'MYR': 3930, 'IDR': 1
}

CURRENCY_WITHDRAW_DATA = {
    'USD': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 3.02, 'max_amount_curr_lain': 603.5, 'step_curr_lain': 3.02},
    'EUR': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 2.59, 'max_amount_curr_lain': 517.87, 'step_curr_lain': 2.59},
    'GBP': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 2.25, 'max_amount_curr_lain': 449.44, 'step_curr_lain': 2.25},
    'KRW': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 4291.85, 'max_amount_curr_lain': 858369.1, 'step_curr_lain': 4291.85},
    'JPY': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 455.17, 'max_amount_curr_lain': 91033.23, 'step_curr_lain': 455.17},
    'CNY': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 21.51, 'max_amount_curr_lain': 4301.08, 'step_curr_lain': 21.51},
    'MYR': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 12.725, 'max_amount_curr_lain': 2544.53, 'step_curr_lain': 12.725},
}

KUMPULAN_BANK = {
    '001': 'BRI', '007': 'MANDIRI', '002': 'BNI', '008': 'BTN',
    '003': 'BCA', '009': 'PERMATA', '004': 'RBS', '010': 'DKI',
    '005': 'CITIBANK', '011': 'BSI', '006': 'MUAMALAT', '012': 'KB BUKOPIN',
}

KODE_PERUSAHAAN_MAP = {
    "401": 'PAM KOTA BOGOR', "406": 'PAM KOTA CIREBON',
    "402": 'PAM KOTA CIANJUR', "407": 'PAM KOTA SUBANG',
    "403": 'PAM KOTA KUNINGAN', "408": 'PAM KOTA CILEGON',
    "404": 'PAM KOTA SUMEDANG', "409": 'PAM KOTA DEPOK',
    "405": 'PAM KOTA SUKABUMI', "410": 'PAM KOTA BANDUNG',
}

#Fungsi Bantuan
def format_rupiah(angka):
    """Memformat angka menjadi format Rupiah."""
    return f"Rp{angka:,.0f}".replace(',', '.')

def format_currency(angka, kode_mata_uang):
    """Memformat angka sesuai mata uang."""
    if kode_mata_uang == 'IDR':
        return format_rupiah(angka)
    elif kode_mata_uang in ['USD', 'EUR', 'GBP', 'MYR', 'CNY']:
        return f"{kode_mata_uang} {angka:,.2f}"
    elif kode_mata_uang in ['JPY', 'KRW']:
         return f"{kode_mata_uang} {angka:,.0f}"
    else:
        return f"{kode_mata_uang} {angka:,.2f}"

#Fungsi Bahasa
def load_language(lang_code):
    if lang_code == 'id':
        return {
            "buat_akun": "Silakan buat akun jika belum memiliki akun",
            "masukkan_data_anda": "Silakan masukkan data-data di bawah ini!",
            "selamat_datang": "SELAMAT DATANG DI BANK BERKOM A TEBAL",
            "masukkan_kartu_prompt": "Silakan masukkan kartu Anda untuk memulai.",
            "tekan_enter_kartu": "Tekan Enter untuk memasukkan kartu...",
            "kartu_berhasil": "Kartu berhasil dimasukkan!",
            "pilih_bahasa_atm": "PILIH BAHASA YANG ANDA INGIN GUNAKAN!",
            "masukkan_pin": "Masukkan PIN anda: ",
            "pin_salah_sisa": "PIN yang dimasukkan salah. Silakan coba lagi. Anda memiliki {} kesempatan lagi",
            "akun_dikunci": "Akun anda telah dikunci karena terlalu banyak percobaan PIN yang salah.",
            "kartu_diblokir": "Kartu ATM Anda diblokir.",
            "anda_berhasil_masuk": "Anda berhasil masuk",
            "pilih_menu_transaksi": "SILAHKAN PILIH MENU TRANSAKSI YANG ANDA INGINKAN",
            "menu_info_saldo": "1. Informasi Saldo",
            "menu_tarik_tunai": "2. Penarikan Tunai",
            "menu_transfer": "3. Transfer",
            "menu_pembayaran": "4. Pembayaran",
            "menu_ganti_pin": "5. Ganti PIN",
            "menu_selesai": "6. Selesai Transaksi",
            "masukkan_pilihan_menu": "Masukkan menu yang anda inginkan: ",
            "harap_menunggu": "HARAP MENUNGGU",
            "transaksi_diproses": "TRANSAKSI ANDA SEDANG DIPROSES",
            "saldo_rekening_anda": "SALDO REKENING ANDA",
            "lanjut_transaksi_tanya": "Lanjut Transaksi?",
            "opsi_ya": "1. Ya",
            "opsi_tidak": "2. Tidak",
            "masukkan_respon": "Masukkan Respon Anda: ",
            "menu_penarikan_cepat": "MENU PENARIKAN CEPAT",
            "pilih_jumlah_penarikan": "SILAKAN PILIH JUMLAH PENARIKAN",
            "jumlah_lain": "5. JUMLAH LAIN",
            "penarikan_berhasil": "Anda telah berhasil menarik {}",
            "sisa_saldo_anda": "Sisa saldo di rekening anda adalah {}",
            "cetak_receipt_tanya": "Apakah anda ingin mencetak receipt?",
            "saldo_tidak_cukup": "SALDO TIDAK MENCUKUPI",
            "masukkan_jumlah_penarikan_lain": "MASUKKAN JUMLAH PENARIKAN TUNAI YANG ANDA INGINKAN",
            "dalam_kelipatan": "(DALAM KELIPATAN {})",
            "maksimal": "MAKSIMAL {}",
            "jumlah_penarikan_input": "JUMLAH PENARIKAN: ",
            "nominal_terlalu_kecil": "NOMINAL YANG DIINPUT TERLALU KECIL",
            "nominal_terlalu_besar": "NOMINAL YANG DIINPUT TERLALU BESAR",
            "nominal_tidak_valid": "NOMINAL TIDAK VALID (Harus kelipatan {} dan antara {} - {})",
            "nominal_anda_input": "NOMINAL YANG ANDA INPUT ADALAH {}",
            "apakah_yakin": "APAKAH ANDA YAKIN?",
            "konfirmasi_y_n": "Konfirmasi (y/n): ",
            "sisa_saldo_min_tidak_cukup": "Penarikan gagal. Saldo minimal setelah penarikan adalah {}",
            "header_receipt_tarik": "TARIK TUNAI",
            "jumlah_receipt": "JUMLAH            : {}",
            "sisa_saldo_receipt": "SISA SALDO        : {}",
            "waktu_transaksi_receipt": "WAKTU TRANSAKSI   : {}",
            "header_transfer": "===================ATM TRANSFER===================",
            "prompt_kode_bank_rek": "MASUKKAN KODE BANK DAN NOMOR REKENING TUJUAN",
            "ket_kode_bank_rek": "3 digit kode bank diikuti nomor rekening",
            "contoh_transfer": "Cth. 0011234567 (Untuk BRI)",
            "lihat_kode_bank_tanya": "Apakah anda ingin melihat kode bank terlebih dahulu (y/n)?",
            "daftar_kode_bank": "DAFTAR KODE BANK",
            "transaksi_dilanjutkan": "Transaksi Akan Dilanjutkan",
            "rek_tujuan_input": "Nomor Rekening Tujuan (Kode Bank + No. Rek): ",
            "nama_penerima_input": "Nama Penerima: ",
            "nominal_transfer_input": "Masukkan Jumlah Nominal Yang Akan Ditransfer: ",
            "nominal_transfer_ulang_input": "Masukkan Kembali Nominal Yang Akan Ditransfer: ",
            "konfirmasi_transfer_data": "KONFIRMASI DATA TRANSFER",
            "bank_receipt": "Bank              : {}",
            "tujuan_receipt": "Tujuan            : {}",
            "penerima_receipt": "Penerima          : {}",
            "jumlah_transfer_receipt": "Jumlah Transfer   : {}",
            "data_sesuai_tanya": "Apakah data sudah sesuai (y/n)? ",
            "transaksi_selesai": "TRANSAKSI TELAH SELESAI",
            "perlu_transaksi_lain": "PERLU TRANSAKSI YANG LAIN?",
            "header_pembayaran": "---------------JENIS PEMBAYARAN/PEMBELIAN-----------------",
            "pilih_pembayaran": "1. Telepon/HP",
            "pilih_listrik": "2. Listrik/PLN",
            "pilih_air": "3. Air/PDAM",
            "prompt_input_telepon": "MASUKKAN NOMOR HANDPHONE ANDA",
            "nomor_telepon_input": "Nomor Telepon: ",
            "pilih_nominal_pulsa": "PILIH JUMLAH NOMINAL PULSA",
            "pulsa_lainnya": "8. LAINNYA", 
            "pilih_nominal_isi_ulang": "Pilih nominal isi ulang anda: ",
            "masukkan_nominal_lain": "Masukkan nominal pulsa lainnya: ",
            "header_konfirmasi_pulsa": "-------------------KONFIRMASI PEMBELIAN PULSA PRABAYAR-------------------",
            "nomor_hp_receipt": "Nomor Handphone   : {}",
            "jumlah_pulsa_receipt": "Jumlah            : {}",
            "biaya_admin_receipt": "Biaya Admin       : {}",
            "total_receipt": "TOTAL             : {}",
            "proses_transaksi_tanya": "PROSES TRANSAKSI (y/n)? ",
            "transaksi_berhasil": "TRANSAKSI BERHASIL",
            "berikut_struk": "BERIKUT ADALAH STRUK ANDA",
            "header_struk_bank": "---------------------BANK BERKOM A TEBAL----------------------",
            "header_struk_pulsa": "-----------------PEMBELIAN PULSA PRABAYAR-----------------",
            "voucher_reff_receipt": "Voucher Reff      : {}",
            "footer_struk_1": "---------Jl. Jalan di Bandung-------",
            "footer_struk_pulsa_1": "-----------PROVIDER BERKOM MENYATAKAN STRUK INI-----------",
            "footer_struk_sah": "-------------SEBAGAI BUKTI PEMBAYARAN YANG SAH------------",
            "prompt_input_listrik": "MASUKKAN NOMOR METER ANDA",
            "header_konfirmasi_listrik": "---------------KONFIRMASI PEMBELIAN LISTRIK PRABAYAR---------------",
            "nomor_meter_receipt": "Nomor Meter       : {}",
            "idpel_receipt": "IDPEL             : {}",
            "nama_receipt": "Nama              : {}",
            "tarif_daya_receipt": "Tarif/Daya        : R1M / 900 VA",
            "pilih_nominal_token": "PILIH JUMLAH NOMINAL TOKEN",
            "admin_rp_1000": "BIAYA ADMIN RP 1.000",
            "header_struk_listrik": "-------------STRUK PEMBELIAN LISTRIK PRABAYAR--------------",
            "stroom_token_receipt": "Stroom/Token      : {}",
            "footer_struk_listrik_1": "-----------------PLN MENYATAKAN STRUK INI-----------------",
            "prompt_input_air": "MASUKKAN KODE PERUSAHAAN DIIKUTI NOMOR PELANGGAN",
            "contoh_air": "Contoh: 4011234567890 (PAM KOTA BOGOR)",
            "lihat_kode_pdam_tanya": "Apakah anda ingin melihat daftar kode air minum/PDAM (y/n)? ",
            "daftar_kode_pdam": "DAFTAR KODE PERUSAHAAN PDAM",
            "nomor_pelanggan_input": "Masukkan kode perusahaan + nomor pelanggan: ",
            "header_konfirmasi_air": "-------------------KONFIRMASI PEMBAYARAN AIR/PDAM-------------------",
            "tagihan_receipt": "TAGIHAN {}",
            "no_pelanggan_receipt": "No Pelanggan      : {}",
            "total_bayar_receipt": "Total Bayar       : {}",
            "lanjut_pembayaran_tanya": "Ingin Melanjutkan Pembayaran (y/n)? ",
            "header_struk_air": "----------------STRUK PEMBAYARAN AIR/PDAM-----------------",
            "footer_struk_air_1": "-----------------PDAM MENYATAKAN STRUK INI----------------",
            "masukkan_pin_lama": "Masukkan PIN lama anda: ",
            "masukkan_pin_baru": "Masukkan PIN baru anda (6 digit): ",
            "konfirmasi_pin_baru": "Konfirmasikan kembali PIN baru anda: ",
            "pin_berhasil_diubah": "PIN berhasil diubah!",
            "pin_lama_salah": "PIN lama yang dimasukkan salah.",
            "pin_baru_tidak_cocok": "PIN baru dan konfirmasi tidak cocok.",
            "pin_baru_harus_6_digit": "PIN baru harus 6 digit angka.",
            "ambil_kartu": "Silakan Ambil Kartu Anda",
            "terima_kasih": "Terima Kasih telah menggunakan ATM BANK BERKOM A TEBAL",
            "pilih_mata_uang": "PILIH MATA UANG UTAMA AKUN ANDA",
            "pilihan_anda": "Pilihan Anda: ",
            "pilihan_tidak_valid": "Pilihan tidak valid.",
            "masukkan_angka": "Masukkan angka.",
            "masukkan_angka_valid": "Masukkan angka yang valid.",
            "buat_pin_6_digit": "Silahkan buat PIN anda (6 Digit Angka): ",
            "konfirmasi_pin": "Masukkan kembali PIN yang telah anda buat: ",
            "pin_harus_6_digit": "PIN harus terdiri dari 6 digit angka.",
            "pin_tidak_cocok": "PIN yang anda masukkan belum sama. Silahkan coba lagi.",
            "masukkan_saldo_awal": "Masukkan jumlah saldo awal (minimum {}): ",
            "saldo_awal_kurang": "Mohon maaf, saldo awal minimal adalah {}.",
            "data_pribadi_anda": "Berikut adalah data-data pribadi anda!",
            "nama_lengkap": "Nama Lengkap      ",
            "tanggal_lahir": "Tanggal Lahir     ",
            "asal_negara": "Asal Negara       ",
            "pin": "PIN               ",
            "mata_uang_utama": "Mata Uang Utama ",
            "saldo_awal": "Saldo Awal        ",
            "menu_utama_non_idr": "MENU UTAMA (Non-IDR)",
            "menu_info_saldo_non_idr": "1. Informasi Saldo ({})", 
            "menu_tarik_tunai_non_idr": "2. Penarikan Tunai", 
            "menu_ganti_pin_non_idr": "3. Ganti PIN", 
            "menu_selesai_non_idr": "4. Selesai Transaksi", 
            "saldo_dalam_idr_tanya": "Lanjut melihat saldo dalam IDR?",
            "saldo_dalam_idr_label": "Saldo Dalam IDR (Kurs Beli)", 
            "kurs_beli_terkini": "KURS BELI TERKINI (1 Mata Uang Asing = X IDR)", 
            "penarikan_non_idr_header": "PENARIKAN TUNAI ({})",
            "penarikan_non_idr_prompt": "PILIH JUMLAH PENARIKAN (ekuivalen IDR)",
            "penarikan_non_idr_lainnya": "5. JUMLAH LAIN (dalam {})",
            "masukkan_jumlah_lain_curr": "MASUKKAN JUMLAH PENARIKAN DALAM {}",
            "jumlah_penarikan_curr_input": "Jumlah Penarikan ({}): ",
            "penarikan_berhasil_curr": "Anda telah berhasil menarik {} (Ekuivalen {})",
            "nominal_tidak_valid_curr": "NOMINAL TIDAK VALID (Harus kelipatan {} dan antara {} - {})",
            "jumlah_receipt_non_idr": "JUMLAH            : {} (Ekuivalen {})",
        }
    elif lang_code == 'en':
        return {
            "buat_akun": "Silakan buat akun jika belum memiliki akun",
            "masukkan_data_anda": "Please enter your data below!",
            "selamat_datang": "WELCOME TO BANK BERKOM A TEBAL",
            "masukkan_kartu_prompt": "Please insert your card to begin.",
            "tekan_enter_kartu": "Press Enter to insert card...",
            "kartu_berhasil": "Card inserted successfully!",
            "pilih_bahasa_atm": "PLEASE SELECT YOUR LANGUAGE!",
            "masukkan_pin": "Enter your PIN: ",
            "pin_salah_sisa": "Wrong PIN entered. Please try again. You have {} more chances",
            "akun_dikunci": "Your account has been locked due to too many incorrect PIN attempts.",
            "kartu_diblokir": "Your ATM card is blocked.", 
            "anda_berhasil_masuk": "You have logged in.",
            "pilih_menu_transaksi": "PLEASE SELECT YOUR DESIRED TRANSACTION MENU",
            "menu_info_saldo": "1. Balance Information",
            "menu_tarik_tunai": "2. Cash Withdrawal",
            "menu_transfer": "3. Transfer",
            "menu_pembayaran": "4. Payment",
            "menu_ganti_pin": "5. Change PIN",
            "menu_selesai": "6. Finish Transaction",
            "masukkan_pilihan_menu": "Enter your desired menu: ",
            "harap_menunggu": "PLEASE WAIT",
            "transaksi_diproses": "YOUR TRANSACTION IS BEING PROCESSED",
            "saldo_rekening_anda": "YOUR ACCOUNT BALANCE",
            "lanjut_transaksi_tanya": "Continue Transaction?",
            "opsi_ya": "1. Yes",
            "opsi_tidak": "2. No",
            "masukkan_respon": "Input Your Response Here: ",
            "menu_penarikan_cepat": "FAST WITHDRAWAL MENU",
            "pilih_jumlah_penarikan": "PLEASE SELECT WITHDRAWAL AMOUNT",
            "jumlah_lain": "5. OTHER AMOUNT",
            "penarikan_berhasil": "You have successfully withdrawn {}",
            "sisa_saldo_anda": "Your remaining account balance is {}",
            "cetak_receipt_tanya": "Do you wish to print the receipt?",
            "saldo_tidak_cukup": "BALANCE NOT ENOUGH",
            "masukkan_jumlah_penarikan_lain": "ENTER YOUR DESIRED CASH AMOUNT",
            "dalam_kelipatan": "(MULTIPLE OF {})",
            "maksimal": "MAXIMUM {}",
            "jumlah_penarikan_input": "WITHDRAWAL AMOUNT: ",
            "nominal_terlalu_kecil": "AMOUNT TOO SMALL",
            "nominal_terlalu_besar": "AMOUNT TOO LARGE",
            "nominal_tidak_valid": "AMOUNT INVALID (Must be multiple of {} and between {} - {})",
            "nominal_anda_input": "THE AMOUNT YOU INPUTTED IS {}",
            "apakah_yakin": "ARE YOU SURE?",
            "konfirmasi_y_n": "Confirmation (y/n): ",
            "sisa_saldo_min_tidak_cukup": "Withdrawal failed. Minimum balance after withdrawal is {}",
            "header_receipt_tarik": "CASH WITHDRAWAL",
            "jumlah_receipt": "AMOUNT            : {}",
            "sisa_saldo_receipt": "REMAINING BALANCE : {}",
            "waktu_transaksi_receipt": "TRANSACTION TIME  : {}",
            "header_transfer": "====================ATM TRANSFER===================",
            "prompt_kode_bank_rek": "ENTER BANK CODE AND DESTINATION ACCOUNT NUMBER",
            "ket_kode_bank_rek": "3 digits bank code followed by account number",
            "contoh_transfer": "e.g. 0011234567 (For BRI)",
            "lihat_kode_bank_tanya": "Do you wish to see the bank codes first (y/n)?",
            "daftar_kode_bank": "BANK CODES LIST",
            "transaksi_dilanjutkan": "Transaction Will Be Continued",
            "rek_tujuan_input": "Destination Account Number (Bank Code + Acc. No): ",
            "nama_penerima_input": "Recipient Name: ",
            "nominal_transfer_input": "Enter The Amount You Wish To Transfer: ",
            "nominal_transfer_ulang_input": "Re-enter The Amount You Wish To Transfer: ",
            "konfirmasi_transfer_data": "TRANSFER DATA CONFIRMATION",
            "bank_receipt": "Bank              : {}",
            "tujuan_receipt": "Destination       : {}",
            "penerima_receipt": "Recipient         : {}",
            "jumlah_transfer_receipt": "Transfer Amount   : {}",
            "data_sesuai_tanya": "Is the data correct (y/n)? ",
            "transaksi_selesai": "TRANSACTION COMPLETED",
            "perlu_transaksi_lain": "NEED ANOTHER TRANSACTION?",
            "header_pembayaran": "----------------PAYMENT / PURCHASE TYPE-------------------",
            "pilih_pembayaran": "1. Telephone/Mobile",
            "pilih_listrik": "2. Electricity/PLN",
            "pilih_air": "3. Water/PDAM",
            "prompt_input_telepon": "ENTER YOUR MOBILE PHONE NUMBER",
            "nomor_telepon_input": "Phone Number: ",
            "pilih_nominal_pulsa": "CHOOSE MOBILE CREDIT AMOUNT",
            "pulsa_lainnya": "8. OTHER", 
            "pilih_nominal_isi_ulang": "Select your top-up amount: ",
            "masukkan_nominal_lain": "Enter other credit amount: ",
            "header_konfirmasi_pulsa": "-------------------PREPAID CREDIT PURCHASE CONFIRMATION-------------------",
            "nomor_hp_receipt": "Phone Number      : {}",
            "jumlah_pulsa_receipt": "Amount            : {}",
            "biaya_admin_receipt": "Admin Fee         : {}",
            "total_receipt": "TOTAL             : {}",
            "proses_transaksi_tanya": "PROCESS TRANSACTION (y/n)? ",
            "transaksi_berhasil": "TRANSACTION SUCCESSFUL",
            "berikut_struk": "HERE IS YOUR RECEIPT",
            "header_struk_bank": "---------------------BANK BERKOM A TEBAL----------------------",
            "header_struk_pulsa": "-----------------PREPAID CREDIT PURCHASE-----------------",
            "voucher_reff_receipt": "Voucher Reff      : {}",
            "footer_struk_1": "---------Jl. Jalan di Bandung-------",
            "footer_struk_pulsa_1": "----------PROVIDER BERKOM DECLARES THIS RECEIPT-----------",
            "footer_struk_sah": "----------------AS VALID PROOF OF PURCHASE----------------",
            "prompt_input_listrik": "ENTER YOUR METER NUMBER",
            "header_konfirmasi_listrik": "---------------PREPAID ELECTRICITY PURCHASE CONFIRMATION---------------",
            "nomor_meter_receipt": "Meter Number      : {}",
            "idpel_receipt": "Customer ID       : {}",
            "nama_receipt": "Name              : {}",
            "tarif_daya_receipt": "Tariff/Power      : R1M / 900 VA",
            "pilih_nominal_token": "CHOOSE TOKEN AMOUNT",
            "admin_rp_1000": "ADMIN FEE RP 1,000",
            "header_struk_listrik": "-------------PREPAID ELECTRICITY PURCHASE RECEIPT--------------",
            "stroom_token_receipt": "Stroom/Token      : {}",
            "footer_struk_listrik_1": "-----------------PLN DECLARES THIS RECEIPT----------------",
            "prompt_input_air": "ENTER COMPANY CODE FOLLOWED BY CUSTOMER NUMBER",
            "contoh_air": "Example: 4011234567890 (PAM KOTA BOGOR)",
            "lihat_kode_pdam_tanya": "Do you wish to see the water/PDAM company codes (y/n)? ",
            "daftar_kode_pdam": "PDAM COMPANY CODES LIST",
            "nomor_pelanggan_input": "Enter company code + customer number: ",
            "header_konfirmasi_air": "-------------------WATER/PDAM PAYMENT CONFIRMATION-------------------",
            "tagihan_receipt": "BILL {}",
            "no_pelanggan_receipt": "Customer No.      : {}",
            "total_bayar_receipt": "Total Payment     : {}",
            "lanjut_pembayaran_tanya": "Continue Payment (y/n)? ",
            "header_struk_air": "----------------WATER/PDAM PAYMENT RECEIPT-----------------",
            "footer_struk_air_1": "-----------------PDAM DECLARES THIS RECEIPT----------------",
            "masukkan_pin_lama": "Enter your old PIN: ",
            "masukkan_pin_baru": "Enter your new PIN (6 digits): ",
            "konfirmasi_pin_baru": "Please confirm your new PIN: ",
            "pin_berhasil_diubah": "PIN changed successfully!",
            "pin_lama_salah": "Incorrect old PIN entered.",
            "pin_baru_tidak_cocok": "New PIN and confirmation do not match.",
            "pin_baru_harus_6_digit": "New PIN must be 6 digits.",
            "ambil_kartu": "Please Take Your Card",
            "terima_kasih": "Thanks For Using ATM BANK BERKOM A TEBAL",
            "pilih_mata_uang": "SELECT YOUR ACCOUNT'S PRIMARY CURRENCY",
            "pilihan_anda": "Your Choice: ",
            "pilihan_tidak_valid": "Invalid choice.",
            "masukkan_angka": "Enter a number.",
            "masukkan_angka_valid": "Enter a valid number.",
            "buat_pin_6_digit": "Please create your PIN (6 Digits): ",
            "konfirmasi_pin": "Re-enter the PIN you created: ",
            "pin_harus_6_digit": "PIN must be 6 digits.",
            "pin_tidak_cocok": "The PINs you entered do not match. Please try again.",
            "masukkan_saldo_awal": "Enter initial balance amount (minimum {}): ",
            "saldo_awal_kurang": "Sorry, the minimum initial balance is {}.",
            "data_pribadi_anda": "Here is your personal data!",
            "nama_lengkap": "Full Name         ",
            "tanggal_lahir": "Date of Birth     ",
            "asal_negara": "Country           ",
            "pin": "PIN               ",
            "mata_uang_utama": "Primary Currency  ",
            "saldo_awal": "Initial Balance   ",
            "menu_utama_non_idr": "MAIN MENU (Non-IDR)",
            "menu_info_saldo_non_idr": "1. Balance Information ({})", 
            "menu_tarik_tunai_non_idr": "2. Cash Withdrawal",
            "menu_ganti_pin_non_idr": "3. Change PIN",
            "menu_selesai_non_idr": "4. Finish Transaction",
            "saldo_dalam_idr_tanya": "Continue to view balance in IDR?",
            "saldo_dalam_idr_label": "Balance In IDR (Buy Rate)",
            "kurs_beli_terkini": "CURRENT BUY RATES (1 Foreign Currency Unit = X IDR)",
            "penarikan_non_idr_header": "CASH WITHDRAWAL ({})",
            "penarikan_non_idr_prompt": "SELECT WITHDRAWAL AMOUNT (IDR equivalent)",
            "penarikan_non_idr_lainnya": "5. OTHER AMOUNT (in {})",
            "masukkan_jumlah_lain_curr": "ENTER WITHDRAWAL AMOUNT IN {}",
            "jumlah_penarikan_curr_input": "Withdrawal Amount ({}): ",
            "penarikan_berhasil_curr": "You have successfully withdrawn {} (Equivalent to {})",
            "nominal_tidak_valid_curr": "AMOUNT INVALID (Must be multiple of {} and between {} - {})",
            "jumlah_receipt_non_idr": "AMOUNT            : {} (Equivalent to {})",
        }
    else:
        return load_language('id') 

@app.route('/')
def index():
    """Menyajikan halaman index.html."""
    return render_template('index.html')

@app.route('/create_account_page')
def create_account_page():
    """Menyajikan halaman form pembuatan akun."""
    return render_template('create_account.html')

@app.route('/api/status')
def get_status():
    """Mendapatkan status login, data user, dan config."""
    if 'user_data' in session:
        return jsonify({
            'logged_in': True,
            'user_data': session.get('user_data'),
            'terms': session.get('TERMS'),
            'config': {
                'kurs_beli': KURS_BELI,
                'currency_data': CURRENCY_WITHDRAW_DATA,
                'bank_codes': KUMPULAN_BANK,
                'pdam_codes': KODE_PERUSAHAAN_MAP,
                'min_saldo_awal_idr': MIN_SALDO_AWAL_IDR,
                'min_sisa_saldo_idr': MIN_SISA_SALDO_IDR
            }
        })
    else:
        return jsonify({
            'logged_in': False,
            'terms': load_language('id'),
            'config': {
                'kurs_beli': KURS_BELI,
                'currency_data': CURRENCY_WITHDRAW_DATA,
                'bank_codes': KUMPULAN_BANK,
                'pdam_codes': KODE_PERUSAHAAN_MAP,
                'min_saldo_awal_idr': MIN_SALDO_AWAL_IDR,
                'min_sisa_saldo_idr': MIN_SISA_SALDO_IDR
            }
        })

@app.route('/api/set_language', methods=['POST'])
def set_language():
    """Mengatur bahasa yang dipilih pengguna."""
    data = request.json
    lang_code = data.get('lang', 'id')
    session['TERMS'] = load_language(lang_code)
    session['current_lang'] = lang_code
    if 'user_data' in session:
        user_data = session['user_data']
        user_data['bahasa'] = lang_code
        session['user_data'] = user_data
        session.modified = True
        
    return jsonify({'success': True, 'terms': session['TERMS']})

@app.route('/api/logout')
def logout():
    """Menghapus sesi pengguna."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/create_account', methods=['POST'])
def create_account():
    """Membuat akun baru."""
    data = request.json
    try:
        nama_lengkap = data['nama_lengkap']
        tanggal_lahir = data['tanggal_lahir']
        asal_negara = data['asal_negara']
        bahasa = session.get('current_lang', 'id')
        mata_uang_utama = data['mata_uang_utama']
        pin = data['pin']
        pin_konfirmasi = data['pin_konfirmasi']
        saldo = float(data['saldo'])
        
        TERMS = load_language(bahasa)
        session['TERMS'] = TERMS

        if len(pin) != 6 or not pin.isdigit():
            return jsonify({'success': False, 'message': TERMS['pin_harus_6_digit']})
        if pin != pin_konfirmasi:
            return jsonify({'success': False, 'message': TERMS['pin_tidak_cocok']})

        min_saldo_awal = MIN_SALDO_AWAL_IDR if mata_uang_utama == 'IDR' else MIN_SALDO_AWAL_IDR / KURS_BELI.get(mata_uang_utama, 1)
        if saldo < min_saldo_awal:
            min_saldo_awal_str = format_currency(min_saldo_awal, mata_uang_utama)
            return jsonify({'success': False, 'message': TERMS['saldo_awal_kurang'].format(min_saldo_awal_str)})

        user_data = {
            'nama_lengkap': nama_lengkap,
            'tanggal_lahir': tanggal_lahir,
            'asal_negara': asal_negara,
            'pin': pin,
            'saldo': saldo,
            'mata_uang_utama': mata_uang_utama,
            'bahasa': bahasa,
            'percobaan_pin': 0,
            'diblokir': False
        }
        session['user_data'] = user_data
        session.modified = True

        return jsonify({'success': True, 'user_data': user_data, 'terms': TERMS})

    except Exception as e:
        return jsonify({'success': False, 'message': f"Error: {str(e)}"})

@app.route('/api/login', methods=['POST'])
def login():
    if 'user_data' not in session:
        return jsonify({'success': False, 'message': 'Sesi tidak ditemukan. Silakan mulai ulang.'})

    data = request.json
    pin_masuk = data.get('pin')
    user_data = session['user_data']
    TERMS = session['TERMS']

    if user_data.get('diblokir', False):
        return jsonify({'success': False, 'blocked': True, 'message': TERMS['akun_dikunci'] + "\n" + TERMS['kartu_diblokir']})

    if pin_masuk == user_data['pin']:
        user_data['percobaan_pin'] = 0
        session['user_data'] = user_data
        session.modified = True
        return jsonify({'success': True, 'message': TERMS['anda_berhasil_masuk'], 'user_data': user_data})
    else:
        user_data['percobaan_pin'] += 1
        sisa_percobaan = MAKS_PERCOBAAN_PIN - user_data['percobaan_pin']
        session['user_data'] = user_data
        session.modified = True

        if sisa_percobaan > 0:
            return jsonify({'success': False, 'message': TERMS['pin_salah_sisa'].format(sisa_percobaan)})
        else:
            user_data['diblokir'] = True
            session['user_data'] = user_data
            session.modified = True
            return jsonify({'success': False, 'blocked': True, 'message': TERMS['akun_dikunci'] + "\n" + TERMS['kartu_diblokir']})

@app.route('/api/get_balance')
def get_balance():
    """Mendapatkan info saldo."""
    if 'user_data' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_data = session['user_data']
    TERMS = session['TERMS']
    mata_uang = user_data['mata_uang_utama']

    saldo_utama_str = format_currency(user_data['saldo'], mata_uang)
    
    if mata_uang == 'IDR':
        return jsonify({
            'success': True,
            'message': f"{TERMS['saldo_rekening_anda']}\n{saldo_utama_str}",
            'saldo_utama': saldo_utama_str
        })
    else:
        kurs = KURS_BELI.get(mata_uang, 1)
        saldo_idr = user_data['saldo'] * kurs
        saldo_idr_str = format_rupiah(saldo_idr)
        
        return jsonify({
            'success': True,
            'message': f"{TERMS['saldo_rekening_anda']}\n{saldo_utama_str}",
            'saldo_utama': saldo_utama_str,
            'saldo_idr_ekuivalen': saldo_idr_str,
            'kurs_info': f"({TERMS['saldo_dalam_idr_label']}: {saldo_idr_str})"
        })

@app.route('/api/withdraw/idr', methods=['POST'])
def withdraw_idr():
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    try:
        tarik_nominal = int(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})

    user_data = session['user_data']
    TERMS = session['TERMS']
    saldo_sebelum = user_data['saldo']

    if tarik_nominal < 50000:
        return jsonify({'success': False, 'message': TERMS['nominal_terlalu_kecil']})
    if tarik_nominal > 10000000:
        return jsonify({'success': False, 'message': TERMS['nominal_terlalu_besar']})
    if tarik_nominal % 50000 != 0:
        return jsonify({'success': False, 'message': TERMS['nominal_tidak_valid'].format(format_rupiah(50000), format_rupiah(50000), format_rupiah(10000000))})

    if saldo_sebelum < tarik_nominal:
        return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})
        
    if (saldo_sebelum - tarik_nominal) < MIN_SISA_SALDO_IDR:
        return jsonify({'success': False, 'message': TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR))})

    user_data['saldo'] -= tarik_nominal
    session['user_data'] = user_data
    session.modified = True

    waktu = datetime.now().isoformat(' ', 'seconds')
    struk = [
        '---------------------------------------------------',
        TERMS['header_receipt_tarik'],
        TERMS['jumlah_receipt'].format(format_rupiah(tarik_nominal)),
        TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])),
        TERMS['waktu_transaksi_receipt'].format(waktu),
        '---------------------------------------------------'
    ]

    return jsonify({
        'success': True,
        'message': TERMS['penarikan_berhasil'].format(format_rupiah(tarik_nominal)) + "\n" + TERMS['sisa_saldo_anda'].format(format_rupiah(user_data['saldo'])),
        'receipt': "\n".join(struk),
        'new_balance': format_rupiah(user_data['saldo'])
    })

@app.route('/api/withdraw/non_idr', methods=['POST'])
def withdraw_non_idr():
    """Memproses penarikan tunai Non-IDR."""
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    amount_data = data.get('amount')

    try:
        tarik_nominal_curr = float(amount_data)
        if tarik_nominal_curr <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})

    user_data = session['user_data']
    TERMS = session['TERMS']
    mata_uang_akun = user_data['mata_uang_utama']
    saldo_sebelum = user_data['saldo']

    if mata_uang_akun not in CURRENCY_WITHDRAW_DATA:
         return jsonify({'success': False, 'message': f"Penarikan {mata_uang_akun} tidak didukung."})

    data_curr = CURRENCY_WITHDRAW_DATA[mata_uang_akun]
    kurs = KURS_BELI[mata_uang_akun]

    multiplier = 1000
    tarik_nominal_int = int(round(tarik_nominal_curr * multiplier))

    min_lain_int = int(round(data_curr['min_amount_curr'] * multiplier))
    max_lain_int = int(round(data_curr['max_amount_curr_lain'] * multiplier))
    step_lain_int = int(round(data_curr['step_curr_lain'] * multiplier))

    if tarik_nominal_int < min_lain_int:
        return jsonify({'success': False, 'message': TERMS['nominal_terlalu_kecil']})

    if tarik_nominal_int > max_lain_int:
        return jsonify({'success': False, 'message': TERMS['nominal_terlalu_besar']})
        
    if tarik_nominal_int % step_lain_int != 0:
        error_msg = TERMS['nominal_tidak_valid_curr']
        try:
            step_lain_float_str = format_currency(data_curr['step_curr_lain'], mata_uang_akun)
            min_lain_float_str = format_currency(data_curr['min_amount_curr'], mata_uang_akun)
            max_lain_float_str = format_currency(data_curr['max_amount_curr_lain'], mata_uang_akun)
            
            error_msg = error_msg.replace('{}', step_lain_float_str, 1)
            error_msg = error_msg.replace('{}', min_lain_float_str, 1)
            error_msg = error_msg.replace('{}', max_lain_float_str, 1)
        except Exception:
             error_msg = "Nominal tidak valid (kelipatan, min/max error)."
        return jsonify({'success': False, 'message': error_msg})

    saldo_sebelum_int = int(round(saldo_sebelum * multiplier))
    if saldo_sebelum_int < tarik_nominal_int:
         return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})

    user_data['saldo'] -= tarik_nominal_curr
    session['user_data'] = user_data
    session.modified = True

    nominal_idr_ekuivalen = tarik_nominal_curr * kurs
    waktu = datetime.now().isoformat(' ', 'seconds')

    struk = [
        '---------------------------------------------------',
        TERMS['header_receipt_tarik'] + f" ({mata_uang_akun})",
        TERMS['jumlah_receipt_non_idr'].replace( 
            '{}', format_currency(tarik_nominal_curr, mata_uang_akun), 1
        ).replace(
            '{}', format_rupiah(nominal_idr_ekuivalen), 1
        ),
        TERMS['sisa_saldo_receipt'].replace('{}', format_currency(user_data['saldo'], mata_uang_akun)),
        TERMS['waktu_transaksi_receipt'].replace('{}', waktu),
        '---------------------------------------------------'
    ]

    return jsonify({
        'success': True,
        'message': TERMS['penarikan_berhasil_curr'].replace(
            '{}', format_currency(tarik_nominal_curr, mata_uang_akun), 1
        ).replace(
            '{}', format_rupiah(nominal_idr_ekuivalen), 1
        ) + "\n" + TERMS['sisa_saldo_anda'].replace('{}', format_currency(user_data['saldo'], mata_uang_akun)),
        'receipt': "\n".join(struk),
        'new_balance': format_currency(user_data['saldo'], mata_uang_akun)
    })

@app.route('/api/transfer/idr', methods=['POST'])
def transfer_idr():
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    try:
        rekening_tujuan = data.get('rek_tujuan')
        nama_penerima = data.get('nama_penerima')
        nominal_transfer = int(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})

    user_data = session['user_data']
    TERMS = session['TERMS']
    
    kode_bank = rekening_tujuan[:3]
    if kode_bank not in KUMPULAN_BANK:
        return jsonify({'success': False, 'message': f"Kode bank {kode_bank} tidak valid."})
    
    if nominal_transfer <= 0:
        return jsonify({'success': False, 'message': "Nominal harus positif."})

    if user_data['saldo'] < nominal_transfer:
        return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})
    
    if (user_data['saldo'] - nominal_transfer) < MIN_SISA_SALDO_IDR:
        return jsonify({'success': False, 'message': TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR))})

    user_data['saldo'] -= nominal_transfer
    session['user_data'] = user_data
    session.modified = True

    waktu = datetime.now().isoformat(' ', 'seconds')
    struk = [
        '------------------------------------------------------',
        TERMS['header_transfer'].split('\n')[0],
        TERMS['transaksi_selesai'],
        TERMS['bank_receipt'].format(KUMPULAN_BANK[kode_bank]),
        TERMS['tujuan_receipt'].format(rekening_tujuan),
        TERMS['penerima_receipt'].format(nama_penerima),
        TERMS['jumlah_transfer_receipt'].format(format_rupiah(nominal_transfer)),
        TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])),
        TERMS['waktu_transaksi_receipt'].format(waktu),
        '------------------------------------------------------'
    ]

    return jsonify({
        'success': True,
        'message': TERMS['transaksi_selesai'],
        'receipt': "\n".join(struk),
        'new_balance': format_rupiah(user_data['saldo'])
    })

@app.route('/api/payment/phone', methods=['POST'])
def payment_phone():
    """Memproses pembayaran pulsa."""
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    try:
        nomor_hp = data.get('nomor_hp')
        nominal_pilihan = int(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})

    user_data = session['user_data']
    TERMS = session['TERMS']
    admin_bank = 1000
    total_bayar = nominal_pilihan + admin_bank

    if user_data['saldo'] < total_bayar:
        return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})
        
    if (user_data['saldo'] - total_bayar) < MIN_SISA_SALDO_IDR:
        return jsonify({'success': False, 'message': TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR))})
    
    user_data['saldo'] -= total_bayar
    session['user_data'] = user_data
    session.modified = True

    waktu = datetime.now().isoformat(' ', 'seconds')
    struk = [
        TERMS['header_struk_bank'],
        TERMS['header_struk_pulsa'],
        TERMS['nomor_hp_receipt'].format(nomor_hp),
        TERMS['voucher_reff_receipt'].format(random.randint(10000000000, 99999999999)),
        TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)),
        TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)),
        TERMS['total_receipt'].format(format_rupiah(total_bayar)),
        TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])),
        TERMS['waktu_transaksi_receipt'].format(waktu),
        TERMS['footer_struk_1'],
        TERMS['footer_struk_pulsa_1'],
        TERMS['footer_struk_sah']
    ]

    return jsonify({
        'success': True,
        'message': TERMS['transaksi_berhasil'],
        'receipt': "\n".join(struk),
        'new_balance': format_rupiah(user_data['saldo'])
    })

@app.route('/api/payment/electricity', methods=['POST'])
def payment_electricity():
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    try:
        nomor_meter = data.get('nomor_meter')
        nominal_pilihan = int(data.get('amount'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})

    user_data = session['user_data']
    TERMS = session['TERMS']
    admin_bank = 1000
    total_bayar = nominal_pilihan + admin_bank
    id_pelanggan = random.randint(100000000000, 999999999999)
    token = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"

    if user_data['saldo'] < total_bayar:
        return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})

    if (user_data['saldo'] - total_bayar) < MIN_SISA_SALDO_IDR:
        return jsonify({'success': False, 'message': TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR))})

    user_data['saldo'] -= total_bayar
    session['user_data'] = user_data
    session.modified = True

    waktu = datetime.now().isoformat(' ', 'seconds')
    struk = [
        TERMS['header_struk_bank'],
        TERMS['header_struk_listrik'],
        TERMS['nomor_meter_receipt'].format(nomor_meter),
        TERMS['idpel_receipt'].format(id_pelanggan),
        TERMS['nama_receipt'].format(user_data['nama_lengkap']),
        TERMS['tarif_daya_receipt'],
        TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)),
        TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)),
        TERMS['total_receipt'].format(format_rupiah(total_bayar)),
        TERMS['stroom_token_receipt'].format(token),
        TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])),
        TERMS['waktu_transaksi_receipt'].format(waktu),
        TERMS['footer_struk_1'],
        TERMS['footer_struk_listrik_1'],
        TERMS['footer_struk_sah']
    ]
    
    return jsonify({
        'success': True,
        'message': TERMS['transaksi_berhasil'],
        'receipt': "\n".join(struk),
        'new_balance': format_rupiah(user_data['saldo'])
    })

@app.route('/api/payment/water_check', methods=['POST'])
def payment_water_check():
    """Mengecek tagihan air (simulasi)."""
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    nomor_pelanggan_full = data.get('nomor_pelanggan')
    user_data = session['user_data']
    TERMS = session['TERMS']

    if len(nomor_pelanggan_full) < 4 or not nomor_pelanggan_full.isdigit():
        return jsonify({'success': False, 'message': "Format input tidak valid."})

    kode_input = nomor_pelanggan_full[:3]
    nomor_saja = nomor_pelanggan_full[3:]

    if kode_input not in KODE_PERUSAHAAN_MAP:
        return jsonify({'success': False, 'message': f"Kode perusahaan {kode_input} tidak dikenal."})

    nama_perusahaan = KODE_PERUSAHAAN_MAP[kode_input]
    tagihan = random.randint(50000, 500000)
    biaya_admin = 2500
    total_bayar = tagihan + biaya_admin

    konfirmasi_data = {
        'nama_perusahaan': nama_perusahaan,
        'nomor_pelanggan_saja': nomor_saja,
        'nama_pelanggan': user_data['nama_lengkap'],
        'tagihan_str': format_rupiah(tagihan),
        'admin_str': format_rupiah(biaya_admin),
        'total_bayar_str': format_rupiah(total_bayar),
        'total_bayar_int': total_bayar,
        'nomor_pelanggan_full': nomor_pelanggan_full
    }
    
    return jsonify({'success': True, 'data': konfirmasi_data})

@app.route('/api/payment/water_pay', methods=['POST'])
def payment_water_pay():
    """Memproses pembayaran air."""
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    try:
        total_bayar = int(data.get('total_bayar'))
        nama_perusahaan = data.get('nama_perusahaan')
        nomor_saja = data.get('nomor_pelanggan_saja')
        tagihan_str = data.get('tagihan_str')
        admin_str = data.get('admin_str')
        total_bayar_str = data.get('total_bayar_str')
        
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': session['TERMS']['masukkan_angka_valid']})
        
    user_data = session['user_data']
    TERMS = session['TERMS']

    if user_data['saldo'] < total_bayar:
        return jsonify({'success': False, 'message': TERMS['saldo_tidak_cukup']})
        
    if (user_data['saldo'] - total_bayar) < MIN_SISA_SALDO_IDR:
        return jsonify({'success': False, 'message': TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR))})
    
    user_data['saldo'] -= total_bayar
    session['user_data'] = user_data
    session.modified = True

    waktu = datetime.now().isoformat(' ', 'seconds')
    struk = [
        TERMS['header_struk_bank'],
        TERMS['header_struk_air'],
        f"Perusahaan        : {nama_perusahaan}",
        TERMS['no_pelanggan_receipt'].format(nomor_saja),
        TERMS['nama_receipt'].format(user_data['nama_lengkap']),
        f"Tagihan           : {tagihan_str}",
        TERMS['biaya_admin_receipt'].format(admin_str),
        TERMS['total_bayar_receipt'].format(total_bayar_str),
        TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])),
        TERMS['waktu_transaksi_receipt'].format(waktu),
        TERMS['footer_struk_1'],
        TERMS['footer_struk_air_1'],
        TERMS['footer_struk_sah']
    ]

    return jsonify({
        'success': True,
        'message': TERMS['transaksi_berhasil'],
        'receipt': "\n".join(struk),
        'new_balance': format_rupiah(user_data['saldo'])
    })


@app.route('/api/change_pin', methods=['POST'])
def change_pin():
    if 'user_data' not in session: return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.json
    user_data = session['user_data']
    TERMS = session['TERMS']
    
    pin_lama = data.get('pin_lama')
    pin_baru = data.get('pin_baru')
    pin_konfirmasi = data.get('pin_konfirmasi')

    if pin_lama != user_data['pin']:
        return jsonify({'success': False, 'message': TERMS['pin_lama_salah']})
    
    if len(pin_baru) != 6 or not pin_baru.isdigit():
        return jsonify({'success': False, 'message': TERMS['pin_baru_harus_6_digit']})

    if pin_baru != pin_konfirmasi:
        return jsonify({'success': False, 'message': TERMS['pin_baru_tidak_cocok']})

    user_data['pin'] = pin_baru
    session['user_data'] = user_data
    session.modified = True
    
    return jsonify({'success': True, 'message': TERMS['pin_berhasil_diubah']})


if __name__ == "__main__":
    app.run(debug=True)