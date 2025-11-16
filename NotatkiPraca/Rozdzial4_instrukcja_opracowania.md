# Instrukcja opracowania Rozdziału 4 (maks ~15 stron z SA)

Cele: zwięźle pokazać wyniki heurystyk (Savings vs Insertion), wyciągnąć kluczowe obserwacje i płynnie przejść do eksperymentów SA bez przeładowania tabelami.

## 1. Proponowana struktura rozdziału (alokacja stron)
1. Wprowadzenie i cel (0.5 strony)
2. Dane testowe + generator (0.5 strony)
3. Metody startowe (Savings, Insertion) – bardzo krótki opis (0.5 strony)
4. Wyniki heurystyk – tabele i wykresy + obserwacje (5–6 stron)
5. Podsumowanie heurystyk i wybór rozwiązania bazowego (0.5 strony)
6. Parametry i plan eksperymentów SA (1 strona)
7. Wyniki SA (6 stron: przebieg, porównanie parametrów, wnioski)
8. Wnioski końcowe rozdziału i przejście dalej (0.5 strony)
Total ~15 stron.

## 2. Minimalny zestaw danych do pokazania (heurystyki)
Używamy wyłącznie `heurystyki_batch.csv` (finalny). Nie wspominamy starszych plików.

## 3. Ograniczenie liczby tabel (maks 5 dla heurystyk)
T1: Rozmiary 20–40 (profil, cost_S, cost_I, % gain, veh_S, veh_I)
T2: Rozmiary 80–120 (jak wyżej)
T3: Rozmiar 200 (profil, cost_S, cost_I, % gain, veh_S, veh_I, avg_wait_per_client)
T4: Średni % gain i średni veh_diff per profil (4 wiersze)
T5: Średni % gain i średni veh_diff per rozmiar (5 wierszy) – opcjonalnie przenieś do załącznika jeśli ciasno

Jeśli ubyć miejsca: skasuj T2 i scal 80–120 z T3 (dodając kolumnę size).

## 4. Wykresy (maks 4 dla heurystyk + 1 dla SA)
F1: vehicles_used vs size (Savings vs Insertion) – linie lub punkty.
F2: Heatmapa % gain (profil × size).
F3: Boxplot avg_wait_per_client (profil × heurystyka).
F4: (opcjonalnie) Słupki cost dla rozmiaru 200 (profil × heurystyka) – tylko jeśli heatmapa mało czytelna dla dużych.
F5 (SA): Krzywe best_cost vs epoka dla różnych alpha.

Jeśli ograniczenia: zostaw F1, F2, F3 i F5.

## 5. Kroki przygotowania w Excelu / narzędziu BI
1. Import CSV.
2. Dodaj dwie nowe kolumny (to tylko różnice / procent):
	- cost_pct_gain_insertion = (cost_S − cost_I) / cost_S  → "o ile % Savings jest droższy od Insertion". Przykład: Savings=1000, Insertion=930 → (1000−930)/1000=0.07=7%.
	- veh_diff = veh_S − veh_I  → "o ile więcej pojazdów potrzebuje Savings". Przykład: veh_S=12, veh_I=9 → 12−9=3.
	Excel formuły w tabeli: =([@cost_S]-[@cost_I]) / [@cost_S] oraz = [@veh_S] - [@veh_I]. Przeciągnij w dół.
3. Filtrowanie arkuszy: (20–40), (80–120), (200).
4. Budowa T1–T3: kopiuj jako obraz (unikaj screenshotów niskiej jakości).
5. Pivot: Rows=size, Columns=profile, Value=AVERAGE(cost_pct_gain_insertion) → format warunkowy → eksport jako F2 heatmapa.
6. Slack: Boxplot (jeśli Excel utrudnia → alternatywnie histogramy z grupowaniem profili).
7. T4 / T5: drugi pivot (profil / size) → oblicz średnie.

