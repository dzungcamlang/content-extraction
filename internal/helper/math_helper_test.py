import unittest

from internal.helper.math_helper import MathHelper


class TestMathHelper(unittest.TestCase):
    __math_helper = MathHelper()

    def test_get_mean(self):
        nums = [1, 2, 3, 4, 5]
        mean = self.__math_helper.get_mean(nums)
        expect_result = 3

        self.assertEqual(mean, expect_result, '{} should be {}'.format(mean, expect_result))

        nums = [1.5, 2.5, 3, 4, 5]
        mean = self.__math_helper.get_mean(nums)
        expect_result = 3.2

        self.assertEqual(mean, expect_result, '{} should be {}'.format(mean, expect_result))

    def test_get_standard_deviation(self):
        nums = [600, 470, 170, 430, 300]
        standard_deviation = int(self.__math_helper.get_standard_deviation(nums))
        expect_result = 147

        self.assertEqual(standard_deviation, expect_result, '{} should be {}'.format(standard_deviation, expect_result))

if __name__ == '__main__':
    unittest.main()