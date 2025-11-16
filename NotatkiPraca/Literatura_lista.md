# Lista literatury – skróty i zastosowanie

| Skrót | Pozycja (placeholder) | Zastosowanie w tekście |
|-------|-----------------------|-------------------------|
| TothVigo | Toth, Vigo (eds.), *The Vehicle Routing Problem* | Definicje VRP/VRPTW, klasy wariantów (2.1) |
| LaporteReview | Laporte, *Fifty Years of VRP* | Kontekst, znaczenie problemu (1, 2.1) |
| Solomon1987 | Solomon, *Algorithms for VRPTW* | Profile okien, benchmark, instancje (2.3, 2.6, 3.4) |
| Desrochers1992 | Desrochers et al., *New Optimization Algorithm for VRPTW* | Trudność czasowa, horyzont dnia (2.4) |
| ClarkeWright1964 | Clarke & Wright, *Scheduling of Vehicles* | Heurystyka Savings (4.1) |
| InsertionClassic | (Klasyczne źródło insertion) | Heurystyka wstawiania (4.1) |
| Kirkpatrick1983 | Kirkpatrick et al., *Optimization by Simulated Annealing* | Mechanizm SA (4.2) |
| Cerny1985 | Černý, *Thermodynamical Approach to TSP* | Fundament SA (4.2) |
| Osman1993 | Osman, *Metaheuristics for VRP* | Zastosowanie SA do VRP (4.2, 4.3) |
| LinSA_VRPTW | Lin et al., *SA for VRPTW* | Dobór sąsiedztw (4.3) |
| TabuVRP | Gendreau/Hertz/Laporte, *Tabu Search for VRP* | Alternatywna metaheurystyka (4.2/5.7) |
| DorigoACS | Dorigo & Gambardella, *ACS* | Spektrum metaheurystyk (Wstęp, 4.2) |
| PrinsEA | Prins, *Evolutionary Algorithm for VRP* | Inne podejście – kontekst (4.2) |
| RobustVRPTW | Sungur/Ordonez/Dessouky, *Robust VRPTW* | Robust vs filtr E/P (2.3, 2.7) |
| BertsimasSim | Bertsimas & Sim, *Price of Robustness* | Kompromis koszt–robustness (2.7) |
| StochasticTravelTimes | (Źródło dot. stochastycznych czasów) | Uzasadnienie potrzeb scenariuszy (2.3) |
| PukaEPO2025 | Puka R., Skalna I., Duda J., Derlecki T., "EPO Extension of Dispatching Rules to Minimize Effects of Time Uncertainty in Production Scheduling", Applied Sciences 15(13):7408, 2025, doi:10.3390/app15137408 | Adaptacja idei EPO – filtr dwóch scenariuszy w VRPTW (1.1, 1.3, 1.9) |
| CordeauTS | Cordeau et al., *Unified TS Heuristic* | Balansowanie tras, trade-off (5.6) |
| VidalHGS | Vidal et al., *Hybrid Genetic Search* | Zaawansowane metody, balancing (4.7/5.7) |
| Uchoa2017 | Uchoa et al., *New Benchmark Instances (CVRPLIB)* | Uzasadnienie syntetycznych danych (3.4) |
| ParamTuning | Lopez-Ibanez et al., *Adaptive Parameter Control* | Rozszerzenia (4.7, 6.3) |

Uwagi: Zastąp placeholdery pełnymi danymi bibliograficznymi przed finalizacją. Można dodać DOI.

---
Notka stylu (aktualizacja – przypisy dolne):
1. Akapity krótkie (3–6 zdań); pierwsze zdanie wyznacza zakres lub tezę akapitu.
2. Definicje: najpierw zdanie opisowe, potem wzór \( \) lub blok \[ \] (jeśli dłuższy); unikać nadmiaru symboli w jednym wzorze.
3. Cytowania: w wersji roboczej używać skrótów w nawiasach kwadratowych po frazie źródłowej (np. klasyczny VRPTW [Solomon1987]); przy składzie końcowym w Word/LaTeX konwertować skróty na przypisy dolne z pełną informacją. Jeden akapit → zwykle jeden przypis jeśli źródła się pokrywają; gdy różne zakresy merytoryczne, dopuszczalne 2–3 przypisy.
4. Możliwa forma: zdanie kończy się kropką i numerem przypisu (np. „…model quasi‑robust.”[^12]) – numeracja automatyczna w edytorze końcowym.
5. Unikać dygresji historycznych >2 zdań w sekcjach technicznych – przenieść do Wstępu lub tła literaturowego.
6. Przy nowym pojęciu (filtr E/P) najpierw intuicja (dlaczego), potem formalny warunek (jak) – dwa osobne zdania lub dwa krótkie akapity.
7. Lista uproszczeń jako punktor + konsekwencja po myślniku; przy wielu punktach ostatni akapit z syntetycznym skutkiem dla interpretacji wyników.
8. Ograniczyć przymiotniki wartościujące („bardzo”, „ogromny”); preferować neutralne („istotny” tylko jeśli poparte metryką).
9. Spójne skróty: E, P, SA, VRPTW, H – nie rozwijać ponownie po pierwszej definicji w rozdziale.
10. Weryfikacja przypisów: przed final export każdy skrót [Solomon1987] odwzorowany w pełny zapis bibliograficzny w przypisie lub w systemie referencji (Zotero/BibTeX).
