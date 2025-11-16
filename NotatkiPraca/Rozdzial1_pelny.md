# Rozdział 1. Problem VRPTW i model scenariuszowy E/P


Problem trasowania pojazdów (ang. Vehicle Routing Problem, VRP) stanowi jedno z centralnych zagadnień logistyki i badań operacyjnych[^I1]. Jest to zadanie wyznaczenia zbioru tras obsługujących klientów przy minimalizacji kosztu, którego składniki typowo obejmują dystans, czas oraz zasoby[^I2]. Warianty VRP pojawiają się m.in. w dystrybucji detalicznej, usługach serwisowych oraz logistyce ostatniej mili (dystrybucja miejska/e‑commerce)[^I3][^I4].
W tym rozdziale zarysowano genezę i ewolucję VRP (1.1), przedstawiono wybrane zastosowania VRP/VRPTW (1.2), opisano podejście EPO i zakres jego adaptacji (1.3), scalono kompletny, sformalizowany opis zastosowanego modelu VRPTW z filtrem E/P (1.4).

[^I1]: Toth, P.; Vigo, D. (eds.) (2002). The Vehicle Routing Problem. SIAM Monographs on Discrete Mathematics and Applications.
[^I2]: Laporte, G. (2009). Fifty Years of Vehicle Routing. Transportation Science 43(4):408–416.
[^I3]: Savelsbergh, M.; Van Woensel, T. (2016). City Logistics: Challenges and Opportunities. Transportation Science 50(2):579–590.
[^I4]: Mangiaracina, R.; Perego, A.; Seghezzi, A.; Tumino, A. (2019). Innovative solutions to last mile delivery challenges in urban areas. International Journal of Physical Distribution & Logistics Management 49(9):901–931.


## 1.1. Geneza i ewolucja VRP


Początki badań nad trasowaniem pojazdów sięgają roku 1959, kiedy Dantzig i Ramser sformułowali problem dystrybucji paliw jako zadanie optymalizacyjne minimalizujące koszt tras ciężarówek.[^H1] W 1964 Clarke i Wright zaproponowali heurystykę oszczędności (Savings), której prosta reguła łączenia par klientów stała się fundamentem szybkich metod konstrukcyjnych.[^H2] Lata 70. i 80. przyniosły rozwój metod dokładnych: modele całkowitoliczbowe 0–1 z ograniczeniami eliminującymi podcykle oraz procedury branch‑and‑bound rozszerzające skalę rozwiązywalnych instancji VRP.[^H3] Równolegle zaczęto systematyzować odmiany problemu według cech takich jak: struktura floty (jednorodna/heterogeniczna), ograniczenia popytu i pojemności, czas serwisu, wielość depotów czy obecność okien czasowych – w ujęciach klasyfikacyjnych i monograficznych.[^H4] Fundamentalnym rozszerzeniem struktury zadania było wprowadzenie okien czasowych i zestawu instancji VRPTW (typy R, C, RC) przez Solomona (1987), który stał się zestawem referencyjnym do porównań algorytmów.[^H5] Typy R, C, RC różnią się rozmieszczeniem klientów: R – rozproszone (random/uniform), C – skupione w klastrach (clustered), RC – mieszane; różnica ta wpływa na możliwości konsolidacji tras. Wczesne przekrojowe opracowania (Bodin & Golden 1981 – klasyfikacja[^H6]; Golden & Assad 1988 – kompendium metod[^H7]) skonsolidowały ówczesne heurystyki konstrukcyjne i dokładne, ułatwiając późniejszą standaryzację terminologii. Lata 90. i 2000. przyniosły dalsze monografie i szerokie przeglądy pogłębiające i ujednolicające klasyfikację.[^H3]

