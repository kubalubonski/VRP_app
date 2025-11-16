Architektura aplikacji oraz proces transformacji danych dla wariantu VRPTW E/P
Wprowadzenie i rola moduły aplikacyjnego
Poniższy rozdział opisuje warstwę aplikacyjną, odpowiedzialną za przygotowanie i udostępnienie danych oraz środowiska uruchomieniowe dla wariantu VRPTW z filtrem E/P, zdefiniowanego wcześniej. Jej zadaniem jest powtarzalne przekształcenie danych wejściowych wprowadzonych przez użytkownika (magazyn, adresy punktów dostaw, okna czasowe) w struktury numeryczne - macierze czasów przejazdu (oczekiwanych i pesymistycznych, opcjonalnie także optymistycznych) oraz dystanse - przy ograniczeniu do minimum operacji manualnych. Każdy etap pozostawia trwały rezultat (plik CSV lub JSON), co umożliwia pełną weryfikację i replikację eksperymentów. 
Zakres funkcjonalny modułu obejmuje:
	pobór i podstawową walidację danych wejściowych pobranych z formularza,
	sekwencyjne wykonanie trzech etapów przetwarzania danych,
	udostępnienie spójnych struktur indeksowych dla modułów optymalizacyjnych,
	zapewnienie lekkiej warstwy integracyjnej dla heurystyk i metaheurystyk (uruchamianie, monitorowanie, parametryzacja serii eksperymentów).
Warto podkreślić, że rola modułu nie ogranicza się jedynie do „dostarczenia danych”. Stanowi on zalążek platformy eksperymentalnej, a w przyszłości może być podstawą komercyjnej aplikacji, która:
	standaryzuje interfejs wymiany danych (format macierzy, indeksacja, kontrakt okien czasowych),
	rozdziela odpowiedzialności (przygotowanie danych \leftrightarrow optymalizacja),
	umożliwia rozszerzenie o sterowanie wieloma przebiegami optymalizacyjnymi bez naruszania istniejącego kodu transformacji danych.
Moduł zapewnia także kanał zwrotu wyników (trasy, metryki agregowane, logi parametrów) w formacie CSV lub JSON, dzięki czemu rezultaty są tak samo audytowalne jak dane wejściowe.

Przegląd architektury i podział odpowiedzialności
Architektura aplikacji opiera się na dwóch warstwach technologicznych: interfejsie webowym opartym na ASP.NET Razor Pages , odpowiedzialnym za obsługę formularza i konfigurację, oraz zestawie skryptów w języku Python, realizujących etapy pozyskiwania i przetwarzania danych przestrzenno-czasowych. Rozdzielenie tych warstw wynika z dojrzałości ekosystemu bibliotek numerycznych dostępnych w Pythonie, prostoty implementacji interfejsu w .NET oraz czytelnej granicy wymiany danych pomiędzy nimi, opartej na plikach CSV. Komponent ProcessingService koordynuje kolejne etapy przetwarzania, stosując zasadę wczesnego zakończenia w przypadku błędu (ang. fail-fast) , czyli natychmiastowego przerwania procesu , jeśli którykolwiek etap zakończy się niepowodzeniem. Dzięki temu nie tworzą się błędne pliki wynikowe. Serwis StatusService udostępnia prosty, odporny mechanizm sygnalizacji postępu poprzez aktualizację pliku tekstowego. Skrypty Python pozostają bezstanowe – każdy z nich przyjmuje plik wejściowy i generuje wynik w postaci osobnego pliku wyjściowego. Na rysunku 2 znajduje się diagram architektury wysokiego poziomu, obrazujący podział na warstwę prezentacji (formularz UI), warstwę orkiestracji (ProcessingService), trzy niezależne skrypty Python i komponent statusów. Strzałki jednokierunkowe oznaczają przepływ sterowania, a pliki CSV stanowią trwałe punkty kontroli procesu.
 
