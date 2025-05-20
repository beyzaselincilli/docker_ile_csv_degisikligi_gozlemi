import pandas as pd
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import hashlib

# CSV dosyasının yolu
CSV_PATH = os.path.join('data', 'data.csv')

class CSVHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_hash = None
        self.last_content = None
        print(f"CSV dosyası izleniyor: {os.path.abspath(CSV_PATH)}")

    def get_file_hash(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return None

    def on_modified(self, event):
        if event.src_path.endswith('data.csv'):
            print(f"\nDeğişiklik algılandı: {event.src_path}")
            current_hash = self.get_file_hash(event.src_path)
            
            if current_hash != self.last_hash:
                print("\nCSV dosyası değişti! Yeni içerik:")
                try:
                    df = pd.read_csv(event.src_path)
                    print("\nGüncel CSV İçeriği:")
                    print(df)
                    print("\n" + "="*50)
                    
                    # Değişiklikleri göster
                    if self.last_content is not None:
                        print("\nDeğişiklikler:")
                        if len(df) > len(self.last_content):
                            print("Yeni satırlar eklendi!")
                        elif len(df) < len(self.last_content):
                            print("Satırlar silindi!")
                        
                        # Güncellenen satırları kontrol et
                        for idx, row in df.iterrows():
                            if idx < len(self.last_content):
                                if not row.equals(self.last_content.iloc[idx]):
                                    print(f"\nSatır {idx+1} güncellendi:")
                                    print("Eski:", self.last_content.iloc[idx])
                                    print("Yeni:", row)
                    
                    self.last_content = df.copy()
                    self.last_hash = current_hash
                except Exception as e:
                    print(f"CSV okuma hatası: {e}")

def read_csv():
    try:
        df = pd.read_csv(CSV_PATH)
        print("\nCSV Dosyası İçeriği:")
        print(df)
        print("\n" + "="*50)
        return df
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return None

if __name__ == "__main__":
    print("CSV dosyası izleniyor...")
    
    # CSV dosyasının varlığını kontrol et
    if not os.path.exists(CSV_PATH):
        print(f"HATA: {CSV_PATH} dosyası bulunamadı!")
        print(f"Lütfen {os.path.abspath('data')} klasöründe data.csv dosyasının olduğundan emin olun.")
        exit(1)
    
    initial_df = read_csv()
    
    event_handler = CSVHandler()
    if initial_df is not None:
        event_handler.last_content = initial_df
        event_handler.last_hash = event_handler.get_file_hash(CSV_PATH)
    
    observer = Observer()
    observer.schedule(event_handler, path='data', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join() 