#!/usr/bin/env python3

"""Basic MySQL examples matching basic-sql.ipynb (media.MOCK_DATA)."""

import json
import os

import mysql.connector
import pandas as pd

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME") 

db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DBNAME)
cur = db.cursor()

def get_data_by_group(groupname):
    """Return mock rows whose group matches ``groupname`` (list of tuples)."""
    query = "SELECT * FROM mock WHERE `group` = %s;"
    try:
        cur.execute(query, (groupname,))
        results = cur.fetchall()
        output = []
        for r in results:
            output.append(r)
        return output
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def plot_counts():
    """Count people per continent, show a bar chart, and return the DataFrame."""
    query = "SELECT `group`, COUNT(`group`) FROM mock GROUP BY `group`;"
    try:
        cur.execute(query)
        results = cur.fetchall()
        output = []
        for r in results:
            output.append(r)
        return output
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def main():
    """Run the demo queries and close the database connection."""

    print("=== by group ===")
    print(get_data_by_group("fries"))

    print(plot_counts())

    cur.close()
    db.close()


if __name__ == "__main__":
    main()