Rysunek 2 Diagram architektury wysokiego poziomu (źródło: opracowanie własne)
Przepływ danych
Przepływ danych w aplikacji ma charakter deterministyczny – identyczne dane wejściowe generują identyczny zestaw plików pośrednich. Każdy etap zapisuje wynik w pliku CSV, co umożliwia audyt, diagnostykę i kontrolę błędów.
Skrócony przebieg procesu:
	Formularz \rightarrow dane_wejściowe.csv (magazyn, adresy, okna).
	Geokodowanie \rightarrow dane_wejsciowe_geocoded.csv (dodanie kolumny z uzyskanymi współrzędnymi Lat, Lon).
	Czasy przejazdu \rightarrow czasy_przejazdu.csv (czas i dystans dla par (i,j)).
	Scenariusze \rightarrow czasy_scenariusze.csv (oczekiwane, pesymistyczne, opcjonalnie optymistyczne czasy).
	Budowa macierzy \rightarrow struktury NumPy z mapami okien czasowych.
	Generowanie rozwiązań początkowych przez heurystyki konstrukcyjne.
	Optymalizacja tras przez algorytm optymalizacyjny.
Po zbudowaniu macierzy czasów przejazdu i okien czasowych proces kończy etap przygotowania danych. Na rysunku 3 przedstawiono diagram przepływu plików, ilustrujący liniowy ciąg transformacji. Każdy skrypt pobiera jeden plik wejściowy i generuje kolejny artefakt. Ostatni etap tworzy struktury pamięciowe wykorzystywane przez moduł optymalizacyjny.
 
Rysunek 3 Diagram przepływu plików (źródło: opracowanie własne)
Dane wejściowe i formularz użytkownika
Formularz użytkownika umożliwia wprowadzenie podstawowych danych dotyczących instancji problemu, takich jak adres magazynu oraz lista punktów dostaw wraz z oknami czasowymi („od” / „do”). Konstrukcja formularza odzwierciedla przyjęty w pracy zakres modelu skoncentrowany na aspekcie czasowym trasowania. Dlatego celowo pominięto dodatkowe elementy często spotykane w wariantach VRPTW, takie jak pojemności pojazdów czy priorytety klientów. Taki dobór parametrów pozwala jednoznacznie ukazać wpływ filtra E/P na strukturę rozwiązań, bez zakłóceń wynikających z innych źródeł ograniczeń operacyjnych. Przykładowy plik wejściowy dane_wejsciowe.csv, generowany jako wynik zatwierdzenia formularza przez użytkownika po wprowadzeniu danych, został zaprezentowany w tabeli 1.

Tabela 1 Format wejściowy danych zapisany do pliku .csv
Typ	Nazwa	Adres	Okno od	Okno do
MAGAZYN	Magazyn Centralny	Poznań, ul. Głogowska 1	08:00	18:00
KLIENT	K1	Poznań, ul. Dąbrowskiego 50	09:00	11:30
KLIENT	K2	Poznań, ul. Święty Marcin 12	10:15	13:45

Zastosowanie tekstowego formatu CSV umożliwia prostą inspekcję oraz wersjonowanie danych w systemie kontroli wersji. Interfejs formularza zaprojektowano w sposób intuicyjny – użytkownik kolejno definiuje magazyn oraz wprowadza punkty dostaw z ich oknami czasowymi. Formularz zawiera również podstawowe mechanizmy walidacji, których zadaniem jest weryfikacja kompletności i poprawności formalnej danych jeszcze przed ich zapisem do pliku wejściowego. Aplikacja prezentuje także bieżący status przetwarzania, co ułatwia pracę z większymi zestawami adresów. Choć w obecnej implementacji dominują parametry czasowe, przyjęta architektura danych pozwala na naturalne rozszerzenie modelu o dodatkowe atrybuty (np. zapotrzebowanie ładunkowe czy priorytety dostaw) bez ingerencji w podstawowy przepływ przetwarzania danych. (Tu może screen formularza z apki?)
Konfiguracja ścieżek i parametrów wykonania
System konfiguracji pełni kluczową rolę w utrzymaniu przejrzystości kodu oraz przenośności projektu. Został on podzielony na dwa komponenty: PathConfiguration oraz ProcessingConfiguration. Pierwszy z nich odpowiada za centralne przechowywanie nazw i lokalizacji plików – danych wejściowych, wynikowych, scenariuszy, logów oraz konfiguracji. Dodatkowo definiuje katalog roboczy oraz konwencje nazewnicze artefaktów. Drugi komponent gromadzi parametry wykonawcze, takie jak ścieżka do interpretera Pythona, nazwy skrótów, limity czasu wykonania oraz flagi sterujące (np. generowanie wariantu optymistycznego w scenariuszach).
Taki podział zapewnia pełną separację między warstwą interfejsu użytkownika a logiką wykonawczą. Dodanie nowego skryptu lub zmiana lokalizacji plików nie wymaga modyfikacji w warstwie UI – wystarczy aktualizacja odpowiednich wpisów w konfiguracji. Zastosowanie mechanizmu wstrzykiwania zależności (ang. dependency injection) eliminuje konieczność stosowania ścieżek (ang. hard-coded paths), co zwiększa elastyczność systemu i ułatwia testowanie jednostkowe. 

