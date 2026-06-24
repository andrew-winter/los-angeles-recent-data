import os
import requests
import pandas as pd

# %%
# Constants
app_token = os.environ.get("LA_RECENT_DATA_TOKEN")
headers = {"X-App-Token": app_token}

# Data sources: data.lacity.org
id_ramp_bids = "hf3r-utnq"
id_parking_meters = "e7h6-4a3e"
id_311_cases = "2cy6-i7zn"

# %%
# Function make_endpoint()
def make_endpoint(id, query = True) -> str:
    """Creates an API endpoint to access Los Angeles open data.
    
    Updated for SODA3 API. Intended for POST requests. No parameters.
    """
    soda3_api = "https://data.lacity.org/api/v3/views"
    endpoint = f"{soda3_api}/{id}"
    
    # Export supports more formats and intends to be readable by humans
    if not query:
        endpoint += "/export.csv"
    # Query primarily supports machine readability and more customization
    else:
        endpoint += "/query.json"
    
    return endpoint

# %%
# Function query_endpoint()
def query_endpoint(
    url: str,
    query: str = None,
    *,
    page: int = 1,
    limit: int = 100,
) -> requests.Request:
    """Make a POST request to query a dataset.
    
    More info: https://dev.socrata.com/docs/queries/
    """
    # Default query if none is provided
    if not query:
        request_body = {"query": "SELECT *"}
    else:
        request_body = {"query": query}
    
    # Pages, explicitly-requested columns only, shorter timeout
    request_body["page"] = {"pageNumber": page, "pageSize": limit}
    request_body["includeSynthetic"] = False
    request_body["timeout"] = 45
    
    response = requests.post(url, json=request_body, headers=headers)
    return response

# %%
# Function check_response()
def check_response(response):
    """Check response for status code and structure. Decode into JSON.
    
    ...
    """
    print(f"Status code:\t\t{response.status_code}")
    print(f"Status code ok:\t\t{response.ok}")
    response_json = response.json()
    print(f"Rows:\t\t\t{len(response_json)}")
    # Check if the same number of "columns" are in each "row"
    check_columns = set([len(row) for row in response_json])
    print(f"Columns:\t\t{check_columns}")
    return response_json

# %%
# RAMP open bids example
if __name__ == "__main__":
    endpoint = make_endpoint(id=id_311_cases, query=True)
    soql_query = "SELECT systemmodstamp AS updateddate, casenumber, createddate"
    response = query_endpoint(url=endpoint, query=soql_query, page=1, limit=25)
    response_json = check_response(response)
    df = pd.DataFrame(response_json)

# %%


# %%