## 6. Sekwencja narracji (heurystyki) – akapity
A1: "Dwie heurystyki porównano na zbiorze 20 instancji (pięć rozmiarów × cztery profile okien)."
A2: "Insertion uzyskuje niższy koszt i mniej pojazdów w każdej grupie rozmiarowej (T1–T3)." – cytuj 1–2 ekstremalne liczby.
A3: "Wraz z zawężaniem okien rośnie przewaga kosztowa Insertion (F2, T4)." – wskazanie największego % gain.
A4: "Savings generuje większy slack (F3), co odzwierciedla zachowawczą konstrukcję tras." – cytuj przykładowe wartości.
A5: "Makespan E pozostaje porównywalny – redukcja pojazdów nie wydłuża końca." – jeśli faktycznie tak.
A6: "Dlatego jako bazę dla SA przyjmujemy rozwiązania Insertion." – jedno zdanie.

## 7. Styl zdań obserwacyjnych (szablony)
- "Największa względna redukcja kosztu występuje dla instancji 200_tight (−X%)."
- "Różnica liczby pojazdów między Savings a Insertion dla profilu medium osiąga maksymalnie Y przy rozmiarze 120."
- "Średni slack Savings w profilach loose i very_loose jest Z–W minut wyższy niż Insertion, wskazując potencjał dalszej kompresji."
- "Brak spóźnień potwierdza skuteczność filtrów okien czasowych – komponent lateness nie pojawia się w kosztach."

## 8. Przejście do SA
Wstaw po A6 krótką sekcję "Parametry metaheurystyki":
- Model chłodzenia: T_{k+1} = alpha * T_k.
- Badane parametry: t_max (500,1000), alpha (0.90,0.95,0.98), iters_per_T (200,500), neighborhood (mixed, two_opt).
- Kryterium porównania: improvement_pct.

## 9. SA – minimalny zestaw raportowania
Tabela SA: wiersze = kombinacje (alpha, iters_per_T) dla jednego t_max na instancji referencyjnej (np. 80_medium), kolumny: best_cost, improvement_pct, accepted_moves, improving_moves.
Następnie ogranicz parametry do najlepszej pary i pokaż wyniki dla większych instancji (120_tight, 200_loose) – druga mała tabela.
Wykres F5: Krzywe best_cost vs epoka (3 wartości alpha).
Jedno zdanie o acceptance_ratio_worse – spadek z ~R_start do ~R_end.

## 10. Lista kontrolna (odhacz przed finalnym złożeniem)
[ ] Wszystkie tabele opisane w tekście w kolejności przywołania.
[ ] Żadna tabela nie przenosi zbędnych kolumn (usuń total_distance_km jeśli nie analizujesz dystansu osobno).
[ ] Heatmapa ma legendę (%) i równą paletę (zielony = większy zysk).
[ ] Boxplot osi Y podpisany "Średni slack [min]".
[ ] Formuły w tekście: % gain, improvement_pct, T_{k+1}.
[ ] Wnioski bazowe przed SA nie sugerują metaheurystyki zanim ją wprowadzisz.

## 11. Co pominąć (żeby zmieścić się w 15 stronach)
- Szczegółowe rozpisanie generatora – zostawić jedno zwarte zdanie.
- Dystans per route i sum_route_time jeśli nie używasz ich w argumentacji (przenieś do załącznika).
- Ranking top 10 instancji – opcjonalny.

## 12. Najkrótsza wersja (awaryjna jeśli objętość rośnie)
Usuń T2 oraz F4, ogranicz Slack do jednego zdania z liczbami, SA pokaż tylko jedną tabelę i jeden wykres.

## 13. Gotowe mikrownioski do klejenia
1. "Insertion kompresuje klientów – redukuje liczbę pojazdów o 2–4 w dużych instancjach względem Savings." 
2. "Przewaga rośnie przy profilach tight: zysk kosztowy przekracza X%." 
3. "Wyższy slack Savings (do Y min średnio) wskazuje zachowawczość konstrukcji." 
4. "SA ma potencjał dalej redukować koszt z już zwartej bazy – parametry chłodzenia będą kontrolować balans eksploracja/eksploatacja." 

