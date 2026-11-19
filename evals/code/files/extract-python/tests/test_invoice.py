import unittest

from app.billing.invoice import build_invoice


class BuildInvoiceTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(
            build_invoice("a@b.com", "  Q4   fee ", 10),
            {"email": "a@b.com", "title": "Q4 fee", "amount": 10},
        )

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            build_invoice("not-an-email", "t", 10)


if __name__ == "__main__":
    unittest.main()
