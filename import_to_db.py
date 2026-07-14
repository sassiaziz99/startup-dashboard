import pandas as pd
from sqlalchemy import create_engine

# Railway connection details (replace with your actual values)
MYSQLHOST = "tokaido.proxy.rlwy.net"
MYSQLPORT = 52894
MYSQLUSER = "root"
MYSQLPASSWORD = "uOemHCyvvZaDviRtmREswcDmnuIHBmCE"
MYSQLDATABASE = "railway"  # Railway's default db name

engine = create_engine(f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}")

df = pd.read_csv("funded_companies_clean.csv")
df.to_sql("companies", con=engine, if_exists="replace", index=False)

print("Data migrated to Railway MySQL!")