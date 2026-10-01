"""Load a CSV file into a MySQL table using row-by-row parameterized INSERTs."""

import logging
import os
import re
import sys

import mysql.connector
import pandas as pd

# Configure logging so every function can report its status
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Read database credentials from environment variables
DBHOST = os.environ.get("DBHOST")
DBNAME = os.environ.get("DBNAME")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")

# Default CSV path (override by passing a path as the first command-line argument)
DEFAULT_CSV = "MOCK_DATA.csv"

type_mapping = {
    "int64": "BIGINT",
    "string": "VARCHAR(255)",
    "str": "VARCHAR(255)"
}

def read_data(filename):
    """Read a CSV file into a pandas DataFrame.
    arguments: path to the CSV file
    output: df containing the CSV contents
    """
    logger.info("Reading data from %s", filename)
    data = pd.read_csv(filename)
    logger.info("Read %d rows and %d columns", data.shape[0], data.shape[1])
    return data


def clean_data(data):
    """Clean and normalize data by removing rows with empty values and normalizing values
    arguments: data: The raw pandas DataFrame.
    output: The cleaned pandas DataFrame.
    """
    logger.info("Cleaning data (%d rows before cleaning)", len(data))

    # strip whitespace, set to lower, replace symbols
    data = data.rename(
        columns=lambda c: re.sub(r"\W+", "_", str(c).strip().lower()).strip("_")
    )

    # drop any row that has a missing value
    data = data.dropna().reset_index(drop=True)

    logger.info("Cleaning complete (%d rows after cleaning)", len(data))
    return data


def load_data(data, table):
    """Create the table (if needed) and insert the DataFrame row by row.
    arguments:
        data: The cleaned pandas DataFrame to upload.
        table: The destination table name.
    """
    logger.info("Loading %d rows into table '%s'", len(data), table)
 
    # Build the column definitions from the DataFrame dtypes
    # (backticks protect reserved words like `group`)
    columns = ", ".join(
        f"`{col}` {type_mapping[str(dtype)]}" for col, dtype in data.dtypes.items()
    )
    create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({columns})"
 
    col_names = ", ".join(f"`{col}`" for col in data.columns)
    placeholders = ", ".join(["%s"] * len(data.columns))
    insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
 
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DBHOST, database=DBNAME, user=DBUSER, password=DBPASS
        )
        cursor = conn.cursor()
 
        cursor.execute(create_sql)
 
        # tolist() converts numpy types to plain Python values
        for row in data.values.tolist():
            cursor.execute(insert_sql, tuple(row))
 
        conn.commit()
        logger.info("Inserted %d rows into '%s'", len(data), table)
    except mysql.connector.Error as err:
        logger.error("Database error: %s", err)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            logger.info("Connection closed")
 


def main():
    """Run the full pipeline: read, clean, then load the data."""
    logger.info("Starting pipeline")
    filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    data = read_data(filename)
    data = clean_data(data)
    load_data(data, 'mock')
    logger.info("Pipeline finished")


if __name__ == "__main__":
    main()