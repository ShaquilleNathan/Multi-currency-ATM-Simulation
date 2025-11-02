# Author             : Kelompok 7 Berkom K.33

import os
import time
import random
import sys
from datetime import datetime

#Konfigurasi Awal
MIN_SALDO_AWAL_IDR = 50000
MIN_SISA_SALDO_IDR = 10000
MAKS_PERCOBAAN_PIN = 3

KURS_BELI = {
    'USD': 16570, 
    'EUR': 19310, 
    'GBP': 22225, 
    'KRW': 11.65, 
    'JPY': 109.85,
    'CNY': 2325,  
    'MYR': 3930,
    'IDR': 1      
}

#Fungsi Bantuan
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_effect(text, delay=0.025):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def format_rupiah(angka):
    return f"Rp{angka:,.0f}".replace(',', '.')

def format_currency(angka, kode_mata_uang):
    if kode_mata_uang == 'IDR':
        return format_rupiah(angka)
    elif kode_mata_uang in ['USD', 'EUR', 'GBP', 'MYR', 'CNY']:
        return f"{kode_mata_uang} {angka:,.2f}"
    elif kode_mata_uang == 'JPY':
         return f"{kode_mata_uang} {angka:,.0f}"
    elif kode_mata_uang == 'KRW':
         return f"{kode_mata_uang} {angka:,.0f}"
    else:
        return f"{kode_mata_uang} {angka:,.2f}"

#Fungsi Awal (Akun dan Bahasa)
def buat_akun():
    clear_screen()
    print("Silakan masukkan data-data di bawah ini!")
    nama_lengkap = input("Nama Lengkap: ")
    tanggal_lahir = input("Tanggal Lahir (DD/MM/YYYY): ")
    asal_negara = input("Asal Negara: ")

    print("\nPilih Bahasa / Select Language:")
    print("1. Indonesia")
    print("2. English")
    while True:
        try:
            pilihan_bahasa = int(input("Pilihan Anda / Your Choice: "))
            if pilihan_bahasa in [1, 2]:
                bahasa = 'id' if pilihan_bahasa == 1 else 'en'
                break
            else:
                print("Pilihan tidak valid / Invalid choice.")
        except ValueError:
            print("Masukkan angka / Enter a number.")

    TERMS = load_language(bahasa)

    clear_screen()
    print(TERMS['pilih_mata_uang'])
    currencies = ['IDR', 'USD', 'GBP', 'EUR', 'KRW', 'JPY', 'CNY', 'MYR']
    for i, curr in enumerate(currencies):
        print(f"{i+1}. {curr}")
    while True:
        try:
            pilihan_curr = int(input(TERMS['pilihan_anda']))
            if 1 <= pilihan_curr <= len(currencies):
                mata_uang_utama = currencies[pilihan_curr-1]
                break
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

    clear_screen()
    status_pin = False
    while not status_pin:
        pin = input(TERMS['buat_pin_6_digit'])
        if len(pin) != 6 or not pin.isdigit():
            print(TERMS['pin_harus_6_digit'])
            continue
        pin_konfirmasi = input(TERMS['konfirmasi_pin'])
        if pin == pin_konfirmasi:
            status_pin = True
        else:
            print(TERMS['pin_tidak_cocok'])
            time.sleep(2)
            clear_screen()

    clear_screen()
    min_saldo_awal = MIN_SALDO_AWAL_IDR if mata_uang_utama == 'IDR' else MIN_SALDO_AWAL_IDR / KURS_BELI.get(mata_uang_utama, 1)
    min_saldo_awal_str = format_currency(min_saldo_awal, mata_uang_utama)

    while True:
        try:
            saldo_str = input(TERMS['masukkan_saldo_awal'].format(min_saldo_awal_str))
            saldo = float(saldo_str)
            if saldo >= min_saldo_awal:
                break
            else:
                print(TERMS['saldo_awal_kurang'].format(min_saldo_awal_str))
        except ValueError:
            print(TERMS['masukkan_angka_valid'])

    clear_screen()
    typing_effect(TERMS['data_pribadi_anda'])
    typing_effect(f"{TERMS['nama_lengkap']}: {nama_lengkap}")
    typing_effect(f"{TERMS['tanggal_lahir']}: {tanggal_lahir}")
    typing_effect(f"{TERMS['asal_negara']}: {asal_negara}") 
    typing_effect(f"{TERMS['pin']}: {'*' * 6}")
    typing_effect(f"{TERMS['mata_uang_utama']}: {mata_uang_utama}") 
    typing_effect(f"{TERMS['saldo_awal']}: {format_currency(saldo, mata_uang_utama)}")
    time.sleep(4)

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
    return user_data, TERMS

