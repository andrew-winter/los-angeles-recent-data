import os
import logging
import requests
import mysql.connector

logger = logging.getLogger(__name__)

# %%
# Constants
ID_311_CASES_2026 = "2cy6-i7zn"
APP_TOKEN = os.environ.get("LA_RECENT_DATA_TOKEN")

# Application token and MySQL configuration
headers = {"X-App-Token": APP_TOKEN}
mysql_config = {
    "user": "admin",
    "password": os.environ.get("MYSQL_ADMIN_PASSWORD"),
    "host": "127.0.0.1",
    "port": 3306
}

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
    request_body["timeout"] = 30
    
    logger.info("Starting POST request")
    response = requests.post(url, json=request_body, headers=headers)
    return response

# %%
# Function check_response()
def check_response(raw_response):
    """Check response status code. Decode JSON.
    
    ...
    """
    logger.info("Response status code: %d", raw_response.status_code)
    if raw_response.ok:
        try:
            output = raw_response.json()
        except requests.exceptions.JSONDecodeError as err:
            logger.info("JSON Decode Error: %s", err)
            output = None
        return output

# %%
if __name__ == "__main__":
    endpoint = make_endpoint(id=ID_311_CASES_2026)
    soql_query = "SELECT systemmodstamp AS updateddate, casenumber, createddate"
    response = query_endpoint(url=endpoint, query=soql_query, page=1, limit=25)
    output = check_response(response)
