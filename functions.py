import os
import logging
import requests
import mysql.connector

logger = logging.getLogger(__name__)

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

# Function make_endpoint()
def make_endpoint(api_id, query = True) -> str:
    """Creates an API endpoint to access Los Angeles open data.
    
    Updated for SODA3 API. Intended for POST requests. No parameters.
    """
    soda3_api = "https://data.lacity.org/api/v3/views"
    endpoint = f"{soda3_api}/{api_id}"
    
    # Export supports more formats and intends to be readable by humans
    if not query:
        endpoint += "/export.csv"
    # Query primarily supports machine readability and more customization
    else:
        endpoint += "/query.json"
    
    return endpoint

# Function make_query()
def make_soql_query(where = None, order_by = "casenumber") -> str:
    """Query the MyLA 311 dataset.
    
    Simplify column names. Should add some more utility.
    """
    query_raw = """
        SELECT
            casenumber AS case_number
            ,createddate AS created_date
            ,systemmodstamp AS updated_date
            ,action_taken__c AS action_taken
            ,department_name__c AS department
            ,type AS request_type
            ,status AS status
            ,origin AS request_source
            ,created_by_user_organization
            ,reported_anonymously__c AS anonymous
            ,assigned_to__c AS assign_to
            ,service_date__c AS service_date
            ,closeddate AS closed_date
            ,date_service_was_rendered AS date_service_rendered
            ,reason_code__c AS reason_code
            ,resolution_code__c AS resolution_code
            ,zipcode__c AS zip_code
            ,geolocation__latitude__s AS latitude
            ,geolocation__longitude__s AS longitude
            ,location
            ,locator_sr_area_planning AS area_planning_commission
            ,locator_council_district AS council_district
            ,locator_sr_council_district AS council_district_member
            ,locator_sr_neigborhood_council AS neighborhood_council_code
            ,locator_sr_neigborhood_council_1 AS neighborhood_council_name
            ,locator_sr_community_police AS police_precinct
    """
    #if where:
    #    query = query_raw += f" WHERE {where}"
    #else:
    #    query = f"{query_raw}"
    query = f"{query_raw}"
    query += f" ORDER BY {order_by}"
    
    return query

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

# Function check_response()
def check_response(response_raw):
    """Checks that response status code is ok. Decodes JSON.
    
    Returns a list of dictionaries.
    """
    logger.info("Response status code: %d", response_raw.status_code)
    if response_raw.ok:
        try:
            output = response_raw.json()
        except requests.exceptions.JSONDecodeError as err:
            logger.info("JSON Decode Error: %s", err)
            output = None
    return output

# Function transpose_tuples()
def transpose_tuples(tuples):
    """Transposes a list of tuples into a dictionary.
    
    Append the ith value of each row to each column.
    """
    columns = [
        "case_number", "created_date", "updated_date", "department",
        "request_type", "status", "request_source",
        "created_by_user_organization", "anonymous", "assign_to",
        "closed_date", "resolution_code", "zip_code", "latitude",
        "longitude", "area_planning_commission", "council_district",
        "council_district_member", "neighborhood_council_code",
        "neighborhood_council_name", "police_precinct"]
    output = {key: [] for key in columns}
    for row in tuples:
        for i, col in enumerate(columns):
            output[col].append(row[i])
    return output

if __name__ == "__main__":
    endpoint = make_endpoint(ID_311_CASES_2026)
    soql_query = make_soql_query(order_by="casenumber")
    response_raw = query_endpoint(url=endpoint, query=soql_query, page=1, limit=1000)
    response_json = check_response(response_raw)
    response_dict = transpose_tuples(response_json)
