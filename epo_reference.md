# EPO Extension Reference (Extracted Notes)

Źródło: Puka et al., "EPO Extension of Dispatching Rules to Minimize Effects of Time Uncertainty in Production Scheduling", 2025.
(Dostarczone screenshoty stron: tytuł, abstrakt, sekcje 1–3.2 fragmenty.)

## 1. Cel i kontekst
- Problem: Niepewność czasów przetwarzania (processing times) utrudnia tworzenie stabilnych harmonogramów.
- EPO rozszerza reguły dispatchingu o trzy wartości czasu operacji: E (expected), P (pessimistic), O (optimistic) dla jednego zadania/job.
- Założenie: O ≤ E ≤ P.
- Celem jest zwiększenie robustowości bez zwiększania złożoności obliczeniowej heurystyk (reguł dispatchingu) — brak konieczności symulacji Monte Carlo.

## 2. Definicje kluczowe
- Job (zadanie) ma niepewny czas przetwarzania PT.
- Zamiast jednej liczby używa się trzech estymatorów: O, E, P.
- Wartości E,P,O wyznaczane na podstawie historycznych PT (PTU) *poprzez selekcję podobnych zadań* (Similarity function) ograniczoną horyzontem czasowym (TH).
- Zbiór PTUL_{jD} (historyczne czasy dla jobów podobnych do JD) sortowany nierosnąco; z niego wyznacza się kwantyle / statystyki do konstrukcji:
  - PTU_E: mean/median/PERT ((o + 4m + p)/6)
  - PTU_P: 1 quartile / 1 decile / min / p * PTU_E (p∈[0.5,1])
  - PTU_O: 3 quartile / 9 decile / max / o * PTU_E (o∈[1,1.5])
- Następnie korygowane o agregowany czas przygotowawczy AT:
  - E = PTU_E + U + AT
  - P = PTU_P + U + AT
  - O = PTU_O + U + AT
  (U – liczba jednostek do wyprodukowania lub komponent skali w formule PTU_{R,jD} = PTR_{k,jD} / U; tutaj notacja częściowo niepełna – do weryfikacji w dalszych stronach.)

## 3. Intuicja buforowania
- Użycie E,P,O pozwala implicit tworzyć bufory czasowe: jeśli zadanie zakończy się szybciej (O), następne może ruszyć wcześniej; jeśli dłużej (P), harmonogram nadal pozostaje wykonalny bez natychmiastowego przeliczenia.

## 4. Forward Scheduling (sekcja 3.2 – fragment)
- W harmonogramowaniu w przód każde zadanie ma earliest start time EST_{jTD}.
- Dla jobów startowych (bez poprzedników) EST może pochodzić z daty dostępności materiałów.
- Dla jobów z poprzednikami EST_{jTD} = max po poprzednikach z formuły (6)/(7) – wykorzystuje końce E, P lub O poprzedników + czasy transportu TT + lags LAG.
- Formuły końca zadania jR (poprzednika):
  - FTE_{jR,k} = ST_{jR,k} + E
  - FTP_{jR,k} = ST_{jR,k} + P
  - FTO_{jR,k} = ST_{jR,k} + O
- Wybór użytej wartości do wyznaczenia EST_{jTD} zależy od relacji maszyn M_{jR}, M_{jTD} i lagów; pessimistic (FTP) stosowane, gdy różne maszyny (aby ograniczyć overlap i ryzyko downtime), E/O gdy na tej samej maszynie i brak zagrożenia.
- Idea: konserwatywne przejścia między maszynami (użyj P), mniej konserwatywne w obrębie tej samej maszyny (użyj E lub O) — szczegóły wymagają dalszych stron.

## 5. Funkcja Similarity (wstęp)
- Binary similarity: 1 jeśli joby spełniają zestaw warunków parametrów (identyczne kluczowe parametry), 0 w p.p.
- Rozszerzenie z horyzontem czasu: Similarity(jTD,jD,TH)=1 jeśli jTD ~ jD i PD_{jD} ⊆ TH (start date mieści się w oknie analizowanego horyzontu).
- Zbiór SS_{jTD} = { PTUL_{R,jD} | Similarity(...)=1 }.
- Dalsze szczegóły (parametry, metryki odległości) mogą być na kolejnych stronach.