def load_language(lang_code):
    if lang_code == 'id':
        return {
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
            "pilih_pecahan": "PILIH PECAHAN UANG ANDA",
            "pecahan_100k": "1. Pecahan Rp 100.000",
            "pecahan_50k": "2. Pecahan Rp 50.000",
            "ambil_uang_pecahan": "Silakan ambil uang Anda dalam pecahan {}.",
            "ambil_uang_campur": "Silakan ambil uang Anda. (Transaksi ini akan menyertakan pecahan Rp 50.000).",
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
            "mata_uang_utama": "Mata Uang Utama   ",
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
            "pilih_pecahan": "PLEASE SELECT YOUR DENOMINATION",
            "pecahan_100k": "1. Rp 100,000 Bills",
            "pecahan_50k": "2. Rp 50,000 Bills",
            "ambil_uang_pecahan": "Please take your cash in {} bills.",
            "ambil_uang_campur": "Please take your cash. (This transaction will include Rp 50,000 bills).",
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

#Fungsi Menu Utama
def menu_utama_idr(user_data, TERMS):
    pilihan = 0
    while pilihan != 6:
        clear_screen()
        print(TERMS['pilih_menu_transaksi'])
        print(TERMS['menu_info_saldo'])
        print(TERMS['menu_tarik_tunai'])
        print(TERMS['menu_transfer'])
        print(TERMS['menu_pembayaran'])
        print(TERMS['menu_ganti_pin'])
        print(TERMS['menu_selesai'])

        while True:
            try:
                pilihan = int(input(TERMS['masukkan_pilihan_menu']))
                if 1 <= pilihan <= 6:
                    break
                else:
                    print(TERMS['pilihan_tidak_valid'])
            except ValueError:
                print(TERMS['masukkan_angka'])

        lanjut = True
        if pilihan == 1:
            info_saldo_idr(user_data, TERMS)
        elif pilihan == 2:
            user_data = tarik_tunai_idr(user_data, TERMS)
        elif pilihan == 3:
            user_data = transfer_bank_idr(user_data, TERMS)
        elif pilihan == 4:
            user_data = menu_pembayaran_idr(user_data, TERMS)
        elif pilihan == 5:
            user_data = ganti_pin(user_data, TERMS)
        elif pilihan == 6:
            lanjut = False 
            break

        if pilihan != 6:
             lanjut = tanya_lanjut_transaksi(TERMS)
             if not lanjut:
                 pilihan = 6

    return user_data

def menu_utama_non_idr(user_data, TERMS):
    pilihan = 0
    mata_uang = user_data['mata_uang_utama']
    while pilihan != 4:
        clear_screen()
        print(TERMS['menu_utama_non_idr'])
        print(TERMS['menu_info_saldo_non_idr'].format(mata_uang))
        print(TERMS['menu_tarik_tunai_non_idr'])
        print(TERMS['menu_ganti_pin_non_idr'])
        print(TERMS['menu_selesai_non_idr'])

        while True:
            try:
                pilihan = int(input(TERMS['masukkan_pilihan_menu']))
                if 1 <= pilihan <= 4:
                    break
                else:
                    print(TERMS['pilihan_tidak_valid'])
            except ValueError:
                print(TERMS['masukkan_angka'])

        lanjut = True
        if pilihan == 1:
            info_saldo_non_idr(user_data, TERMS)
        elif pilihan == 2:
            user_data = tarik_tunai_non_idr(user_data, TERMS)
        elif pilihan == 3:
            user_data = ganti_pin(user_data, TERMS)
        elif pilihan == 4:
            lanjut = False 
            break

        if pilihan != 4:
             lanjut = tanya_lanjut_transaksi(TERMS)
             if not lanjut:
                 pilihan = 4 

    return user_data

def tanya_lanjut_transaksi(TERMS):
    print("\n" + TERMS['lanjut_transaksi_tanya'])
    print(TERMS['opsi_ya'])
    print(TERMS['opsi_tidak'])
    while True:
        try:
            respon = int(input(TERMS['masukkan_respon']))
            if respon == 1:
                return True
            elif respon == 2:
                return False
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

#Fungsi Detail Transaksi
def info_saldo_idr(user_data, TERMS):
    clear_screen()
    print(TERMS['harap_menunggu'])
    print(TERMS['transaksi_diproses'])
    time.sleep(2)
    clear_screen()
    print(TERMS['saldo_rekening_anda'])
    print(format_currency(user_data['saldo'], 'IDR'))

def info_saldo_non_idr(user_data, TERMS):
    clear_screen()
    print(TERMS['harap_menunggu'])
    print(TERMS['transaksi_diproses'])
    time.sleep(2)
    clear_screen()
    mata_uang = user_data['mata_uang_utama']
    print(TERMS['saldo_rekening_anda'])
    print(format_currency(user_data['saldo'], mata_uang))

    print("\n" + TERMS['saldo_dalam_idr_tanya'])
    print(TERMS['opsi_ya'])
    print(TERMS['opsi_tidak'])
    while True:
        try:
            respon = int(input(TERMS['masukkan_respon']))
            if respon == 1:
                saldo_idr = user_data['saldo'] * KURS_BELI[mata_uang]
                print(f"\n{TERMS['saldo_dalam_idr_label']}: {format_rupiah(saldo_idr)}")
                break
            elif respon == 2:
                break
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

def tarik_tunai_idr(user_data, TERMS):
    clear_screen()
    print(TERMS['menu_penarikan_cepat'])
    print(TERMS['pilih_jumlah_penarikan'])
    print(f"1. {format_rupiah(50000)}")
    print(f"2. {format_rupiah(100000)}")
    print(f"3. {format_rupiah(500000)}")
    print(f"4. {format_rupiah(1000000)}")
    print(TERMS['jumlah_lain'])

    saldo_sebelum = user_data['saldo']
    tarik_nominal = 0
    berhasil = False

    while True:
        try:
            pilihan_tarik = int(input(TERMS['masukkan_respon']))
            if pilihan_tarik == 1:
                tarik_nominal = 50000
                break
            elif pilihan_tarik == 2:
                tarik_nominal = 100000
                break
            elif pilihan_tarik == 3:
                tarik_nominal = 500000
                break
            elif pilihan_tarik == 4:
                tarik_nominal = 1000000
                break
            elif pilihan_tarik == 5:
                while True:
                    clear_screen()
                    print(TERMS['masukkan_jumlah_penarikan_lain'])
                    print(TERMS['dalam_kelipatan'].format(format_rupiah(50000)))
                    print(TERMS['maksimal'].format(format_rupiah(10000000)))
                    try:
                        tunai_lain = int(input(TERMS['jumlah_penarikan_input']))
                        if tunai_lain < 50000:
                            print(TERMS['nominal_terlalu_kecil'])
                        elif tunai_lain > 10000000:
                            print(TERMS['nominal_terlalu_besar'])
                        elif tunai_lain % 50000 != 0:
                            print(TERMS['nominal_tidak_valid'].format(format_rupiah(50000), format_rupiah(50000), format_rupiah(10000000)))
                        else:
                            if user_data['saldo'] >= tunai_lain:
                                if user_data['saldo'] - tunai_lain >= MIN_SISA_SALDO_IDR:
                                    tarik_nominal = tunai_lain
                                    break
                                else:
                                    print(TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR)))
                            else:
                                print(TERMS['saldo_tidak_cukup'])
                        time.sleep(3)
                    except ValueError:
                        print(TERMS['masukkan_angka_valid'])
                        time.sleep(2)
                if tarik_nominal > 0:
                    break
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

    clear_screen()
    print(TERMS['harap_menunggu'])
    print(TERMS['transaksi_diproses'])
    time.sleep(2)
    clear_screen()

    if tarik_nominal > 0:
        if saldo_sebelum >= tarik_nominal and (saldo_sebelum - tarik_nominal >= MIN_SISA_SALDO_IDR):
            user_data['saldo'] -= tarik_nominal
            berhasil = True
            print(TERMS['penarikan_berhasil'].format(format_rupiah(tarik_nominal)))
            print(TERMS['sisa_saldo_anda'].format(format_rupiah(user_data['saldo'])))

            print("\n" + "="*40)
            if tarik_nominal % 100000 == 0:
                print(TERMS['pilih_pecahan'])
                print(TERMS['pecahan_100k'])
                print(TERMS['pecahan_50k'])
                while True:
                    try:
                        pilihan_pecahan = int(input(TERMS['masukkan_respon']))
                        if pilihan_pecahan == 1:
                            print(TERMS['ambil_uang_pecahan'].format(format_rupiah(100000)))
                            break
                        elif pilihan_pecahan == 2:
                            print(TERMS['ambil_uang_pecahan'].format(format_rupiah(50000)))
                            break
                        else:
                            print(TERMS['pilihan_tidak_valid'])
                    except ValueError:
                        print(TERMS['masukkan_angka'])
            else:
                print(TERMS['ambil_uang_campur'])
            
            print("="*40)
            time.sleep(3)

            print("\n" + TERMS['cetak_receipt_tanya'])
            print(TERMS['opsi_ya'])
            print(TERMS['opsi_tidak'])
            while True:
                try:
                    cetak = int(input(TERMS['masukkan_respon']))
                    if cetak == 1:
                        clear_screen()
                        waktu = datetime.now().isoformat(' ', 'seconds')
                        print('---------------------------------------------------')
                        print(TERMS['header_receipt_tarik'])
                        print(TERMS['jumlah_receipt'].format(format_rupiah(tarik_nominal)))
                        print(TERMS['sisa_saldo_receipt'].format(format_rupiah(user_data['saldo'])))
                        print(TERMS['waktu_transaksi_receipt'].format(waktu))
                        print('---------------------------------------------------')
                        break
                    elif cetak == 2:
                        break
                    else:
                        print(TERMS['pilihan_tidak_valid'])
                except ValueError:
                    print(TERMS['masukkan_angka'])
        elif saldo_sebelum < tarik_nominal:
             print(TERMS['saldo_tidak_cukup'])
        else:
             print(TERMS['sisa_saldo_min_tidak_cukup'].format(format_rupiah(MIN_SISA_SALDO_IDR)))
    else:
         pass

    return user_data

