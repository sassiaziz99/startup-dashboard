import pandas as pd

df = pd.read_csv("objects.csv", encoding='latin1', low_memory=False)

# Filter to companies only (this dataset includes people, financial orgs, etc. as "objects")
companies = df[df["entity_type"] == "Company"].copy()

print(companies.shape)
print(companies[["name", "category_code", "country_code", "founded_at", "funding_total_usd", "funding_rounds", "status"]].head(10))
print(companies["funding_total_usd"].describe())
print(companies["category_code"].value_counts().head(10))
print(companies["country_code"].value_counts().head(10))