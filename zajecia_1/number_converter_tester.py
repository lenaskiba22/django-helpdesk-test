# czarnoskrzynkowe testy jednostkowe funkcji


import unittest
from number_converter import convert_to_polish_name


class ConvertToPolishNameTests(unittest.TestCase):
    def check(self, cases):
        for number, expected in cases:
            with self.subTest(number=number):
                self.assertEqual(convert_to_polish_name(number), expected)

# zero i jedności

    def test_zero(self):  # TC-01
        self.assertEqual(convert_to_polish_name(0), "zero")

    def test_units(self):  # TC-02
        self.check([
            (1, "jeden"),
            (2, "dwa"),
            (3, "trzy"),
            (4, "cztery"),
            (5, "pięć"),
            (6, "sześć"),
            (7, "siedem"),
            (8, "osiem"),
            (9, "dziewięć"),
        ])
# liczby 10-19 - nastki

    def test_teens(self):  # TC-03
        self.check([
            (10, "dziesięć"),
            (11, "jedenaście"),
            (12, "dwanaście"),
            (13, "trzynaście"),
            (14, "czternaście"),
            (15, "piętnaście"),
            (16, "szesnaście"),
            (17, "siedemnaście"),
            (18, "osiemnaście"),
            (19, "dziewiętnaście"),
        ])

# dziesiątki
    def test_round_tens(self):  # TC-04
        self.check([
            (20, "dwadzieścia"),
            (30, "trzydzieści"),
            (40, "czterdzieści"),
            (50, "pięćdziesiąt"),
            (60, "sześćdziesiąt"),
            (70, "siedemdziesiąt"),
            (80, "osiemdziesiąt"),
            (90, "dziewięćdziesiąt"),
        ])

    def test_tens_with_units(self):  # TC-05
        self.check([
            (21, "dwadzieścia jeden"),
            (47, "czterdzieści siedem"),
            (99, "dziewięćdziesiąt dziewięć"),
        ])

# setki
    def test_round_hundreds(self):  # TC-06
        self.check([
            (100, "sto"),
            (200, "dwieście"),
            (300, "trzysta"),
            (400, "czterysta"),
            (500, "pięćset"),
            (600, "sześćset"),
            (700, "siedemset"),
            (800, "osiemset"),
            (900, "dziewięćset"),
        ])

    def test_hundreds_with_remainder(self):  # TC-07
        self.check([
            (101, "sto jeden"),
            (110, "sto dziesięć"),
            (115, "sto piętnaście"),
            (123, "sto dwadzieścia trzy"),
            (999, "dziewięćset dziewięćdziesiąt dziewięć"),
        ])

    # GRUPA 5: TYSIĄCE - ODMIANA RZECZOWNIKA

    def test_one_thousand_has_no_jeden(self):  # TC-08
        self.assertEqual(convert_to_polish_name(1000), "tysiąc")

    def test_thousands_plural_form_tysiace(self):  # TC-09
        self.check([
            (2000, "dwa tysiące"),
            (3000, "trzy tysiące"),
            (4000, "cztery tysiące"),
            (22000, "dwadzieścia dwa tysiące"),
            (134000, "sto trzydzieści cztery tysiące"),
        ])

    def test_thousands_plural_form_tysiecy(self):  # TC-10
        self.check([
            (5000, "pięć tysięcy"),
            (9000, "dziewięć tysięcy"),
            (10000, "dziesięć tysięcy"),
            (100000, "sto tysięcy"),
            (200000, "dwieście tysięcy"),
        ])

    def test_teen_thousands_use_tysiecy(self):  # TC-11
        self.check([
            (11000, "jedenaście tysięcy"),
            (12000, "dwanaście tysięcy"),
            (13000, "trzynaście tysięcy"),
            (14000, "czternaście tysięcy"),
            (19000, "dziewiętnaście tysięcy"),
        ])

    def test_thousands_ending_in_one_use_tysiecy(self):  # TC-12
        self.check([
            (21000, "dwadzieścia jeden tysięcy"),
            (101000, "sto jeden tysięcy"),
        ])

# liczby złożone (tysiące + reszta)
    def test_thousands_with_remainder(self):  # TC-13

        self.check([
            (1001, "tysiąc jeden"),
            (1234, "tysiąc dwieście trzydzieści cztery"),
            (10500, "dziesięć tysięcy pięćset"),
            (123456, "sto dwadzieścia trzy tysiące czterysta pięćdziesiąt sześć"),
        ])

    def test_upper_boundary(self):  # TC-14
        self.assertEqual(
            convert_to_polish_name(999999),
            "dziewięćset dziewięćdziesiąt dziewięć tysięcy "
            "dziewięćset dziewięćdziesiąt dziewięć",
        )

# format wyniku
    def test_result_is_a_string(self):  # TC-15
        self.assertIsInstance(convert_to_polish_name(42), str)

    def test_no_extra_whitespace(self):  # TC-16
        for number in (0, 7, 15, 70, 100, 1000, 10500, 999999):
            with self.subTest(number=number):
                result = convert_to_polish_name(number)
                self.assertEqual(result, result.strip())
                self.assertNotIn("  ", result)

# przypadki negatywne - poza przedziałem
    def test_below_range_is_rejected(self):  # TC-17
        for number in (-1, -999999):
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    convert_to_polish_name(number)

    def test_above_range_is_rejected(self):  # TC-18
        for number in (1000000, 1234567):
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    convert_to_polish_name(number)

# przypadki negatywne - niepoprawny typ
    def test_non_integer_types_are_rejected(self):  # TC-19
        for value in ("5", 3.5, None, [1], {}):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    convert_to_polish_name(value)

    def test_float_with_integer_value_is_rejected(self):  # TC-20
        with self.assertRaises(TypeError):
            convert_to_polish_name(5.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
