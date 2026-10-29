import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Data Analysis Dashboard")
st.write("Explore sales performance with interactive analytics.")

# Sample dataset so the dashboard works immediately
@st.cache_data
def get_sample_data():
    data = {
        "Order Date": [
            "2026-01-05", "2026-01-12", "2026-01-20",
            "2026-02-03", "2026-02-14", "2026-02-25",
            "2026-03-04", "2026-03-15", "2026-03-22",
            "2026-04-02", "2026-04-17", "2026-04-26",
            "2026-05-08", "2026-05-19", "2026-06-11",
            "2026-06-24", "2026-07-09", "2026-07-21"
        ],
        "Product": [
            "Laptop", "Phone", "Headphones",
            "Laptop", "Tablet", "Phone",
            "Headphones", "Laptop", "Phone",
            "Tablet", "Laptop", "Headphones",
            "Phone", "Tablet", "Laptop",
            "Phone", "Headphones", "Tablet"
        ],
        "Category": [
            "Electronics", "Electronics", "Accessories",
            "Electronics", "Electronics", "Electronics",
            "Accessories", "Electronics", "Electronics",
            "Electronics", "Electronics", "Accessories",
            "Electronics", "Electronics", "Electronics",
            "Electronics", "Accessories", "Electronics"
        ],
        "Sales": [
            55000, 25000, 3000, 60000, 18000, 28000,
            3500, 52000, 30000, 20000, 65000, 4000,
            32000, 22000, 58000, 27000, 4500, 19000
        ],
        "Quantity": [
            2, 3, 5, 2, 2, 3, 4, 2, 3,
            2, 2, 5, 4, 2, 2, 3, 6, 2
        ],
        "Region": [
            "South", "North", "East", "West", "South", "North",
            "East", "South", "West", "North", "South", "East",
            "West", "South", "North", "West", "East", "South"
        ]
    }

    df = pd.DataFrame(data)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df


# Upload your own CSV or use sample data
uploaded_file = st.sidebar.file_uploader(
    "Upload Sales CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Order Date", "Product", "Category",
            "Sales", "Quantity", "Region"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            st.error(
                "Missing columns: " + ", ".join(missing)
            )
            st.stop()

        df["Order Date"] = pd.to_datetime(
            df["Order Date"], errors="coerce"
        )
        df["Sales"] = pd.to_numeric(
            df["Sales"], errors="coerce"
        )
        df["Quantity"] = pd.to_numeric(
            df["Quantity"], errors="coerce"
        )
        df = df.dropna(subset=required_columns)

    except Exception as error:
        st.error(f"Could not read the CSV: {error}")
        st.stop()
else:
    df = get_sample_data()

if df.empty:
    st.warning("No valid sales records found.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Sales")

regions = sorted(df["Region"].unique().tolist())
categories = sorted(df["Category"].unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    categories,
    default=categories
)

filtered_df = df[
    df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
].copy()

if filtered_df.empty:
    st.warning("No sales records match these filters.")
    st.stop()

# Key performance indicators
total_sales = filtered_df["Sales"].sum()
total_orders = len(filtered_df)
total_quantity = filtered_df["Quantity"].sum()
average_order = total_sales / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_quantity:,.0f}")
col4.metric("Average Order Value", f"₹{average_order:,.0f}")

st.divider()

# Monthly sales chart
st.subheader("📈 Monthly Sales Trend")

filtered_df["Month"] = (
    filtered_df["Order Date"].dt.to_period("M").astype(str)
)

monthly_sales = (
    filtered_df.groupby("Month", as_index=False)["Sales"]
    .sum()
)

fig_monthly = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    markers=True,
    title="Revenue by Month"
)
st.plotly_chart(fig_monthly, use_container_width=True)

# Product and category charts
left, right = st.columns(2)

with left:
    st.subheader("🏆 Sales by Product")
    product_sales = (
        filtered_df.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_product = px.bar(
        product_sales,
        x="Product",
        y="Sales",
        color="Sales",
        title="Revenue by Product"
    )
    st.plotly_chart(fig_product, use_container_width=True)

with right:
    st.subheader("🗂️ Sales by Category")
    category_sales = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
    )

    fig_category = px.pie(
        category_sales,
        names="Category",
        values="Sales",
        title="Revenue Share by Category"
    )
    st.plotly_chart(fig_category, use_container_width=True)

# Regional analysis
st.subheader("🌍 Sales by Region")

region_sales = (
    filtered_df.groupby("Region", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

fig_region = px.bar(
    region_sales,
    x="Region",
    y="Sales",
    title="Revenue by Region",
    text_auto=True
)
st.plotly_chart(fig_region, use_container_width=True)

# Data table and download
st.subheader("📋 Sales Records")
st.dataframe(
    filtered_df.drop(columns=["Month"], errors="ignore"),
    use_container_width=True
)

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Sales CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.caption(
    "Portfolio project built with Python, Pandas, "
    "Streamlit, and Plotly."
)