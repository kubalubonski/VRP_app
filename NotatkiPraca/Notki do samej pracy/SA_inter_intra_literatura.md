# Sąsiedztwa w SA dla VRP – praktyka i literatura

W każdej iteracji algorytmu SA losowo wybierany jest operator oraz trasy i klienci do modyfikacji, co pozwala na realizację zarówno ruchów wewnątrz jednej trasy (intra-route), jak i między trasami (inter-route). Takie podejście jest typowe w literaturze VRP (Lin et al., 1999; Braysy & Gendreau, 2005) i zapewnia efektywną eksplorację przestrzeni rozwiązań.

**Źródła:**
- Lin, Yu, et al. "A simulated annealing heuristic for the vehicle routing problem with time windows." Computers & Operations Research 26.6 (1999): 651-665.
- Braysy, Gendreau. "Vehicle routing problem with time windows, Part I: Route construction and local search algorithms." Transportation Science 39.1 (2005): 104-118.

**Komentarz:**
W obu publikacjach stosuje się losowe wybieranie tras/klientów i operatorów, co prowadzi do naturalnego mieszania ruchów intra/inter. Adaptacyjne sterowanie proporcją jest możliwe, ale nie jest wymagane – losowanie jest uznawane za standardową praktykę w SA dla VRP.