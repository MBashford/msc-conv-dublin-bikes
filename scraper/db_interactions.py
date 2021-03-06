"""
Created on 16 Feb 2020
@author: Milo Bashford
methods for retrieving and sending data to the Team 14 RDS Database
"""

import mysql.connector
from configparser import ConfigParser

# read DataBase info from the config file
config = ConfigParser()
config.read("config.ini")
options = config["DataBase"]


def db_query(**kwargs):
    """Constructs & sends a query to the RDS database

    Takes **kwargs: 'query', 'table', 'data'. """

    # dict that associates value of **kwarg["query"] with sql query
    valid_queries = {"push": "INSERT INTO", "pull": "SELECT * FROM", "update": "UPDATE", "keys": "SHOW KEYS FROM"}

    # dict that associates passed **kwarg["table"] with a valid table
    valid_tables = {"w_dynamic": "dublinbikes.weather_dynamic",
                    "static": "dublinbikes.static_data",
                    "dynamic": "dublinbikes.dynamic_data",
                    "w_static": "dublinbikes.weather_static",
                    "assoc": "dublinbikes.bike_weather_assoc",
                    "w_current": "dublinbikes.weather_current",
                    "w_forecast": "dublinbikes.weather_forecast",
                    "current": "dublinbikes.bikes_current"}

    # host & login information to database
    host = options["host"]
    passwd = options["passwd"]
    user = options["user"]
    database = options["database"]

    # establish connection to database
    connection = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)

    # construct the sql query from the passed arguments
    if "query" in kwargs:
        query = valid_queries[kwargs["query"]]
    else:
        return "Error: no such query: " + kwargs["query"]

    if "table" in kwargs:
        table = valid_tables[kwargs["table"]]
    else:
        return "Error: no such table: " + kwargs["table"]

    if "data" in kwargs:
        data = kwargs["data"]
    
    if "pkeys" in kwargs:
        pkeys = kwargs["pkeys"]
    else:
        pkeys = None

    sql = query + " " + table

    # if db query is to insert rows;
    if kwargs["query"] == "push":
        values = []
        fields = ""
        fields_type = ""

        # extract each key, value and datatype from data into list 'values' & strings 'fields' & 'fields_type'
        for key in data:
            if len(fields) < 1:
                fields += key
                fields_type += "%s"
            else:
                fields += ", " + key
                fields_type += ", %s"

            values.append(str(data[key]))

        sql += " (" + fields + ") VALUES (" + fields_type + ")"

    # else if db query is to update rows;
    elif kwargs["query"] == "update":

        # query db for table primary keys
        p_keys = []
        for item in db_query(query="keys", table=kwargs["table"]):
            p_keys.append(item[4])

        sql += " SET"

        # checks to see if primary keys are supplied
        # added in so that primary key data could be changed
        if pkeys is None:
            for key in data:
                sql += " `%s` = '%s'," % (key, data[key])
            sql = sql[:-1]
    
            sql += " WHERE"
            for key in pkeys:
                if key in p_keys:
                    if p_keys.index(key) > 0:
                        sql += " AND"
                    sql += " %s = '%s'" % (key, pkeys[key])
                else:
                    return "Primary Keys are: ", p_keys
        else:
            for key in data:
                if key not in p_keys:
                    sql += " `%s` = '%s'," % (key, data[key])
            sql = sql[:-1]
    
            sql += " WHERE"
            for key in p_keys:
                if p_keys.index(key) > 0:
                    sql += " AND"
                sql += " %s = '%s'" % (key, pkeys[key])

    # else if db query is to show keys;
    elif kwargs["query"] == "keys":
        sql += " WHERE key_name = 'PRIMARY'"

    # execute the sql query
    try:

        # on insert query
        if kwargs["query"] == "push":
            dbcursor = connection.cursor(buffered=True)
            dbcursor.execute(sql, values)
            connection.commit()

        # on update query
        elif kwargs["query"] == "update":
            dbcursor = connection.cursor(buffered=True)
            dbcursor.execute(sql)
            return connection.commit()

        # on select query
        elif kwargs["query"] == "pull":
            dbcursor = connection.cursor(dictionary=True, buffered=True)
            dbcursor.execute(sql)
            return dbcursor.fetchall()

        # on keys query
        elif kwargs["query"] == "keys":
            dbcursor = connection.cursor(buffered=True)
            dbcursor.execute(sql)
            return dbcursor.fetchall()

        # query not defined
        else:
            print("Error: query not defined")
            return False

    except Exception as e:
        return e.errno, e.msg
