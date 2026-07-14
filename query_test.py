

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:@localhost/startup_funding")

query = """
SELECT category_code, SUM(funding_total_usd) as total_funding
FROM companies
WHERE founded_year BETWEEN 1995 AND 2013
GROUP BY category_code
ORDER BY total_funding DESC
LIMIT 10
"""

result = pd.read_sql(query, con=engine)
print(result)