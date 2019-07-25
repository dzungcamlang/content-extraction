# -*- coding: utf-8 -*-

import unittest

from internal.helper.string_helper import StringHelper


class TestStringHelper(unittest.TestCase):
    __string_helper = StringHelper()

    def test_convert_vietnamese_to_eng(self):
        text = 'thiên hạ vô địch'
        process_text = self.__string_helper.convert_vietnamese_to_eng(text)
        expect_result = 'thien ha vo dich'

        self.assertEqual(process_text, expect_result, '{} should be {}'.format(process_text, expect_result))

        text = 'THIÊN HẠ VÔ ĐỊCH'
        process_text = self.__string_helper.convert_vietnamese_to_eng(text)
        expect_result = 'THIEN HA VO DICH'

        self.assertEqual(process_text, expect_result, '{} should be {}'.format(process_text, expect_result))

    def test_is_paragraph(self):
        paragraph = 'Mr. Trump moved unapologetically to realize his campaign’s vision of a nation that relentlessly enforces immigration laws; views Muslims with deep suspicion; aggressively enforces drug laws; second-guesses post-World War II alliances; and sends suspected terrorists to Guantánamo Bay or C.I.A. prisons to be interrogated with methods that have been banned as torture.'
        is_paragraph = self.__string_helper.is_paragraph(paragraph)
        expect_result = True

        self.assertEqual(is_paragraph, expect_result, '{} should be {}'.format(is_paragraph, expect_result))

        paragraph = 'Mr. Trump moved.'
        is_paragraph = self.__string_helper.is_paragraph(paragraph)
        expect_result = False

        self.assertEqual(is_paragraph, expect_result, '{} should be {}'.format(is_paragraph, expect_result))

    def test_total_sentences(self):
        paragraph = 'He moved to the Hanoi. Then he traveled to Sapa'
        total_sentence = self.__string_helper.total_sentences(paragraph)
        expect_result = 2

        self.assertEqual(total_sentence, expect_result, '{} should be {}'.format(total_sentence, expect_result))

if __name__ == '__main__':
    unittest.main()