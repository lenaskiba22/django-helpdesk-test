# Testy czarnoskrzynkowe - zmianę liczb zapisywanych cyframi arabskimi na polskie nazwy  
# Zajęcia 1 zadanie 1

**Funkcja pod testami:** `convert_to_polish_name(number: int) -> str`  
**Zakres:** liczby całkowite z przedziału <0, 999 999>  
**Plik z testami:** `number_coverter_tester.py`  
**Liczba metod testowych:** 20  

## Założenia
- wynik to napis zapisany małymi literami,
- wyrazy rozdzielone pojedynczą spacją, bez spacji na początku i na końcu,
- `0` -> `"zero"`,
- liczba poza przedziałem -> `ValueError`,
- argument niebędący typem `int` -> `TypeError`.


### Reguła odmiany „tysiąc"

| Liczba tysięcy | Forma | Przykład |
|---|---|---|
| dokładnie 1 | `tysiąc` (bez słowa „jeden") | 1000 -> `tysiąc` |
| końcówka 2, 3, 4 | `tysiące` | 22 000 -> `dwadzieścia dwa tysiące` |
| końcówka 5-9 oraz 0 | `tysięcy` | 5000 -> `pięć tysięcy` |
| 12, 13, 14 (wyjątek od reguły wyżej) | `tysięcy` | 13 000 -> `trzynaście tysięcy` |
| liczby złożone z końcówką 1 | `tysięcy` | 21 000 -> `dwadzieścia jeden tysięcy` |

## Przypadki testowe

### Przypadki pozytywne

| ID | Co sprawdza | Przykładowe wejścia -> wyjścia |
|---|---|---|
| TC-01 | Zero - jedyna liczba nieskładana z rzędów | `0` -> `zero` |
| TC-02 | Jedności 1-9 | `5` -> `pięć` |
| TC-03 | Nastki 10-19 (nieregularne) | `15` -> `piętnaście` |
| TC-04 | Pełne dziesiątki 20-90 | `50` -> `pięćdziesiąt` |
| TC-05 | Dziesiątki z jednością | `47` -> `czterdzieści siedem` |
| TC-06 | Pełne setki 100-900 | `400` -> `czterysta` |
| TC-07 | Setki z resztą; brak dopisanego „zero" | `123` -> `sto dwadzieścia trzy` |
| TC-08 | **1000 to `tysiąc`, nie `jeden tysiąc`** | `1000` -> `tysiąc` |
| TC-09 | Forma `tysiące` (końcówka 2, 3, 4) | `22000` -> `dwadzieścia dwa tysiące` |
| TC-10 | Forma `tysięcy` (końcówka 5-9, 0) | `200000` -> `dwieście tysięcy` |
| TC-11 | **Wyjątek: 12, 13, 14 tysięcy -> `tysięcy`** | `13000` -> `trzynaście tysięcy` |
| TC-12 | **Wyjątek: złożone z końcówką 1 -> `tysięcy`** | `21000` -> `dwadzieścia jeden tysięcy` |
| TC-13 | Tysiące z resztą | `123456` -> `sto dwadzieścia trzy tysiące czterysta pięćdziesiąt sześć` |
| TC-14 | **Górna granica przedziału** | `999999` -> `dziewięćset dziewięćdziesiąt dziewięć tysięcy dziewięćset dziewięćdziesiąt dziewięć` |

### Format wyniku

| ID | Co sprawdza |
|---|---|
| TC-15 | Funkcja zwraca napis (`str`)|
| TC-16 | Brak spacji na brzegach i brak podwójnych spacji w środku |

### Przypadki negatywne

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-17 | `-1`, `-999999` | `ValueError` | Liczba ujemna jest poza przedziałem |
| TC-18 | `1000000`, `1234567` | `ValueError` | Wartość brzegowa - pierwsza liczba poza przedziałem |
| TC-19 | `"5"`, `3.5`, `None`, `[1]`, `{}` | `TypeError` | Niepoprawny typ odrzucony, a nie przekonwertowany |
| TC-20 | `5.0` | `TypeError` | Pułapka - wartość całkowita, ale typ `float` |

## Uruchomienie

```bash
python -m unittest number_coverter_tester -v
```

## Podział przypadków

- przypadki poprawne (słowniki i składanie nazw): 7
- odmiana słowa „tysiąc", w tym dwa wyjątki językowe: 5
- wartości brzegowe (`0`, `999 999`, `1 000 000`): 3
- format wyniku: 2
- przypadki negatywne (oczekiwany wyjątek): 4