def transfer_bank_idr(user_data, TERMS):
    kumpulan_bank = {
        '001': 'BRI', '007': 'MANDIRI', '002': 'BNI', '008': 'BTN',
        '003': 'BCA', '009': 'PERMATA', '004': 'RBS', '010': 'DKI',
        '005': 'CITIBANK', '011': 'BSI', '006': 'MUAMALAT', '012': 'KB BUKOPIN',
    }

    while True:
        clear_screen()
        print(TERMS['header_transfer'])
        print("\n" + TERMS['lihat_kode_bank_tanya'])
        cek_kode_bank = input(TERMS['masukkan_respon']).lower()

        if cek_kode_bank == 'y':
            clear_screen()
            print(TERMS['daftar_kode_bank'])
            banks = list(kumpulan_bank.items())
            half = len(banks) // 2
            for i in range(half):
                print(f"{banks[i][0]}: {banks[i][1]:<15} | {banks[i+half][0]}: {banks[i+half][1]}")
            if len(banks) % 2 != 0:
                 print(f"{banks[-1][0]}: {banks[-1][1]}")
            print("\n" + TERMS['transaksi_dilanjutkan'])
            time.sleep(7)

        clear_screen()
        print(TERMS['header_transfer'])
        print(TERMS['prompt_kode_bank_rek'])
        print(TERMS['ket_kode_bank_rek'])
        print(TERMS['contoh_transfer'])

        rekening_tujuan = input(TERMS['rek_tujuan_input'])
        kode_bank = rekening_tujuan[:3]
        nama_penerima = input(TERMS['nama_penerima_input'])

        if kode_bank not in kumpulan_bank:
            print(f"Kode bank {kode_bank} tidak valid.")
            time.sleep(3)
            if not tanya_lanjut_transaksi(TERMS): return user_data 
            continue

        while True:
            try:
                nominal_transfer = int(input(TERMS['nominal_transfer_input']))
                if nominal_transfer <= 0:
                    print("Nominal harus positif.")
                    continue

                if user_data['saldo'] >= nominal_transfer:
                    break 
                else:
                    print(TERMS['saldo_tidak_cukup'])
                    retry = input("Coba masukkan nominal lain (y/n)? ").lower()
                    if retry != 'y':
                         if not tanya_lanjut_transaksi(TERMS): return user_data 
                         return user_data

            except ValueError:
                print(TERMS['masukkan_angka_valid'])

        clear_screen()
        print(TERMS['konfirmasi_transfer_data'])
        print('---------------------------------------------------')
        print(TERMS['bank_receipt'].format(kumpulan_bank[kode_bank]))
        print(TERMS['tujuan_receipt'].format(rekening_tujuan))
        print(TERMS['penerima_receipt'].format(nama_penerima))
        print(TERMS['jumlah_transfer_receipt'].format(format_rupiah(nominal_transfer)))
        print('---------------------------------------------------')

        konfirmasi = input(TERMS['data_sesuai_tanya']).lower()

        if konfirmasi == 'y':
            clear_screen()
            print(TERMS['harap_menunggu'])
            print(TERMS['transaksi_diproses'])
            time.sleep(2)
            clear_screen()

            user_data['saldo'] -= nominal_transfer
            waktu = datetime.now().isoformat(' ', 'seconds')

            print('------------------------------------------------------')
            typing_effect(TERMS['header_transfer'].split('\n')[0])
            typing_effect(TERMS['bank_receipt'].format(kumpulan_bank[kode_bank]))
            typing_effect(TERMS['tujuan_receipt'].format(rekening_tujuan))
            typing_effect(TERMS['penerima_receipt'].format(nama_penerima))
            typing_effect(TERMS['jumlah_transfer_receipt'].format(format_rupiah(nominal_transfer)))
            typing_effect(TERMS['waktu_transaksi_receipt'].format(waktu))
            print('------------------------------------------------------')
            print('\n' + TERMS['transaksi_selesai'])

            return user_data

        else:
            print("Membatalkan transfer...")
            time.sleep(2)

