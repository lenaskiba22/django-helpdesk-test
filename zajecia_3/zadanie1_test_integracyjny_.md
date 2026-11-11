#Test integracyjny: zależności między zgłoszeniami
# Zajęcia 3 zadanie 1


## 1. Wybrany punkt integracji

Przetestowano integrację pomiędzy:

- **modułem zależności zgłoszeń** ("TicketDependency" / logika "can_be_resolved"),
- **modułem zmiany statusu zgłoszenia** ("update_ticket()" / zapis modelu "Ticket"),
- **interfejsem użytkownika** 

### Wybrany punkt integracji
Ze wzlędu na fakt, że badany przez nas system służy do zgłaszania ticketów zdecydowano się na przetestowanie
zależności pomiędzy zgłoszeniami. Zgłoszenie nie powinno dać się rozwiązać/zamknąć, dopóki zgłoszenia, od których zależy, nie są rozwiązane. Ta reguła wymaga współpracy co najmniej dwóch elementów w systemie:

1. logiki sprawdzającej zależności ("can_be_resolved"),
2. logiki zapisującej nowy status zgłoszenia ("update_ticket()" oraz, niżej, samego "Ticket.save()"),
3. szablonu UI, który ma o tym ostrzegać.

To miejsce, w którym dane muszą być poprawnie przekazane między komponentami.

---

## 2. Scenariusze testów integracyjnych

### Scenariusz 1 - „Happy path”: blokada rozwiązania zgłoszenia z aktywną zależnością

| Element | Opis |
|---|---|
| **Stan początkowy** | Zgłoszenie **A** (id=8) zależy od zgłoszenia **B** (id=9, blokujące). Zgłoszenie B ma status "Open". |
| **Dane wejściowe** | Próba zmiany statusu zgłoszenia A na "Resolved" przez formularz. |
| **Kolejne działania** | 1. Otwarcie widoku zgłoszenia A. <br>2. Sprawdzenie sekcji "Depends on". <br>3. Wybieranie nowy status "Rozwiązane". <br>4. Wpisanie komentarz. <br>5. Zapisanie formularza. |
| **Oczekiwany wynik** | System nie pozwala wybrać innego statusu, dopóki B jest "Open". UI wyświetla komunikat ostrzegawczy: 'To zgłoszenie nie może być rozwiązane ani zamknięte dopóki zgłoszenia od których ono zależy nie są rozwiązane'. |
| **Miejsca obserwacji** | - Komunikat wyświetla ostrzeżenie w UI, <br>- wartość "ticket.status" w bazie po próbie zapisu, <br>- wynik funkcji "can_be_resolved()". |

### Scenariusz 2 - Błąd / niepoprawne dane: zapis mimo niespełnionego warunku

| Element | Opis |
|---|---|
| **Stan początkowy** | Ponownie zgłoszenie A zależy od B, B ma status "Open". |
| **Dane wejściowe** | Status docelowy "Resolved" dla zgłoszenia A, przekazany **z pominięciem formularza UI** - bezpośrednio przez "update_ticket()" i, osobno, przez surowy zapis modelu ("ticket.save()"). Symuluje to sytuację, w której dane "niepoprawne" trafiają do warstwy zapisu, ale inną drogą niż przez formularz z włączoną blokadą. |
| **Kolejne działania** | 1. Ustawienie B na "Open". <br>2. Pominięcie formularza UI. W konsoli wywołano "manage.py shell" wywołano "update_ticket(user, ticket_a, new_status=Ticket.RESOLVED_STATUS)". <br>3. Sprawdzenie "ticket_a.status" po operacji. <br>4. Powtórznie próby poprzez ustawwienie "ticket_a.status = Ticket.RESOLVED_STATUS" i wywołanie samego "ticket_a.save()" bez "update_ticket()". <br>5. Sprawdzenie "ticket_a.status" po tej drugiej próbie. |
| **Oczekiwany wynik** | W obu przypadkach status A powinien pozostać "Open". |
| **Zaobserwowany wynik** | W **obu** przypadkach status A zostaje zapisany jako "Resolved", mimo że B nadal jest "Open" i UI wcześniej wyświetliło ostrzeżenie. |
| **Miejsca obserwacji** | - Komunikat w UI działa i ostrzega, <br>- zapis w bazie danych nie działa, nie blokuje zarówno przy wywołaniu "update_ticket()", jak i przy gołym "Ticket.save()". |

---

## 3. Wykonane testy manualne - przebieg

1. **Utworzono zgłoszenia** przez profil admina: "http://127.0.0.1:8000/admin/helpdesk/ticket/" lub "manage.py shell":
   - utworzono dwa zgłoszenia: A (id=8) i B (id=9),
   - utworzono zależność: A zależy od B - blokująca,
   - ustawiono B na status "Open".

2. **Test przez interfejs webowy** ("/tickets/8/"):
   - zweryfikowano, że sekcja "Depends on" poprawnie pokazuje zależność od #9,
   - w formularzu potwierdzono, że **UI poprawnie wyświetla komunikat ostrzegawczy**: *"To zgłoszenie nie może być rozwiązane ani zamknięte dopóki zgłoszenia od których ono zależy nie są rozwiązane."*

3. **Właściwy test integracyjny**:
   - zresetowano status A z powrotem na "Open", żeby test był powtarzalny,
   - wykonano zapis statusu dwiema niezależnymi drogami przez "update_ticket()" i przez "Ticket.save()"


Na tym etapie zidentyfikowano rozbieżność między dwiema warstwami systemu:

- **Warstwa prezentacji** - działa poprawnie, informuje użytkownika o blokadzie.
- **Warstwa zapisu (backend/"update_ticket" oraz "Ticket.save()")** - pozwala zapisać status "Resolved" mimo niespełnionego warunku "can_be_resolved".


