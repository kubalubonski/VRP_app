# Uproszczenia i dalsze kroki (diagnostyka / post-processing)

Data: 2025-09-30

## 1. Dlaczego jeden skrypt (`run_heuristics_demo.py`)
- Zastępuje wcześniejsze rozdzielenie na różne formaty danych (pierwotny wwwroot + nowy edge-list aplikacji).
- Automatyczna detekcja źródła: jeśli podasz `--app-csv`, ładuje format aplikacyjny; w przeciwnym razie używa bazowych plików.
- Unikamy dublowania logiki kosztu, inicjalizacji i zapisu tras.
- Parametry (wagi, horizon, service_time) skoncentrowane w jednym miejscu → spójna ewolucja.

## 2. Uproszczenia modelu (aktualny stan)
| Obszar | Aktualne założenie | Co pominięto | Powód |
|--------|--------------------|--------------|-------|
| Scenariusze O/E/P | O i P lokalnie do okna, E do propagacji | Brak globalnej ścieżki O/P | Redukcja złożoności czasowej |
| Horyzont dnia | Sprawdzany na expected (E) | Brak globalnej kary za P>horizon | Decyzja: P tylko lokalne okna |
| Service time | 0 (lub minimalny) | Brak zróżnicowania per klient | Skupienie na czasach przejazdu |
| Flota | Nieograniczona, koszt rośnie wykładniczo | Brak twardego limitu pojazdów | Elastyczna penalizacja |
| Waiting | Pełny koszt w E | Brak różnicowania typów postoju | Wystarcza do separacji jakości tras |
| Korelacje odcinków | Ignorowane | Brak macierzy kowariancji | Prostota i brak źródła danych |
| Opóźnienia w P | Hard lokalnie do okien | Brak soft-late adaptacji | Jasne narzędzie kontroli wykonalności |
| Przerwy kierowców | Brak | Regulacje 4.5h/9h | Etap future work |

## 3. Unikalne nazwy wyników
Nowy schemat zapisu: `routes_<heurystyka>_<nazwaDanych>_<YYYYMMDD_HHMMSS>.txt` np.
```
routes_insertion_app_medium_20250930_153210.txt
```
Eliminuje nadpisywanie i pozwala archiwizować historię uruchomień.

## 4. Co oznaczają główne metryki (skrót)
- `travel_E`: suma oczekiwanych przejazdów całej floty.
- `waiting_E`: suma czekania (flota) → wysokie = potencjał do reorder.
- `vehicles_used`: liczba tras z co najmniej jednym klientem.
- `violations_P`: lokalne naruszenia okien w pesymistycznym czasie (powinno być 0).
- `horizon_violations`: liczba tras przekraczających horyzont w expected (obecnie 0 = ok).
- `route_end_times_E`: zakończenia tras (oś E), max ≤ day_horizon.

### 4.1 Definicje formalne (violations_P vs horizon_violations)

| Wskaźnik | Oś czasowa | Zakres | Kryterium naruszenia | Interpretacja | Typowa reakcja |
|----------|------------|--------|----------------------|---------------|----------------|
| `violations_P` | Pesymistyczna (P) | Lokalnie: pojedynczy klient | arrival_P > due_time klienta | Trasa w najgorszym scenariuszu spóźnia się do okna | Jeśli `enforce_hard_P=True` → kara big_M lub odrzucenie ruchu |
| `horizon_violations` | Expected (E) | Globalnie: cała flota / trasy | max_route_end_E > day_horizon | Plan przekracza dozwolony horyzont dnia w średnim scenariuszu | Dodanie kary / raport ostrzegawczy |

Uwagi:
1. Rozdzielenie osi (P lokalnie, E globalnie) upraszcza model: nie wymuszamy ultra-konserwatywnego dnia opartego na P, co ograniczałoby konsolidację tras.
2. `violations_P` mierzy liczbę (lub w alternatywnym wariancie sumę) punktów, gdzie spełnienie okna nie jest gwarantowane w scenariuszu pesymistycznym.
3. `horizon_violations` w obecnej implementacji jest zwykle binarne (0 = brak, >0 = przekroczenie); można rozszerzyć o `horizon_excess_minutes = max(0, max_route_end_E - day_horizon)`.

### 4.2 Przykład ilustrujący

Załóżmy:
- day_horizon = 600
- Dwie trasy: A kończy o 585 (E), B kończy o 612 (E)
- W obu trasach wszystkie arrival_P ≤ due_time klientów

Skutki:
- `violations_P = 0` (lokalnie ok w P)
- `horizon_violations = 1` (co najmniej jedna trasa ma koniec > 600 w E)

Interpretacja: plan operacyjny jest lokalnie robust wobec okien, ale globalny harmonogram przekracza długość dnia w średnim scenariuszu – potrzebna skrócona lub podzielona trasa B.

## 5. Post-processing – kontekst i odwołanie
Szczegółowy szkic modułu post-processingu (cele, ruchy, kryteria stopu, rozszerzenia) został przeniesiony do osobnego pliku:

`PropozycjeRozszerzen/post_processing_szkic.md`

W tym dokumencie pozostawiamy jedynie kontekst:
- Cel PP: redukcja `waiting_E`, konsolidacja tras (mniej `vehicles_used`), okazjonalne skrócenie `travel_E`.
- Moment użycia: po konstrukcji (Insertion / Savings), przed ewentualnym metaheurystycznym ulepszaniem.
- Kluczowe ryzyko: nadmierne psucie slacku w osi P – należy monitorować brak wzrostu `violations_P`.

## 6. Dlaczego PP nie jest jeszcze wdrożony
Najpierw ustalono stabilny model danych i kosztu (robust lokalnie na P, globalny na E). Dopiero na tej bazie PP ma sens jako dodatkowa warstwa. Różnice jakości między Savings a Insertion pokazują, że poprawa konstrukcji już daje duży zysk – PP będzie krokiem iteracyjnym, a nie naprawczym.

## 7. Podsumowanie
Uproszczenia koncentrują system na kluczowej idei: lokalna robust feasibility (P) + globalny koszt w expected (E). 
Unikalne nazwy wyników eliminują konflikt plików. Szczegóły planu PP są wydzielone, aby bazowa dokumentacja nie mieszała koncepcji implementowanych z przyszłymi.

---
Jeśli chcesz wdrożyć minimalny post-processing – można zacząć od prostego intra-route 2-opt + relocate pojedynczego klienta.