#Fungsi Pembayaran (IDR)
def menu_pembayaran_idr(user_data, TERMS):
    clear_screen()
    print('----------------------SILAHKAN PILIH----------------------')
    print(TERMS['header_pembayaran'])
    print(TERMS['pilih_pembayaran'])
    print(TERMS['pilih_listrik'])
    print(TERMS['pilih_air'])

    while True:
        try:
            pilih_pembayaran = int(input(TERMS['masukkan_respon']))
            if pilih_pembayaran == 1:
                return pembayaran_telepon(user_data, TERMS)
            elif pilih_pembayaran == 2:
                return pembayaran_listrik(user_data, TERMS)
            elif pilih_pembayaran == 3:
                return pembayaran_air(user_data, TERMS)
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

def pembayaran_telepon(user_data, TERMS):
    clear_screen()
    print(TERMS['prompt_input_telepon'])
    nomor_hp = input(TERMS['nomor_telepon_input'])

    clear_screen()
    daftar_nominal = {
        '1': 20000, '2': 30000, '3': 50000, '4': 100000, 
        '5': 150000, '6': 200000, '7': 300000
    }
    print(TERMS['pilih_nominal_pulsa'])
    for key, value in daftar_nominal.items():
        print(f"{key}. {format_rupiah(value)}")
    print(TERMS['pulsa_lainnya'])

    admin_bank = 1000
    nominal_pilihan = 0

    while True:
        pilihan_nominal_str = input(TERMS['pilih_nominal_isi_ulang'])
        if pilihan_nominal_str in daftar_nominal:
            nominal_pilihan = daftar_nominal[pilihan_nominal_str]
            break
        elif pilihan_nominal_str == '8':
             while True:
                 try:
                     nominal_lain = int(input(TERMS['masukkan_nominal_lain']))
                     if nominal_lain > 0:
                         nominal_pilihan = nominal_lain
                         break
                     else:
                         print("Nominal harus positif.")
                 except ValueError:
                     print(TERMS['masukkan_angka_valid'])
             break
        else:
            print(TERMS['pilihan_tidak_valid'])

    total_bayar = nominal_pilihan + admin_bank

    clear_screen()
    print(TERMS['header_konfirmasi_pulsa'])
    print(TERMS['nomor_hp_receipt'].format(nomor_hp))
    print(TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)))
    print(TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)))
    print(TERMS['total_receipt'].format(format_rupiah(total_bayar)))
    print('----------------------------------------------------------------------')

    if user_data['saldo'] < total_bayar:
        print("\n" + TERMS['saldo_tidak_cukup'])
        time.sleep(3)
        return user_data

    konfirmasi = input(TERMS['proses_transaksi_tanya']).lower()

    if konfirmasi == 'y':
        clear_screen()
        print(TERMS['harap_menunggu'])
        print(TERMS['transaksi_diproses'])
        time.sleep(2)
        clear_screen()

        user_data['saldo'] -= total_bayar
        print(TERMS['transaksi_berhasil'])
        print(TERMS['berikut_struk'])
        time.sleep(2)
        clear_screen()

        waktu = datetime.now().isoformat(' ', 'seconds')
        print(TERMS['header_struk_bank'])
        print(TERMS['header_struk_pulsa'])
        typing_effect(TERMS['nomor_hp_receipt'].format(nomor_hp))
        typing_effect(TERMS['voucher_reff_receipt'].format(random.randint(10000000000, 99999999999)))
        typing_effect(TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)))
        typing_effect(TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)))
        typing_effect(TERMS['total_receipt'].format(format_rupiah(total_bayar)))
        typing_effect(TERMS['waktu_transaksi_receipt'].format(waktu))
        print(TERMS['footer_struk_1'])
        print(TERMS['footer_struk_pulsa_1'])
        print(TERMS['footer_struk_sah'])

    else:
        print("Transaksi dibatalkan.")
        time.sleep(2)

    return user_data