### Scenariusz 1 (happy path) - wynik zgodny z oczekiwaniem

Test wykonany przez przeglądarkę ("/tickets/8/"):

- zgłoszenie A zależy od B, B ma status "Open",
- w formularzu "Odpowiedz na to zgłoszenie" przycisk "Rozwiązane" jest nieaktywny,
- pod listą statusów wyświetla się komunikat: *"To zgłoszenie nie może być rozwiązane ani zamknięte dopóki zgłoszenia od których ono zależy nie są rozwiązane."*

**Wniosek:** warstwa UI poprawnie uniemożliwia użytkownikowi przez formularz wybranie statusu "Resolved", dopóki zależność blokująca nie jest spełniona. Zgodne z oczekiwanym wynikiem.

### Scenariusz 2 (błąd / obejście warstwy UI) - wynik niezgodny z oczekiwaniem - potwierdzony błąd integracji

Test wykonany przez "manage.py shell"  z obserwacją dwoma drogami, żeby sprawdzić, na którym poziomie dokładnie brakuje walidacji.

**Przez "update_ticket()"**, ta sama funkcja, którą wywołuje formularz "Respond" po stronie serwera:

```python
>>> from helpdesk.models import Ticket
>>> from helpdesk.update_ticket import update_ticket
>>> from django.contrib.auth import get_user_model
>>> ticket_a = Ticket.objects.get(id=8)
>>> ticket_b = Ticket.objects.get(id=9)
>>> print("B status:", ticket_b.status)
B status: 1          # Open
>>> print("A can_be_resolved:", ticket_a.can_be_resolved)
A can_be_resolved: False
>>> user = get_user_model().objects.filter(is_staff=True).first()
>>> update_ticket(user, ticket_a, comment="test integracji", new_status=Ticket.RESOLVED_STATUS)
>>> ticket_a.refresh_from_db()
>>> print("A status po update_ticket():", ticket_a.status)
A status po update_ticket(): 3   # Resolved
```

**Bez "update_ticket()"**, żeby sprawdzić, czy walidacja jest w poźniejszym kroku, w "Ticket.save()"):

```python
>>> ticket_a.status = Ticket.OPEN_STATUS
>>> ticket_a.save()        # reset, żeby test był powtarzalny
>>> print("A can_be_resolved przed drugą próbą:", ticket_a.can_be_resolved)
A can_be_resolved przed drugą próbą: False
>>> ticket_a.status = Ticket.RESOLVED_STATUS
>>> ticket_a.save()
>>> ticket_a.refresh_from_db()
>>> print("A status po save():", ticket_a.status)
A status po save(): 3  # Resolved
```


**Wynik:** w obu przypadkach status zgłoszenia A został zapisany jako "Resolved" (3), mimo że zgłoszenie B wciąż ma status "Open", a "can_be_resolved" jednoznacznie zwracało "False" tuż przed każdym z zapisów.

**Wniosek:** nie powinna istniec możliwość rozwiązania zgłoszenia zależnego od innych, dopóki zależności te nie są rozwiązane".  Reguła wyłącznie działa w warstwie prezentacji, można ją obejść z dwóch poziomów zapisu w "update_ticket()" oraz w samym "Ticket.save()". Może to doprowadzić system do niespójnego stanu, którego UI miało zapobiegać, i to na dwóch niezależnych poziomach jednocześnie.

---

## 4. Bug report

| Pole | Opis |
|---|---|
| **Tytuł** | Reguła "nie można rozwiązać zgłoszenia z aktywną zależnością blokującą" wymuszana tylko w UI, nie w warstwie zapisu danych ani w "update_ticket()", ani w "Ticket.save()" |
| **Komponent, w którym wystąpił problem** | Model "Ticket" oraz funkcja "update_ticket()"; dotyczy wszystkich ścieżek zapisu nie przez formularz. |
| **Sposób komunikacji między komponentami** | Szablon UI odczytuje wynik "can_be_resolved" i na jego podstawie renderuje atrybut "disabled" na polu formularza oraz komunikat ostrzegawczy. Informacja ta nie jest zgodna z UI, te miejsca w kodzie nie są ze sobą zintegrowane, mimo że operują na tych samych danych ("can_be_resolved"). |
| **Dane testowe** | Zgłoszenie A z relacją zależności blokującej od zgłoszenia B, B w statusie "Open" ("status=1"); próba zmiany statusu A na "Resolved" ("status=3"), sprawdzona zarówno przez "update_ticket()", jak i przez goły "ticket_a.save()". |
| **Pokazanie** | 1. Utwórz zależność blokującą B od A. 2. Ustaw B na "Open". 3a. W shellu wywołaj "update_ticket(user, ticket_a, new_status=Ticket.RESOLVED_STATUS)" - status mimo to zmienia się na "Resolved". 3b. Niezależnie, zresetuj A na "Open" i spróbuj samego "ticket_a.status = Ticket.RESOLVED_STATUS; ticket_a.save()" - wynik identyczny. 4. Sprawdź status po każdej próbie. |
| **Wynik oczekiwany** | Zapis odrzucony lub cofnięty |
| **Wynik rzeczywisty** | Status zapisany jako "Resolved" (3), w obu wariantach. |
| **Sugerowana naprawa** | Dodać walidację "can_be_resolved" bezpośrednio w metodzie "save()" modelu "Ticket" (lub w "clean()" wywoływanym przed zapisem) i podnosić wyjątek / blokować zapis, gdy warunek nie jest spełniony - niezależnie od tego, czy formularz, "update_ticket()" czy komenda zarządzająca inicjuje zmianę statusu. Dzięki temu integracja byłaby poprawna w obu miejscach, a nie tylko odzwierciedlana w szablonie. |

---


