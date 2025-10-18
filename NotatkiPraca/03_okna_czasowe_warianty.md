# Warianty okien czasowych (tight / medium / loose / very_loose)

## 1. Cel
Cztery warianty szerokości okien czasowych pozwalają obserwować wpływ restrykcyjności ograniczeń czasowych na strukturę tras oraz komponenty kosztu.

## 2. Definicja wariantów
- **tight** – wąskie okna (najtrudniejszy scenariusz); mniejsza tolerancja na kolejność odwiedzin → częściej powstają spóźnienia i potrzeba większej liczby tras.
- **medium** – umiarkowane; część ograniczeń nadal aktywna, ale możliwe ograniczone manewrowanie kolejnością.
- **loose** – okna znacząco szersze; spóźnienia rzadziej występują, zaczyna rosnąć udział czasu oczekiwania (wcześniejsze przyjazdy).
- **very_loose** – okna bardzo szerokie (prawie „brak” ograniczeń); heurystyki działają podobnie jak w klasycznym VRP bez okien; spóźnienia minimalne lub zerowe, możliwe większe czekanie.

(Generowanie: instancje syntetyczne różnią się jedynie parametrycznym rozszerzaniem szerokości przedziałów czasowych – ten sam zestaw punktów i macierzy przejazdów.)

## 3. Faktyczny wpływ na metryki (na podstawie bieżących wyników)
Ogólny trend zachowany (poluzowanie okien zmniejsza spóźnienia i zwykle liczbę pojazdów), ALE:
- waiting_total nie rośnie monotonnie – przy bardzo luźnych oknach część tras kończy wcześniej i całkowite oczekiwanie może nawet spaść (np. app_20: loose < medium; very_loose podobny poziom do loose).
- very_loose potrafi mieć wyższy total_cost niż loose w większych instancjach, jeśli rosną inne komponenty (np. dystans / pojazdy / horizon_excess), mimo że spóźnienia są niskie.

| Wariant | lateness_P_sum | horizon_excess_E | waiting_total (trend) | vehicles_used (trend) | total_cost (trend) |
|---------|----------------|------------------|-----------------------|-----------------------|--------------------|
| tight | Wysokie | Istotne / wysokie | Wysokie (blokady kolejności) | Najwyższe | Wysoki (kary dominują) |
| medium | Niższe vs tight | Spada / stabilizuje się | Często spadek | Spadek | Spadek |
| loose | Bardzo niskie | Niskie / 0 | Może spaść dalej | Dalszy spadek | Dalszy spadek |
| very_loose | Minimalne / 0 | Zmienny (może wzrosnąć przy wydłużeniu tras) | Płaskie lub niższe | Blisko minimum | Może wzrosnąć (inne składniki) |

## 4. Interpretacja
- Spadek lateness od tight do loose jest wyraźny; very_loose nie poprawia już znacząco (bo lateness ~0 wcześniej).
- waiting_total nie jest dobrym prostym proxy „luzu” – spadki wynikają z krótszych tras i wcześniejszych końców (mniej segmentów wymagających czekania).
- Wariant very_loose potrafi mieć wyższy koszt niż loose przy większych instancjach (np. wzrost horizon_excess lub większy dystans w rozproszonych trasach).
- Multi-start insertion nadal krytyczny przy tight (duża wrażliwość na permutację), mniej istotny przy loose / very_loose.

## 5. Zastosowanie w analizie
- Porównanie spadku lateness względem wzrostu waiting_total pokazuje, jak „elastyczność” okien amortyzuje konieczność dodawania pojazdów.
- Zestawienie makespan_E między wariantami pokazuje, czy poluzowanie okien skraca realny koniec dnia, czy tylko rozsmarowuje pracę (często przy very_loose makespan niewiele spada – trasy się wydłużają dystansowo optymalizując kolejność).

## 6. Skrót do pracy
Cztery warianty (tight→very_loose) zmniejszają spóźnienia i liczbę tras, ale wpływ na waiting_total i koszt całkowity nie jest monotoniczny: przy very_loose spadek lateness już się nasyca, a koszt może odbić przez inne komponenty (dystans, horizon_excess). To pokazuje, że luz w oknach nie zawsze gwarantuje dalszą optymalizację kosztu – po pewnym progu korzyści znikają.

## 7. Jak generowane są okna (fakty)
- Dla każdego klienta losujemy szerokość z przedziału zależnego od profilu:
	- tight: 70–90 min
	- medium: 150–180 min
	- loose: 240–300 min
	- very_loose: 330–380 min
- Losujemy środek okna (center) w zakresie 60–540 min od startu dnia (08:00) i odkładamy okno symetrycznie (start = center - width/2, koniec = start + width) przycinając do [0,600].
- Każdy klient dostaje niezależne okno; depot nie ma okna (puste pole).
- Różnice między wariantami wynikają wyłącznie z innej losowej szerokości (dane geograficzne i czasy przejazdów są wspólne bazowo dla każdej instancji delta-rozmiaru).
 - Przy osobnych wywołaniach generatora współrzędne i okna są losowane niezależnie dla każdego wariantu; więc różnice między wariantami w obecnym zestawie danych wynikają zarówno z okien, jak i z geometrii (to trzeba mieć w pamięci przy interpretacji wyników).