Od przełomu lat 80./90. do początku lat 2020 obserwuje się systematyczny rozwój metaheurystyk. Najpierw symulowane wyżarzanie (SA) wprowadziło kontrolowaną, malejącą w czasie akceptację gorszych ruchów, aby uniknąć przedwczesnego zastoju.[^H10] Następnie idea tabu search Glovera wykorzystała listy tabu do zapamiętywania świeżych ruchów i utrudniania cofania się, wzmacniając eksplorację przestrzeni rozwiązań.[^H8a] Osman zaproponował integrację SA i tabu jako metastrategię łączącą akceptację pogorszeń z pamięcią strukturalną.[^H9] Adaptacja tabu search do VRP przez Gendreau, Hertza i Laporte’a dostarczyła skuteczne ruchy trasowe i potwierdziła efektywność pamięciowej heurystyki w logistyce.[^H8] Kolejnym krokiem były zunifikowane ramy tabu (Unified Tabu), które ujednoliciły podejście dla wielu wariantów problemu (multi‑depot, okresowe, z oknami czasowymi).[^H11] Równolegle nastąpiła ekspansja dużych sąsiedztw (LNS), gdzie usuwa się naraz grupę klientów i rekonstruuje trasę lepszym wstawieniem,[^H14] oraz ich adaptacyjne uogólnienie (ALNS), wybierające operator według aktualnej skuteczności.[^H16] Hybrydowe algorytmy genetyczne HGS wykorzystały reprezentację giant tour dzieloną na trasy i procedury naprawcze dla utrzymania różnorodności i jakości rozwiązań.[^H12] Najnowszy etap rozwoju przesuwa akcent na niepewność parametrów (czasy przejazdu, popyt) oraz dwa podejścia: quasi‑robust (działanie w kilku wybranych scenariuszach bez pełnego modelowania rozkładów) i stochastic (modelowanie zmienności poprzez rozkłady lub szeroki zestaw scenariuszy), co motywuje wieloscenariuszową weryfikację wykonalności.[^H13] W praktyce oznacza to częstsze sprawdzanie tras w więcej niż jednym scenariuszu (tu: E i P), ograniczające liczbę kandydatów, ale zmniejszające ryzyko opóźnień.



[^H1]: Dantzig, G.B.; Ramser, J.H. (1959). The Truck Dispatching Problem. Management Science 6(1):80–91.
[^H2]: Clarke, G.; Wright, J.W. (1964). Scheduling of Vehicles from a Central Depot. Operations Research 12(4):568–581.
[^H3]: Laporte, G. (2009). Fifty Years of Vehicle Routing. Transportation Science 43(4):408–416.
[^H4]: Toth, P.; Vigo, D. (eds.) (2002). The Vehicle Routing Problem. SIAM Monographs on Discrete Mathematics and Applications.
[^H5]: Solomon, M.M. (1987). Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints. Operations Research 35(2):254–265.
[^H6]: Bodin, L.; Golden, B. (1981). Classification of Vehicle Routing and Scheduling Problems. Networks 11(2):97–108.
[^H7]: Golden, B.L.; Assad, A.A. (eds.) (1988). Vehicle Routing: Methods and Studies. Elsevier.
[^H8]: Gendreau, M.; Hertz, A.; Laporte, G. (1994). A Tabu Search Heuristic for the Vehicle Routing Problem. Management Science 40(10):1276–1290.
[^H8a]: Glover, F. (1989). Tabu Search—Part I. ORSA Journal on Computing 1(3):190–206.
[^H9]: Osman, I.H. (1993). Metastrategy Simulated Annealing and Tabu Search Algorithms for the Vehicle Routing Problem. Annals of Operations Research 41(4):421–451.
[^H10]: Kirkpatrick, S.; Gelatt, C.D.; Vecchi, M.P. (1983). Optimization by Simulated Annealing. Science 220(4598):671–680.
[^H11]: Cordeau, J.-F.; Gendreau, M.; Laporte, G. (1999). A Tabu Search Heuristic for the Multi-Depot Vehicle Routing Problem. Computers & Operations Research 27(11–12): 1171–1182.
[^H12]: Vidal, T.; Crainic, T.G.; Gendreau, M.; Prins, C. (2012). A Hybrid Genetic Algorithm with Adaptive Diversity Management for a Large Class of Vehicle Routing Problems with Time Windows. Computers & Operations Research 40(1):475–489; Vidal, T.; Crainic, T.G.; Gendreau, M.; Prins, C. (2013). A Unified Solution Framework for Multi-Attribute Vehicle Routing Problems. European Journal of Operational Research 234(3):658–673.
[^H13]: Gendreau, M.; Laporte, G.; Vigo, D. (2016). Stochastic Vehicle Routing: A Review. Transportation Research Part B 79:401–425.
[^H14]: Shaw, P. (1998). Using Constraint Programming and Local Search for Vehicle Routing and Scheduling. In: Principles and Practice of Constraint Programming—CP98, LNCS 1520:417–431.
[^H16]: Ropke, S.; Pisinger, D. (2006). An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows. Transportation Science 40(4):455–472.

