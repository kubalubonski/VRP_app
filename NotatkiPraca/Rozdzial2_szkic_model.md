# Rozdział 2 – Problem i model (Szkic formalny)

## 2.1 Definicja wariantu VRPTW
Mamy zbiór klientów \(V = \{1,2,\dots,n\}\) oraz depot \(0\). Pełny zbiór indeksów \(V_0 = V \cup \{0\}\). Każdy klient \(i\) ma okno czasowe \([a_i, b_i]\). Pojazdy startują i kończą w depot.

## 2.2 Reprezentacja rozwiązania
Rozwiązanie to zbiór tras \(R = \{r_1, r_2, \dots, r_m\}\), gdzie trasa \(r_k = (0, i_1, i_2, \dots, i_{p_k}, 0)\). Każdy klient pojawia się dokładnie w jednej trasie (brak podziału dostaw).

Nie modelujemy pojemności: brak ograniczeń ładunkowych (uproszczenie). Czas obsługi przy węźle \(i\) można traktować jako \(s_i\) (w danych bieżących \(s_i = 0\)).

## 2.3 Czasy przejazdu i scenariusze E/P (podejście EPO)
Dla każdej pary \((i,j)\) mamy deterministyczny czas przejazdu scenariusza oczekiwanego \(t_{ij}^E\) oraz pesymistycznego \(t_{ij}^P\), gdzie typowo \(t_{ij}^P \ge t_{ij}^E\).

Czas przyjazdu w scenariuszu E do klienta \(i\) w trasie \(r_k\):
\[
T_i^E = T_{prev}^E + t_{prev,i}^E + s_{prev}
\]
Jeśli \(T_i^E < a_i\) to pojazd czeka (waiting) i rozpoczęcie obsługi to \(S_i^E = a_i\), inaczej \(S_i^E = T_i^E\). Analogicznie dla scenariusza P:
\[
T_i^P = T_{prev}^P + t_{prev,i}^P + s_{prev}
\]
Warunek akceptowalności wizyty (quasi-robust filter):
\[
S_i^E \le b_i \quad \text{i} \quad S_i^P \le b_i
\]
Jeśli warunek nie spełniony – ruch (kandydat rozwiązania) odrzucamy bez naliczania kary.

## 2.4 Horyzont dnia
Horyzont \(H\) – maksymalny dopuszczalny czas zakończenia trasy (w scenariuszu E i analogicznie kontrolowany w P). Dla trasy \(r_k\):
\[
Finish_k^E \le H, \quad Finish_k^P \le H
\]
Ruchy naruszające horyzont eliminowane (rejected_horizon_moves).

## 2.5 Funkcja kosztu
Całkowity koszt rozwiązania \(R\):
\[
Cost(R) = c_d \cdot Dist(R) + c_v \cdot Vehicles(R) + w_t \cdot TimeSum(R)
\]
Gdzie:
- \(Dist(R) = \sum_{r_k \in R} \sum_{(i,j) \in r_k} d_{ij}\) (dystans lub przewidywany dystans – w implementacji oparty na macierzy),
- \(Vehicles(R) = |R|\) (liczba użytych tras ≈ pojazdów),
- \(TimeSum(R) = \sum_{r_k \in R} (Finish_k^E - Start_k^E)\) – suma czasów trwania tras w scenariuszu E,
- \(c_d, c_v, w_t\) – odpowiednio stawka dystansu, koszt stały pojazdu, waga komponentu czasu.

Kary za spóźnienie lub naruszenia okien są nieaktywne (wartości 0) – ograniczenia egzekwowane przez filtr (hard w praktyce).

## 2.6 Metryki pomocnicze / raportowane
- \(vehicles\_used = Vehicles(R)\)
- \(total\_distance\_km = Dist(R)\)
- \(makespan_E = \max_{r_k} Finish_k^E\)
- \(sum\_route\_time_E = \sum_{r_k} (Finish_k^E - Start_k^E)\)
- \(avg\_route\_time_E = \frac{1}{Vehicles(R)} \sum_{r_k} (Finish_k^E - Start_k^E)\)
- \(waiting_E = \sum_{i} \max(0, a_i - T_i^E)\)

## 2.7 Uproszczenia i konsekwencje
1. Brak pojemności → model skupia się na strukturze czasowej i kolejności.
2. Brak kosztu opóźnienia pieniężnego → interpretacja wyników koncentruje się na dystansie, liczbie pojazdów i balansie czasu.
3. Filtr E/P zamiast kary → prostsza kalibracja wag, ale brak gradientu „jak blisko” naruszenia (binarny odrzut).
4. Scenariusze ograniczone do dwóch (E i P) → brak pełnej dystrybucji; możliwa przyszła rozszerzalność do wielu scenariuszy lub modelu probabilistycznego.

## 2.8 Notatki implementacyjne (most do kolejnych rozdziałów)
- W SA ruchy generowane przez operatory (swap, relocate, 2-opt) są odrzucane wcześnie jeśli naruszą E lub P.
- Statystyka `rejected_horizon_rate` = liczba ruchów naruszających horyzont / wszystkie próby.
- Dalsze parametry (\(c_d, c_v, w_t\)) logowane w sekcji `parameters` w plikach JSON.

(Koniec szkicu – do rozwinięcia o cytowania i opis słowny.)
