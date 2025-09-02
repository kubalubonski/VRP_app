import csv
import requests
import time
import sys

# Konfiguracja
INPUT_CSV = 'wwwroot/dane_wejsciowe.csv'  # Plik wejściowy
OUTPUT_CSV = 'wwwroot/dane_wejsciowe_geocoded.csv'  # Plik wyjściowy
LOG_FILE = 'Logs/log_python.txt'
API_URL = 'https://nominatim.openstreetmap.org/search'
USER_AGENT = 'OptymalizacjaTrasMagisterska/1.0'
SLEEP_BETWEEN_REQUESTS = 1 #żeby nie przekroczyć limitów API

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log(f"[PYTHON][GEOCODE][START] Geokodowanie adresów: {INPUT_CSV} -> {OUTPUT_CSV}")

# Funkcja do pobierania współrzędnych z Nominatim
def geocode_address(ulica, numer, miasto, kod_pocztowy):
    address = f"{ulica} {numer}, {miasto}, {kod_pocztowy}"
    log(f"[INFO] Geokoduję: {address}")
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(API_URL, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            log(f"[OK] {address} -> {data[0]['lat']}, {data[0]['lon']}")
            return data[0]['lat'], data[0]['lon']
        else:
            log(f"[WARN] Brak wyników dla: {address}")
    else:
        log(f"[ERROR] Błąd API dla: {address} ({response.status_code})")
    return '', ''

log("[INFO] Wczytuję dane wejściowe...")
with open(INPUT_CSV, newline='', encoding='utf-8') as infile, open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    typ_key = 'Typ'
    if reader.fieldnames and reader.fieldnames[0].startswith('\ufeff'):
        typ_key = reader.fieldnames[0]
    fieldnames = reader.fieldnames + ['Lat', 'Lon']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        if typ_key not in row:
            log(f"[ERROR] Brak klucza '{typ_key}' w wierszu: {row}")
            continue
        lat, lon = '', ''
        if row[typ_key] in ['PunktDostawy', 'Magazyn']:
            lat, lon = geocode_address(row['Ulica'], row['Numer'], row['Miasto'], row['KodPocztowy'])
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        row['Lat'] = lat
        row['Lon'] = lon
        writer.writerow(row)
        log(f"[INFO] Zapisano wiersz: {row}")
log(f"[END] Geokodowanie zakończone. Wynik zapisano do {OUTPUT_CSV}")
