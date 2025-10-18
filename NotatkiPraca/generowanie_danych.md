# Generowanie danych VRP (skrót)

Cel: realistyczne czasy przejazdu umożliwiające wieloklientowe trasy w horyzoncie dnia 600 min bez nadmiernych naruszeń okien czasowych.

## Zakres wygenerowanych instancji
Rozmiary: 20, 40, 80, 120, 200 (liczba klientów, depot = 0)
Profile okien: tight, medium, loose, very_loose → 4 warianty × 5 rozmiarów = 20 plików `app_final_{n}_{profile}.csv`.

## Geometria i prędkości
- Współrzędne losowane równomiernie w kwadracie 0..120 km (pierwotnie było 0..500, zmniejszone dla skrócenia czasów).
- Odległość euklidesowa w km.
- Prędkość losowana 55–75 km/h (wcześniej większe rozrzuty; zawężone dla stabilizacji dystrybucji czasu).

## Czasy przejazdu (warianty)
Dla każdej krawędzi liczony czas oczekiwany E = dystans / v.
Następnie:
- Optymistyczny O = E * f_O, gdzie f_O ∈ [0.88, 0.95]
- Pessymistyczny P = E * f_P z dwóch koszy:
  - niski: f_P ∈ [1.08, 1.15]
  - wysoki: f_P ∈ [1.20, 1.30]
  (dobór mieszany aby uzyskać umiarkowaną asymentrię, bez ekstremów)
- Twardy limit: E cap ≤ 160 min (przycięcie wartości odstających).

## Cele dystrybucyjne (osiągnięte orientacyjnie)
- Średni leg (E): ~45–60 min
- 90 percentyl: ≤ ~110–120 min
- Maks (E): ≤ 160 min (kap twardy)
- Pessymistyczny wzrost zwykle ≤ +30% względem E (dla większości krawędzi).

## Okna czasowe (profilowane)
Profile różnią szerokością i offsetami (tight → krótsze, very_loose → szerokie). Wszędzie dopasowane tak, by przy nowych czasach większość tras była w pełni wykonalna (zero lateness w testach heurystyk na 40_loose i 120_loose).

## Walidacja po refaktorze
- Heurystyka Insertion: wieloklientowe trasy (np. 120_loose → 5 pojazdów) bez spóźnień.
- Heurystyka Savings: większa liczba pojazdów (brak kosztowej oceny przy łączeniach) – potwierdza różnicę konstrukcji.
- Brak przekroczeń horyzontu dziennego (600) w przykładowych instancjach.

## Powody zmian vs pierwotna wersja
Pierwotne czasy (duży obszar 500×500) dawały zbyt wiele długich legów (250–350+ min) → sztuczne wymuszanie tras jednoklientowych. Redukcja przestrzeni + zawężenie prędkości + umiarkowane multiplikatory P/O przywróciły strukturę problemu.

## Użycie plików
Każdy CSV: edge list + czasy O/E/P + okna. Służy do:
1. Heurystyki: konstrukcja rozwiązań startowych i eksport `routes_{dataset}_{alg}.json`.
2. SA: ładowanie CSV → rekonstrukcja macierzy dystansów/czasów lub (docelowo) z `matrices.npz`.

---
Skrót gotowy; dalsze szczegóły (np. seed, format kolumn) można dopisać jeśli zajdzie potrzeba dokumentacyjna.
