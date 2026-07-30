from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums:
            return 0

        num_set = set(nums)
        max_sequence_length = 1
        current_sequence_length = 0

        for num in nums:
            if num - 1 not in num_set:
                current_sequence_length = 1
                while num + 1 in num_set:
                    current_sequence_length += 1
                    num += 1
                max_sequence_length = max(max_sequence_length, current_sequence_length)

        return max_sequence_length


if __name__ == "__main__":
    solution = Solution()
    # nums = [100, 4, 200, 1, 3, 2]
    # nums = [1, 2, 6, 7, 8]
    nums = [0, 1, 2, 4, 8, 5, 6, 7, 9, 3, 55, 88, 77, 99, 999999999]
    print(solution.longestConsecutive(nums))