Orkiestracja procesu – ProcessingService
Centralnym elementem logiki aplikacji jest serwis ProcessingService, odpowiedzialny za orkiestrację kolejnych etapów przetwarzania danych. Komponent ten inicjuje sekwencyjne wywołania skryptów odpowiedzialnych za geokodowanie adresów, pozyskanie czasów przejazdu oraz tworzenie scenariuszy czasowych. Każdy etap kończy się weryfikacją kodu zakończenia procesu (0 – wykonanie poprawne, 2 – limit usług zewnętrznych, pozostałe – błąd krytyczny). Na podstawie uzyskanego statusu serwis podejmuje decyzję o kontynuacji lub przerwaniu pracy. W przypadku wykrycia błędu wykonywanie zostaje zakończone, zgodnie z zasadą przerwania (fail-fast), co pozwala na szybkie wykrycie i izolację źródła problemu oraz minimalizuje koszty propagacji błędów w kolejnych fazach. Równolegle zapisywany jest plik config.csv, zawierający parametry uruchomienia oraz dane wejściowe, które umożliwiają pełną replikację danego przebiegu. 
Takie podejście zapewnia powtarzalność eksperymentów oraz ułatwia analizę wyników w kontekście modyfikacji parametrów wykonawczych. Serwis ProcessingService został zrealizowany w sposób modułowy, co umożliwia rozszerzanie procesu o kolejne etapy bez konieczności ingerencji w logikę istniejących kroków czy format wymiany między warstwą webową a modułami obliczeniowymi. Dzięki temu aplikacja stanowi elastyczną platformę do dalszych eksperymentów obliczeniowych w obszarze VRPTW oraz rozszerzanie funkcjonalności modułu. Na rysunku 4 został przedstawiony diagram sekwencji, zawierający przebieg wywołań od formularza użytkownika po zakończenie procesu wraz z punktami decyzyjnymi po każdym etapie.

 
Rysunek 4 Diagram sekwencji przebiegu wywołań


System statusów i sygnalizacja postępu
Monitorowanie postępu procesu realizowane jest w sposób minimalistyczny poprzez pojedynczy plik tekstowy, nadpisywany kolejnymi komunikatami. Interfejs webowy cyklicznie odczytuje jego zawartość, aktualizując pasek statusu. Mimo prostoty, takie rozwiązanie jest w pełni wystarczające w kontekście aplikacji – użytkownik oczekuje bowiem na zakończenie całego procesu, a implementacja rozwiązań w czasie rzeczywistym (np. wykorzystując WebSocket) byłaby w tym wypadku nadmiarowa.
Zastosowanie konwencji prefiksów komunikatów ( ERROR:, COMPLETED: ) umożliwia warstwie prezentacji odróżnić stany i stosować odpowiednie formatowanie (np. kolory sygnalizujące sukces lub błąd). W przyszłości plik statusu mógłby zostać zastąpiony lekkim API REST zwracającym obiekt statusu w formacie JSON. Diagram stanów, zilustrowany na rysunku 5, prezentuje przejścia między głównymi fazami procesu.


 
Rysunek 5 Diagram stanów procesu przetwarzanie danych