<!-- Dotąd mamy ---->
## 1.2. Zastosowanie VRP
Problemy trasowania pojazdów (VRP) i ich warianty, takie jak problem trasowania pojazdów z oknami czasowymi (VRPTW), stanowią ważny obszar badań w dziedzinie optymalizacji kombinatorycznej oraz badań operacyjnych . Ich rozwiązania mają istotne znaczenie dla optymalizacji procesów logistycznych, transportowych oraz usługowych, umożliwiając firmom obniżkę kosztów operacyjnych, wzrost efektywności oraz poprawę jakości obsługi klienta . Różnorodność zastosowań wynika z możliwości dopasowania modelu VRP do konkretnych warunków, w których oprócz planowania tras, uwzględnione są również pojemność pojazdów, harmonogramy dostaw czy specyficzne wymagania klientów (VRPTW) . 

1.2.1	Logistyka i dystrybucja
W sektorze logistycznym planowanie tras za pomocą omawianych modeli pozwala na minimalizację zużycia paliwa, czasu pracy kierowców oraz liczby potrzebnych pojazdów . Firmy kurierskie, w obliczu stale rosnącej liczby zamówień, wykorzystują VRP do wyznaczania najbardziej wydajnych ścieżek dostaw przesyłek do odbiorców. Wariant z oknami czasowymi jest tu szczególnie istotny, ponieważ pozwala na uwzględnienie niekiedy ściśle określonych okien czasowych, w których klienci są dostępni na odbiór zamówień . Duże sieci handlowe wykorzystują VRP do planowania zaopatrzenia swoich punktów sprzedaży. Modele VRPTW pozwalają na synchronizację dostaw z godzinami otwarcia sklepów, co minimalizuje przestoje i usprawnia cały proces . W miastach, gdzie ruch drogowy bywa utrudniony, uwzględnienie dynamiki ruchu w modelach pozwala na zwiększenie liczby obsłużonych klientów w ciągu przeciętnego dnia roboczego.
1.2.2	Sektor usług
Firmy oferujące usługi serwisowe (takie jak np. naprawy sprzętów, instalacje, konserwacje) wykorzystują narzędzia optymalizacyjne do efektywniejszego planowania swoich usług. Podobnie jak wyżej, dopasowanie do dostępności klientów jest tutaj bardzo istotne. W przypadku usług komunalnych w postaci odśnieżania dróg, minimalizacja floty pojazdów oraz sumy pokonanych kilometrów ma bezpośredni wpływ na obniżenia kosztów operacyjnych. W zarówno prywatnej jaki i publicznej opiece zdrowotnej VRP może być używane do optymalizacji wizyt pielęgniarskich, szczególnie w dużych miastach. 

1.2.3	Zastosowania innowacyjne i dynamiczne
Współczesne zastosowania problemów VRP wykraczają poza statyczne planowanie tras dla tradycyjnych flot pojazdów. W odpowiedzi na rozwój technologii oraz rosnące zapotrzebowanie na elastyczne rozwiązania, coraz większe znaczenie zyskują warianty dynamiczne, które uwzględniają zmieniające się warunki w czasie rzeczywistym. Prowadzi to do powstania tzw. Rich Vehicle Routing Problem, uwzględniający szeroki zestaw ograniczeń występujący w rzeczywistym świecie . Takie modele mogą uwzględniać wiele depozytów, priorytety klientów oraz flotę heterogeniczna, czyli pojazdy o różnej ładowności i koszcie eksploatacji.
VRP zakłada, że wszystkie dane (klienci, okna) są znane z góry. W praktyce jednak, np. w usługach taksówkowych czy pomocy drogowej, zgłoszenia pojawiają się w trakcie trwania tras. Algorytmy DVRP  reagują dynamicznie na te zmiany, podejmując decyzje w czasie rzeczywistym. Najlepszym przykładem tego rozwiązania jest monitoring ruchu drogowego występujący w Google Maps . Integruje on dane z map drogowych w czasie rzeczywistym, co pozwala na dynamiczną zmianę tras w przypadku korków, wypadków czy objazdów. 