def pembayaran_listrik(user_data, TERMS):
    clear_screen()
    print(TERMS['prompt_input_listrik'])
    nomor_meter = input("Nomor Meter: ")
    id_pelanggan = random.randint(100000000000, 999999999999)

    clear_screen()
    print(TERMS['harap_menunggu'])
    print(TERMS['transaksi_diproses'])
    time.sleep(1)
    clear_screen()

    print(TERMS['header_konfirmasi_listrik'])
    print(TERMS['nomor_meter_receipt'].format(nomor_meter))
    print(TERMS['idpel_receipt'].format(id_pelanggan))
    print(TERMS['nama_receipt'].format(user_data['nama_lengkap']))
    print(TERMS['tarif_daya_receipt'])
    print("-" * 70)

    daftar_nominal = {
        '1': 20000, '2': 50000, '3': 100000, '4': 200000,
        '5': 500000, '6': 1000000, '7': 5000000, '8': 10000000
    }
    print(TERMS['pilih_nominal_token'])
    for key, value in daftar_nominal.items():
        print(f"{key}. {format_rupiah(value)}")
    print(TERMS['admin_rp_1000'])

    admin_bank = 1000
    nominal_pilihan = 0

    while True:
        pilihan_nominal_str = input(TERMS['pilih_nominal_isi_ulang'])
        if pilihan_nominal_str in daftar_nominal:
            nominal_pilihan = daftar_nominal[pilihan_nominal_str]
            break
        else:
            print(TERMS['pilihan_tidak_valid'])

    total_bayar = nominal_pilihan + admin_bank

    clear_screen()
    print(TERMS['header_konfirmasi_listrik'])
    print(TERMS['nomor_meter_receipt'].format(nomor_meter))
    print(TERMS['idpel_receipt'].format(id_pelanggan))
    print(TERMS['nama_receipt'].format(user_data['nama_lengkap']))
    print(TERMS['tarif_daya_receipt'])
    print(TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)))
    print(TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)))
    print(TERMS['total_receipt'].format(format_rupiah(total_bayar)))
    print("-" * 70)

    if user_data['saldo'] < total_bayar:
        print("\n" + TERMS['saldo_tidak_cukup'])
        time.sleep(3)
        return user_data 

    konfirmasi = input(TERMS['proses_transaksi_tanya']).lower()

    if konfirmasi == 'y':
        clear_screen()
        print(TERMS['harap_menunggu'])
        print(TERMS['transaksi_diproses'])
        time.sleep(2)
        clear_screen()

        user_data['saldo'] -= total_bayar
        print(TERMS['transaksi_berhasil'])
        print(TERMS['berikut_struk'])
        time.sleep(2)
        clear_screen()

        waktu = datetime.now().isoformat(' ', 'seconds')
        token = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        print(TERMS['header_struk_bank'])
        print(TERMS['header_struk_listrik'])
        typing_effect(TERMS['nomor_meter_receipt'].format(nomor_meter))
        typing_effect(TERMS['idpel_receipt'].format(id_pelanggan))
        typing_effect(TERMS['nama_receipt'].format(user_data['nama_lengkap']))
        typing_effect(TERMS['tarif_daya_receipt'])
        typing_effect(TERMS['jumlah_pulsa_receipt'].format(format_rupiah(nominal_pilihan)))
        typing_effect(TERMS['biaya_admin_receipt'].format(format_rupiah(admin_bank)))
        typing_effect(TERMS['total_receipt'].format(format_rupiah(total_bayar)))
        typing_effect(TERMS['stroom_token_receipt'].format(token))
        typing_effect(TERMS['waktu_transaksi_receipt'].format(waktu))
        print(TERMS['footer_struk_1'])
        print(TERMS['footer_struk_listrik_1'])
        print(TERMS['footer_struk_sah'])

    else:
        print("Transaksi dibatalkan.")
        time.sleep(2)

    return user_data

