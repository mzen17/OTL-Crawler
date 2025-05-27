import sqlite3
import pandas as pd

# 1. Connect and read a table into a DataFrame
conn = sqlite3.connect("datadir/crawl-data.sqlite")
reqs = pd.read_sql_query("SELECT * FROM http_requests LIMIT 1000;", conn)

# 2. Peek at the data
print(reqs.head())