## 6. Mapowanie wstępne na VRP (draft)
- Job ↔ łuk (podróż między klientami) lub obsługa klienta.
- Processing time niepewny ↔ czas przejazdu (travel time) niepewny.
- Trójka (O,E,P) ↔ (czas optymistyczny, oczekiwany, pesymistyczny) na krawędzi.
- EST / start times ↔ czasy przyjazdu do klienta (arrival times).
- LAG / TT ↔ ewentualny czas serwisu / przerwy / przeładunku; w VRP zwykle 0 lub service time.
- Reguły wyboru (dispatching rules) ↔ heurystyczne operatory sąsiedztwa / kryteria akceptacji w SA/GA/ACO.

## 7. Co jeszcze potrzebne z dalszych stron
- Precyzyjna reguła kiedy używać P vs E vs O w aktualizacji EST.
- Czy jest definicja funkcji celu explicit (robust objective) poza zestawem klasycznych metryk.
- Jak autorzy oceniają robustowość (miary: makespan pod niepewnością? tardiness?).
- Czy przewidziane jest łączenie (np. ważona kombinacja) czy raczej wybór adaptacyjny.

## 8. Otwarte pytania do VRP
1. Czy przy obliczaniu arrival time używać mieszanego schematu: gdy przejście do nowego klienta na innej „resource” (pojazd?) bierzemy P, w obrębie tej samej trasy E? (Analog: różne maszyny vs ta sama maszyna.)
2. Czy koszt oceniamy na podstawie E, a naruszenia okien testujemy na P (konserwatywnie)?
3. Jak modelować implicit buffer – wprowadzić dynamiczne przesuwanie startu następnego klienta jeśli poprzedni zakończy się wcześniej (O)?
4. Jak agregować wielo-scenariuszową ocenę (max tardiness, expected tardiness, probability of feasibility)?

## 9. Proponowane warianty implementacyjne (skrót – pełny plan później)
- Deterministyczny: użyj tylko E.
- Konserwatywny: do testu okien użyj P; koszt = E.
- Dwupoziomowy: Feasibility sprawdzaj P, koszt licz jako α*E + (1-α)*P.
- Symulacyjny lekki: arrival liczone kaskadowo z regułą (ta sama trasa ⇒ E, inna interakcja ⇒ P), plus penalty za prawdopodobny tardiness.
- Pełny robust: Multi-scenario evaluation (3 scenariusze) i max penalty w koszcie.

---
(Dodajemy kolejne sekcje po otrzymaniu następnych stron.)

## 10. Dalsze fragmenty – Forward Scheduling (uzupełnienie)
Formuła (8) – warunek dodatkowy zapewniający, że maszyna nie będzie bezczynna dłużej niż konieczne:
\\(
EST_{jTD} \le \begin{cases}
FTO_{jlast} & \text{jeśli } |SV|_{FTO_{jlast}}| > 0,\\\\
FTE_{jlast} & \text{jeśli } |SV|_{FTE_{jlast}}| > 0,\\\\
\infty & \text{w przeciwnym razie}
\end{cases}
\\)
gdzie \(j_{last}\) – ostatni job na maszynie M, a \(SV_t = \{ j | EST_j < t \}\) – zbiór jobów możliwych do uruchomienia przed czasem t. Intencja: jeśli coś może zostać uruchomione zaraz po optymistycznym (O) zakończeniu poprzednika, to można przyspieszyć; w przeciwnym razie patrzymy na expected (E). W praktyce – wprowadza mechanizm wczesnego startu (eksploatacja O), ale tylko jeśli istnieje kolejny kandydat gotowy czasowo.

Formuła (9) – dostępność maszyny:
\\( MAT_M = \min_{j \in F_M} EST_j \\)
czyli najwcześniejszy czas startu spośród aktualnie feasible jobów na maszynie M.

## 11. Backward Scheduling (sekcja 3.3)
Analogiczny mechanizm do forward, ale operujemy latest finish time (LFT). Dla następnika \(jTD\) estymujemy starty poprzedników, tu definiowane są trzy start times następców (STE, STP, STO) obliczane od końca:
Formuły (10):
\\[
STE_{jSC} = FTS_{jSC} - E, \quad STP_{jSC} = FTS_{jSC} - P, \quad STO_{jSC} = FTS_{jSC} - O
\\]
Następnie latest end (LFT) jobu wyznaczany wzorem (11) – wybór zależny od relacji maszyn i lagów (analogiczne rozróżnienie jak przy forward). Warunek dodatkowy (12) – lustrzany do (8), używa zbioru \(SV_t = \{ j | LFT_j > t \}\) i wartości startów STO lub STE pierwszego jobu.