def pembayaran_air(user_data, TERMS):
    kode_perusahaan_map = {
        "401": 'PAM KOTA BOGOR', "406": 'PAM KOTA CIREBON',
        "402": 'PAM KOTA CIANJUR', "407": 'PAM KOTA SUBANG',
        "403": 'PAM KOTA KUNINGAN', "408": 'PAM KOTA CILEGON',
        "404": 'PAM KOTA SUMEDANG', "409": 'PAM KOTA DEPOK',
        "405": 'PAM KOTA SUKABUMI', "410": 'PAM KOTA BANDUNG',
    }

    while True:
        clear_screen()
        print(TERMS['prompt_input_air'])
        print(TERMS['contoh_air'])
        print("\n" + TERMS['lihat_kode_pdam_tanya'])
        lihat_kode = input(TERMS['masukkan_respon']).lower()

        if lihat_kode == 'y':
            clear_screen()
            print(TERMS['daftar_kode_pdam'])
            for kode, nama in kode_perusahaan_map.items():
                print(f"{nama:<25} : {kode}")
            print("\n" + TERMS['transaksi_dilanjutkan'])
            time.sleep(7)
           
        clear_screen()
        print(TERMS['prompt_input_air'])
        print(TERMS['contoh_air'])
        nomor_pelanggan_full = input(TERMS['nomor_pelanggan_input'])

        if len(nomor_pelanggan_full) < 4 or not nomor_pelanggan_full.isdigit():
             print("Format input tidak valid.")
             time.sleep(2)
             continue 

        kode_input = nomor_pelanggan_full[:3]
        nomor_saja = nomor_pelanggan_full[3:]

        if kode_input not in kode_perusahaan_map:
            print(f"Kode perusahaan {kode_input} tidak dikenal.")
            time.sleep(3)
            continue 

        clear_screen()
        print(TERMS['harap_menunggu'])
        print(TERMS['transaksi_diproses'])
        time.sleep(2)
        clear_screen()

        nama_perusahaan = kode_perusahaan_map[kode_input]

        tagihan = random.randint(50000, 500000) 
        biaya_admin = 2500
        total_bayar = tagihan + biaya_admin

        print(TERMS['header_konfirmasi_air'])
        print(TERMS['tagihan_receipt'].format(nama_perusahaan))
        print(TERMS['no_pelanggan_receipt'].format(nomor_saja))
        print(TERMS['nama_receipt'].format(user_data['nama_lengkap']))
        print(f"Tagihan           : {format_rupiah(tagihan)}")
        print(TERMS['biaya_admin_receipt'].format(format_rupiah(biaya_admin)))
        print(TERMS['total_bayar_receipt'].format(format_rupiah(total_bayar)))
        print('------------------------------------------------------------')

        konfirmasi = input(TERMS['lanjut_pembayaran_tanya']).lower()

        if konfirmasi == 'y':
            if user_data['saldo'] >= total_bayar:
                clear_screen()
                print(TERMS['harap_menunggu'])
                print(TERMS['transaksi_diproses'])
                time.sleep(2)
                clear_screen()

                user_data['saldo'] -= total_bayar
                print(TERMS['transaksi_berhasil'])
                print(TERMS['berikut_struk'])
                time.sleep(2)
                clear_screen()

                waktu = datetime.now().isoformat(' ', 'seconds')
                print(TERMS['header_struk_bank'])
                print(TERMS['header_struk_air'])
                typing_effect(f"Perusahaan        : {nama_perusahaan}")
                typing_effect(TERMS['no_pelanggan_receipt'].format(nomor_saja))
                typing_effect(TERMS['nama_receipt'].format(user_data['nama_lengkap']))
                typing_effect(f"Tagihan           : {format_rupiah(tagihan)}")
                typing_effect(TERMS['biaya_admin_receipt'].format(format_rupiah(biaya_admin)))
                typing_effect(TERMS['total_bayar_receipt'].format(format_rupiah(total_bayar)))
                typing_effect(TERMS['waktu_transaksi_receipt'].format(waktu))
                print(TERMS['footer_struk_1'])
                print(TERMS['footer_struk_air_1'])
                print(TERMS['footer_struk_sah'])

                return user_data 

            else:
                print(TERMS['saldo_tidak_cukup'])
                time.sleep(3)
                
                return user_data
        else:
            print("Pembayaran dibatalkan.")
            time.sleep(2)
            
            return user_data

#Fungsi Ganti PIN
def ganti_pin(user_data, TERMS):
    clear_screen()
    while True: 
        pin_lama = input(TERMS['masukkan_pin_lama'])
        if pin_lama == user_data['pin']:
            break
        else:
            print(TERMS['pin_lama_salah'])
            time.sleep(2)
            clear_screen()

    while True:
        pin_baru = input(TERMS['masukkan_pin_baru'])
        if len(pin_baru) != 6 or not pin_baru.isdigit():
             print(TERMS['pin_baru_harus_6_digit'])
             continue

        pin_konfirmasi = input(TERMS['konfirmasi_pin_baru'])
        if pin_baru == pin_konfirmasi:
            user_data['pin'] = pin_baru
            clear_screen()
            print(TERMS['pin_berhasil_diubah'])
            return user_data
        else:
            print(TERMS['pin_baru_tidak_cocok'])
            time.sleep(2)
            clear_screen()
            print(TERMS['pin_lama_salah'])
            clear_screen()
            print(TERMS['pin_baru_tidak_cocok'] + " Silakan ulangi.")