[^A1]: Pillac, O.; Gendreau, M.; Guéret, C.; Medaglia, A.L. (2013). A survey on dynamic and stochastic vehicle routing problems. International Journal of Production Research 51(23):7115–7139.
[^A2]: Braekers, K.; Ramaekers, K.; Van Nieuwenhuyse, I. (2016). The vehicle routing problem: State of the art classification and review. Computers & Industrial Engineering 99:300–313.
[^A3]: Cattaruzza, D.; Absi, N.; Feillet, D. (2017). Vehicle routing problems for city logistics. EURO Journal on Transportation and Logistics 6:51–79.
[^A4]: Fikar, C.; Hirsch, P. (2017). Home health care routing and scheduling: A review. Computers & Operations Research 77:86–95.
[^A5]: Nuortio, T.; Kytöjoki, J.; Niska, H.; Bräysy, O. (2006). Improved route planning and scheduling of waste collection. Waste Management 26(12):1247–1256.
[^A6]: Ichoua, S.; Gendreau, M.; Potvin, J.-Y. (2003). Vehicle dispatching with time-dependent travel times. European Journal of Operational Research 144(2):379–396.
[^A7]: Van Wassenhove, L.N. (2006). Humanitarian aid logistics: supply chain management in high gear. Journal of the Operational Research Society 57(5):475–489.
[^A8]: Campbell, A.M.; Jones, P.C. (2011). Prepositioning supplies in preparation for disasters. European Journal of Operational Research 209(2):156–165.

