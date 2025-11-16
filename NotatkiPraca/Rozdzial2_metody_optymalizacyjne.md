# Rozdział 3. Wybrane metody optymalizacji tras

W tym rozdziale w przystępny sposób omawiam wybrane metody, które pomagają budować i ulepszać rozwiązania problemu trasowania pojazdów (VRP) oraz jego wariantu z oknami czasowymi (VRPTW). Najpierw pokazuję proste heurystyki tworzące rozwiązania startowe, następnie krótką listę podstawowych ruchów (operatorów), a potem bardziej zaawansowane podejścia – metaheurystyki – które te ruchy wykorzystują do dalszej poprawy. Rozdział nie wchodzi w detale implementacji ani dobór parametrów; te elementy pojawią się później. Celem tutaj jest zrozumienie „jak działa” każda metoda i dlaczego jest przydatna.

## 3.1. Heurystyka oszczędności Clarke’a–Wrighta
Ta klasyczna metoda (Clarke i Wright, 1964) [1] zaczyna od najprostszego możliwego układu: dla każdego klienta istnieje osobna krótka trasa typu magazyn → klient → magazyn. Następnie obliczana jest tak zwana „oszczędność” dla każdej pary klientów i, j:

S(i, j) = d(m, i) + d(m, j) − d(i, j)

Inaczej mówiąc: ile dystansu zaoszczędzimy, jeżeli zamiast dwóch oddzielnych przejazdów połączymy obsługę i oraz j w jedną wspólną trasę. Te pary są sortowane malejąco według wartości oszczędności. Algorytm przechodzi przez listę od największych korzyści do najmniejszych i próbuje scalić trasy, ale tylko wtedy, gdy nie łamie to żadnego ograniczenia (np. okien czasowych). Jeśli połączenie jest poprawne – zostaje, jeśli nie – jest pomijane. Cały proces jest jednokrotnym przejściem przez listę. Dzięki prostocie jest to szybka metoda dająca sensowny punkt wyjścia.

## 3.2. Heurystyka wstawiania (Solomon insertion)
Druga popularna heurystyka (Solomon, 1987) [2] działa odwrotnie niż poprzednia: zamiast łączyć gotowe krótkie trasy, buduje je „od zera”. Na początku nie ma żadnej trasy z klientami. Bierzemy kolejnych nieobsłużonych klientów i dla każdego testujemy wszystkie miejsca wstawienia do już istniejących tras. Dla każdej możliwej pozycji liczymy przyrost kosztu (np. dodatkowy dystans lub czas) oraz sprawdzamy, czy dalej da się zmieścić w oknach czasowych. Wybieramy tę pozycję, która daje najmniejszy przyrost i jest dopuszczalna. Jeśli klient nie może być wstawiony nigdzie – tworzymy dla niego nową krótką trasę. Tak krok po kroku powstaje zestaw tras, które już „od urodzenia” respektują ograniczenia czasowe.

## 3.3. Podstawowe operatory lokalne
Proste ruchy na trasach są potrzebne, aby móc poprawiać rozwiązanie małymi krokami. Trzy najczęściej spotykane operatory to:

- 2‑opt – wycina dwie krawędzie i odwraca fragment trasy między nimi. Często skraca trasę usuwając „zagięcia”.
- Relokacja – przenosi jednego klienta w inne miejsce (w tej samej lub innej trasie), próbując uzyskać krótszy lub lepiej dopasowany układ.
- Zamiana (swap) – wymienia ze sobą dwóch klientów (w jednej trasie lub między trasami).

Te proste ruchy są później wielokrotnie używane w bardziej zaawansowanych metodach. Każdy z nich delikatnie zmienia strukturę, pozwalając szukać lepszych układów bez budowania wszystkiego od nowa.

## 3.4. Symulowane wyżarzanie
Symulowane wyżarzanie (Kirkpatrick i in., 1983; Černý, 1985) [3] to metoda, która przez pewien czas dopuszcza „gorsze” ruchy, aby nie utknąć w pierwszym napotkanym lokalnym minimum. Działa w rundach (epokach). W każdej rundzie wykonuje się wiele prób modyfikacji rozwiązania korzystając z operatorów lokalnych. Jeśli nowe rozwiązanie jest lepsze – przyjmujemy je. Jeśli jest gorsze – możemy je zaakceptować z pewnym malejącym w czasie prawdopodobieństwem zależnym od temperatury. Temperatura zaczyna się wysoko (łatwiej akceptować pogorszenia), a potem spada według prostego wzoru (najczęściej mnożenie przez stały współczynnik). Gdy temperatura jest już bardzo niska, metoda zachowuje się prawie jak zwykłe lokalne ulepszanie.


