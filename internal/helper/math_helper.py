import math


class MathHelper:
    def __init__(self):
        pass

    def get_mean(self, nums=[]):
        if len(nums) < 1:
            return 0.0

        total = 0.0
        for num in nums:
            total += num

        return total / len(nums)

    def get_standard_deviation(self, nums=[]):
        if len(nums) < 1:
            return 0.0

        mean = self.get_mean(nums)
        total = 0.0
        for num in nums:
            total += math.pow(float(num) - mean, 2)

        return math.sqrt(total / len(nums))