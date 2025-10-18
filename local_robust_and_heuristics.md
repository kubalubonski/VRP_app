# Local Robust – wyjaśnienie + heurystyki startowe

## 1. Czym jest "local robust" w naszej aplikacji

"Local robust" = strategia, w której przy budowie i ocenie trasy:
- Koszt liczony jest na podstawie OCZEKIWANYCH (E) czasów przejazdu + oczekiwanego czekania (`travel_E + w_wait * waiting_E`).
- Każdy krok (przejazd z A do B) MUSI być potencjalnie wykonalny nawet w wariancie PESYMISTYCZNYM (P): arrival_P_B ≤ window_end_B.
- Nie propagujemy pełnej pesymistycznej osi przez cały dzień, tylko sprawdzamy lokalnie: "czy ten odcinek + okno klienta nie wywali się w P" oraz finalnie czy powrót do magazynu w P < horyzont.
- Horyzont dnia (600 minut = 10h) sprawdzany jest w pesymistycznym przebiegu (timeline_P_finish ≤ 600).

Dlaczego "local"? Bo zamiast budować globalną przesuniętą w czasie trasę w trybie P (co szybko robi się bardzo konserwatywne), stosujemy P tylko jako filtr wykonalności dla każdego klienta + końca dnia.

## 2. Składniki kosztu w local_robust
```
Cost = travel_E
     + w_wait * waiting_E
     + w_penalty_P * sum(lateness_P)  (jeśli soft) lub big_M * (#violations_P) przy enforce_hard_P
     + w_penalty_E * sum(lateness_E)  (opcjonalnie informacja)
     + vehicle_cost(k)  # rosnący koszt uruchamiania kolejnych pojazdów
     - slack_bonus (jeśli w_slack != 0 i chcemy nagradzać zapas)
```
Gdzie:
- lateness_P = max(0, arrival_P - window_end)
- waiting_E = max(0, window_start - arrival_E)
- vehicle_cost(k) = base_vehicle_cost * growth_factor^(k-1)
- enforce_hard_P=True → każde naruszenie P daje big_M * violations_P (praktycznie odrzuca rozwiązanie)

## 3. Dlaczego tak
- Optymalizujemy zwykły dzień (expected) – to jest biznesowo sensowne.
- Chcemy mieć gwarancję, że nawet jeśli trafi się gorszy wariant (P), to nadal się mieścimy w oknach i kończymy dzień na czas.
- Nie chcemy nadmiernego pesymizmu (globalnej kumulacji P) – to ograniczałoby przestrzeń rozwiązań.

## 4. Heurystyki startowe
Używane przed uruchomieniem SA aby wygenerować lepszy punkt startowy niż losowy podział klientów.

### 4.1 Clarke–Wright Savings (plik `heuristic_savings.py`)
1. Początek: każda trasa to `[0, i, 0]` dla klienta i.
2. Obliczamy oszczędności: s(i,j) = d(0,i) + d(0,j) - d(i,j) dla expected.
3. Sortujemy malejąco.
4. Próbujemy scalać trasy kończące się na i oraz zaczynające się od j.
5. Przed akceptacją łączenia symulujemy trasę w PESYMISTYCZNYCH czasach aby sprawdzić:
   - arrival_P ≤ window_end klientów,
   - timeline_P ≤ horyzont.
6. Jeśli feasible → łączymy.

Zalety: szybkie grupowanie bliskich klientów, mniejsza liczba pojazdów.
Wady: decyzje zachłanne – później może wymagać poprawek SA.

### 4.2 Greedy Insertion (plik `heuristic_insertion.py`)
1. Start z jednym klientem w trasie `[0, c, 0]`.
2. Iteracyjnie pobieramy kolejnego klienta (losowa kolejność) i próbujemy wstawić w każdą pozycję każdej istniejącej trasy.
3. Obliczamy przyrost kosztu (pełna funkcja local_robust) jeśli wstawka jest pesymistycznie feasible.
4. Wybieramy najmniejszy dodatni przyrost (lub najbardziej ujemny) – wykonujemy wstawkę.
5. Jeśli żadna pozycja nie jest feasible → tworzymy nową trasę `[0, c, 0]`.

Zalety: bezpośrednio minimalizuje koszt funkcji docelowej.
Wady: wolniejsze (częste pełne wywołania oceny) – ale lepsze jakościowo starty.

### 4.3 best_of_both
- Liczymy savings i insertion.
- Bierzemy tę wersję, która ma niższy koszt local_robust.

## 5. Jak uruchomić tylko heurystyki (bez SA)
Możesz stworzyć mały skrypt np. `run_heuristics_demo.py`:
```
from vrp_common_utilities import load_epo_times, load_time_windows, get_epo_matrices, calculate_vrp_cost_local_robust
from heuristic_savings import clarke_wright_savings
from heuristic_insertion import greedy_insertion

matrices = get_epo_matrices(load_epo_times())
time_windows, _ = load_time_windows()

sol_s = clarke_wright_savings(matrices, time_windows)
cs, ms = calculate_vrp_cost_local_robust(sol_s, matrices, time_windows)
print('SAVINGS:', sol_s, ms)

sol_i = greedy_insertion(matrices, time_windows)
ci, mi = calculate_vrp_cost_local_robust(sol_i, matrices, time_windows)
print('INSERTION:', sol_i, mi)
```
(Jeśli chcesz, mogę ten plik dodać.)

## 6. Sygnały że wszystko działa
- Wynik heurystyk: listy tras typu `[[0, 5, 3, 0], [0, 2, 0], ...]`.
- Metryki (dla local_robust) nie mają dużych wartości `hard_penalty` (0 przy enforce_hard_P=True).
- `vehicles_used` mniejsze dla savings niż dla insertion (często) – ale insertion może mieć niższy koszt.

## 7. Co dalej
- Plan walidacji (eksperymenty) – osobny plik.
- Parametry referencyjne i przykładowy JSON – ułatwienie integracji.

---
Dokument możesz rozszerzyć w pracy w sekcji “Algorytmy konstrukcyjne i definicja odporności lokalnej”.
