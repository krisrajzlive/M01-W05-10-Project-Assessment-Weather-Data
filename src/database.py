# Imports MongoClient for base level access to the local MongoDB
from pymongo import MongoClient
from datetime import datetime

class Database:
    # Class static variables used for database host ip and port information, database name
    # Static variables are referred to by using <class_name>.<variable_name>
    HOST = '127.0.0.1'
    PORT = '27017'
    DB_NAME = 'weather_db'
    WEATHER_DATA = 'weather_data'

    def __init__(self):
        self._db_conn = MongoClient(f'mongodb://{Database.HOST}:{Database.PORT}')
        self._db = self._db_conn[Database.DB_NAME]
    
    # This method finds a single document using field information provided in the key parameter
    # It assumes that the key returns a unique document. It returns None if no document is found
    # Problem statement: 1-a - Allowing only admin users to write or read data
    def get_single_data(self, collection, key):
        db_collection = self._db[collection]
        document = db_collection.find_one(key)
        return document

    # get_single_data_byquery method returns a document based on query which may include one or more simple or complex condition
    def get_single_data_byquery(self, collection, query):
        db_collection = self._db[collection]
        document = db_collection.find(query)
        return document
    
    # This method inserts the data in a new document. It assumes that any uniqueness check is done by the caller
    def insert_single_data(self, collection, data):
        #if(usertype.strip().upper() == 'ADMIN'):
            #raise Exception('Sorry, The user is not allowed to perform this operation!')
        db_collection = self._db[collection]
        document = db_collection.insert_one(data)
        return document.inserted_id

    # This method returns aggregate device data per device per day for the given deviceid and and date ranges
    # Assumption: date should be in date format, not in string.
    def get_admin_aggregate_weather_data(self, startdate, enddate, role, deviceids = None):
        db_collection = self._db[Database.WEATHER_DATA]
        
        if self.__truncateandcapitalize(role) == 'ADMIN' and deviceids == None:
            documents = db_collection.aggregate([
            {
                "$match": {
                    "timestamp" : {
                        "$gte" : startdate,
                        "$lte" : enddate
                    }
                }
            },
            {
                "$group": {
                        "_id": {
                            "deviceid": "$device_id",
                            "month": { "$month": "$timestamp" },
                            "day": { "$dayOfMonth": "$timestamp" },
                            "year": { "$year": "$timestamp" }
                        },
                        "Average" : {
                            "$avg" : "$value"
                        },
                        "Minimum" : {
                            "$min" : "$value"
                        },
                        "Maximum" : {
                            "$max" : "$value"
                        }
                    }
            },
            {
                "$project": {
                    "deviceid": "$_id.deviceid",
                    "day": ["$_id.year", "$_id.month", "$_id.day"],
                    "Average": "$Average",
                    "Minimum": "$Minimum",
                    "Maximum": "$Maximum",
                }
            },
            {
                "$sort": {
                    "deviceid": 1,
                    "day": 1
                }
            }
        ])
        elif self.__truncateandcapitalize(role) == 'ADMIN' and deviceids != None:
            documents = db_collection.aggregate([
                {
                    "$match": {
                        "device_id" : {'$in': deviceids},
                        "timestamp" : {
                            "$gte" : startdate,
                            "$lte" : enddate
                        }
                    }
                },
                {
                    "$group": {
                            "_id": {
                                "deviceid": "$device_id",
                                "month": { "$month": "$timestamp" },
                                "day": { "$dayOfMonth": "$timestamp" },
                                "year": { "$year": "$timestamp" }
                            },
                            "Average" : {
                                "$avg" : "$value"
                            },
                            "Minimum" : {
                                "$min" : "$value"
                            },
                            "Maximum" : {
                                "$max" : "$value"
                            }
                        }
                },
                {
                    "$project": {
                        "deviceid": "$_id.deviceid",
                        "day": ["$_id.year", "$_id.month", "$_id.day"],
                        "Average": "$Average",
                        "Minimum": "$Minimum",
                        "Maximum": "$Maximum",
                    }
                },
                {
                    "$sort": {
                        "deviceid": 1,
                        "day": 1
                    }
                }
            ])
        else:
            raise Exception('Aggregate report has invalid parameter(s)')
        return documents

    # This method returns aggregate device data per device per day for the given deviceid and and date ranges
    # Assumption: date should be in date format, not in string.
    def get_aggregate_weather_data(self, startdate, enddate, role, deviceids = None):
        db_collection = self._db[Database.WEATHER_DATA]
        
        if self.__truncateandcapitalize(role) != 'ADMIN' and deviceids != None:
            documents = db_collection.aggregate([
                {
                    "$match": {
                        "device_id" : {'$in': deviceids},
                        "timestamp" : {
                            "$gte" : startdate,
                            "$lte" : enddate
                        }
                    }
                },
                {
                    "$group": {
                            "_id": {
                                "deviceid": "$device_id",
                                "month": { "$month": "$timestamp" },
                                "day": { "$dayOfMonth": "$timestamp" },
                                "year": { "$year": "$timestamp" }
                            },
                            "Average" : {
                                "$avg" : "$value"
                            },
                            "Minimum" : {
                                "$min" : "$value"
                            },
                            "Maximum" : {
                                "$max" : "$value"
                            }
                        }
                },
                {
                    "$project": {
                        "deviceid": "$_id.deviceid",
                        "day": ["$_id.year", "$_id.month", "$_id.day"],
                        "Average": "$Average",
                        "Minimum": "$Minimum",
                        "Maximum": "$Maximum",
                    }
                },
                {
                    "$sort": {
                        "deviceid": 1,
                        "day": 1
                    }
                }
            ])
        elif self.__truncateandcapitalize(role) == 'ADMIN' and deviceid == None:
            documents = db_collection.aggregate([
            {
                "$match": {
                    "timestamp" : {
                        "$gte" : startdate,
                        "$lte" : enddate
                    }
                }
            },
            {
                "$group": {
                        "_id": {
                            "deviceid": "$device_id",
                            "month": { "$month": "$timestamp" },
                            "day": { "$dayOfMonth": "$timestamp" },
                            "year": { "$year": "$timestamp" }
                        },
                        "Average" : {
                            "$avg" : "$value"
                        },
                        "Minimum" : {
                            "$min" : "$value"
                        },
                        "Maximum" : {
                            "$max" : "$value"
                        }
                    }
            },
            {
                "$project": {
                    "deviceid": "$_id.deviceid",
                    "day": ["$_id.year", "$_id.month", "$_id.day"],
                    "Average": "$Average",
                    "Minimum": "$Minimum",
                    "Maximum": "$Maximum",
                }
            },
            {
                "$sort": {
                    "deviceid": 1,
                    "day": 1
                }
            }
        ])
        elif self.__truncateandcapitalize(role) == 'ADMIN' and deviceid != None:
            documents = db_collection.aggregate([
                {
                    "$match": {
                        "device_id" : deviceid,
                        "timestamp" : {
                            "$gte" : startdate,
                            "$lte" : enddate
                        }
                    }
                },
                {
                    "$group": {
                            "_id": {
                                "deviceid": "$device_id",
                                "month": { "$month": "$timestamp" },
                                "day": { "$dayOfMonth": "$timestamp" },
                                "year": { "$year": "$timestamp" }
                            },
                            "Average" : {
                                "$avg" : "$value"
                            },
                            "Minimum" : {
                                "$min" : "$value"
                            },
                            "Maximum" : {
                                "$max" : "$value"
                            }
                        }
                },
                {
                    "$project": {
                        "deviceid": "$_id.deviceid",
                        "day": ["$_id.year", "$_id.month", "$_id.day"],
                        "Average": "$Average",
                        "Minimum": "$Minimum",
                        "Maximum": "$Maximum",
                    }
                },
                {
                    "$sort": {
                        "deviceid": 1,
                        "day": 1
                    }
                }
            ])
        else:
            raise Exception('Aggregate report has invalid parameter(s)')
        return documents
    
    # method used to truncate leading and trailing spaces and convert the parameter to uppercase
    def __truncateandcapitalize(self, arg):
        return arg.strip().upper()
