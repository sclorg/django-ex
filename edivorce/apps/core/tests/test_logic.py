from django.test import TestCase
from edivorce.apps.core.utils.conditional_logic import get_cleaned_response_value


class ConditionalLogicTestCase(TestCase):
    def test_get_cleaned_response_no_value(self):
        self.assertIsNone(get_cleaned_response_value(None))
        self.assertIsNone(get_cleaned_response_value(''))
        self.assertIsNone(get_cleaned_response_value('  '))
        self.assertIsNone(get_cleaned_response_value('[]'))
        self.assertIsNone(get_cleaned_response_value('[["","  "]]'))
        self.assertIsNone(get_cleaned_response_value('[["also known as",""]]'))
        self.assertIsNone(get_cleaned_response_value('[["also known as",""],["also known as",""]]'))

    def test_get_cleaned_response_with_value(self):
        self.assertIsNotNone(get_cleaned_response_value('0'))
        self.assertIsNotNone(get_cleaned_response_value('["hi"]'))
        self.assertIsNotNone(get_cleaned_response_value('[["also known as","a"]]'))