## 14. Struktura akapitów w finalnym
Akapit 1: Cel i zakres.
Akapit 2: Dane + jedno zdanie generatora.
Akapit 3: Krótka charakterystyka Savings vs Insertion.
Akapit 4–8: Wyniki (koszt/pojazdy, profile, slack, wniosek o wyborze bazy).
Akapit 9: Parametry SA.
Akapit 10: Zapowiedź wyników SA w kolejnej części.

---
Ta instrukcja ma prowadzić od pustej sekcji do gotowego rozdziału bez przeładowania – edytuj liczby X,Y,Z po wstawieniu rzeczywistych wartości z CSV.

## Dodatek A. Proste wyjaśnienie metryk i szablony
### A1. Co pokazujemy
- Koszt (cost_S, cost_I): niższy = lepiej.
- Liczba pojazdów (veh_S, veh_I): mniej = lepiej.
- % zysk kosztu (cost_pct_gain_insertion): procent oszczędności kosztu.
- Różnica pojazdów (veh_diff): oszczędzone pojazdy.
- Slack (avg_wait_per_client): luz czasowy; mniejszy = bardziej „ciasne” trasy.

### A2. Metryki słownie
- % zysk kosztu: jaki kawałek kosztu Savings ucinamy używając Insertion.
- Różnica pojazdów: ile pojazdów mniej potrzeba.
- Slack: średni czas „czekania” przed oknem klienta.

### A3. Przykładowe tabele (fikcyjne)
T1:
| size | profile | cost_S | cost_I | %gain | veh_S | veh_I | veh_diff |
|------|---------|--------|--------|-------|-------|-------|----------|
| 20   | tight   | 1000   | 930    | 7%    | 8     | 7     | 1        |
| 40   | medium  | 2100   | 1950   | 7.1%  | 12    | 10    | 2        |

T4 (średnie per profil):
| profile    | avg_%gain | avg_veh_diff | komentarz |
|------------|-----------|--------------|-----------|
| tight      | 9%        | 3.2          | Największa przewaga |
| very_loose | 4%        | 1.1          | Profil luźny |

### A4. Gdy się gubisz
1. Zrób tylko T1 (20–40) i wykres F1.
2. Dopisz dwa zdania interpretacji.
3. Rozbuduj o heatmapę i slack później.

### A5. Mini skrypt Python (opcjonalnie)
```python
import pandas as pd
df = pd.read_csv('heurystyki_batch.csv')
df['cost_pct_gain_insertion'] = (df['cost_S'] - df['cost_I']) / df['cost_S']
df['veh_diff'] = df['veh_S'] - df['veh_I']
print(df.groupby('profile')[['cost_pct_gain_insertion','veh_diff']].mean())
```

### A6. Szablony zdań
- "Insertion obniża koszt o 7% przy 20_tight." 
- "Oszczędzamy 3 pojazdy przy 120_tight." 
- "Slack Savings jest o 6 min większy (profil loose)."

## Dodatek B. Szczegółowe kroki w Excelu (tabele i wykresy)

Przyjmuję, że plik `heurystyki_batch.csv` ma kolumny: dataset, size, window_profile (profile), algorithm (Savings/Insertion), total_cost, vehicles_used, avg_wait_per_client, itd.

### B1. Przygotowanie danych podstawowych
1. Otwórz Excel → Dane → Pobierz dane z tekstu/CSV → wybierz `heurystyki_batch.csv` → Załaduj jako Tabela.
2. Upewnij się, że kolumny mają nagłówki: `algorithm`, `total_cost`, `vehicles_used`, `size`, `window_profile`, `avg_wait_per_client`.
3. Dodaj kolumnę `cost_pct_gain_insertion`:
	- Wstaw nową kolumnę na końcu, nazwij `cost_pct_gain_insertion`.
	- W pierwszym wierszu filtruji tak, aby wyświetlał się wiersz z Savings i Insertion dla tej samej instancji? Prostszą metodą: Zrobimy to później pivotem – ALE jeśli masz już wersję z podwójnymi rekordami (Savings i Insertion osobno), przejdź do kroku 4.
