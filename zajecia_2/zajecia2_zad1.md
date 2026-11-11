# Analiza weryfikacji pokrycia kodu

**funkcja pod testami:** `convert_to_polish_name(number: int) -> str`  
**plik z implementacją (z eportalu):** `number_converter.py`  
**plik z testami:** `number_converter_tester.py` (20 metod testowych, TC-01 do TC-20)  
**narzędzie:** `coverage.py`  

## Poprawki w testach

Testy uruchomiono bez żadnych zmian w pliku testowym:

```bash
python -m unittest number_converter_tester -v
```

Zestaw uruchamia się poprawnie, więc nie były potrzebne żadne poprawki, żeby testy w ogóle zadziałały. Wynik to jednak 17 testów zakończonych sukcesem i 3 niepowodzenia:

```
FAIL: test_one_thousand_has_no_jeden
AssertionError: 'jeden tysiąc' != 'tysiąc'

FAIL: test_thousands_with_remainder (number=1001)
AssertionError: 'jeden tysiąc jeden' != 'tysiąc jeden'

FAIL: test_thousands_with_remainder (number=1234)
AssertionError: 'jeden tysiąc dwieście trzydzieści cztery' != 'tysiąc dwieście trzydzieści cztery'

Ran 20 tests in 0.006s
FAILED (failures=3)
```

Niepowodzenia te to nie są błędy testów, testy poprawnie wykryły błąd w kodzie: dla liczby 1000 i liczb z nią związanych funkcja zwraca `"jeden tysiąc"` zamiast `"tysiąc"`. Ponieważ zastosowano podejście czarnoskrzynkowe, testy pozostawiono bez zmian (nie są dopasowywane do błędów implementacji), bo to one są tu punktem odniesienia, a nie kod.

## Pokrycie całego zestawu testów

```bash
coverage erase
coverage run --branch --source=number_converter -m unittest number_converter_tester
coverage report -m
```

```
Name                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------
number_converter.py      37      1     22      1    97%   25
-----------------------------------------------------------------
TOTAL                    37      1     22      1    97%
```

Cały zestaw 20 testów pokrywa 97% linii i rozgałęzień kodu funkcji (36 z 37 instrukcji), więc mimo 1 niepowodzenia pokrycie kodu jest wysokie. Należy jednak pamiętać, że pokrycie i poprawność to dwie różne miary: kod może być w dużej mierze testowany, a mimo to zwracać błędne wyniki.

## Przypadek testowy z największym samodzielnym pokryciem

Każdą z 20 metod testowych uruchomiono osobno (bez wsparcia pozostałych):

```bash
coverage erase
coverage run --branch --source=number_converter -m unittest number_converter_tester.ConvertToPolishNameTests.<nazwa_testu>
coverage report -m
```

Największe samodzielne pokrycie osiąga:

`test_no_extra_whitespace` (TC-16) - 90% (34/37 linii, 19/22 rozgałęzień pokryte):

```
Name                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------
number_converter.py      37      3     22      3    90%   3, 25, 57
-----------------------------------------------------------------
TOTAL                    37      3     22      3    90%
```

Test sprawdza tylko, czy wynik nie ma zbędnych spacji, ale robi to na 8 liczbach (`0, 7, 15, 70, 100, 1000, 10500, 999999`) obejmujących różne zakresy wartości, dzięki czemu przy okazji przechodzi przez większość kodu funkcji.
Wysokie pokrycie zawdzięcza się zatem różnorodności liczb użytych w jednej metodzie, a nie celowi samego testu.

Dla porównania, pozostałe testy osiągały pokrycie od **7%** (testy odrzucenia wartości spoza zakresu `<0, 999999>`, ponieważ funkcja wyrzuca wyjątek od razu na wejściu, więc reszta logiki konwersji w ogóle się nie wykonuje) do **86%** (`test_thousands_with_remainder`). 

Nawet najlepszy pojedynczy test (90%) nie dorównuje pełnemu zestawowi wszystkich 20 testów razem (97%).

## Linie niewykonane

Przy pełnym zestawie 20 testów niepokryta jest linia 25.:

```python
23  def three_digits_to_words(n):
24      if n == 0:
25          return ""        # niepokryte
```

Jest to spowodowane tym, że `three_digits_to_words` jest wywoływana tylko wtedy, gdy liczba tysięcy (`thousands`) lub reszta (`remainder`) jest większa od zera, co wynika to z warunków `if thousands > 0:` (linia 53) i `if remainder > 0:` (linia 61), które są spełnione przed każdym wywołaniem tej funkcji. W efekcie `three_digits_to_words` nigdy nie dostaje w argumencie `0`, więc warunek w linii 24 nigdy nie jest prawdziwy, a linia 25 nigdy się nie wykonuje.

Żadne poprawne wywołanie `convert_to_polish_name` z liczby z przedziału `<0, 999999>` nie jest w stanie dotrzeć do tej linii, to jest nieużywany kod wynikający ze struktury funkcji (zabezpieczenie na wypadek wywołania z zerem, które w obecnej logice nigdy nie następuje). Nie da się więc dopisać sensownego przypadku testowego z czarnej skrzynki, który pokryłby tę linię, ponieważ to wymagałoby wywołania `three_digits_to_words(0)` bezpośrednio, czyli testu znającego wnętrze implementacji (test białoskorzynkowy), a nie tylko wejście/wyjście funkcji `convert_to_polish_name`.