## 1.3. Podejście EPO i adaptacja do VRPTW
Podejście EPO (Expected-Pessimistic-Optimistic) autorów Puka, Skalna, Duda, Derlecki (2025)  przedstawia koncepcję trójwartościowego szacowania czasów, z której w niniejszej pracy wykorzystano dwa poziomy (E i P) jako podstawę filtra scenariuszowego w adaptowaym wariancie VRPTW. W harmonogramowaniu produkcji każdej operacji przypisuje się trzy uporządkowane estymacje  O ≤E≤P  wyznaczane z danych historycznych (np. kwartyle, miary średnie). Triada tworzy przedział absorbujący typowe wahania empirycznie obserwowane w danych, bez potrzeby modelowania pełnych rozkładów: P wyznacza konserwatywną granicę, E odzwierciedla przebieg typowy, a O pozwala wykorzystać wcześniejsze zakończenia do kompresji sekwencji. Mechanizm ogranicza różnicę między planem a realizacją i redukuje konieczność ponownej kalkulacji. 
W kontekście trasowania pojazdów niepewność materializuje się przede wszystkim w zmienności czasów przejazdów pomiędzy klientami (intensywność ruchu, incydenty, warunki drogowe). Strukturalna analogia polega na odwzorowaniu „czasu przetwarzania” operacji na czas przejazdu między klientami, odpowiadający łukowi sieci transportowej (połączeniu między dwoma węzłami grafu reprezentującego sieć tras). Potencjalne pełne przeniesienie EPO oznaczałoby utrzymywanie trzech macierzy czasów przejazdu t_{ij}^O,t_{ij}^E,t_{ij}^P i jednoczesną propagację trzech linii czasowych. Analiza koszt-korzyść sugeruje jednak, że w VRPTW komponent „optymistyczny” może mieć ograniczoną wartość operacyjną: wcześniejszy przyjazd skutkuje zwykle jedynie oczekiwaniem na otwarcie okna, nie tworząc realnej możliwości przyspieszenia kolejnych obsług poza tym, co już zapewnia standardowy mechanizm waiting. Asymetria ryzyka – polegająca na tym, że szkodliwe są głównie opóźnienia – uzasadnia redukcję triady do pary E/P.
Adaptacja zastosowana w niniejszej polega zatem na: (1) odrzucenie scenariusza O, jako mającego ograniczoną wartość operacyjną; (2) zastąpieniu dynamicznych reguł wyboru estymacji prostym równoległym testem wykonalności w dwóch scenariuszach (E i P); (3) konstrukcji macierzy pesymistycznej t_{ij}^P poprzez jednolite przeskalowanie czasów bazowych t_{ij}^E stałym współczynnikiem pogorszenia, np.:
t_{ij}^P= β\,t_{ij}^E,β> 1
gdzie β oznacza stały współczynnik pogorszenia czasów przejazdu (np. β=1.1 dla wydłużenia o 10%). Takie jednolite przeskalowanie pozwala zachować spójność struktury macierze przy wprowadzeniu umiarkowanego marginesu bezpieczeństwa. (4) zastosowanie twardego filtra przecięcia zbiorów wykonalności pomijając umieszczanie tych parametru P  w funkcji kosztu, co skutkuje brakiem konieczności kalibracji wagi penalizacji. W implementacji przyjętej w niniejszej pracy test wykonalności tras przeprowadzany jest równolegle w scenariuszach E i P, natomiast wartość funkcji celu (omówiona w sekcji 1.4) obliczana jest wyłącznie dla scenariusza typowego E. Takie rozwiązanie pełni podwójną rolę: filtr P zapewnia odporność rozwiązania na wydłużenia czasów przejazdu, a koszt oparty na E zachowuje realizm ekonomiczny i unika nadmiernej penalizacji długości tras. Rezygnacja z trzeciej macierzy (Optimistic) redukuje obciążenie obliczeniowe i upraszcza implementację lokalnych ruchów (brak potrzeby utrzymywania dodatkowych buforów), przy jednoczesnym zachowaniu kluczowej właściwości: trasa zaakceptowana w obu scenariuszach ma mniejsze prawdopodobieństwo naruszenia okien czasowych w przypadku rzeczywistego wydłużenia przejazdów.
Mapowanie elementów z harmonogramowania produkcji na problem VRPTW można przedstawić następująco: zadanie (job) odpowiada przejazdowi lub fragmentowi trasy między dwoma obsługami, czas przetwarzania odpowiada przejazdowi, maszyna reprezentuje pojedynczy pojazd (trasę), a okres bezczynności maszyny – czas oczekiwania (waiting) przed otwarciem okna czasowego klienta. Koncepcja „wykorzystania wcześniejszego zakończenia” w produkcji przekłada się tu na naturalny mechanizm czekania: wcześniejszy dojazd do klienta nie skraca całego harmonogramu, jeśli kolejny klient ma nieotwarte okno czasowe. W związku z tym wartość informacyjna scenariusza O jest mniejsza (od E i P), co uzasadnia jego eliminację w adaptacji E/P.
Zastosowany filtr E/P można interpretować jako deterministyczne ograniczenie o charakterze oportunistycznym: przy minimalnym zwiększeniu złożoności danych wejściowych (druga macierz czasów) zawęża przestrzeń przeszukiwania do rozwiązań bardziej stabilnych względem opóźnień. Kosztem tej konserwatywności jest potencjalne odrzucenie konfiguracji, które byłyby poprawne w scenariuszu typowym, ale nie spełniają wymagań w przypadku pogorszenia czasów przejazdu w scenariuszu P. Formalnie adaptację można zapisać poprzez definicję zbiorów wykonalności F_E i F_█(P@) scenariuszach E i P oraz ich przesunięcie:
F_E∩F_P
które staje się obszarem eksploracji dla heurystyk i późniejszego algorytmu optymalizacyjnego. W praktyce oznacza to, że trasy zaakceptowane w obu scenariuszach są bardziej odporne na nieprzewidywane opóźnienia, co minimalizuje ryzyko naruszenia okien czasowych w rzeczywistych warunkach.

<!-- Dotąd mamy ---->

## 1.4. Zastosowany model VRPTW z filtrem E/P