4. Stwórz tabelę pomocniczą z kosztami obu heurystyk:
	- Dane → Tabela przestawna.
	- Wiersze: `size`, `window_profile`.
	- Kolumny: `algorithm`.
	- Wartości: `total_cost` (SUMA lub ŚREDNIA – jeśli jedna wartość na kombinację, wynik i tak będzie równy).
	- Otrzymasz kolumny `Savings` i `Insertion` obok siebie.
	- Dodaj obok pivotu dwie formuły: w komórce np. G5: =(B5-C5)/B5 aby uzyskać %gain (zakładając B= Savings, C=Insertion). Sformatuj jako procent z jednym miejscem po przecinku.

Alternatywa (jeśli w oryginalnej tabeli jeden rekord = jedna heurystyka):
	- Dodaj kolumnę pomocniczą klucz: =[@size]&"_"&[@window_profile].
	- Użyj WYSZUKAJ.PIONOWO lub XLOOKUP aby dla klucza pobrać koszt Savings i Insertion w jednej linii.

### B2. Tabela T1 (rozmiary 20–40)
1. Wróć do pivotu lub tabeli scalonej.
2. Filtrowanie `size`: zaznacz 20 i 40.
3. Skopiuj widoczne wiersze (size, profile/window_profile, cost_S (Savings), cost_I (Insertion), %gain, veh_S, veh_I, veh_diff).
	- veh_diff: jeśli w pivotcie dodasz drugi zestaw wartości `vehicles_used` z kolumnami heurystyk, w sąsiedniej komórce wpisz =Veh_S - Veh_I i przeciągnij.
4. Wklej do nowego arkusza nazwij `T1`. Uporządkuj nagłówki: size | profile | cost_S | cost_I | %gain | veh_S | veh_I | veh_diff.
5. Sformatuj %gain procent z jednym miejscem po przecinku.

### B3. Tabela T2 (rozmiary 80–120)
Powtórz kroki z T1, tylko filtrujesz size: 80 i 120. Arkusz nazwij `T2`.

### B4. Tabela T3 (rozmiar 200 + slack)
1. Filtr size = 200.
2. Dodaj do pivotu kolumnę wartości `avg_wait_per_client` (ŚREDNIA).
3. Skopiuj: profile | cost_S | cost_I | %gain | veh_S | veh_I | veh_diff | avg_wait_per_client do arkusza `T3`.

### B5. Tabela T4 (średnie per profil)
1. Dane → Tabela przestawna z oryginalnej tabeli (nie z już filtrowanej).
2. Wiersze: `window_profile`.
3. Wartości: `total_cost` z kolumną `algorithm` w kolumnach (Savings i Insertion) ORAZ `vehicles_used`.
4. Obok pivotu dodaj formuły dla każdego profilu: %gain = (cost_S - cost_I)/cost_S; veh_diff = veh_S - veh_I.
5. Utwórz czystą tabelkę z czterema wierszami: profile | avg_%gain | avg_veh_diff | komentarz.

### B6. (Opcjonalne) T5 średnie per size
Jak T4, lecz Wiersze: `size`, Kolumny: `algorithm`.

### B7. Wykres F1 (vehicles_used vs size)
1. Z pivotu z kolumnami Vehicles dla Savings i Insertion usuń filtry profilu (lub wybierz jeden jeśli chcesz linię na profil).
2. Zaznacz zakres: kolumna size + kolumny veh_S, veh_I.
3. Wstaw → Wykres liniowy (zwykły).
4. Zmień nazwy serii: zaznacz serię → Formatuj serię → Nazwa (Savings / Insertion).
5. Oś X: format → Jednostka główna = 20 (jeśli rozmiary 20,40,80,120,200).
6. Dodaj etykietę osi Y: "Liczba pojazdów".

