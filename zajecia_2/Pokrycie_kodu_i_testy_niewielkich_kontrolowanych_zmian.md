# Pokrycie kodu i testy niewielkich kontrolowanych zmian  
# Zajęcia 2 zadanie 2


**Zestaw testów - testy z 1 zajęć:** `tests/test_blackbox.py`  
**Narzędzie:** `coverage.py`

Badane funkcje:

| Funkcja | Plik |
|---|---|
| `format_time_spent` | `src/helpdesk/lib.py` |
| `convert_value` | `src/helpdesk/lib.py` |
| `daily_time_spent_calculation` | `src/helpdesk/lib.py` |
| `in_list` | `src/helpdesk/templatetags/in_list.py` |
| `num_to_link` | `src/helpdesk/templatetags/ticket_to_link.py` |
| `Ticket.can_be_resolved` | `src/helpdesk/models.py` |

## Uruchomienie z pomiarem pokrycia

```bash
pip install -e .
coverage run --branch --source=helpdesk.lib,helpdesk.templatetags.in_list,helpdesk.templatetags.ticket_to_link,helpdesk.models quicktest.py tests.test_blackbox
coverage json -o coverage.json
```

Cały zestaw 31 testów przechodzi (`OK`).

## Ile linii nie zostało pokrytych

Licząc tylko instrukcje należące do 6 badanych funkcji (z pominięciem reszty ogromnych plików `lib.py`/`models.py`, które zawierają też niezwiązany kod):

| Funkcja | Instrukcji | Niepokrytych |
|---|---|---|
| `format_time_spent` | 5 | 0 |
| `convert_value` | 8 | 0 |
| `daily_time_spent_calculation` | 24 | **2** |
| `in_list` | 2 | 0 |
| `num_to_link` | 17 | 0 |
| `can_be_resolved` | 5 | 0 |
| **Razem** | **61** | **2** |

**Sumarycznie niepokryte: 2 linie**, obie w `daily_time_spent_calculation`:

```python
262  if latest_f >= MIDNIGHT and end == MIDNIGHT:
263      time_spent_seconds += 1          # NIEPOKRYTE

...

272  if latest_f < start:
273      latest = latest.replace(         # NIEPOKRYTE
             hour=start_hour, minute=start_minute, second=start_second
         )
```

Linia 263 wykonuje się tylko wtedy, gdy koniec przedziału (`latest`) przypada na samą północ i skonfigurowana godzina zamknięcia wynosi dokładnie północ, gdzie domyślna wartość `MIDNIGHT = 23.9999`, używana gdy dla danego dnia tygodnia nie podano godzin otwarcia. Żaden z 7 testów `daily_time_spent_calculation` nie używa ani czasu blisko północy, ani brakującego wpisu dla dnia tygodnia, ponieważ wszystkie korzystają z jawnie podanych godzin `(9, 17)`.
Linia 273 wykonuje się, gdy cały przedział (`earliest` i `latest`) przypada przed otwarciem, a w obecnym zestawie nie ma takiego przypadku, istnieje tylko test na przedział przed otwarciem (`test_interval_starting_before_opening_is_clipped`, 8:00-10:00 przy otwarciu 9-17), ale tam `latest` (10:00) mieści się już w godzinach pracy, więc wtedy warunek na linii 272 nie jest spełniony.

## Testy odpowiedzialne za wykonanie poszczególnych gałęzi

### `format_time_spent`
| Gałąź | Test |
|---|---|
| `if time_spent:` - prawda | `test_hours_and_minutes`, `test_just_below_one_hour`, `test_more_than_one_day_is_counted_in_hours`, `test_one_minute` |
| `else:` (fałsz) | `test_none_gives_empty_string` |

### `convert_value`
| Gałąź | Test |
|---|---|
| `type(value) is datetime` | `test_datetime_is_formatted_as_string` |
| `elif type(value) is date` | `test_date_is_formatted_as_string` |
| `elif type(value) is time` | `test_time_is_formatted_as_string` |
| `else:` | `test_none_is_returned_unchanged`, `test_string_is_returned_unchanged` |

