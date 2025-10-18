# Wynik SA – aktualny (SLIM) format i interpretacja

Ten plik opisuje bieżący odchudzony format wyników z Symulowanego Wyżarzania (SA) oraz wskazuje jakie pola zachować do analizy w pracy. Poprzednia „bogata” wersja została zredukowana dla łatwiejszej obróbki w Excel / pandas i szybszych eksperymentów.

## 1. Struktura skróconego JSON
Główne grupy kluczy (format slim):

1. `parameters` – pełna konfiguracja uruchomienia (temperatura startowa, alpha, liczba iteracji w epoce, rodzaj sąsiedztwa, itp.). Zapewnia replikowalność.
2. `best_routes` – finalny układ tras (lista list indeksów klientów, depot = 0). Podstawowe źródło do wizualizacji i analizy wykorzystania pojazdów.
3. `best_cost` – końcowy całkowity koszt wg funkcji celu.
4. `metrics_initial` / `metrics_best` – wybrane (11) metryk stanu początkowego i końcowego.
5. `metrics_delta` – różnice (best - initial) dla tych metryk: pozwala szybko zobaczyć kierunek zmian (ujemne dla distance = poprawa).
6. `process_stats` – statystyki przebiegu SA (epochs, accepted_moves, improving_moves, total_attempts, rejected_horizon_moves, rejected_horizon_rate).
7. `runtime_seconds` – czas całkowity wykonywania (porównania efektywności konfiguracji).
8. `trace_improvements` – lista punktów (epoch, best_cost) tylko gdy nastąpiła poprawa rozwiązania (wersja lekka do wykresu konwergencji).

Zredukowane zostały: pełna co-epoch trace, odchylenia std, udziały komponentów kosztu, szczegóły per-trasa (distance per route, end_time per route). Jeśli potrzebne wrócą – można przywrócić osobnym trybem.

## 2. Lista metryk (zachowane pola slim)
Przykład zestawu w `metrics_*` (identyczne nazwy w initial/best/delta):
- `vehicles_used` – liczba aktywnych pojazdów.
- `total_distance_km` – suma kilometrów.
- `cost_distance` – koszt komponentu dystansu.
- `cost_time` – koszt komponentu czasu (waga * suma czasów tras).
- `vehicle_cost` – koszt stały floty (pojazdy * stawka).
- `waiting_E` – oczekiwanie (czas przyjazdu przed oknem) – sprzyja potencjalnej kompresji.
- `lateness_P_sum` – sumaryczne przekroczenia okien (powinny być ≈0 przy hard TW).
- `horizon_excess_E` – przekroczenia horyzontu dnia (ruchy z naruszeniem odrzucane → zwykle 0).
- `makespan_E` – czas zakończenia najdłuższej trasy (równoważenie obciążenia).
- `sum_route_time_E` – łączny czas wszystkich tras.
- `avg_route_time_E` – średni czas trasy (balansowanie).

`metrics_delta` ma te same klucze (wartość_best - wartość_initial). Dla kosztów/dystansu poprawa oznacza wartość ujemną.

## 3. Interpretacja wybranych statystyk procesu
- `accepted_moves` – ile ruchów zaakceptowano (zarówno poprawiających jak i pogarszających).
- `improving_moves` – ile ruchów bezpośrednio polepszyło best_cost.
- `rejected_horizon_moves` – ile ruchów odrzucono z powodu naruszenia horyzontu (limit czasowy dnia).
- `rejected_horizon_rate` – odsetek odrzuceń horyzontu względem wszystkich prób (wskazuje ciasnotę ograniczeń czasu).
- `epochs` – liczba iteracji zmian temperatury (każda epoka = blok prób przy aktualnej T).

Wysokie `accepted_moves` przy relatywnie niskim `improving_moves` → SA skutecznie eksploruje poprzez kontrolowaną akceptację gorszych rozwiązań. Wysoki `rejected_horizon_rate` sugeruje potrzebę korekty: np. modyfikacja operatorów skracających trasy lub zmiana parametrów czasu.

## 4. Format CSV (plik zbiorczy slim)
Kolumny: `dataset,size,window_profile,t_max,alpha,iters,neigh,vehicles_initial,vehicles_best,vehicles_delta,total_distance_initial,total_distance_best,total_distance_delta,makespan_initial,makespan_best,makespan_delta,sum_time_initial,sum_time_best,sum_time_delta,waiting_initial,waiting_best,waiting_delta,runtime_seconds` (+ ewentualne dodatkowe jeśli dodamy). Wartości delta = best - initial.

Użycie: szybkie tabelaryczne porównania konfiguracji; pivoty: (window_profile, size) vs median improvement distance.

## 5. Cooling schedule (redukcja temperatury)
Aktualnie stosowany typ: GEOMETRYCZNE (multiplikatywne) chłodzenie.

Formuła aktualizacji w każdej epoce:
T_{new} = T_{old} * alpha

Gdzie `alpha` ∈ (0,1). Stała wartość `alpha` daje wykładniczy (geometric) spadek temperatury: T_k = T_0 * alpha^k. Konsekwencje:
- Łatwe sterowanie tempem wychładzania (bliżej 1.0 → wolne; dalej od 1.0 → szybkie).
- Prosty do analizy (logarytmiczny związek liczby epok z docelowym T_min).
- Ryzyko zbyt szybkiego zamrożenia przy zbyt niskiej alpha → mniej akceptacji pogorszeń → możliwe lokalne minimum.

Możliwe alternatywy (gdyby potrzebne): logarytmiczne T = T0 / (1 + c * k), adaptacyjne (uzależnione od braku poprawy), piecewise (zmiana alpha w segmentach), reheating (okazjonalne podbicie temperatury przy stagnacji).

## 6. Gdzie umieścić informację o chłodzeniu w pracy
- Sekcja „Metoda SA”: podrozdział „Harmonogram temperatury” – definicja formuły, uzasadnienie wyboru geometrycznego, parametry T0 i alpha.
- W analizie wyników: krótka obserwacja wpływu alpha (np. porównanie alpha=0.99 vs 0.985 na liczbę accepted_moves i ostateczny cost).

## 7. Wskazówki analityczne (dla slim formatu)
- Skup się na: redukcji `total_distance_km`, zmianie `vehicles_used`, poprawie `makespan_E` (wyrównanie obciążenia) i spadku `sum_route_time_E`.
- Porównaj profil okien (`window_profile`) – oczekiwanie (`waiting_E`) może rosnąć przy luźnych oknach (łatwiej kompresować dystans).
- Stwórz wykres konwergencji z `trace_improvements` (epoch vs best_cost) – pokazuje typowe „schody” SA.
- Pokaż boxplot delt distance/makespan dla różnych alpha – argumentacja wyboru docelowych parametrów.


## 9. Rekomendacja końcowa
Obecny format slim jest wystarczający do: (a) analizy skuteczności SA, (b) porównań konfiguracji, (c) wizualizacji konwergencji. Nie usuwaj kluczy związanych z procesem (`process_stats`) dopóki nie wykonasz serii eksperymentów – pozwalają one wyjaśnić różnice między parametrami.