### B8. Wykres F2 (heatmapa %gain)
1. Pivot: Wiersze=size, Kolumny=window_profile, Wartości=ŚREDNIA %gain (jeśli masz %gain w scalonej tabeli; jeśli nie – dodaj dodatkową tabelę gdzie wyliczysz %gain per instancja przed pivotem).
2. Zaznacz komórki wartości (bez nagłówków).
3. Narzędzia główne → Formatowanie warunkowe → Skale kolorów → wybierz zielony→biały→czerwony (lub zielony→żółty→czerwony) i ewentualnie Odwróć tak aby zielony = większa wartość.
4. Dodaj pasek nagłówka tekstowego nad pivotem: "Średni % zysk kosztowy Insertion względem Savings".
5. Kopiuj jako obraz (Schowek → Kopiuj jako obraz) żeby wkleić do pracy.

### B9. Wykres F3 (boxplot slack)
Metoda 1 (Excel 365):
1. Przygotuj tabelę: kolumny = slack_Savings, slack_Insertion z wartościami dla każdej instancji (filtrowanie size jeśli chcesz tylko 200, albo wszystko).
2. Zaznacz dwie kolumny → Wstaw → Wykres statystyczny → Wykres pudełkowy.
3. Zmień nazwy serii na "Savings" i "Insertion"; tytuł: "Slack avg_wait_per_client".
4. Oś Y: jednostka główna np. 5 (minuty).

Metoda 2 (manualnie):
1. Dla każdej heurystyki policz: MIN(), QUARTILE.INC(...,1), MEDIAN(), QUARTILE.INC(...,3), MAX().
2. Użyj wykresu skumulowanego słupkowego + paski błędów albo gotowego szablonu jeśli masz.

### B10. Wykres F5 (SA – krzywe best_cost vs epoka)
1. Przygotuj arkusz `SA_data`: kolumna epoch (0..N), kolumny best_cost_alpha_090, best_cost_alpha_095, best_cost_alpha_098.
2. Zaznacz wszystkie kolumny.
3. Wstaw → Wykres liniowy (wiele serii).
4. Legenda: α=0.90, α=0.95, α=0.98.
5. Dodaj etykietę osi X: "Epoka"; oś Y: "Najlepszy koszt".
6. Jeśli chcesz wygładzenie: Formatuj serię → Styl wygładzony (opcjonalnie).

### B11. Formatowanie końcowe tabel
- Usuń nadmiarowe miejsca po przecinku w kosztach (format liczbowy bez tysięcy jeśli mało miejsca).
- Użyj jednolitego stylu czcionki (Calibri 11 lub Times 11 – zależnie od wymogów).
- W %gain zachowaj jedno miejsce po przecinku (7.1%).

### B12. Eksport do pracy
1. Zaznacz gotową tabelę → Narzędzia główne → Kopiuj → Kopiuj jako obraz.
2. Wstaw do edytora tez (Word/Latex) jako obraz (nie screenshot zamazany) lub tabelę jeśli styl pozwala.

### B13. Szybka kontrola jakości
- Czy %gain nie jest ujemny? (jeśli tak – opisz wyjątek).
- Czy veh_diff >= 0? Jeśli nie – wspomnij, że Savings czasem używa mniej pojazdów (rzadkie przypadki?).
- Czy wykresy mają czytelne legendy?

### B14. Najkrótsza ścieżka (kompresja do 10 min pracy)
T1 → F1 → Pivot %gain → Heatmapa F2 → Boxplot F3 → Gotowe.

Jeśli którykolwiek krok jest wciąż niejasny – wskaż jego numer (np. B8) i doprecyzuję.
