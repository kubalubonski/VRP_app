import csv
import requests
import time
import sys

# Konfiguracja
INPUT_CSV = 'wwwroot/dane_wejsciowe_geocoded.csv'  # Plik z współrzędnymi
OUTPUT_CSV = 'wwwroot/czasy_przejazdu.csv'  # Wynikowy plik z czasami przejazdu
LOG_FILE = 'Logs/log_python.txt'
ORS_API_URL = 'https://api.openrouteservice.org/v2/directions/driving-car'
ORS_API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImU3M2E5OTRmZGUxYjQ0NWI4NTM2MDIwOTRiZDA1NzI3IiwiaCI6Im11cm11cjY0In0='  # <-- Uzupełnij swoim kluczem!
SLEEP_BETWEEN_REQUESTS = 1  # sekundy

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log(f"[PYTHON][ROUTE_TIMES][START] Pobieranie czasów przejazdu: {INPUT_CSV} -> {OUTPUT_CSV}")


punkty = []
log("[INFO] Wczytuję punkty z pliku...")
with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        if row.get('Lat') and row.get('Lon'):
            okno_od = row.get('OknoCzasoweOd', '').strip()
            okno_do = row.get('OknoCzasoweDo', '').strip()
            okno_czasowe = ''
            if okno_od and okno_do:
                okno_czasowe = f"{okno_od}-{okno_do}"
            
            punkty.append({
                'Typ': row.get('Typ', row.get('\ufeffTyp', '')),
                'Ulica': row.get('Ulica',''),
                'Miasto': row.get('Miasto',''),
                'Lat': row['Lat'],
                'Lon': row['Lon'],
                'TimeWindow': okno_czasowe
            })
            log(f"[INFO] Dodano punkt: {row}")

pary = []
for i, start in enumerate(punkty):
    for j, end in enumerate(punkty):
        if i != j:
            pary.append((i, j, start, end))
log(f"[INFO] Utworzono {len(pary)} par punktów.")

# Funkcja pobierająca czas przejazdu z ORS
def get_route_time(lat1, lon1, lat2, lon2):
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [
            [float(lon1), float(lat1)],
            [float(lon2), float(lat2)]
        ]
    }
    log(f"[INFO] Zapytanie ORS: {lat1},{lon1} -> {lat2},{lon2}")
    response = requests.post(ORS_API_URL, json=body, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            duration = data['routes'][0]['segments'][0]['duration'] / 60.0
            distance = data['routes'][0]['segments'][0]['distance'] / 1000.0
            log(f"[OK] Czas: {duration:.2f} min, Dystans: {distance:.2f} km")
            return duration, distance
        except Exception as e:
            log(f"[ERROR] Błąd parsowania odpowiedzi ORS: {e}")
            log(f"[DEBUG] Odpowiedź ORS: {data}")
    else:
        log(f"[ERROR] Błąd API ORS: {response.status_code}")
        log(f"[DEBUG] Odpowiedź ORS: {response.text}")
    return None, None

log("[INFO] Pobieram czasy przejazdu dla par punktów...")
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['StartIdx','EndIdx','StartTyp','EndTyp','StartUlica','StartMiasto','EndUlica','EndMiasto','DeliveryTimeWindow','Distance_km','Duration_time']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for i, j, start, end in pary:
        duration, distance = get_route_time(start['Lat'], start['Lon'], end['Lat'], end['Lon'])
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        writer.writerow({
            'StartIdx': i,
            'EndIdx': j,
            'StartTyp': start['Typ'],
            'EndTyp': end['Typ'],
            'StartUlica': start['Ulica'],
            'StartMiasto': start['Miasto'],
            'EndUlica': end['Ulica'],
            'EndMiasto': end['Miasto'],
            'DeliveryTimeWindow': end['TimeWindow'],
            'Distance_km': round(distance,2) if distance else '',
            'Duration_time': round(duration,2) if duration else ''
        })
        log(f"[INFO] Zapisano parę: {i}->{j}")
log(f"[END] Pobieranie czasów zakończone. Wynik zapisano do {OUTPUT_CSV}")
