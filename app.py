import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")

# --- Database connection ---
engine = create_engine("mysql+pymysql://root:@localhost/startup_funding")

# --- Helper: get filter options directly from DB ---
@st.cache_data
def get_options():
    countries = pd.read_sql("SELECT DISTINCT country_code FROM companies ORDER BY country_code", engine)
    categories = pd.read_sql("SELECT DISTINCT category_code FROM companies ORDER BY category_code", engine)
    return countries["country_code"].tolist(), categories["category_code"].tolist()

country_options, category_options = get_options()

st.title("Global Startup Funding Dashboard")
st.markdown("Explore funding trends across 25,000+ startups (Crunchbase data, 1995–2013) — powered by MySQL")

# --- Sidebar filters ---
st.sidebar.header("Filters")
selected_countries = st.sidebar.multiselect("Country", options=country_options, default=["USA"])
selected_categories = st.sidebar.multiselect("Category", options=category_options)
year_range = st.sidebar.slider("Founded Year", 1995, 2013, (1995, 2013))

# --- Build dynamic WHERE clause ---
conditions = [f"founded_year BETWEEN {year_range[0]} AND {year_range[1]}"]

if selected_countries:
    countries_str = ",".join(f"'{c}'" for c in selected_countries)
    conditions.append(f"country_code IN ({countries_str})")

if selected_categories:
    categories_str = ",".join(f"'{c}'" for c in selected_categories)
    conditions.append(f"category_code IN ({categories_str})")

where_clause = " AND ".join(conditions)

# --- KPI query ---
kpi_query = f"""
    SELECT COUNT(*) as company_count,
           SUM(funding_total_usd) as total_funding,
           AVG(funding_total_usd) as avg_funding
    FROM companies
    WHERE {where_clause}
"""
kpi = pd.read_sql(kpi_query, engine).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Companies", f"{int(kpi['company_count']):,}")
col2.metric("Total Funding", f"${kpi['total_funding']:,.0f}" if kpi['total_funding'] else "$0")
col3.metric("Avg Funding per Company", f"${kpi['avg_funding']:,.0f}" if kpi['avg_funding'] else "$0")

# --- Chart 1: Funding over time ---
year_query = f"""
    SELECT founded_year, SUM(funding_total_usd) as total_funding
    FROM companies
    WHERE {where_clause}
    GROUP BY founded_year
    ORDER BY founded_year
"""
by_year = pd.read_sql(year_query, engine)
fig1 = px.line(by_year, x="founded_year", y="total_funding", title="Total Funding by Founding Year")
st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Top categories by funding ---
category_query = f"""
    SELECT category_code, SUM(funding_total_usd) as total_funding
    FROM companies
    WHERE {where_clause}
    GROUP BY category_code
    ORDER BY total_funding DESC
    LIMIT 10
"""
by_category = pd.read_sql(category_query, engine)
fig2 = px.bar(by_category, x="category_code", y="total_funding", title="Top 10 Categories by Total Funding")
st.plotly_chart(fig2, use_container_width=True)

# --- Table: Top funded companies ---
top_query = f"""
    SELECT name, category_code, country_code, founded_year, funding_total_usd
    FROM companies
    WHERE {where_clause}
    ORDER BY funding_total_usd DESC
    LIMIT 20
"""
top_companies = pd.read_sql(top_query, engine)
st.subheader("Top Funded Companies")
st.dataframe(top_companies)

map_query = f"""
    SELECT country_code, SUM(funding_total_usd) as total_funding
    FROM companies
    WHERE {where_clause}
    GROUP BY country_code
"""
by_country = pd.read_sql(map_query, engine)
fig3 = px.choropleth(by_country, locations="country_code", locationmode="ISO-3",
                      color="total_funding", title="Total Funding by Country")
st.plotly_chart(fig3, use_container_width=True)

tier_query = f"""
    SELECT
        CASE
            WHEN funding_total_usd >= 100000000 THEN 'Mega ($100M+)'
            WHEN funding_total_usd >= 10000000 THEN 'Large ($10M-$100M)'
            WHEN funding_total_usd >= 1000000 THEN 'Medium ($1M-$10M)'
            ELSE 'Small (<$1M)'
        END as tier,
        COUNT(*) as num_companies
    FROM companies
    WHERE {where_clause}
    GROUP BY tier
"""
by_tier = pd.read_sql(tier_query, engine)
fig4 = px.pie(by_tier, names="tier", values="num_companies", title="Funding Tier Distribution")
st.plotly_chart(fig4, use_container_width=True)


st.markdown("*Insight: Software, web, and mobile categories dominate global funding volume, while sectors like biotech show fewer but significantly larger individual rounds.*")