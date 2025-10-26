#!/usr/bin/env python3
"""
Test script to verify column name cleaning works correctly
"""
import pandas as pd
import re

def test_column_cleaning():
    # Create test dataframe with ___N suffixes
    test_df = pd.DataFrame({
        'Person___0': ['Alice', 'Bob', 'Charlie'],
        'Task___1': ['Task 1', 'Task 2', 'Task 3'],
        'Project___2': ['Marketing', 'Products', 'General'],
        'Status___3': ['Open', 'Working', 'Done'],
        'Due Date___4': ['2024-01-01', '2024-02-01', '2024-03-01']
    })

    print("Original DataFrame columns:")
    print(test_df.columns.tolist())
    print("\nOriginal DataFrame:")
    print(test_df)

    # Clean column names using rename (as in our code)
    column_rename_map = {}
    for col in test_df.columns:
        # Remove everything from __ onwards (two or more underscores)
        clean_col = re.sub(r'__+.*$', '', str(col))
        column_rename_map[col] = clean_col

    cleaned_df = test_df.rename(columns=column_rename_map)

    print("\n\nCleaned DataFrame columns:")
    print(cleaned_df.columns.tolist())
    print("\nCleaned DataFrame:")
    print(cleaned_df)

    # Verify all suffixes are removed
    has_suffixes = any('___' in col for col in cleaned_df.columns)

    if has_suffixes:
        print("\n❌ ERROR: Some columns still have suffixes!")
        return False
    else:
        print("\n✅ SUCCESS: All column suffixes removed!")
        return True

if __name__ == "__main__":
    success = test_column_cleaning()
    exit(0 if success else 1)
