# czarnoskrzynkowe testy jednostkowe dla django-helpdesk

from datetime import date, datetime, time, timedelta

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from helpdesk.lib import (
    convert_value,
    daily_time_spent_calculation,
    format_time_spent,
)
from helpdesk.models import Queue, Ticket, TicketDependency
from helpdesk.templatetags.in_list import in_list
from helpdesk.templatetags.ticket_to_link import num_to_link

# poniedziałek 12.10.2026 - dzień tygodnia ma znaczenie dla godzin otwarcia
MONDAY = date(2026, 10, 12)


def at(hour, minute=0):
    return datetime(MONDAY.year, MONDAY.month, MONDAY.day, hour, minute)

# OBSZAR 1: format_time_spent(time_spent) na str
# zamienia timedelta na czytelny string "GGh:MMm" w raportach czasu pracy

class FormatTimeSpentTests(SimpleTestCase):

    def test_none_gives_empty_string(self):  # TC-FTS-01
        self.assertEqual(format_time_spent(None), "")

    def test_one_minute(self):  # TC-FTS-02
        self.assertEqual(format_time_spent(timedelta(minutes=1)), "00h:01m")

    def test_hours_and_minutes(self):  # TC-FTS-03
        self.assertEqual(format_time_spent(timedelta(hours=1, minutes=5)), "01h:05m")

    def test_just_below_one_hour(self):  # TC-FTS-04
        self.assertEqual(
            format_time_spent(timedelta(minutes=59, seconds=59)), "00h:59m"
        )

    def test_more_than_one_day_is_counted_in_hours(self):  # TC-FTS-05
        self.assertEqual(format_time_spent(timedelta(days=1, hours=2)), "26h:00m")

# OBSZAR 2: convert_value(value) na str, wartość bez zmian
# ujednolica typy daty albo czasu do formatu tekstowego, a pozostałe typy przepuszcza bez zmian
class ConvertValueTests(SimpleTestCase):

    def test_datetime_is_formatted_as_string(self):  # TC-CV-01
        self.assertEqual(
            convert_value(datetime(2026, 10, 15, 17, 30, 45)), "2026-10-15T17:30"
        )

    def test_date_is_formatted_as_string(self):  # TC-CV-02
        self.assertEqual(convert_value(date(2026, 10, 15)), "2026-10-15")

    def test_time_is_formatted_as_string(self):  # TC-CV-03
        self.assertEqual(convert_value(time(9, 5, 7)), "09:05:07")

    def test_string_is_returned_unchanged(self):  # TC-CV-04
        self.assertEqual(convert_value("abc"), "abc")

    def test_none_is_returned_unchanged(self):  # TC-CV-05
        self.assertIsNone(convert_value(None))

# OBSZAR 3: daily_time_spent_calculation(earliest, latest, open_hours) na int
# liczy, ile sekund z podanego przedziału mieści się w godzinach pracy, przyjęłyśmy w testach godziny otwarcia: poniedziałek 9-17

class DailyTimeSpentCalculationTests(SimpleTestCase):
    OPEN = {"monday": (9, 17)}

    def calc(self, earliest, latest, open_hours=None):
        return daily_time_spent_calculation(
            earliest, latest, self.OPEN if open_hours is None else open_hours
        )

    def test_interval_inside_open_hours(self):  # TC-DTS-01
        self.assertEqual(self.calc(at(10), at(12)), 7200)

    def test_interval_starting_before_opening_is_clipped(self):  # TC-DTS-02
        self.assertEqual(self.calc(at(8), at(10)), 3600)

    def test_interval_ending_after_closing_is_clipped(self):  # TC-DTS-03
        self.assertEqual(self.calc(at(16), at(18)), 3600)

    def test_interval_entirely_after_closing(self):  # TC-DTS-04
        self.assertEqual(self.calc(at(18), at(20)), 0)

    def test_interval_exactly_equal_to_open_window(self):  # TC-DTS-05
        self.assertEqual(self.calc(at(9), at(17)), 8 * 3600)

    def test_zero_length_interval(self):  # TC-DTS-06
        self.assertEqual(self.calc(at(10), at(10)), 0)

    def test_start_after_end_is_rejected(self):  # TC-DTS-07
        with self.assertRaises(ImproperlyConfigured):
            self.calc(at(10), at(12), {"monday": (17, 9)})

