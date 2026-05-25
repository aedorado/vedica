"""
Test to understand pyswisseph API
"""
import swisseph as swe
from datetime import datetime

# Test JD calculation
def test_swisseph():
    # 1994-03-15 06:31:00 UTC (Anurag Sharma chart)
    jd = 2449083.7715277777  # Pre-calculated JD
    
    # Test with Sun
    result = swe.calc_ut(jd, 0)  # 0 = Sun
    
    print(f"calc_ut result type: {type(result)}")
    print(f"calc_ut result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    print(f"calc_ut full result: {result}")
    
    # Try to understand structure
    for i, item in enumerate(result):
        print(f"  result[{i}] type={type(item)}, value={item}")

if __name__ == '__main__':
    test_swisseph()