## 3.5. Tabu Search
Tabu Search (Glover, 1986) [4] to przeszukiwanie lokalne z „pamięcią” ruchów, których chwilowo nie wolno powtarzać. Niedozwolone ruchy trafiają na listę tabu na kilka kolejnych kroków, żeby nie kręcić się w kółko. Jeśli jednak ruch z listy tabu dałby nowe globalnie najlepsze rozwiązanie – można zrobić wyjątek (tzw. aspiracja). Dodatkowe proste pomysły jak czasowe skupienie się na trudniejszych fragmentach (intensyfikacja) albo na rzadko ruszanych trasach (dywersyfikacja) pomagają wyjść poza utarte schematy.

## 3.6. Algorytm genetyczny (GA)
Algorytm genetyczny pracuje na grupie (populacji) różnych rozwiązań. Z nich wybiera się „rodziców”, miesza ich fragmenty (krzyżowanie), a czasem celowo wprowadza drobne zmiany (mutacje), aby utrzymać różnorodność. Dzięki temu nie koncentruje się od razu na jednym pomyśle. Główne trudności w praktyce to: jak zapisać trasę tak, żeby łatwo ją dzielić i składać oraz jak nie dopuścić do sytuacji, w której wszystkie rozwiązania szybko stają się bardzo podobne.

## 3.7. Adaptacyjna metoda ALNS
ALNS (Adaptive Large Neighborhood Search) [5] działa naprzemiennie: najpierw „rozbija” część rozwiązania (usuwając wybranych klientów), potem „składa” je z powrotem przez stopniowe wstawianie. Ma kilka różnych sposobów usuwania (np. losowo, tych z największym kosztem, tych z ciasnych fragmentów) i kilka sposobów wstawiania (np. najtańsze miejsce, wstawienie poprawiające czasy, wstawienie częściowo losowe). Śledzi, które warianty dają poprawy i dostosowuje ich wagi – wzmacnia te skuteczniejsze. Dzięki temu z czasem dobiera kombinacje ruchów lepiej pasujące do danego zestawu danych.

## 3.8. Rola prostych ruchów w metodach zaawansowanych
Symulowane wyżarzanie oraz Tabu Search bezpośrednio używają 2‑opt, relokacji i zamiany jako podstawowych kroków. W algorytmie genetycznym mutacja często polega właśnie na relokacji lub zamianie, a krzyżowanie przenosi większe fragmenty tras do nowych rozwiązań. W ALNS faza „naprawy” to nic innego jak inteligentne wstawianie – czasem wielokrotne – a faza „rozbicia” tworzy miejsce na przebudowę większych kawałków. Jakość i różnorodność tych prostych ruchów wprost wpływa na to, jak skutecznie cała metoda potrafi przeszukiwać nowe obszary.

## 3.9. Krótkie porównanie
Clarke–Wright: błyskawiczne zbudowanie rozsądnej bazy, ale bez dalszych ulepszeń – końcowa jakość ograniczona.
Wstawianie Solomona: buduje trasy „od razu dobrze” pod względem okien czasowych.
Operatory lokalne: tanie w użyciu, szybko prowadzą do pierwszego lokalnego minimum.
Symulowane wyżarzanie: kontrolowane dopuszczanie gorszych ruchów pozwala wyjść poza najbliższe minimum.
Tabu Search: blokowanie niedawnych ruchów zapobiega kręceniu się w kółko, a wyjątki (aspiracje) dodają elastyczność.
Algorytm genetyczny: różnorodność populacji spowalnia zbyt wczesne „zlepienie się” rozwiązań, ale wymaga ostrożnego projektowania krzyżowania.
ALNS: adaptacja zestawu operatorów często daje najwyższą jakość, kosztem większej złożoności wdrożenia.

## 3.10. Przejście do rozdziału 4
W kolejnym rozdziale pokażę: użyte zestawy danych testowych, metryki porównania (dystans, czasy, naruszenia), sposób strojenia temperatury w symulowanym wyżarzaniu, przykładowe parametry dla pozostałych metod oraz krótką analizę wpływu prostych operatorów na końcowy wynik. Tam też pojawi się opis funkcji kosztu i mechanizmu sprawdzania dopuszczalności tras, na których opiera się implementacja.

## Literatura
1. Clarke, G., Wright, J. (1964). Scheduling of Vehicles from a Central Depot.
2. Solomon, M. (1987). Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints.
3. Kirkpatrick, S., Gelatt, C., Vecchi, M. (1983); Černý, V. (1985). Optimization by Simulated Annealing.
4. Glover, F. (1986). Future Paths for Integer Programming and Links to Artificial Intelligence.
5. Ropke, S., Pisinger, D. (2006). An Adaptive Large Neighborhood Search for the Pickup and Delivery Problem with Time Windows.
6. Holland, J. (1975). Adaptation in Natural and Artificial Systems.
