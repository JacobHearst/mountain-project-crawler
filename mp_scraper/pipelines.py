from collections.abc import Sequence, Collection
import json
import logging
import mysql.connector
from mysql.connector import errors, errorcode
from scrapy.exceptions import DropItem


class SqlPipeline(object):
    """Pipeline to insert items into the database if they don't already exist"""
    item_sql_metadata = {
        "Area": {
            "table_name": "area",
            "required_fields": ["area_id", "name", "link"]
        },
        "Route": {
            "table_name": "route",
            "required_fields": ["route_id", "parent_id", "name", "link"]
        },
        "MonthlyTempAvgs": {
            "table_name": "temp_avg",
            "required_fields": ["area_id", "month", "avg_low", "avg_high"]
        },
        "MonthlyPrecipAvgs": {
            "table_name": "precip_avg",
            "required_fields": ["area_id", "month", "avg_low", "avg_high"]
        },
        "ClimbSeasonValue": {
            "table_name": "climb_season",
            "required_fields": ["area_id", "month", "value"]
        },
        "RouteGrade": {
            "table_name": "route_grade",
            "required_fields": ["route_id", "grade", "grade_system"]
        }
    }

    def open_spider(self, spider):
        """Open a database connection and create a cursor"""
        with open("db_config.json", "r") as json_file:
            db_config = json.load(json_file)

            self.db = mysql.connector.connect(
                host=db_config["host"],
                user=db_config["user"],
                passwd=db_config["passwd"],
                database=db_config["database"]
            )

        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        """Commit data and close database connection"""
        self.db.commit()
        self.db.close()

    def process_item(self, item, spider):
        """Process an SQL query and execute it
        
        Arguments:
            item {scrapy.Item} -- Item to add to the database
            spider {scrapy.Spider} -- Spider that the item came from
        
        Raises:
            DropItem: Drops items missing required keys
        
        Returns:
            scrapy.Item -- The unmodified scraped item
        """
        item_class_name = item.__class__.__name__
        item_metadata = self.item_sql_metadata[item_class_name]

        missing_keys = [
            field for field in item_metadata["required_fields"] if item[field] is None]

        if len(missing_keys) > 0:
            raise DropItem("MISSING_KEYS: %s" % missing_keys)
        else:
            logging.debug("Processing %s" % item_class_name)

            try:
                self.insert_item(item_metadata["table_name"], item)            
            except Exception as e:
                self.handle_exception(e)

            return item

    def insert_item(self, table_name, item):
        encoded_vals = [self.sql_encode(val) for val in item.values()]
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            table_name,
            ", ".join(item.keys()),
            ", ".join(encoded_vals)
        )

        self.cursor.execute(sql)

    def sql_encode(self, value):
        """Encode provided value and return a valid SQL value
        
        Arguments:
            value {Any} -- Value to encode
        
        Returns:
            str -- SQL encode value as a str
        """
        encoded_val = None
        is_empty = False

        if isinstance(value, str):
            is_empty = len(value) == 0

        encoded_val = "NULL" if is_empty or value is None else value

        if isinstance(encoded_val, str) and encoded_val is not "NULL":
            encoded_val = "\"%s\"" % encoded_val

        return str(encoded_val)

    def handle_exception(self, exception):
        """Handle exceptions arising from inserting records
        
        Arguments:
            exception {Exception} -- The exception that was thrown
        
        Raises:
            exception: Raises the original exception if it's unrecognized
        """        
        if type(exception) is errors.IntegrityError:
            if exception.errno != errorcode.ER_DUP_ENTRY:
                raise exception
        
        else:
            raise exception