Formuła (13) – dostępność maszyny w backward:
\\( MAT_M = \max_{j \in F_M} EST_j \\) (w tekście pojawia się analogiczny zapis – kontekst: wybór maszyny o najwcześniejszej dostępności lub przy backward adaptacja; należy zweryfikować w oryginale czy to literówka – forward używa min, backward logicznie maks lub specyficzna interpretacja; potencjalna niejednoznaczność do sprawdzenia przy pełnym PDF).

## 12. Algorytm konstrukcyjny (Pseudo-code EPO-forward – Algorithm 1)
Fazy:
1. Initial phase – assignment & obliczenie EST dla jobów startowych.
2. Scheduling phase – iteracyjnie:
  - Wybierz maszynę M' z minimalnym MAT_M.
  - Wybierz job J' z masywu feasible F_{M'} o maksymalnym PT_{J'} (u nich LPT rule: longest processing time). 
  - Zascheduluj J'. Uaktualnij feasibility następców.
  - Przelicz EST potomków i jobów na maszynie.
Zakończenie gdy brak jobów do przypisania.

Klucz: LPT + rozszerzenie EPO pozwala dynamicznie korzystać z O/E/P przy wybieraniu wczesnego startu i minimalizowaniu idle/downtime.

## 13. Metodologia studium przypadku
Wybrano wartości konstrukcji E,P,O (sekcja 4.1) – dla firmy: \(PTU_E=\text{mean}\), \(PTU_P=1\ quartile\), \(PTU_O=3\ quartile\). Similarity oraz horyzont TH (do roku). Analiza 9 próbek (3 długości okresów × 3 próbki losowe) – 5, 10, 20 dni; liczby jobów ~3.5k–8k.
Evaluacja – dwie funkcje celu: Makespan (C_max) i Average Completion Time (AC). Porównanie: LPT_T (teoretyczny bez EPO), EPO_T (teoretyczny z EPO), LPT_A (rzeczywisty), EPO_A (rzeczywisty). “Teoretyczny” oznacza użycie teoretycznych czasów przetwarzania; “rzeczywisty” użycie rzeczywistych (historycznych) czasów.

## 14. Wyniki – obserwacje z tabel (skrót)
- Tabela 2: W większości próbek teoretyczny makespan EPO_T bliski LPT_T (różnice ± ~0–0.5 jednostki), natomiast rzeczywisty makespan EPO_A często niższy od LPT_A (oszczędność nawet do 5%).
- Tabela 3: Różnice LPT_T − EPO_T oraz LPT_A − EPO_A – te drugie większe korzyści (efekt robust). EPO redukuje gap między teoretycznym a rzeczywistym w 8/9 przypadków.
- Tabela 4: Średnia różnica (LPT_A−LPT_T) wyższa niż (EPO_A−EPO_T) – EPO lepiej przewiduje realny makespan.
- Tabela 5–7 (AC): EPO także poprawia średni czas zakończenia lub zbliża do realnych wartości; redukcja błędów predykcji, czasem znaczące skrócenie (np. >3 jednostki).
- Statystyka: Test Wilcoxona (α=0.1) – potwierdza istotność w części przypadków (szczegóły numeryczne w tabelach – do skopiowania jeśli potrzebne do pracy).

## 15. Wnioski z wyników (implikacje dla VRP)
1. EPO nie poprawia znacznie “teoretycznego” planu (bo konstrukcyjnie blisko LPT), ale czyni go bardziej odpornym – realny wynik bliżej przewidywanego lub lepszy.
2. Największe zyski przy dłuższych okresach lub wyższej zmienności – analogia: w VRP większa korzyść przy dłuższych trasach / bardziej zmiennych odcinkach.
3. Mechanizm poprawy: wykorzystanie okna między O i P do wcześniejszego uruchamiania kolejnych zadań gdy rzeczywistość bliższa O/E niż P.
4. EPO redukuje potrzebę reschedulingu / interwencji – w VRP może oznaczać mniej konieczności dynamicznej korekty trasy.

## 16. Uściślone mapowanie EPO → VRP
| Produkcja (paper) | Interpretacja VRP | Uwagi |
|-------------------|------------------|-------|
| Job | Klient lub przejazd (edge) | Lepiej: odcinek (travel) + obsługa klienta jako service time |
| Processing time PT | Travel time | Niepewność ruchu drogowego |
| O,E,P | (t_opt, t_exp, t_pes) | Z pliku scenariuszy | 
| EST_j | Czas przyjazdu earliest | Liczony sekwencyjnie zgodnie z trasą |
| LFT_j (backward) | Najpóźniejszy dopuszczalny przyjazd (okno czasowe end) | Można użyć do konserwatywnego feasibility |
| Machine | Pojazd | Każda trasa odrębny zasób |
| Idle machine | Czekanie pojazdu (waiting) | Ograniczane przez okna czasowe klientów |
| Lag / TT | Postój / serwis / przerwa kierowcy | Możemy rozszerzyć później |
| Algorithm 1 (konstrukcja) | Heurystyczne konstruowanie trasy | U nas używamy SA do poprawy już wygenerowanej trasy |

## 17. Rozszerzone warianty implementacji dla VRP (draft)
1. E-only (baseline) – już mamy.
2. Feasibility-P: arrival_time obliczany z czasami E, ale naruszenia okien sprawdzane przeciwko arrival_time_P (=skumulowane E z zastąpieniem ostatniego odcinka pesymistycznym?). Prostsze przybliżenie.
3. Dual timeline: utrzymuj równolegle akumulację (O_sum, E_sum, P_sum). Feasibility test: czy P_sum mieści się w oknach. Koszt główny: np. E_sum lub suma kar tardiness liczona dla P_sum (konserwatywnie). Dodatkowa miara: slack = window_end - P_sum.
4. Adaptive edge selection (analog do formuły 7): jeśli “przejście” do nowego klienta jest krytyczne (zostaje mało slacku) użyj P, inaczej E (lub nawet O) do tymczasowego arrival. W SA: generuj koszt częściowy dynamicznie.
5. Scenario aggregation: koszt = w_O * f(O) + w_E * f(E) + w_P * f(P) (np. f = tardiness; w sumują się do 1). Feasibility: wymagaj brak tardiness dla P (robust hard), lub kara za tardiness_P * duża waga.
6. Buffer-driven penalty: penalty = max(0, P_arrival - window_end) * β + max(0, E_arrival - window_end) * γ, z β >> γ.
7. Probabilistyczne (jeśli przypiszemy rozkład trójpunktowy): aproksymuj prawdopodobieństwo tardiness używając rozkładu PERT (O,E,P) i penalizuj expected tardiness.

## 18. Otwarte kwestie po nowych stronach
1. Czy w VRP chcemy zachować analog (8)/(12) – wczesny start jeśli istnieje feasible klient gotowy wcześniej? (W praktyce: reordering trasy – już robi SA; wystarczy model wieloscenariuszowy bez dodatkowego constraint.)
2. W backward analogia do wyznaczania latest start może pomóc w pre-przetwarzaniu okien: obliczyć konserwatywne “najpóźniejsze wyjazdy” z magazynu.
3. Czy test robustowości w pracy (porównanie teoretyczny vs realny) chcemy odtworzyć: można zasymulować “realny” travel time losując z zakresu [O,P] biasowany w stronę E i porównać wynik planu E vs plan EPO.
4. Wagi w kosztach – brak jednoznacznej wskazówki w artykule; trzeba ustalić własne lub trzymać się prostego kryterium tardiness_P.

## 19. Proponowane następne kroki (przed implementacją)
1. Wybrać minimalny wariant robust (proponuję Dual timeline #3) jako pierwszy krok – łatwo dodać bez ingerencji w sąsiedztwa.
2. Dodać strukturę danych w `calculate_vrp_cost`: akumulacja trzech sum (acc_O, acc_E, acc_P) oraz slack_P.
3. Zmienić walidację: feasible jeśli acc_P dla każdego klienta <= window_end (i arrival earliest >= window_start jeśli model ma wczesne otwarcie; do rozważenia waiting jak dziś).
4. Koszt = sum(E_travel) + penalty_late_P * K (K duże, np. 100) + penalty_late_E * k (mniejsze, np. 10) + total_wait_E (opcjonalnie).
5. Eksperyment: porównanie wyników baseline vs dual timeline na tym samym seedzie.

## 20. Do uzupełnienia przy ostatnich stronach
- Wszelkie dodatkowe definicje z części conclusions (jeśli zawierają wskazówki dot. generalizacji lub ograniczeń metody).
- Ewentualne formuły dla backward w pseudokodzie (jeśli podany).
- Wzmianki o computational complexity (potwierdzenie brak wzrostu) – argument do sekcji metodologii.

---
Aktualizacja zakończona na podstawie dostarczonych nowych screenów. Czekam na ostatnie ~4 strony, aby zamknąć sekcję wniosków i zebrać finalne cytowalne fragmenty.
