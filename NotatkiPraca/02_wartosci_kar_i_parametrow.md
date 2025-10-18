# Wartości kar i parametrów w funkcji kosztu

Użyte wartości (domyślne w kodzie):
- koszt_km: **1.0**
- koszt_pojazdu: **900.0**
- kara_spóźnienie: **120.0** za minutę
- kara_horyzont: **120.0** za minutę

Dlaczego tak?
Kary czasowe (spóźnienia, przekroczenie horyzontu) są ustawione wysoko, żeby nawet kilka minut opóźnienia było droższe niż zysk z skrócenia dystansu czy zmniejszenia liczby pojazdów. To typowe podejście w literaturze VRPTW – priorytet terminowości nad minimalizacją kilometrów. Stały koszt pojazdu jest na tyle duży, by nie generować tras bez potrzeby, ale nie blokuje podziału gdy spóźnienia byłyby zbyt duże.

Wartości można zmieniać w parametrach uruchomienia, jeśli chcesz testować inne proporcje.
