import os
import requests
import pandas as pd
import sqlite3
from functions import make_endpoint
from functions import query_endpoint
from functions import check_response

# %%
# Constants
app_token = os.environ.get("LA_RECENT_DATA_TOKEN")
headers = {"X-App-Token": app_token}
id_parking_meters = "e7h6-4a3e"

# %%
# One "page" example
endpoint = make_endpoint(id_parking_meters, query=True)
response = query_endpoint(endpoint, query="SELECT * ORDER BY spaceid DESC", page=1, limit=100)
response_json = check_response(response)

# %%
# sqlite3 tutorial example
connection = sqlite3.connect("data/ladot_parking_meters.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE original_raw(spaceid, eventtime, occupancystate)")
result = cursor.execute("SELECT name FROM sqlite_master")
result.fetchone()
cursor.executemany("INSERT INTO original_raw VALUES(:spaceid, :eventtime, :occupancystate)", response_json)
connection.commit()
for row in cursor.execute("SELECT spaceid, eventtime, occupancystate FROM original_raw ORDER BY spaceid DESC"):
    print(row)
connection.close()

new_con = sqlite3.connect("data/ladot_parking_meters.db")
new_cur = new_con.cursor()
new_res = new_cur.execute("SELECT spaceid, occupancystate, eventtime FROM original_raw ORDER BY occupancystate DESC, eventtime DESC")
space_id, occupancy_state, event_time = new_res.fetchone()
print(f"The most recently available LADOT metered spot is {space_id} as of {event_time} UTC")
new_con.close()
