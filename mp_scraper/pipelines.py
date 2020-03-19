from collections.abc import Sequence, Collection
import json
import logging
import mysql.connector
from scrapy.exceptions import DropItem


class SqlPipeline(object):
    """Pipeline to insert items into the database if they don't already exist"""

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
        missing_keys = [field for field in item.required_fields if item[field] is None]

        if len(missing_keys) > 0:
            raise DropItem("MISSING_KEYS: %s" % missing_keys)
        else:
            logging.debug("Processing %s" % item.__class__.__name__)
            return item

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
