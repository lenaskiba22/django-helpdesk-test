# Automatyzacja testu integracyjnego
# Zajęcia 3 zadanie 2

## 1. Wybór wariantu i uzasadnienie

Wybrano wariant A ze względu na charakter badanego systemu. Aplikacja Django ma wbudowany framework testowy TestCase, oparty na relacyjnej bazie danych. Pozwala na automatyzację testu integracyjnego ręcznie przeprowadzonego w Zadaniu 1. 

Django dostarcza gotowe narzędzia `django.test.TestCase` do tworzenia izolowanego stanu testowego, uruchamiania logiki aplikacji i automatycznej weryfikacji wyników co pasuje do wariantu A.

---

## 2. Przedmiot testu


W ramach zadania 2 zautomatyzowano test integracyjny stworzony w zadaniu 1, który sprawdzał współpracę:
- modułu zależności zgłoszeń (`TicketDependency` / `can_be_resolved`),
- modułu zapisu statusu zgłoszenia (`Ticket.save()` oraz `update_ticket()`).

---

## 3. Kod testu

Plik: `tests/test_ticket_dependency_integration.py`

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from helpdesk.models import Ticket, TicketDependency, Queue
from helpdesk.update_ticket import update_ticket


class TicketDependencyIntegrationTest(TestCase):

    def setUp(self):
# zgłoszenie A zależy od zgłoszenia B, a B ma status Open.
        self.queue = Queue.objects.create(title="Test Queue", slug="test")
        self.ticket_b = Ticket.objects.create(
            title="Zgłoszenie B", queue=self.queue, status=Ticket.OPEN_STATUS
        )
        self.ticket_a = Ticket.objects.create(
            title="Zgłoszenie A", queue=self.queue, status=Ticket.OPEN_STATUS
        )
        TicketDependency.objects.create(ticket=self.ticket_a, depends_on=self.ticket_b)
        self.user = get_user_model().objects.create(username="tester", is_staff=True)

    def test_save_does_not_resolve_ticket_with_open_dependency(self):
# sprawdza rezultat integracji przy bezpośrednim zapisie modelu
        self.ticket_a.status = Ticket.RESOLVED_STATUS
        self.ticket_a.save()
        self.ticket_a.refresh_from_db()

        self.assertNotEqual(
            self.ticket_a.status,
            Ticket.RESOLVED_STATUS,
            "Integracja nieudana: Ticket.save() pozwolił rozwiązać "
            "zgłoszenie z otwartą zależnością (ticket B wciąż Open)."
        )

    def test_update_ticket_does_not_resolve_ticket_with_open_dependency(self):
# sprawdza rezultat integracji przy zapisie przez funkcję update_ticket(),

        update_ticket(self.user, self.ticket_a, new_status=Ticket.RESOLVED_STATUS)
        self.ticket_a.refresh_from_db()

        self.assertNotEqual(
            self.ticket_a.status,
            Ticket.RESOLVED_STATUS,
            "integracja nieudana: update_ticket() pozwolił rozwiązać "
            "zgłoszenie z otwartą zależnością (ticket B wciąż Open)."
        )
```

---

## 4. Spełnienie wymagań Wariantu A

| Wymaganie | Spełnienie |
|---|---|
| Przygotowuje wymagany stan | ODtwarzając warunki zadania 1, test przygootwuje wymagany stan poprzez: `setUp()` tworzenie Queue, Ticket A, Ticket B, TicketDependency oraz użytkownika  |
| Sprawdza rezultat integracji | Test weryfikuje status zgłoszenia A po wywołaniu `save()` i `update_ticket()`, czyli efekt współdziałania modułu zależności i modułu zapisu |
| Zawiera jednoznaczne asercje | fragment `self.assertNotEqual(self.ticket_a.status, Ticket.RESOLVED_STATUS, ...)` sprawdza czy status ticketu a nie jest równy ststausowi resolved. Jeśli asercja się nie powiedzie daje komunikat o niepowodzeniu|
| Da się uruchomić ponownie | Test da się uruchomić ponownie, niezależny od ręcznie wprowadzanych danych |
| Sprząta dane / izolowane środowisko | Django tworzy osobną bazę testową przed uruchomieniem i usuwa ją po zakończeniu. |

---

## 5. Użyte narzędzie

Uzytko Django `TestCase`wbu bedący wbudowanym frameworkiem testowym Django, opartym na module `unittest`, uruchamianym przez `manage.py test`.

## 6. Instrukcja uruchomienia

```powershell
$env:DJANGO_HELPDESK_SECRET_KEY="123"
cd standalone
python manage.py test tests.test_ticket_dependency_integration -v 2
```

W naszym przypadku wymagało to uprzedniego tymczasowego nadpisania `DATABASES` na SQLite w `local_settings.py`.

## 7. Wynik testu

Oba testy zakończyły się niepowodzeniem, potwierdzając w sposób zautomatyzowany błąd integracyjny, który został wykryty manualnie w Zadaniu 1:

```
Found 2 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).

Failure
AssertionError: 3 == 3 : Integracja nieudana: Ticket.save() pozwolił rozwiązać
zgłoszenie z otwartą zależnością (ticket B wciąż Open).

Failure
AssertionError: 3 == 3 : integracja nieudana: update_ticket() pozwolił rozwiązać
zgłoszenie z otwartą zależnością (ticket B wciąż Open).

Destroying test database for alias 'default'...
```

Wartość 3 odpowiada statusowi `RESOLVED_STATUS` w modelu `Ticket`. Zarówno przy zapisie bezpośrednim (`save()`), jak i przez funkcję `update_ticket()`, zgłoszenie A zostało błędnie oznaczone jako rozwiązane, mimo nierozwiązanej zależności od zgłoszenia B.

Interpretacja wyniku: wynik ten jest oczekiwany i poprawny. Test został napisany tak, aby weryfikować zgodność i sprawdzać błąd wykryty w Zadaniu 1, test słusznie kończy się niepowodzeniem.

## 8. Co było realne, a co zastąpiono atrapą

Wszystkie komponenty biorące udział w teście były rzeczywiste: prawdziwy model `Ticket`, prawdziwa logika `TicketDependency` i `update_ticket()`. Baza danych była rzeczywistą bazą testową Django została jedynie tymczasowo zmieniony z PostgreSQL na SQLite na potrzeby lokalnego środowiska testowego, bez żadnej zmiany logiki aplikacji. Nie zostały zastosowane żadne atrapy.

## 9. Ograniczenia automatyzacji

Test pokrywa wyłącznie warstwę backendu (model i logikę zapisu statusu). Nie weryfikuje warstwy UI, ta część została sprawdzona wyłącznie manualnie, w Zadaniu 1. Aby przetestować warstwę UI wymagałoby to dodatkowo testów np. w Selenium z wariantu B.


Kolejnym ograniczeniem jest domyślna konfiguracja projektu oparta o PostgreSQL, uruchomienie testu lokalnie wymagało tymczasowego nadpisania `DATABASES` na SQLite w pliku `local_settings.py`, co nie jest częścią początkowej konfiguracji systemu.

---

## 10. Podsumowanie

Test automatyczny z Zadania 2 potwierdza błąd integracji manualnie wykryty w Zadaniu 1. Dzięki automatyzacji błąd ten można teraz wykryć jednym poleceniem `manage.py test`.  Ułatwia to jego ponowną weryfikację po ewentualnej naprawie.