Etap I: Geokodowanie ( Nominatim API )
Pierwszy etap przetwarzania danych odpowiada za przekształcenie adresów w pary współrzędnych geograficznych (szerokość i długość geograficzna). W tym celu wykorzystano publiczne API Nominatim , oparte na danych OpenStreetMap (OSM) . Proces geokodowania przebiega w sposób sekwencyjny, z zachowaniem przerw między zapytaniami (1 s), co zapewnia zgodność z polityką wykorzystania usługi. W przypadku przekroczenia limitu zwrotnego (HTTP 429) skrypt kończy się kodem 2, umożliwiając aplikacji interpretację zdarzenia jako przekroczenie limitu API. Wynik zapisywany jest w pliku dane_wejsciowe_geocoded.csv.

Etap II: Czasy przejazdu i dystanse ( OpenRouteService API)
Drugi etap realizuje pozyskanie czasów i odległości między wszystkimi parami lokalizacji za pomocą usługi OpenRouteService , również opartej na danych OSM. Dla każdej pary (i, j) wywoływane jest zapytanie /v2/directions/driving-car, zwracające czas przejazdu w sekundach i dystans w metrach. Dane są konwertowane odpowiednio do minut i kilometrów, a wyniki zapisywane w pliku czasy_przejazdu.csv.
Ze względu na ograniczenia darmowego planu API zastosowano wariant z pojedynczymi zapytaniami parowymi. Dla małych instancji złożoność obliczeniowa O(n²) jest akceptowalna. W przyszłości przewidziano możliwość zastąpienia tego podejścia przez usługę macierzą, co istotnie skróciłoby czas pozyskiwania danych.

Etap III: Generowanie scenariuszy czasowych E/P
Trzeci etap odpowiada za utworzenie wariantów czasów przejazdu dla scenariuszy oczekiwanego (E) i pesymistycznego (P) z wykorzystaniem danych o ruchu drogowym. Podstawowe czasy t_{ij}^Epochodzą z macierzy OpenRouteService, natomiast wartości pesymistyczne t_{ij}^Psą wyznaczane na podstawie zapytań do TomTom Routing API . Dla każdej pary lokalizacji (i,j) wykonywana jest sekwencja zapytań godzinowych w zakresie 08:00–18:00 czasu lokalnego, z parametrem traffic=true. Z otrzymanych wyników travelTimeInSeconds wybierany jest maksymalny czas przejazdu, który stanowi wartość t_{ij}^P. Takie podejście pozwala uchwycić najbardziej niekorzystne warunki ruchu w typowych godzinach operacyjnych. W przypadku braku odpowiedzi API związany z limitem zapytań stosowany jest mechanizm awaryjny, w którym ma miejsce przeskalowanie czasów oczekiwanych stałym współczynnikiem \beta=1.3. Mechanizm został wdrożony ze względu na niepewności związane z dostępem do API i limitem darmowych zapytań. Wyniki scenariuszy (oczekiwany, pesymistyczny, opcjonalnie optymistyczny) zapisywane są do pliku czasy_scenariusze.csv, a w plik z logami zawiera oznaczenia źródła danych (SRC=tomtom lub SRC=fallback, jeśli wykonany został mechanizm awaryjny). Tak zdefiniowany etap umożliwia tworzenie bardziej realistycznych scenariuszy czasowych, zwiększając wiarygodność modelu przy zachowaniu pełnej automatyzacji przetwarzania.

Budowa macierzy i okien czasowych
Zwieńczeniem procesu przetwarzania danych jest moduł vrp_common_utilities.py, który buduje macierze time_expected i time_pessimistic oraz struktury okien czasowych. Indeksacja rozpoczyna się od zera (magazyn), a wartości okien przeliczane są na minuty względem ustalonej godziny bazowej, co upraszcza późniejsze operacje porównawcze. Tak przygotowane dane stanowią ustandaryzowany kontrakt wejściowy dla modułów heurystycznych i optymalizacyjnych.

### Implementacja modułów optymalizacyjnych

Po etapie przygotowania i transformacji danych, ustandaryzowane struktury numeryczne – macierze czasów przejazdu oraz okna czasowe – stają się danymi wejściowymi dla modułów optymalizacyjnych. W architekturze aplikacji zaimplementowano dwuetapowe podejście do rozwiązywania problemu VRPTW. Pierwszy etap polega na szybkim wygenerowaniu dopuszczalnych rozwiązań początkowych za pomocą heurystyk konstrukcyjnych. Drugi etap wykorzystuje te rozwiązania jako punkt startowy dla metaheurystyki symulowanego wyżarzania, której celem jest iteracyjna poprawa jakościowa tras.

