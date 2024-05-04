import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Load sales data from an Excel file
sales_data = pd.read_excel("Data/Adidas.xlsx")
sales_data['Year'] = sales_data['InvoiceDate'].dt.year  # Extract year from InvoiceDate

st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;} select {width: 100% !important; max-width: 300px; padding-right: 20px;}</style>', unsafe_allow_html=True)
logo_image = Image.open('Image/adidas-logo.jpg')

# Display logo and title
logo_column, title_column = st.columns([0.1, 0.9])
with logo_column:
    st.image(logo_image, width=100)

title_html = """
    <style>
    .title-test {
    font-weight:bold;
    padding:5px;
    border-radius:6px;
    }
    </style>
    <center><h1 class="title-test">Adidas Interactive Sales Dashboard</h1></center>"""
with title_column:
    st.markdown(title_html, unsafe_allow_html=True)

# Display last updated date
current_date = str(datetime.datetime.now().strftime("%d %B %Y"))
st.write(f"Last updated by: \n {current_date}")

# Tabs for different sections
overview_tab, analysis_tab, regional_sales_tab = st.tabs(["Dashboard Overview", "Detailed Sales Analysis", "Regional Sales Data"])

with overview_tab:
    # Detailed description about Adidas sales
    st.markdown("""
        ### Sales Overview
        This section provides an overview of Adidas' sales performance across various retailers. The bar chart below represents total sales figures per retailer, giving insights into which retailers are the top performers and how sales distribution looks across different sales channels. Understanding these patterns helps Adidas in strategic planning and marketing efforts to boost sales further.
    """)
    
    retailer_sales_fig = px.bar(sales_data, x="Retailer", y="TotalSales", labels={"TotalSales": "Total Sales ($)"},
                                title="Total Sales by Retailer", hover_data=["TotalSales"],
                                template="gridon", height=500)
    st.plotly_chart(retailer_sales_fig, use_container_width=True)
    st.download_button("Download Retailer Sales Data", data=sales_data.to_csv().encode('utf-8'),
                       file_name="retailer_sales.csv", mime="text/csv")

with analysis_tab:
    # Year filter with modified CSS for width and padding
    years = sales_data['Year'].unique()
    selected_year = st.selectbox('Select Year', options=sorted(years, reverse=True))

    # Filter data based on the selected year
    filtered_data = sales_data[sales_data['Year'] == selected_year]
    filtered_data["Month_Year"] = filtered_data["InvoiceDate"].dt.strftime("%b'%y")
    monthly_sales_summary = filtered_data.groupby(by="Month_Year")["TotalSales"].sum().reset_index()
    monthly_sales_fig = px.line(monthly_sales_summary, x="Month_Year", y="TotalSales", title="Total Sales Over Time",
                                template="gridon")
    st.plotly_chart(monthly_sales_fig, use_container_width=True)

    state_sales_summary = filtered_data.groupby(by="State")[["TotalSales", "UnitsSold"]].sum().reset_index()
    state_sales_fig = go.Figure()
    state_sales_fig.add_trace(go.Bar(x=state_sales_summary["State"], y=state_sales_summary["TotalSales"], name="Total Sales"))
    state_sales_fig.add_trace(go.Scatter(x=state_sales_summary["State"], y=state_sales_summary["UnitsSold"], mode="lines",
                                         name="Units Sold", yaxis="y2"))
    state_sales_fig.update_layout(
        title="Total Sales and Units Sold by State",
        xaxis=dict(title="State"),
        yaxis=dict(title="Total Sales", showgrid=False),
        yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
        template="gridon",
        legend=dict(x=1, y=1.1)
    )
    st.plotly_chart(state_sales_fig, use_container_width=True)

with regional_sales_tab:
    regional_sales_data = sales_data[["Region", "City", "TotalSales"]].groupby(by=["Region", "City"])["TotalSales"].sum().reset_index()
    def format_sales(value):
        return '{:.2f} Lakh'.format(value / 1_000_00) if value >= 0 else '0.00 Lakh'
    regional_sales_data["Formatted TotalSales"] = regional_sales_data["TotalSales"].apply(format_sales)
    regional_sales_fig = px.treemap(regional_sales_data, path=["Region", "City"], values="TotalSales",
                                    hover_name="Formatted TotalSales",
                                    hover_data=["Formatted TotalSales"],
                                    color="City", height=700, width=600)
    regional_sales_fig.update_traces(textinfo="label+value")
    st.subheader(":point_right: Total Sales by Region and City in Treemap")
    st.plotly_chart(regional_sales_fig, use_container_width=True)
    st.download_button("Download Regional Sales Data", data=regional_sales_data.to_csv().encode('utf-8'),
                       file_name="regional_sales.csv", mime="text/csv")
