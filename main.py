import streamlit as st
import pandas as pd
import io

# ----------------------------
# App Configuration
# ----------------------------
st.set_page_config(page_title="Data Tool", layout="wide")

st.title("📊 Data Tool - Streamlit App")
st.markdown("Upload, preview, search, sort, and filter your dataset easily.")

# ----------------------------
# File Upload
# ----------------------------
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "xls", "parquet"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type in ["csv"]:
            df = pd.read_csv(uploaded_file)
        elif file_type in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_type == "parquet":
            df = pd.read_parquet(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.success(f"✅ File loaded successfully ({df.shape[0]} rows, {df.shape[1]} columns)")

    # ----------------------------
    # Search Bar
    # ----------------------------
    search_query = st.text_input("🔍 Search in all columns:")
    if search_query:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False, na=False).any(), axis=1)]

    # ----------------------------
    # Column Filtering
    # ----------------------------
    st.subheader("🔧 Column Filters")
    with st.expander("Click to expand filters"):
        filters = {}
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_vals = df[col].dropna().unique().tolist()
                if len(unique_vals) <= 50:
                    selected = st.multiselect(f"{col}", options=unique_vals)
                    if selected:
                        filters[col] = selected
            else:
                min_val, max_val = float(df[col].min()), float(df[col].max())
                selected_range = st.slider(f"{col} range", min_val, max_val, (min_val, max_val))
                if selected_range != (min_val, max_val):
                    filters[col] = selected_range

        # Apply filters
        for col, condition in filters.items():
            if isinstance(condition, list):
                df = df[df[col].isin(condition)]
            else:
                df = df[df[col].between(condition[0], condition[1])]

    # ----------------------------
    # Sorting
    # ----------------------------
    st.subheader("⬆️ Sorting Options")
    sort_col = st.selectbox("Select column to sort by", options=df.columns)
    sort_order = st.radio("Order", ["Ascending", "Descending"])
    df = df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

    # ----------------------------
    # Data Preview
    # ----------------------------
    st.subheader("📋 Data Preview")
    st.dataframe(df, use_container_width=True)

    # ----------------------------
    # Data Operations
    # ----------------------------
    st.subheader("🧮 Data Operations")
    op = st.selectbox("Select operation", ["None", "Describe (summary stats)", "Show Null Counts", "Column Info"])

    if op == "Describe (summary stats)":
        st.write(df.describe(include="all"))
    elif op == "Show Null Counts":
        st.write(df.isnull().sum())
    elif op == "Column Info":
        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())

    # ----------------------------
    # Download Processed Data
    # ----------------------------
    st.download_button(
        label="💾 Download Processed Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="processed_data.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload a CSV, Excel, or Parquet file to get started.")