#### Heurystyki konstrukcyjne jako źródło rozwiązań początkowych

Celem heurystyk konstrukcyjnych jest szybkie znalezienie rozwiązań dopuszczalnych, czyli takich, które pokrywają wszystkie zdefiniowane punkty dostaw, jednocześnie respektując ograniczenia czasowe modelu. W ramach aplikacji zaimplementowano dwie klasyczne i szeroko stosowane w literaturze metody: heurystykę oszczędności Clarke'a i Wrighta oraz heurystykę zachłannego wstawiania. Obie procedury operują na tym samym zestawie danych wejściowych: macierzach czasów przejazdu (`time_expected`, `time_pessimistic`), macierzy odległości (`distance_km`) oraz słowniku okien czasowych.

**Heurystyka oszczędności (algorytm Clarke'a i Wrighta)**: Implementacja tej metody rozpoczyna się od obliczenia macierzy oszczędności dla wszystkich par klientów na podstawie macierzy dystansu. Następnie, w pętli, algorytm próbuje połączyć dwie trasy, wybierając połączenie o największej, jeszcze nieprzetworzonej oszczędności. Kluczowym elementem implementacji jest fakt, że każda propozycja nowego połączenia jest natychmiast weryfikowana przez centralny moduł `common_feasibility.py`. Jeśli nowo utworzona trasa spełnia wszystkie ograniczenia czasowe (filtr E/P i horyzont dnia), połączenie jest akceptowane. W przeciwnym razie jest odrzucane, a algorytm przechodzi do kolejnej najlepszej oszczędności. Proces kończy się, gdy wyczerpana zostanie lista możliwych do zrealizowania połączeń.

**Heurystyka zachłannego wstawiania (Greedy Insertion)**: Ta metoda została zaimplementowana w sposób iteracyjny. Algorytm utrzymuje listę nieprzypisanych jeszcze klientów i w każdej głównej iteracji wybiera jednego z nich. Następnie, w pętli wewnętrznej, dla wybranego klienta testowane są wszystkie możliwe pozycje wstawienia we wszystkich istniejących trasach. Dla każdej potencjalnej pozycji obliczany jest przyrost funkcji kosztu, a dopuszczalność ruchu jest weryfikowana przez moduł `common_feasibility`. Wybierane jest to wstawienie, które charakteryzuje się najmniejszym kosztem. Jeśli dla danego klienta nie uda się znaleźć żadnego dopuszczalnego miejsca w istniejących trasach, implementacja tworzy dla niego nową, jednoelementową trasę. Proces jest powtarzany, aż wszyscy klienci zostaną przypisani do tras.

Wynikiem działania obu heurystyk jest zestaw kompletnych, dopuszczalnych tras, który jest następnie utrwalany w postaci pliku w formacie JSON. Plik ten, o nazwie `routes_<dataset>_<algorytm>.json`, zawiera nie tylko listę tras (sekwencje indeksów punktów), ale również kluczowe metryki opisujące rozwiązanie, takie jak liczba użytych pojazdów, łączny dystans, suma czasów przejazdu (`sum_route_time_E`), maksymalny czas zakończenia ostatniej trasy (`makespan_E`) oraz łączny czas oczekiwania (`waiting_E`). Dzięki temu artefakty te stanowią w pełni audytowalny i powtarzalny punkt startowy dla dalszych etapów optymalizacji.

#### Centralny moduł weryfikacji dopuszczalności: Filtr E/P i kontrola horyzontu

Kluczowym elementem zapewniającym spójność i poprawność działania zarówno heurystyk, jak i metaheurystyki, jest scentralizowany moduł weryfikacji dopuszczalności trasy (`common_feasibility.py`). Jego zadaniem jest implementacja logiki filtru E/P oraz kontrola nieprzekraczalności horyzontu dnia. Każda kandydacka trasa lub modyfikacja trasy jest poddawana symulacji w dwóch scenariuszach czasowych: oczekiwanym (E) i pesymistycznym (P).

1.  **Weryfikacja okien czasowych**: Dla każdego punktu na trasie obliczany jest czas przyjazdu. Jeśli pojazd dotrze do klienta przed otwarciem jego okna czasowego, generowany jest czas oczekiwania, a obsługa rozpoczyna się o najwcześniejszej możliwej porze. Jeśli jednak czas przyjazdu (w scenariuszu E lub P) przekracza górną granicę okna czasowego, trasa jest uznawana za niedopuszczalną, a ruch ją generujący zostaje odrzucony.
2.  **Kontrola horyzontu dnia**: Czas zakończenia każdej trasy (powrotu do magazynu) jest weryfikowany w scenariuszu pesymistycznym. Jeśli przekracza on zdefiniowany horyzont operacyjny (`day_horizon`), trasa jest natychmiast odrzucana. Zastosowano tu mechanizm "fail-fast", który pozwala uniknąć kosztownych obliczeń pełnych metryk dla rozwiązań, które już na wstępnym etapie łamią fundamentalne ograniczenia.

Moduł ten nie tylko zwraca binarną informację o dopuszczalności (prawda/fałsz), ale także oblicza kluczowe metryki czasowe, takie jak czas oczekiwania czy czas zakończenia trasy, które są następnie wykorzystywane w funkcji celu. Centralizacja tej logiki gwarantuje, że wszystkie komponenty systemu optymalizacyjnego posługują się identyczną definicją "dobrej" trasy, co eliminuje ryzyko niespójności i ułatwia analizę wyników.

#### Metaheurystyka symulowanego wyżarzania (SA)

Jako metodę iteracyjnej poprawy jakości rozwiązań początkowych zaimplementowano algorytm symulowanego wyżarzania, którego kod znajduje się w pliku `sa_vrp.py`. Implementacja ta jest ściśle zintegrowana z architekturą aplikacji, wykorzystując te same moduły i struktury danych co heurystyki.

Proces optymalizacji rozpoczyna się od wczytania rozwiązania startowego, wygenerowanego wcześniej przez jedną z heurystyk. Główna pętla algorytmu jest kontrolowana przez klasyczny schemat chłodzenia geometrycznego, zdefiniowany przez parametry takie jak temperatura początkowa (`T_max`), końcowa (`T_min`) oraz współczynnik chłodzenia (`alpha`).

W każdej iteracji wewnętrznej pętli wykonywane są następujące kroki:
1.  **Generowanie sąsiada**: Za pomocą jednego z zaimplementowanych operatorów sąsiedztwa (`swap`, `relocate`, `two_opt` lub losowego wyboru w trybie `mixed`) tworzone jest nowe, kandydackie rozwiązanie.
2.  **Weryfikacja dopuszczalności**: Każda trasa w kandydackim rozwiązaniu jest sprawdzana przez centralny moduł `route_feasible_ep_classified`. Jeśli choć jedna trasa narusza ograniczenia czasowe (okno E/P lub horyzont dnia), całe rozwiązanie jest natychmiast odrzucane, a algorytm przechodzi do kolejnej próby. Ten krok gwarantuje, że przestrzenią poszukiwań są wyłącznie rozwiązania dopuszczalne.
3.  **Obliczenie kosztu i decyzja**: Jeśli rozwiązanie jest dopuszczalne, obliczana jest zmiana funkcji kosztu (Δ). Ruchy poprawiające jakość (Δ < 0) są akceptowane zawsze. Ruchy pogarszające (Δ > 0) są akceptowane z prawdopodobieństwem `exp(-Δ / T)`, które maleje wraz ze spadkiem temperatury. Co istotne, implementacja funkcji kosztu (`compute_cost`) celowo zeruje karę za spóźnienia, ponieważ mechanizm filtru E/P z twardymi oknami czasowymi uniemożliwia ich wystąpienie.

Algorytm śledzi najlepsze znalezione dotychczas rozwiązanie (`best`) i aktualizuje je za każdym razem, gdy zostanie odkryte rozwiązanie o niższym koszcie.

Wyniki działania algorytmu są zapisywane w sposób umożliwiający szczegółową analizę. Plik JSON zawiera finalny, najlepszy znaleziony zestaw tras (`best_routes`), jego koszt (`best_cost`), a także porównanie kluczowych metryk między rozwiązaniem początkowym a końcowym (`metrics_initial` vs `metrics_best`). Dodatkowo, w pliku zapisywany jest "ślad" procesu optymalizacji (`trace_improvements`), zawierający tylko te epoki, w których odnotowano poprawę najlepszego znanego rozwiązania. Opcjonalnie, zagregowane wyniki mogą być dopisywane do zbiorczego pliku CSV, co ułatwia prowadzenie serii eksperymentów i porównywanie wpływu różnych parametrów na jakość końcową.

### Integracja modułów i przepływ artefaktów w procesie optymalizacji

Architektura aplikacji tworzy spójny i w pełni audytowalny łańcuch przetwarzania danych, w którym każdy etap generuje trwały artefakt. Przepływ ten można podsumować następująco:
`Formularz (dane wejściowe)` → `Geokodowanie (współrzędne)` → `Czasy surowe (ORS API)` → `Scenariusze E/P (TomTom API)` → `Macierze i okna czasowe` → `Heurystyki (routes_*.json)` → `Symulowane Wyżarzanie` → `Wyniki końcowe (JSON/CSV)`.

Taka konstrukcja, oparta na niemutowalnych (niezmienianych) plikach pośrednich, gwarantuje pełną powtarzalność i identyfikowalność wyników. Możliwe jest odtworzenie całego procesu, zaczynając od dowolnego etapu, pod warunkiem dostępności jego pliku wejściowego. Ujednolicona indeksacja (gdzie magazyn zawsze ma indeks 0) oraz współdzielony moduł weryfikacji dopuszczalności zapewniają, że wszystkie komponenty systemu "rozumieją" dane w ten sam sposób.

### Potencjalne kierunki rozwoju i usprawnienia implementacji

Obecna implementacja w pełni realizuje założone cele badawcze. Dalsze prace mogłyby koncentrować się na usprawnieniach o charakterze inżynieryjnym, które podniosłyby elastyczność i łatwość prowadzenia rozbudowanych eksperymentów. Do potencjalnych usprawnień należą:
1.  **Ujednolicenie konwencji nazewniczych**: Standaryzacja nazw plików wynikowych (np. `summary` vs `routes`) w celu ułatwienia automatycznego przetwarzania.
2.  **Centralizacja konfiguracji eksperymentów**: Wprowadzenie jednego pliku konfiguracyjnego (np. w formacie YAML), który sterowałby całą serią uruchomień algorytmu SA z różnymi parametrami, zamiast przekazywać je z linii poleceń.
3.  **Rozbudowa testów jednostkowych**: Stworzenie zestawu testów dla modułu `feasibility`, pokrywających podstawowe przypadki: trasy w pełni dopuszczalnej, trasy naruszającej okno czasowe oraz trasy przekraczającej horyzont dnia.

Wprowadzenie tych zmian, choć nie jest krytyczne dla poprawności obecnych wyników, stanowiłoby naturalny krok w kierunku przekształcenia aplikacji w dojrzałą platformę do badań operacyjnych.

### Podsumowanie warstwy optymalizacyjnej

Zaprojektowana i zaimplementowana warstwa optymalizacyjna stanowi kompletne środowisko do rozwiązywania problemu VRPTW z filtrem E/P. Heurystyki konstrukcyjne dostarczają szybkich i dopuszczalnych rozwiązań bazowych, które następnie są efektywnie ulepszane przez metaheurystykę symulowanego wyżarzania. Centralny mechanizm weryfikacji dopuszczalności, uwzględniający zarówno okna czasowe w dwóch scenariuszach, jak i globalny horyzont dnia, zapewnia realizm operacyjny generowanych tras. Całość procesu, od danych wejściowych po finalne wyniki, jest w pełni zautomatyzowana i audytowalna dzięki trwałym artefaktom w formatach CSV i JSON.

[^tomtom]: TomTom Routing API – dokumentacja: https://developer.tomtom.com/routing-api/documentation (dostęp: 2025-11-07). Parametr `traffic=true` oraz `departAt` umożliwiają pobór prognozowanego czasu przejazdu dla konkretnej godziny.
