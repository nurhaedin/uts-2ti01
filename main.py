import mysql.connector
import pandas as pd
from datetime import datetime

class ZakatManager:
    def __init__(self):
        self.connection = self.create_connection()
        
    def create_connection(self):
        """Create a connection to the MySQL database"""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="zakat"
            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()

    def add_zakat(self, nama, jenis_zakat, jumlah, tanggal):
        """Add new zakat data"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO zakat_data (nama, jenis_zakat, jumlah, tanggal) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal))
            self.connection.commit()
            print("Data zakat berhasil ditambahkan.")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def update_zakat(self, id, nama, jenis_zakat, jumlah, tanggal):
        """Update existing zakat data"""
        try:
            cursor = self.connection.cursor()
            query = """UPDATE zakat_data 
                       SET nama = %s, jenis_zakat = %s, jumlah = %s, tanggal = %s 
                       WHERE id = %s"""
            cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal, id))
            self.connection.commit()
            print("Data zakat berhasil diperbarui.")
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()

    def delete_zakat(self, id):
        """Delete zakat data"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM zakat_data WHERE id = %s"
            cursor.execute(query, (id,))
            self.connection.commit()
            print("Data zakat berhasil dihapus.")
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()

    def add_beras(self, nama_beras, harga_per_kg):
        """Add new rice type to master data"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO master_beras (nama_beras, harga_per_kg) VALUES (%s, %s)"
            cursor.execute(query, (nama_beras, harga_per_kg))
            self.connection.commit()
            print("Data beras berhasil ditambahkan.")
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()

    def view_master_beras(self):
        """View all rice types in master data"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM master_beras"
            cursor.execute(query)
            result = cursor.fetchall()
            
            if not result:
                print("Tidak ada data beras.")
                return []
                
            print("\nMaster Data Beras:")
            for row in result:
                print(f"ID: {row['id']}, Nama Beras: {row['nama_beras']}, Harga per Kg: Rp{row['harga_per_kg']:,.2f}")
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def add_transaksi_zakat(self, id_zakat, id_beras, jumlah_beras, tanggal):
    """Add new zakat transaction (rice distribution)"""
    try:
        cursor = self.connection.cursor()
        
        # Check if zakat data exists
        cursor.execute("SELECT 1 FROM zakat_data WHERE id = %s", (id_zakat,))
        if not cursor.fetchone():
            print("Error: ID zakat tidak ditemukan.")
            return False
            
        # Check if rice type exists
        cursor.execute("SELECT harga_per_kg FROM master_beras WHERE id = %s", (id_beras,))
        result = cursor.fetchone()
        if not result:
            print("Error: ID beras tidak ditemukan.")
            return False
            
        harga_per_kg = float(result[0])  # Convert Decimal to float
        total_harga = harga_per_kg * jumlah_beras
        
        query = """INSERT INTO transaksi_zakat (id_zakat, id_beras, jumlah_beras, total_harga, tanggal) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (id_zakat, id_beras, jumlah_beras, total_harga, tanggal))
        self.connection.commit()
        print("Transaksi zakat berhasil ditambahkan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()

    def view_transaksi_zakat(self):
        """View all zakat transactions"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """SELECT tz.id, z.nama, z.jenis_zakat, m.nama_beras, 
                      tz.jumlah_beras, tz.total_harga, tz.tanggal
                      FROM transaksi_zakat tz
                      JOIN zakat_data z ON tz.id_zakat = z.id
                      JOIN master_beras m ON tz.id_beras = m.id"""
            cursor.execute(query)
            result = cursor.fetchall()
            
            if not result:
                print("Tidak ada data transaksi zakat.")
                return []
                
            print("\nTransaksi Zakat:")
            for row in result:
                print(f"ID: {row['id']}, Nama: {row['nama']}, Jenis: {row['jenis_zakat']}")
                print(f"Beras: {row['nama_beras']}, Jumlah: {row['jumlah_beras']}kg")
                print(f"Total Harga: Rp{row['total_harga']:,.2f}, Tanggal: {row['tanggal']}\n")
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def export_to_excel(self):
        """Export zakat data to Excel file"""
        try:
            query = "SELECT * FROM zakat_data"
            zakat_data = pd.read_sql(query, self.connection)
            
            # Format the filename with current date
            today = datetime.now().strftime("%Y%m%d")
            filename = f"data_zakat_{today}.xlsx"
            
            zakat_data.to_excel(filename, index=False)
            print(f"Data zakat berhasil diekspor ke dalam file '{filename}'")
            return True
        except Exception as e:
            print(f"Error saat mengekspor data: {e}")
            return False

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def input_float(prompt):
    """Get valid float input from user"""
    while True:
        try:
            value = input(prompt)
            # Replace comma with dot if user accidentally uses comma
            value = value.replace(',', '.')
            return float(value)
        except ValueError:
            print("Masukkan angka yang valid (contoh: 2 atau 2.5).")

def input_int(prompt):
    """Get valid integer input from user"""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Masukkan bilangan bulat yang valid.")

def main():
    manager = ZakatManager()
    
    while True:
        print("\n=== Sistem Manajemen Zakat ===")
        print("1. Kelola Data Zakat")
        print("2. Kelola Master Beras")
        print("3. Kelola Transaksi Zakat")
        print("4. Ekspor Data")
        print("5. Keluar")
        
        choice = input("Pilih menu utama (1-5): ")
        
        if choice == "1":
            # Zakat Data Management
            while True:
                print("\nMenu Kelola Data Zakat:")
                print("1. Tambah Data Zakat")
                print("2. Edit Data Zakat")
                print("3. Hapus Data Zakat")
                print("4. Kembali ke Menu Utama")
                
                sub_choice = input("Pilih opsi (1-4): ")
                
                if sub_choice == "1":
                    nama = input("Masukkan nama: ")
                    jenis_zakat = input("Masukkan jenis zakat: ")
                    jumlah = input_float("Masukkan jumlah zakat: ")
                    tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
                    while not validate_date(tanggal):
                        print("Format tanggal salah. Gunakan format YYYY-MM-DD.")
                        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
                    manager.add_zakat(nama, jenis_zakat, jumlah, tanggal)
                
                elif sub_choice == "2":
                    id_zakat = input_int("Masukkan ID zakat yang ingin diubah: ")
                    nama = input("Masukkan nama baru: ")
                    jenis_zakat = input("Masukkan jenis zakat baru: ")
                    jumlah = input_float("Masukkan jumlah zakat baru: ")
                    tanggal = input("Masukkan tanggal baru (YYYY-MM-DD): ")
                    while not validate_date(tanggal):
                        print("Format tanggal salah. Gunakan format YYYY-MM-DD.")
                        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
                    manager.update_zakat(id_zakat, nama, jenis_zakat, jumlah, tanggal)
                
                elif sub_choice == "3":
                    id_zakat = input_int("Masukkan ID zakat yang ingin dihapus: ")
                    confirm = input(f"Yakin ingin menghapus data zakat ID {id_zakat}? (y/n): ")
                    if confirm.lower() == 'y':
                        manager.delete_zakat(id_zakat)
                
                elif sub_choice == "4":
                    break
                else:
                    print("Pilihan tidak valid.")
        
        elif choice == "2":
            # Rice Master Data Management
            while True:
                print("\nMenu Kelola Master Beras:")
                print("1. Tambah Jenis Beras")
                print("2. Lihat Daftar Beras")
                print("3. Kembali ke Menu Utama")
                
                sub_choice = input("Pilih opsi (1-3): ")
                
                if sub_choice == "1":
                    nama_beras = input("Masukkan nama jenis beras: ")
                    harga = input_float("Masukkan harga per kg: ")
                    manager.add_beras(nama_beras, harga)
                
                elif sub_choice == "2":
                    manager.view_master_beras()
                
                elif sub_choice == "3":
                    break
                else:
                    print("Pilihan tidak valid.")
        
        elif choice == "3":
            # Zakat Transaction Management
            while True:
                print("\nMenu Kelola Transaksi Zakat:")
                print("1. Tambah Transaksi")
                print("2. Lihat Transaksi")
                print("3. Kembali ke Menu Utama")
                
                sub_choice = input("Pilih opsi (1-3): ")
                
                if sub_choice == "1":
                    id_zakat = input_int("Masukkan ID zakat: ")
                    manager.view_master_beras()
                    id_beras = input_int("Masukkan ID beras: ")
                    jumlah_beras = input_float("Masukkan jumlah beras (kg): ")
                    tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
                    while not validate_date(tanggal):
                        print("Format tanggal salah. Gunakan format YYYY-MM-DD.")
                        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
                    manager.add_transaksi_zakat(id_zakat, id_beras, jumlah_beras, tanggal)
                
                elif sub_choice == "2":
                    manager.view_transaksi_zakat()
                
                elif sub_choice == "3":
                    break
                else:
                    print("Pilihan tidak valid.")
        
        elif choice == "4":
            # Data Export
            print("\nMenu Ekspor Data:")
            confirm = input("Ekspor data zakat ke Excel? (y/n): ")
            if confirm.lower() == 'y':
                manager.export_to_excel()
        
        elif choice == "5":
            print("Keluar dari program.")
            manager.close_connection()
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()