### `daily_time_spent_calculation`
| Gałąź | Test |
|---|---|
| walidacja błędna (`raise ImproperlyConfigured`) | `test_start_after_end_is_rejected` |
| `if latest_f >= MIDNIGHT and end == MIDNIGHT:` | **żaden** (patrz wyżej) |
| `if earliest_f < start:` (clip początku) | `test_interval_starting_before_opening_is_clipped` |
| `elif earliest_f >= end:` (początek po zamknięciu) | `test_interval_entirely_after_closing` |
| `if latest_f < start:` (clip końca od dołu) | **żaden** (patrz wyżej) |
| `elif latest_f >= end:` (clip końca od góry) | `test_interval_ending_after_closing_is_clipped`, `test_interval_entirely_after_closing`, `test_interval_exactly_equal_to_open_window` |
| żadna z gałęzi clipowania (przedział w całości wewnątrz) | `test_interval_inside_open_hours`, `test_zero_length_interval` |

### `in_list`
Nie ma żadnej gałęzi. Wszystkie trzy testy (test_value_present, test_value_absent, test_none_instead_of_list) wykonują tę samą jedyną linię.

### `num_to_link`
| Gałąź | Test |
|---|---|
| `if text == "":` - prawda (wczesny return) | `test_empty_string` |
| pętla `for match in ...` - 0 dopasowań | `test_hash_without_digits_is_unchanged`, `test_text_without_reference_is_unchanged` |
| pętla - ≥1 dopasowanie | `test_reference_to_existing_ticket_becomes_link`, `test_reference_to_missing_ticket_is_left_as_text` |
| `try: Ticket.objects.get(...)` - sukces | `test_reference_to_existing_ticket_becomes_link` |
| `except Ticket.DoesNotExist:` | `test_reference_to_missing_ticket_is_left_as_text` |
| `if ticket:` - prawda (budowa linku) | `test_reference_to_existing_ticket_becomes_link` (jedyny test!) |

### `can_be_resolved`
nie ma żadnej gałęzi. Różnice między sześcioma testami (test_no_dependencies, test_dependency_open_blocks, test_dependency_reopened_blocks, test_dependency_resolved_allows, test_dependency_closed_allows, test_one_open_among_resolved_blocks) dotyczą tylko danych przekazanych do bazy, nie ścieżki kodu, każdy z nich wykonuje dokładnie te same 3 linie.

## Testy wykonujące te same fragmenty kodu

Testy, które w obrębie badanej funkcji wykonują **identyczny** zestaw linii:

| Funkcja | Testy wykonujące ten sam fragment |
|---|---|
| `format_time_spent` | `test_hours_and_minutes`, `test_just_below_one_hour`, `test_more_than_one_day_is_counted_in_hours`, `test_one_minute` (wszystkie 4 - gałąź "prawda") |
| `convert_value` | `test_none_is_returned_unchanged`, `test_string_is_returned_unchanged` (gałąź `else`) |
| `daily_time_spent_calculation` | `test_interval_ending_after_closing_is_clipped` i `test_interval_exactly_equal_to_open_window` (identyczne); osobno `test_interval_inside_open_hours` i `test_zero_length_interval` (identyczne) |
| `num_to_link` | `test_hash_without_digits_is_unchanged` i `test_text_without_reference_is_unchanged` (pętla 0 dopasowań) |
| `in_list` | wszystkie 3 testy - brak rozgałęzień, więc technicznie wykonują tę samą jedyną linię |
| `can_be_resolved` | wszystkie 6 testów - brak rozgałęzień, technicznie ta sama sekwencja 3 linii |

## Fragmenty kodu nieosiągalne dla danych zgodnych ze specyfikacją

**Nie ma fragmentów badanych, które są nieosiągalne dla danych zgodnych ze specyfikacją, 6 funkcji nie jest strukturalnie nieosiągalna.** Obie niepokryte linie (263 i 273 w `daily_time_spent_calculation`) dają się osiągnąć poprawnymi, zgodnymi ze specyfikacją danymi, tylko po prostu obecny zestaw 7 testów ich nie dostarcza:

Linię 263 osiąga np. wywołanie z `latest` ustawionym na `23:59:59,65` tego samego dnia i `open_hours` bez wpisu dla tego dnia tygodnia (domyślne `MIDNIGHT`),
Linię 273 osiąga przedział w całości przed otwarciem, np. `earliest=6:00, latest=8:00` przy godzinach otwarcia `9-17`.

## Niewielkie kontrolowane zmiany