#Fungsi Tarik Tunai Non-IDR
def tarik_tunai_non_idr(user_data, TERMS):
    clear_screen()
    mata_uang_akun = user_data['mata_uang_utama']

    print(TERMS['kurs_beli_terkini'])
    for curr, rate in KURS_BELI.items():
        if curr != 'IDR':
            print(f"1 {curr} = {format_rupiah(rate)}")
    print("-" * 30)
    time.sleep(4)

    currency_data = {
        'USD': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 3.02, 'max_amount_curr_lain': 603.5, 'step_curr_lain': 3.02},
        'EUR': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 2.59, 'max_amount_curr_lain': 517.87, 'step_curr_lain': 2.59},
        'GBP': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 2.25, 'max_amount_curr_lain': 449.44, 'step_curr_lain': 2.25},
        'KRW': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 4291.85, 'max_amount_curr_lain': 858369.1, 'step_curr_lain': 4291.85},
        'JPY': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 455.17, 'max_amount_curr_lain': 91033.23, 'step_curr_lain': 455.17},
        'CNY': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 21.51, 'max_amount_curr_lain': 4301.08, 'step_curr_lain': 21.51},
        'MYR': {'min_equiv_idr': 50000, 'max_equiv_idr_lain': 10000000, 'kelipatan_idr': 50000, 'min_amount_curr': 12.725, 'max_amount_curr_lain': 2544.53, 'step_curr_lain': 12.725},
    }

    if mata_uang_akun not in currency_data:
        print(f"Penarikan tunai belum didukung untuk mata uang {mata_uang_akun}.")
        time.sleep(3)
        return user_data

    data = currency_data[mata_uang_akun]
    kurs = KURS_BELI[mata_uang_akun]

    clear_screen()
    print(TERMS['penarikan_non_idr_header'].format(mata_uang_akun))
    print(TERMS['penarikan_non_idr_prompt'])
    preset_idr = [50000, 100000, 500000, 1000000]
    preset_curr = {}
    for i, idr_val in enumerate(preset_idr):
        curr_val = idr_val / kurs
        preset_curr[str(i+1)] = curr_val
        print(f"{i+1}. {format_rupiah(idr_val)} ({format_currency(curr_val, mata_uang_akun)})")
    print(TERMS['penarikan_non_idr_lainnya'].format(mata_uang_akun))

    saldo_sebelum = user_data['saldo']
    tarik_nominal_curr = 0.0
    nominal_idr_ekuivalen = 0.0
    berhasil = False

    while True:
        try:
            pilihan_str = input(TERMS['masukkan_respon'])
            if pilihan_str in preset_curr:
                tarik_nominal_curr = preset_curr[pilihan_str]
                nominal_idr_ekuivalen = tarik_nominal_curr * kurs
                break
            elif pilihan_str == '5': 
                while True:
                    clear_screen()
                    print(TERMS['masukkan_jumlah_lain_curr'].format(mata_uang_akun))
    
                    min_lain = data['min_amount_curr']
                    max_lain = data['max_amount_curr_lain']
                    step_lain = data['step_curr_lain']
                    print(f"(Min: {format_currency(min_lain, mata_uang_akun)}, Max: {format_currency(max_lain, mata_uang_akun)}, Step: {format_currency(step_lain, mata_uang_akun)})")

                    try:
                        input_str = input(TERMS['jumlah_penarikan_curr_input'].format(mata_uang_akun))
                        tunai_lain_curr = float(input_str)

                        tolerance = 1e-9
                        is_multiple = abs(round(tunai_lain_curr / step_lain) - (tunai_lain_curr / step_lain)) < tolerance

                        if tunai_lain_curr < min_lain - tolerance:
                            print(TERMS['nominal_terlalu_kecil'])
                        elif tunai_lain_curr > max_lain + tolerance:
                            print(TERMS['nominal_terlalu_besar'])
                        elif not is_multiple:
                             print(TERMS['nominal_tidak_valid_curr'].format(
                                 format_currency(step_lain, mata_uang_akun),
                                 format_currency(min_lain, mata_uang_akun),
                                 format_currency(max_lain, mata_uang_akun)
                             ))
                        else:
                            if user_data['saldo'] >= tunai_lain_curr - tolerance:
                                tarik_nominal_curr = tunai_lain_curr
                                nominal_idr_ekuivalen = tarik_nominal_curr * kurs
                                break
                            else:
                                print(TERMS['saldo_tidak_cukup'])
                        time.sleep(3)
                    except ValueError:
                        print(TERMS['masukkan_angka_valid'])
                        time.sleep(2)
                if tarik_nominal_curr > 0: 
                    break
            else:
                print(TERMS['pilihan_tidak_valid'])
        except ValueError:
            print(TERMS['masukkan_angka'])

    clear_screen()
    print(TERMS['harap_menunggu'])
    print(TERMS['transaksi_diproses'])
    time.sleep(2)
    clear_screen()

    if tarik_nominal_curr > 0:
        tolerance = 1e-9
        if saldo_sebelum >= tarik_nominal_curr - tolerance:
            user_data['saldo'] -= tarik_nominal_curr
            berhasil = True
            print(TERMS['penarikan_berhasil_curr'].format(
                format_currency(tarik_nominal_curr, mata_uang_akun),
                format_rupiah(nominal_idr_ekuivalen)
            ))
            print(TERMS['sisa_saldo_anda'].format(format_currency(user_data['saldo'], mata_uang_akun)))
            print("\n" + "="*40)
            nominal_idr_bulat = round(nominal_idr_ekuivalen)

            if nominal_idr_bulat % 100000 == 0:
                print(TERMS['pilih_pecahan'])
                print(TERMS['pecahan_100k'])
                print(TERMS['pecahan_50k'])
                while True:
                    try:
                        pilihan_pecahan = int(input(TERMS['masukkan_respon']))
                        if pilihan_pecahan == 1:
                            print(TERMS['ambil_uang_pecahan'].format(format_rupiah(100000)))
                            break
                        elif pilihan_pecahan == 2:
                            print(TERMS['ambil_uang_pecahan'].format(format_rupiah(50000)))
                            break
                        else:
                            print(TERMS['pilihan_tidak_valid'])
                    except ValueError:
                        print(TERMS['masukkan_angka'])
            else:
                print(TERMS['ambil_uang_campur'])
            
            print("="*40)
            time.sleep(3)

            print("\n" + TERMS['cetak_receipt_tanya'])
            print(TERMS['opsi_ya'])
            print(TERMS['opsi_tidak'])
            while True:
                try:
                    cetak = int(input(TERMS['masukkan_respon']))
                    if cetak == 1:
                        clear_screen()
                        waktu = datetime.now().isoformat(' ', 'seconds')
                        print('---------------------------------------------------')
                        print(TERMS['header_receipt_tarik'] + f" ({mata_uang_akun})")
                        print(TERMS['jumlah_receipt_non_idr'].format(
                            format_currency(tarik_nominal_curr, mata_uang_akun),
                            format_rupiah(nominal_idr_ekuivalen)
                        ))
                        print(TERMS['sisa_saldo_receipt'].format(format_currency(user_data['saldo'], mata_uang_akun)))
                        print(TERMS['waktu_transaksi_receipt'].format(waktu))
                        print('---------------------------------------------------')
                        break
                    elif cetak == 2:
                        break
                    else:
                        print(TERMS['pilihan_tidak_valid'])
                except ValueError:
                    print(TERMS['masukkan_angka'])
        else:
            print(TERMS['saldo_tidak_cukup'])

    return user_data

