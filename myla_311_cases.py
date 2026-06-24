import os
import requests
import pandas as pd
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
        casenumber
        ,systemmodstamp AS updated_date
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
        ,locator_council_district AS council_district
        ,locator_sr_community_police AS police_precicnt
        ,zipcode__c AS zip_code
        ,locator_sr_neigborhood_council AS neighborhood_code
        ,locator_sr_neigborhood_council_1 AS neighborhood_name
    ORDER BY
        casenumber DESC
"""

# %%
endpoint = make_endpoint(id_311_cases, query=True)
response = query_endpoint(endpoint, query=query_311_cases, page=1, limit=10)
response_json = check_response(response)
df = pd.DataFrame(response_json)

# %%
cases = pd.DataFrame()
for page in range(1, 11):
    response = query_endpoint(endpoint, query=query_311_cases, page=page, limit=500)
    response_json = check_response(response)
    df = pd.DataFrame(response_json)
    cases = pd.concat([cases, df], ignore_index=True)

