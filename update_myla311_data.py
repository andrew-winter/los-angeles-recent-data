import logging
import functions

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename="myla311.log", format="%(name)s\t%(levelname)s\t%(message)s\t%(asctime)s", level=logging.INFO)
    logger.info("Starting")
    endpoint = functions.make_endpoint(id="2cy6-i7zn")
    soql_query = functions.make_query()
    response = functions.query_endpoint(endpoint, query=soql_query, page=1, limit=500)
    output = functions.check_response(response)
    logger.info("Ending")

if __name__ == "__main__":
    main()
