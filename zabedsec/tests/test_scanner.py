import unittest

from zabedsec.scanner import normalize_target


class ScannerTests(unittest.TestCase):
    def test_normalize_hostname(self):
        url, host = normalize_target("example.com")
        self.assertEqual(url, "https://example.com")
        self.assertEqual(host, "example.com")

    def test_normalize_https(self):
        url, host = normalize_target("https://example.com/path")
        self.assertEqual(url, "https://example.com/path")
        self.assertEqual(host, "example.com")


if __name__ == "__main__":
    unittest.main()
