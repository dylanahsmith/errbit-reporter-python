import unittest
from errbit_reporter import Configuration


class ConfigTest(unittest.TestCase):

    def test_required_arguments(self):
        config = Configuration(api_key="c577a99769c12efee8637aa6caf81d5e",
                               errbit_url="http://localhost:3000")
        self.assertEqual(config.api_key, "c577a99769c12efee8637aa6caf81d5e")
        self.assertEqual(config.errbit_url, "http://localhost:3000")