Dla każdej z 6 funkcji wprowadzono co najmniej jedną niewielką, kontrolowaną zmianę, łącznie 8, zgodnie z typami podanymi w poleceniu. Po każdej zmianie uruchomiono cały zestaw 31 testów, zanotowano wynik, a **przed kolejną zmianą kod przywrócono do oryginału**.

|   | Funkcja | Rodzaj zmiany | Zmiana w kodzie | Wynik testów | Test, który wykrył (lub powinien wykryć) |
|---|---|---|---|---|---|
| M1 | `format_time_spent` | zmiana zwracanej wartości | `time_spent = ""` - `time_spent = "00h:00m"` | **1 FAIL** | `test_none_gives_empty_string` |
| M2 | `convert_value` | zmiana zwracanej wartości | `return value` - `return str(value)` | **1 FAIL** | `test_none_is_returned_unchanged` |
| M3 | `daily_time_spent_calculation` | usunięcie zgłaszanego wyjątku | usunięto `raise ImproperlyConfigured(...)` | **1 FAIL** | `test_start_after_end_is_rejected` |
| M4 | `daily_time_spent_calculation` | zamiana `and` na `or` | `latest_f >= MIDNIGHT and end == MIDNIGHT` - `... or ...` | **OK - NIE WYKRYTO** | *(powinien wykryć test z `latest` blisko północy i domyślną konfiguracją dnia - taki test nie istnieje)* |
| M5 | `daily_time_spent_calculation` | zmiana wartości granicznej | `MIDNIGHT = 23.9999` - `MIDNIGHT = 23.99` | **OK - NIE WYKRYTO** | *(powinien wykryć test korzystający z domyślnych/brakujących godzin otwarcia dla danego dnia - taki test nie istnieje)* |
| M6 | `in_list` | zamiana `or` na `and` | `arg or []` - `arg and []` | **2 niepowodzenia** | `test_value_present` (FAIL), `test_none_instead_of_list` (ERROR) |
| M7 | `num_to_link` | zamiana `==` na `!=` | `if text == "":` - `if text != "":` | **1 FAIL** | `test_reference_to_existing_ticket_becomes_link` |
| M8 | `can_be_resolved` | zmiana zwracanej wartości | `return not unresolved_deps.exists()` - `return unresolved_deps.exists()` | **6 FAIL** | wszystkie testy `TicketCanBeResolvedTests` |

### Komentarz do wyników

M4 i M5 nie zostały wykryt, ponieważ obie zmiany dotyczą dokładnie tego fragmentu `daily_time_spent_calculation`, który już w analizie pokrycia  okazał się niepokryty: warunku na linii 262 oraz stałej `MIDNIGHT`, która ma znaczenie tylko wtedy, gdy godziny otwarcia dla danego dnia nie są jawnie podane. Skoro żaden test nie ćwiczy tej ścieżki, żaden test nie mógł też wykryć błędu w tej ścieżce, kod, którego testy nie wykonują, może zawierać dowolny błąd bez żadnego ostrzeżenia.

Dla M7 zmiana `==` na `!=` powoduje, że funkcja dla każdego niepustego tekstu natychmiast zwraca go bez żadnego przetwarzania pomijąc całą logikę zamiany `#123` na link, a mimo to tylko jeden z pięciu testów `NumToLinkTests` to wykrył - `test_reference_to_existing_ticket_becomes_link`. Pozostałe cztery testy przeszły, bo ich oczekiwany wynik przypadkiem pokrywa się z „tekstem bez zmian": `test_empty_string` (pusty tekst faktycznie zostaje pusty), `test_text_without_reference_is_unchanged` i `test_hash_without_digits_is_unchanged`,oczekują tekstu bez zmian - i taki dostają, tylko z zupełnie innego powodu niż zamierzony, `test_reference_to_missing_ticket_is_left_as_text` też oczekuje tekstu bez zmian. To pokazuje, że pokrycie linii/gałęzi samo w sobie nie gwarantuje wykrycia błędu.

Dla M6 zamiana `or` na `and` w `arg and []` powoduje, że dla niepustej listy wyrażenie `arg and []` zwraca `[]`,bo w Pythonie `and` zwraca drugi operand, gdy pierwszy jest prawdziwy, więc `test_value_present` dostaje `False` zamiast `True` (FAIL). Dla `None` natomiast `None and []` zwraca `None`, a `value in None` rzuca `TypeError` zamiast zwrócić `False`, stąd `ERROR`, a nie zwykły `FAIL`, przy teście `test_none_instead_of_list`.