# OBSZAR 4: in_list(value, arg) na bool, sprawdza, czy wartość znajduje się w przekazanej kolekcji
class InListTests(SimpleTestCase):

    def test_value_present(self):  # TC-IL-01
        self.assertTrue(in_list("pizza", ["pizza", "pie", "cake"]))

    def test_value_absent(self):  # TC-IL-02
        self.assertFalse(in_list("sushi", ["pizza", "pie", "cake"]))

    def test_none_instead_of_list(self):  # TC-IL-03
        self.assertFalse(in_list("pizza", None))

# OBSZAR 5: num_to_link(text) na str, zamienia w tekście wzorzec "#123" na link do zgłoszenia o tym numerze,
# o ile takie zgłoszenie istnieje
class NumToLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.queue = Queue.objects.create(title="Support", slug="support")
        cls.t1 = Ticket.objects.create(queue=cls.queue, title="First")

    def test_empty_string(self):  # TC-NTL-01
        self.assertEqual(num_to_link(""), "")

    def test_text_without_reference_is_unchanged(self):  # TC-NTL-02
        self.assertEqual(num_to_link("Brak odwołań"), "Brak odwołań")

    def test_reference_to_existing_ticket_becomes_link(self):  # TC-NTL-03
        result = num_to_link(f"Zobacz #{self.t1.id} teraz")
        self.assertIn(reverse("helpdesk:view", args=[self.t1.id]), result)
        self.assertIn(f">#{self.t1.id}</a>", result)
        self.assertIn("teraz", result)

    def test_reference_to_missing_ticket_is_left_as_text(self):  # TC-NTL-04
        self.assertEqual(num_to_link("Zobacz #999999"), "Zobacz #999999")

    def test_hash_without_digits_is_unchanged(self):  # TC-NTL-05
        self.assertEqual(
            num_to_link("hashtag # bez numeru"), "hashtag # bez numeru"
        )

# OBSZAR 6: Ticket.can_be_resolved na bool - cykl życia zgłoszenia
class TicketCanBeResolvedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.queue = Queue.objects.create(title="Support", slug="support")

    def make_ticket(self, status=Ticket.OPEN_STATUS):
        return Ticket.objects.create(queue=self.queue, title="T", status=status)

    def depends_on(self, ticket, dependency_status):
        dep = self.make_ticket(status=dependency_status)
        TicketDependency.objects.create(ticket=ticket, depends_on=dep)

    def test_no_dependencies(self):  # TC-TCR-01
        self.assertTrue(self.make_ticket().can_be_resolved)

    def test_dependency_open_blocks(self):  # TC-TCR-02
        ticket = self.make_ticket()
        self.depends_on(ticket, Ticket.OPEN_STATUS)
        self.assertFalse(ticket.can_be_resolved)

    def test_dependency_reopened_blocks(self):  # TC-TCR-03
        ticket = self.make_ticket()
        self.depends_on(ticket, Ticket.REOPENED_STATUS)
        self.assertFalse(ticket.can_be_resolved)

    def test_dependency_resolved_allows(self):  # TC-TCR-04
        ticket = self.make_ticket()
        self.depends_on(ticket, Ticket.RESOLVED_STATUS)
        self.assertTrue(ticket.can_be_resolved)

    def test_dependency_closed_allows(self):  # TC-TCR-05
        ticket = self.make_ticket()
        self.depends_on(ticket, Ticket.CLOSED_STATUS)
        self.assertTrue(ticket.can_be_resolved)

    def test_one_open_among_resolved_blocks(self):  # TC-TCR-06
        ticket = self.make_ticket()
        self.depends_on(ticket, Ticket.RESOLVED_STATUS)
        self.depends_on(ticket, Ticket.OPEN_STATUS)
        self.assertFalse(ticket.can_be_resolved)