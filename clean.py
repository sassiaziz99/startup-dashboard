

import pandas as pd

df = pd.read_csv("objects.csv", encoding='latin1', low_memory=False)
companies = df[df["entity_type"] == "Company"].copy()

# Keep only companies with actual disclosed funding
funded = companies[companies["funding_total_usd"] > 0].copy()

# Convert founded_at to datetime, extract year
funded["founded_at"] = pd.to_datetime(funded["founded_at"], errors="coerce")
funded["founded_year"] = funded["founded_at"].dt.year

# Clean up category and country (drop rows with missing values for those, since we'll filter by them)
funded = funded.dropna(subset=["category_code", "country_code"])

# Keep only relevant columns for the dashboard
funded = funded[[
    "name", "category_code", "country_code", "founded_year",
    "funding_total_usd", "funding_rounds", "status"
]]

print(funded.shape)
print(funded.head(10))
print(funded["founded_year"].value_counts().sort_index())

# Save cleaned version so we don't reprocess the big file every time
funded.to_csv("funded_companies_clean.csv", index=False)
print("Saved cleaned file.")