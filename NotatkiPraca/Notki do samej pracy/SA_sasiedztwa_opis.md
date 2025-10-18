# Sąsiedztwa w SA dla VRP – opis

W algorytmie SA dla VRP stosujemy cztery operatory sąsiedztwa:

1. **swap** – zamiana miejscami dwóch klientów (może być intra-route lub inter-route).
2. **relocate** – przeniesienie klienta z jednej pozycji do innej (w tej samej trasie lub do innej trasy).
3. **two_opt** – odwrócenie fragmentu trasy (tylko intra-route; poprawia lokalny układ klientów).
4. **insertion** – wyjęcie klienta z jednej trasy i wstawienie go w dowolne miejsce (intra lub inter-route).

Wybór intra/inter-route jest realizowany losowo: w każdej iteracji operator losuje trasę/trasy i klientów, więc ruch może dotyczyć jednej trasy lub kilku, zgodnie ze standardową praktyką w literaturze VRP.