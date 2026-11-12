# Testy czarnoskrzynkowe 
# Zajęcia 1 zadanie 2

**System:** django-helpdesk służący do zgłoszeń  
**Repozytorium systemu:** (https://github.com/django-helpdesk/django-helpdesk)   
**Plik z testami:** `tests/test_blackbox.py`  
**Liczba przypadków testowych:** 31  


## Wybrane funkcje

Wybrałyśmy 6 obszarów z czterech warstw systemu: dwie funkcje dotyczą rozliczania czasu pracy, dwie to funkcje pomocnicze służace do eksportu danych czy filtrowania szablonu, jedna dotyczy powiązań między zgłoszeniami, a ostatnia dotyczy wprost cyklu życia zgłoszenia.

| Element | Moduł | Dlaczego ważny |
|---|---|---|
| `format_time_spent` | `helpdesk/lib.py` | Wyświetlanie czasu pracy nad zgłoszeniem w raportach |
| `convert_value` | `helpdesk/lib.py` | Zamiana wartości na ustalony format tekstowy przy eksporcie danych |
| `daily_time_spent_calculation` | `helpdesk/lib.py` | Rdzeń rozliczania czasu - ile czasu z przedziału liczy się wg godzin pracy |
| `in_list` | `helpdesk/templatetags/in_list.py` | Filtr szablonów sterujący wyświetlaniem elementów interfejsu |
| `num_to_link` | `helpdesk/templatetags/ticket_to_link.py` | Zamiana `#123` w treści na link do zgłoszenia (powiązane sprawy, duplikaty) |
| `Ticket.can_be_resolved` | `helpdesk/models.py` | Reguła cyklu życia zgłoszenia - czy można je rozwiązać, skoro zależy od innych zgłoszeń |

Funkcje `format_time_spent` i `daily_time_spent_calculation` razem tworzą podsystem rozliczania czasu pracy.

## Przypadki testowe

### `format_time_spent(time_spent) -> str`

w systemie można zapisywać, ile czasu pracownik poświęcił na zgłoszenie. Ta funkcja zamienia ten czas na tekst do wyświetlenia w raportach, w formacie GGh:MMm. Gdy nikt jeszcze nie pracował nad zgłoszeniem, wynikiem jest pusty tekst. Uważamy na to, że sekundy nie zaokrąglają się w górę oraz to, że czas dłuższy niż doba liczy się w godzinach

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-FTS-01 | `None` | `""` | Brak danych nie powoduje błędu |
| TC-FTS-02 | `timedelta(minutes=1)` | `"00h:01m"` | Podstawowy przypadek, zera wiodące |
| TC-FTS-03 | `timedelta(hours=1, minutes=5)` | `"01h:05m"` | Godziny i minuty jednocześnie |
| TC-FTS-04 | `timedelta(minutes=59, seconds=59)` | `"00h:59m"` | Wartość brzegowa - brak przeskoku do 1h |
| TC-FTS-05 | `timedelta(days=1, hours=2)` | `"26h:00m"` | Czas ponad dobę liczony sumarycznie w godzinach |

### `convert_value(value) -> str | wartość bez zmian`

Datę, godzinę lub datę z godziną zamienia na tekst w jednym, stałym formacie, żeby wszędzie wyglądały tak samo, a wszystko inne zostawia bez zmian. Uważamy na to aby każdy z trzech typów (data, godzina, data z godziną) ma swój format, a zwykłe wartości, w tym None, nie mogą zostać zmienione.

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-CV-01 | `datetime(2026, 10, 15, 17, 30, 45)` | `"2026-10-15T17:30"` | Format daty z godziną |
| TC-CV-02 | `date(2026, 10, 15)` | `"2026-10-15"` | Format samej daty |
| TC-CV-03 | `time(9, 5, 7)` | `"09:05:07"` | Format samej godziny |
| TC-CV-04 | `"abc"` | `"abc"` | Tekst przechodzi bez zmian |
| TC-CV-05 | `None` | `None` | `None` nie zamienia się na pusty string |

### `daily_time_spent_calculation(earliest, latest, open_hours) -> int`

Zwraca liczbę sekund z przedziału, które mieszczą się w godzinach pracy. Uważamy na to, czy przedział całkiem w godzinach pracy, wystający przed otwarcie lub po zamknięciu, całkiem poza godzinami, dokładnie równy godzinom pracy, o zerowej długości oraz błędna konfiguracja godzin (koniec przed początkiem). Dane w testach: poniedziałek, godziny otwarcia 9-17.

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-DTS-01 | 10:00-12:00 | `7200` | Przedział w całości w godzinach pracy |
| TC-DTS-02 | 08:00-10:00 | `3600` | Obcięcie części przed otwarciem |
| TC-DTS-03 | 16:00-18:00 | `3600` | Obcięcie części po zamknięciu |
| TC-DTS-04 | 18:00-20:00 | `0` | Przedział poza godzinami pracy - zero, nie wartość ujemna |
| TC-DTS-05 | 09:00-17:00 | `28800` (8h) | Wartość brzegowa - przedział równy oknu otwarcia |
| TC-DTS-06 | 10:00-10:00 | `0` | Wartość brzegowa - przedział zerowej długości |
| TC-DTS-07 | 10:00-12:00, godziny `(17, 9)` | `ImproperlyConfigured` | Przypadek negatywny - błędna konfiguracja zgłasza wyjątek |

### `in_list(value, arg) -> bool`

Sprawdza, czy wartość znajduje się w przekazanej kolekcji. Dzięki czemu szablon może np. pokazać lub ukryć jakiś element interfejsu. Uważamy czy wartość jest na liście, nie ma jej na liście oraz sytuacja, gdy zamiast listy przychodzi None. 

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-IL-01 | `"pizza"`, `["pizza", "pie", "cake"]` | `True` | Przypadek pozytywny |
| TC-IL-02 | `"sushi"`, `["pizza", "pie", "cake"]` | `False` | Przypadek negatywny |
| TC-IL-03 | `"pizza"`, `None` | `False` | `None` zamiast listy nie powoduje wyjątku |

### `num_to_link(text) -> str`

Zamienia wzorzec `#ID` na link do zgłoszenia, o ile zgłoszenie istnieje. Uważamy na pusty tekst, tekst bez odwołań, odwołanie do istniejącego zgłoszenia, odwołanie do nieistniejącego oraz sam znak # bez podanego numeru. Dane w testach: kolejka Support i jedno zgłoszenie.

| ID | Wejście | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-NTL-01 | `""` | `""` | Wartość brzegowa - pusty tekst |
| TC-NTL-02 | `"Brak odwołań"` | bez zmian | Tekst bez odwołań nie jest modyfikowany |
| TC-NTL-03 | `"Zobacz #<id> teraz"` | link do zgłoszenia, otaczający tekst zachowany | Istniejące zgłoszenie staje się linkiem |
| TC-NTL-04 | `"Zobacz #999999"` | bez zmian | Nieistniejące zgłoszenie - brak martwego linku |
| TC-NTL-05 | `"hashtag # bez numeru"` | bez zmian | Sam `#` bez cyfr nie jest odwołaniem |

### `Ticket.can_be_resolved -> bool`

Ze względu na to, że jedno zgłoszenie może zależeć od innych odpowiada na pytanie, czy zgłoszenie można już rozwiązać: True, gdy wszystkie zgłoszenia, od których zależy, są już załatwione, a False, gdy któreś nadal jest otwarte. Dane w testach: kolejka Support, zgłoszenie oraz zgłoszenia, od których ono zależy (TicketDependency)

| ID | Zależności zgłoszenia | Oczekiwane wyjście | Co sprawdza |
|---|---|---|---|
| TC-TCR-01 | brak | `True` | Nic nie blokuje rozwiązania |
| TC-TCR-02 | jedna otwarta | `False` | Otwarta zależność blokuje |
| TC-TCR-03 | jedna ponownie otwarta | `False` | Ponownie otwarta blokuje tak samo |
| TC-TCR-04 | jedna rozwiązana | `True` | Rozwiązana zależność nie blokuje |
| TC-TCR-05 | jedna zamknięta | `True` | Zamknięta zależność nie blokuje |
| TC-TCR-06 | jedna rozwiązana i jedna otwarta | `False` | Warunek dotyczy wszystkich zależności - wystarczy jedna otwarta |

## Uruchomienie

```bash
pip install -e .
python quicktest.py tests.test_blackbox -v 2
```

Testy obszarów 1–4 używają `SimpleTestCase` (funkcje czyste, bez bazy danych); obszary 5 i 6 używają `TestCase`, bo wymagają utworzenia zgłoszenia w bazie.

## Wynik

```
Ran 31 tests in 0.072s

OK
```

