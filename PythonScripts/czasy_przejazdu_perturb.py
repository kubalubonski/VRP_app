import csv
import sys

INPUT_CSV = 'wwwroot/czasy_przejazdu.csv'  # Plik z czasami przejazdu pobranymi z API
OUTPUT_CSV = 'wwwroot/czasy_scenariusze.csv'  # Plik wynikowy
LOG_FILE = 'Logs/log_python.txt'
PESSIMISTIC_MULTIPLIER = 1.3  # Pesymistyczny (ruch, zła pogoda)
OPTIMISTIC_MULTIPLIER = 0.85 # Optymistyczny (noc, brak ruchu)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log(f"[PYTHON][SCENARIOS][START] Generowanie scenariuszy czasowych: {INPUT_CSV} -> {OUTPUT_CSV}")

log("[INFO] Wczytuję czasy przejazdu...")
with open(INPUT_CSV, newline='', encoding='utf-8') as infile, open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['StartIdx','EndIdx','StartTyp','EndTyp','StartUlica','StartMiasto','EndUlica','EndMiasto','DeliveryTimeWindow','Distance_km','Duration_time_expected','Duration_time_pessimistic','Duration_time_optimistic']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        try:
            duration_min = float(row['Duration_time'])
            writer.writerow({
                'StartIdx': row.get('StartIdx',''),
                'EndIdx': row.get('EndIdx',''),
                'StartTyp': row.get('StartTyp',''),
                'EndTyp': row.get('EndTyp',''),
                'StartUlica': row.get('StartUlica',''),
                'StartMiasto': row.get('StartMiasto',''),
                'EndUlica': row.get('EndUlica',''),
                'EndMiasto': row.get('EndMiasto',''),
                'DeliveryTimeWindow': row.get('DeliveryTimeWindow',''),
                'Distance_km': row.get('Distance_km',''),
                'Duration_time_expected': round(duration_min, 2),
                'Duration_time_pessimistic': round(duration_min * PESSIMISTIC_MULTIPLIER, 2),
                'Duration_time_optimistic': round(duration_min * OPTIMISTIC_MULTIPLIER, 2)
            })
            log(f"[OK] Scenariusz: {row.get('StartIdx','')}->{row.get('EndIdx','')} | {duration_min:.2f} min")
        except Exception as e:
            writer.writerow({
                'StartIdx': row.get('StartIdx',''),
                'EndIdx': row.get('EndIdx',''),
                'StartTyp': row.get('StartTyp',''),
                'EndTyp': row.get('EndTyp',''),
                'StartUlica': row.get('StartUlica',''),
                'StartMiasto': row.get('StartMiasto',''),
                'EndUlica': row.get('EndUlica',''),
                'EndMiasto': row.get('EndMiasto',''),
                'DeliveryTimeWindow': row.get('DeliveryTimeWindow',''),
                'Distance_km': row.get('Distance_km',''),
                'Duration_time_expected': '',
                'Duration_time_pessimistic': '',
                'Duration_time_optimistic': ''
            })
            log(f"[ERROR] Błąd scenariusza: {e}")
    log(f"[END] Generowanie scenariuszy zakończone. Wynik zapisano do {OUTPUT_CSV}")
