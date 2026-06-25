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

# Data sources: data.lacity.org
id_ramp_bids = "hf3r-utnq"
id_parking_meters = "e7h6-4a3e"
id_311_cases = "2cy6-i7zn"

# %%
query_311_cases = f"""
    SELECT
        casenumber AS case_number
        ,systemmodstamp AS updated_date
        ,createddate AS created_date
        ,created_by_user_organization AS created_by
        ,origin
        ,status
        ,action_taken__c AS action_taken
        ,department_name__c AS owner
        ,assigned_to__c AS assign_to
        ,type AS request_type
        ,date_service_was_rendered AS service_date
        ,service_date__c AS service_date_san
        ,closeddate AS closed_date
        ,resolution_code__c AS resolution_code
        ,reason_code__c AS reason_code
        ,locator_sr_area_planning AS area_planning_commission
        ,locator_council_district AS council_district
        ,locator_sr_community_police AS police_precicnt
        ,zipcode__c AS zip_code
        ,locator_sr_neigborhood_council AS neighborhood_code
        ,locator_sr_neigborhood_council_1 AS neighborhood_name
    ORDER BY
        casenumber DESC
"""

# There has to be a better way
table_311_cases = f"""
    DROP TABLE IF EXISTS
        raw_cases;

    CREATE TABLE
        raw_cases(
            case_number
            ,updated_date
            ,created_date
            ,created_by
            ,origin
            ,status
            ,action_taken
            ,owner
            ,assign_to
            ,request_type
            --,service_date
            ,service_date_san
            ,closed_date
            ,resolution_code
            ,reason_code
            ,area_planning_commission
            ,council_district
            ,police_precicnt
            ,zip_code
            ,neighborhood_code
            ,neighborhood_name
        );
"""

insert_311_cases = f"""
    INSERT INTO
        raw_cases
    VALUES(
        :case_number
        ,:updated_date
        ,:created_date
        ,:created_by
        ,:origin
        ,:status
        ,:action_taken
        ,:owner
        ,:assign_to
        ,:request_type
        --,:service_date
        ,:service_date_san
        ,:closed_date
        ,:resolution_code
        ,:reason_code
        ,:area_planning_commission
        ,:council_district
        ,:police_precicnt
        ,:zip_code
        ,:neighborhood_code
        ,:neighborhood_name
    )
"""

# %%
# One "page" example
endpoint = make_endpoint(id_311_cases, query=True)
response = query_endpoint(endpoint, query=query_311_cases, page=1, limit=100)
response_json = check_response(response)
df = pd.DataFrame(response_json)

# %%
# sqlite3 tutorial example
con = sqlite3.connect("data/myla_311_cases_2026.db")
cur = con.cursor()
cur.execute(table_311_cases)
res = cur.execute("SELECT name FROM sqlite_master")
res.fetchone()
# Insert data
#data = [("", 0, 9.9), ("", 0, 9.9), ("", 0, 9.9)]
#cur.executemany("INSERT INTO raw_cases VALUES(?, ?, ?)", data)
#con.commit()
for row in cur.execute("SELECT case_number, updated_date FROM raw_cases ORDER BY case_number DESC"):
    print(row)

con.close()

# %%
# Iterate through pages and concatenate into DataFrame example
loops = 5
cases = pd.DataFrame()
for page in range(1, loops + 1):
    responses = query_endpoint(endpoint, query=query_311_cases, page=page, limit=1000)
    responses_json = check_response(responses)
    dfs = pd.DataFrame(responses_json)
    cases = pd.concat([cases, dfs], ignore_index=True)

# %%
# Iterate through pages and insert into sqlite database example
connection = sqlite3.connect("data/myla_311_cases_2026.db")
cursor = connection.cursor()
# Need to add logic to the structure of the data
# Flexible number of named values-- there are a ton of missing values
# And should write Pythonic code to be elegant but precise
cursor.executemany(insert_311_cases, response_json[0:3])
connection.commit()
connection.close()

# Should practice SQL with parking meters (three columns!) instead
