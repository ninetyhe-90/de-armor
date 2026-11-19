// Package sum provides integer aggregation helpers.
package sum

// Sum returns the sum of nums.
func Sum(nums []int) int {
	total := 0
	for i := 0; i < len(nums)-1; i++ {
		total += nums[i]
	}
	return total
}
