import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

st.title("COVID-19 Data Visualization Dashboard")
st.markdown("Visualizing confirmed, recovered and death cases by country over time.")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Sidebar - filters
st.sidebar.header("Filter Options")
country_list = df['Country'].unique()
country = st.sidebar.selectbox("Select Country", options=country_list, index=list(country_list).index("Malaysia") if "Malaysia" in country_list else 0)

metric = st.sidebar.radio("Select Metric", ['Confirmed', 'Recovered', 'Deaths'])
date_range = st.sidebar.slider("Date range",
                               min_value=df['Date'].min().date(),
                               max_value=df['Date'].max().date(),
                               value=(df['Date'].min().date(), df['Date'].max().date()))

show_raw = st.sidebar.checkbox("Show raw data", value=False)
log_scale = st.sidebar.checkbox("Log scale for Y axis", value=False)

# Filter dataframe
filtered_df = df[(df['Country'] == country) &
                 (df['Date'].dt.date >= date_range[0]) &
                 (df['Date'].dt.date <= date_range[1])].sort_values('Date')

# Layout: metrics + charts
col1, col2, col3 = st.columns([1, 1, 2])

# Latest metrics (show latest numbers for the selected metric and country)
latest = filtered_df.iloc[-1] if not filtered_df.empty else None
total_confirmed = filtered_df['Confirmed'].max() if not filtered_df.empty else 0
total_recovered = filtered_df['Recovered'].max() if not filtered_df.empty else 0
total_deaths = filtered_df['Deaths'].max() if not filtered_df.empty else 0

col1.metric("Total Confirmed", f"{int(total_confirmed):,}")
col2.metric("Total Recovered", f"{int(total_recovered):,}")
col3.metric("Total Deaths", f"{int(total_deaths):,}")

st.markdown("---")

# Two visualization types:
left_col, right_col = st.columns(2)

# Time series line chart (Plotly)
if not filtered_df.empty:
    fig_line = px.line(filtered_df, x='Date', y=metric,
                       title=f"{metric} Cases Over Time — {country}",
                       labels={'Date': 'Date', metric: metric})
    if log_scale:
        fig_line.update_yaxes(type="log")
    left_col.plotly_chart(fig_line, use_container_width=True)
else:
    left_col.info("No data for selected filters.")

# Second visualization: bar chart of daily new cases
if not filtered_df.empty:
    # compute daily new cases
    filtered_df = filtered_df.assign(**{'Daily New': filtered_df[metric].diff().fillna(0).clip(lower=0)})
    fig_bar = px.bar(filtered_df, x='Date', y='Daily New',
                     title=f"Daily New {metric} — {country}",
                     labels={'Daily New': f"Daily New {metric}"})
    right_col.plotly_chart(fig_bar, use_container_width=True)
else:
    right_col.info("No data for selected filters.")

st.markdown("## Data Summary")
# show aggregated summary table
summary = {
    'Metric': ['Total Confirmed', 'Total Recovered', 'Total Deaths'],
    'Value': [int(total_confirmed), int(total_recovered), int(total_deaths)]
}
summary_df = pd.DataFrame(summary)
st.table(summary_df)

# Optionally show raw data
if show_raw:
    st.markdown("### Raw data (filtered)")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

st.markdown("""
**Notes**
- Data source: `datasets/covid-19` (GitHub).
- Use the sidebar to change country, metric and date range.
""")