#Fungsi Animasi Kartu
def animasi_masukkan_kartu(TERMS):
    clear_screen()
    print(TERMS['masukkan_kartu_prompt'])
    input(TERMS['tekan_enter_kartu'])

    card = [
        "|=============|",
        "|             |",
        "|             |",
        "|    KARTU    |",
        "|     ATM     |",
        "|             |",
        "|             |",
        "|=============|"
    ]
    for i in range(len(card), 0, -1):
        clear_screen()
        for line in card[-i:]:
            print(line)
        time.sleep(0.2)
    clear_screen()
    print(TERMS['kartu_berhasil'])
    time.sleep(2)

def animasi_keluarkan_kartu(TERMS):
    clear_screen()
    print(TERMS['ambil_kartu'])
    time.sleep(0.5)
    card = [
        "|=============|",
        "|             |",
        "|             |",
        "|    KARTU    |",
        "|     ATM     |",
        "|             |",
        "|             |",
        "|=============|"
    ]
    for i in range(len(card)):
        clear_screen()
        print(TERMS['ambil_kartu'])
        for line in card[-(i + 1):]:
            print(line)
        time.sleep(0.2)

    clear_screen()
    print(TERMS['ambil_kartu'])
    print("\n" + TERMS['terima_kasih'])
    time.sleep(3)

#Program Utama

if __name__ == "__main__":
    user_data, TERMS = buat_akun()

    animasi_masukkan_kartu(TERMS)

    clear_screen()
    while user_data['percobaan_pin'] < MAKS_PERCOBAAN_PIN and not user_data['diblokir']:
        pin_masuk = input(TERMS['masukkan_pin'])
        if pin_masuk == user_data['pin']:
            print(TERMS['anda_berhasil_masuk'])
            time.sleep(1)
            break 
        else:
            user_data['percobaan_pin'] += 1
            sisa_percobaan = MAKS_PERCOBAAN_PIN - user_data['percobaan_pin']
            if sisa_percobaan > 0:
                print(TERMS['pin_salah_sisa'].format(sisa_percobaan))
            else:
                user_data['diblokir'] = True
                clear_screen()
                print(TERMS['akun_dikunci']) 
                print(TERMS['kartu_diblokir'])
                time.sleep(3)
                animasi_keluarkan_kartu(TERMS)
                exit()

    if not user_data['diblokir']:
        if user_data['mata_uang_utama'] == 'IDR':
            user_data = menu_utama_idr(user_data, TERMS)
        else:
            user_data = menu_utama_non_idr(user_data, TERMS)

        animasi_keluarkan_kartu(TERMS)