W pracy zdefiniowano i zaimplementowano specyficzny wariant problemu VRPTW, którego kluczową cechą jest quasi-odpornościowe podejście do niepewności czasów przejazdu, oparte na filtrze scenariuszowym E/P. Poniżej przedstawiono kompletny, sformalizowany opis modelu, integrujący jego wszystkie komponenty.

### 1.4.1. Formalna definicja i komponenty

Problem jest zdefiniowany na skierowanym grafie pełnym $G=(V, A)$, gdzie $V = \{0\} \cup N$ jest zbiorem wierzchołków, a $A = \{(i, j) : i, j \in V, i \neq j\}$ jest zbiorem łuków. Wierzchołek $0$ reprezentuje depot (bazę), a $N = \{1, 2, ..., n\}$ to zbiór $n$ klientów. Każdemu klientowi $i \in N$ przypisane jest twarde okno czasowe $[a_i, b_i]$, w którym musi rozpocząć się jego obsługa. Czas obsługi u każdego klienta jest zerowy ($s_i=0$). Dostępna jest flota $K$ jednorodnych pojazdów.

Centralnym elementem modelu są dwie macierze czasów przejazdu między wierzchołkami $i$ oraz $j$:
1.  **Macierz czasów oczekiwanych ($T_E$)**: Zawiera estymacje $t_{ij}^E$, reprezentujące typowy, najczęściej spotykany czas podróży.
2.  **Macierz czasów pesymistycznych ($T_P$)**: Zawiera estymacje $t_{ij}^P$, odzwierciedlające warunki najgorszego przypadku (np. korki). W modelu przyjęto, że $t_{ij}^P = t_{ij}^E \cdot \alpha$, gdzie $\alpha=1.3$ jest stałym, jednolitym współczynnikiem pesymizmu.

Dodatkowo, model wykorzystuje macierz odległości $D$, zawierającą dystanse $d_{ij}$ między wierzchołkami, oraz definiuje horyzont planistyczny $H$, oznaczający maksymalny czas pracy każdego pojazdu.

### 1.4.2. Filtr wykonalności E/P

Rozwiązanie, czyli zbiór tras $R = \{r_1, r_2, ..., r_K\}$, jest uznawane za **wykonalne** (dopuszczalne) wtedy i tylko wtedy, gdy spełnia wszystkie poniższe warunki **jednocześnie w obu scenariuszach (E oraz P)**:
1.  **Ograniczenie okien czasowych**: Dla każdego klienta $i$ na każdej trasie, czas rozpoczęcia obsługi $B_i$ musi zawierać się w jego oknie czasowym: $a_i \le B_i \le b_i$.
2.  **Ograniczenie horyzontu**: Czas powrotu każdego pojazdu do depotu na końcu trasy nie może przekroczyć horyzontu $H$.

Obliczenia czasów przyjazdu ($A_j$) i rozpoczęcia obsługi ($B_j$) dla klienta $j$, poprzedzonego przez $i$ na trasie, są prowadzone sekwencyjnie dla każdego scenariusza:
-   $A_j = B_i + t_{ij}$
-   $B_j = \max(A_j, a_j)$ (uwzględnienie oczekiwania na otwarcie okna)

Filtr E/P działa jako mechanizm odrzucający rozwiązania, które są optymalne w warunkach typowych, ale stają się niewykonalne przy niewielkich opóźnieniach. Poniższy schemat ilustruje logikę działania filtra.

