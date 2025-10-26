#!/usr/bin/env python3
"""
Test script to verify the updated regex pattern handles various column name formats
"""
import re

def test_column_patterns():
    """Test that our regex pattern handles all the observed column name formats"""

    # Test cases based on the screenshot
    test_columns = [
        # Original format from code
        "Person___0",
        "Task___1",
        "Project___2",

        # Patterns from the screenshot
        "Transcript__0__...",
        "Date Assigned__...",
        "Person__2__2__...",
        "Task__3__3__...",
        "Project__4__4__...",
        "Status__5__5__...",
        "Due Date__7__...",
        "Notes__8__8__...",
        "Progress %__9__...",

        # Edge cases
        "Column",  # No suffix
        "Column__",  # Just underscores
        "Column__123",  # Double underscore with number
        "Column__123__456",  # Multiple number groups
        "Column__1...",  # With dots
    ]

    # Expected cleaned names
    expected = [
        "Person",
        "Task",
        "Project",
        "Transcript",
        "Date Assigned",
        "Person",
        "Task",
        "Project",
        "Status",
        "Due Date",
        "Notes",
        "Progress %",
        "Column",
        "Column",
        "Column",
        "Column",
        "Column",
    ]

    # Universal pattern: remove everything from __ onwards (two or more underscores)
    pattern = r'__+.*$'

    print(f"Testing column name cleaning with pattern: r'{pattern}'")
    print("=" * 70)

    all_passed = True
    for i, (original, expected_clean) in enumerate(zip(test_columns, expected)):
        cleaned = re.sub(pattern, '', str(original))
        passed = cleaned == expected_clean
        status = "✅" if passed else "❌"

        print(f"{status} '{original}' -> '{cleaned}' (expected: '{expected_clean}')")

        if not passed:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_column_patterns()
    exit(0 if success else 1)
