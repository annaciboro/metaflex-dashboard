"""
Minimal Streamlit app to test column name cleaning
Run with: streamlit run test_streamlit_display.py
"""
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Column Cleaning Test", layout="wide")

st.title("🧪 Column Name Cleaning Test")

# Create test data with ___N suffixes
test_df = pd.DataFrame({
    'Person___0': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Task___1': ['Design mockups', 'Write code', 'Test features', 'Deploy'],
    'Project___2': ['Marketing', 'Products', 'General', 'Marketing'],
    'Status___3': ['Open', 'Working', 'Done', 'Open'],
    'Due Date___4': ['2024-01-15', '2024-02-01', '2024-01-20', '2024-03-01']
})

st.subheader("❌ Before Cleaning (with ___N suffixes)")
st.dataframe(test_df, use_container_width=True, hide_index=True)

# Clean column names
column_rename_map = {}
for col in test_df.columns:
    # Remove everything from __ onwards (two or more underscores)
    clean_col = re.sub(r'__+.*$', '', str(col))
    column_rename_map[col] = clean_col

cleaned_df = test_df.rename(columns=column_rename_map)

st.subheader("✅ After Cleaning (suffixes removed)")
st.dataframe(cleaned_df, use_container_width=True, hide_index=True)

st.success("If the second table shows clean column names (Person, Task, Project, etc.) without ___0, ___1, etc., then the cleaning works!")