![Schemat działania filtra E/P](https://i.imgur.com/r8A3a2c.png)
*Rysunek 1. Schemat działania filtra wykonalności E/P.*

### 1.4.3. Asymetryczna funkcja kosztu

Celem optymalizacji jest minimalizacja funkcji kosztu, która jest obliczana **wyłącznie dla rozwiązań spełniających warunki filtra E/P**, opisane w sekcji 1.4.2. Ponieważ rozwiązania naruszające okna czasowe lub horyzont są odrzucane, funkcja kosztu dla rozwiązań dopuszczalnych nie zawiera składników karnych – ich rolę przejmuje twardy filtr wykonalności.

Funkcja kosztu w sposób asymetryczny traktuje oba scenariusze: do jej obliczenia wykorzystywane są wyłącznie metryki ze scenariusza **oczekiwanego (E)**, co odzwierciedla dążenie do minimalizacji kosztów operacyjnych w typowych warunkach.

Całkowity koszt wykonalnego rozwiązania $R$ jest sumą trzech głównych składników:
$C(R) = c_v \cdot |R_{u}| + c_d \cdot \sum_{r \in R} \sum_{(i,j) \in r} d_{ij} + c_t \cdot \sum_{r \in R} E_r^E$

Gdzie:
-   $c_v$: Koszt stały użycia jednego pojazdu.
-   $|R_u|$: Liczba użytych pojazdów (tras niepustych).
-   $c_d$: Koszt jednego kilometra.
-   $d_{ij}$: Dystans między klientami $i$ oraz $j$.
-   $c_t$: Waga kosztu czasu pracy.
-   $E_r^E$: Czas zakończenia trasy $r$ w scenariuszu **oczekiwanym**.

Wagi poszczególnych składników funkcji kosztu ($c_v, c_d, c_t$) zostały dobrane w celu normalizacji ich wpływu i odzwierciedlenia priorytetów optymalizacyjnych, co jest standardową praktyką w literaturze VRP, gdy nie operuje się na rzeczywistych danych księgowych[^I1]. Wartości przyjęto jako $c_v = 900$, $c_d = 1$ oraz $c_t = 1$. Ustawienie kosztu stałego pojazdu ($c_v$) na znacznie wyższym poziomie niż kosztów zmiennych ma na celu silne premiowanie rozwiązań minimalizujących liczbę użytych pojazdów, co stanowi główny cel optymalizacji. Koszty dystansu i czasu ($c_d, c_t$) przyjęto jako równe, traktując je jako drugorzędne, równoważne cele.

Taka konstrukcja funkcji celu, w połączeniu z filtrem E/P, promuje rozwiązania, które są nie tylko tanie w realizacji, ale również odporne na zakłócenia. Warto przy tym zaznaczyć, że choć formalny model opiera się na twardych ograniczeniach, algorytmy optymalizacyjne (takie jak Symulowane Wyżarzanie) mogą wewnętrznie wykorzystywać funkcje z mechanizmem kar do oceny stopnia niewykonalności odrzucanych kandydatów. Stanowi to jednak wyłącznie aspekt implementacyjny, pozwalający algorytmowi "mierzyć", jak daleko od dopuszczalności znajduje się dane rozwiązanie, podczas gdy model teoretyczny operuje wyłącznie na zbiorze rozwiązań wykonalnych.

## 1.5. Osadzenie w literaturze i metody optymalizacji
## 1.5. Osadzenie w literaturze i przejście do metod optymalizacji

Opisany model, łączący klasyczne VRPTW z dwuscenariuszowym filtrem wykonalności, wpisuje się w nurt badań nad odpornym trasowaniem pojazdów (Robust VRP). W odróżnieniu od pełnych modeli stochastycznych, które wymagają znajomości rozkładów prawdopodobieństwa, oraz od klasycznej optymalizacji odpornej, koncentrującej się wyłącznie na scenariuszu najgorszego przypadku, przyjęte podejście quasi-odporne stanowi pragmatyczny kompromis. Wykorzystuje ono ograniczoną liczbę scenariuszy do zapewnienia stabilności rozwiązania bez konieczności modelowania pełnej niepewności.

Rozwiązanie tak zdefiniowanego problemu wymaga zastosowania metod optymalizacji przybliżonej, które są standardem w rozwiązywaniu problemów VRP o dużej skali[^I1][^I2]. W niniejszej pracy wykorzystano dwuetapowe podejście: najpierw generowano rozwiązania początkowe za pomocą **heurystyk konstrukcyjnych**, a następnie poddawano je iteracyjnej poprawie z użyciem **metaheurystyki opartej na lokalnym przeszukiwaniu**.

Wybór tych metod podyktowany był ich sprawdzoną skutecznością oraz możliwością adaptacji do niestandardowej funkcji kosztu i oceny wykonalności. Szczegółowy opis zastosowanych algorytmów, ich implementacji oraz parametryzacji zostanie przedstawiony w kolejnych rozdziałach pracy.
