import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL_KEY")

print(MONGO_DB_URL)

import certifi
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo

class MilkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise Exception(e,sys)
        
    def csv_to_json(self,file_path):
        df=pd.read_csv(file_path)

        RECORDS= {
            "username": "nimuni",
            "password": "milk7",  # optional
            "milk_log": dict(zip(df.date,df.quantity)),
            "total_days":18,
            "extra_milk": 0.5,
            "naga": 1
            }
        
        return RECORDS

    def insert_data_to_monogdb(self,records,database,collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)

            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]

            self.collection.insert_one(self.records)

            return len(self.records)
        
        except Exception as e:
            raise Exception(e,sys)

if __name__ == "__main__":
    FILE_PATH = "data.csv"
    DATABASE = "milk_app"
    COLLECTION = "milk_log"

    milkobj = MilkDataExtract()
    RECORDS = milkobj.csv_to_json(file_path=FILE_PATH)
    print(RECORDS)
    no_of_records = milkobj.insert_data_to_monogdb(records=RECORDS,database=DATABASE,collection=COLLECTION)

    print("Records : ",no_of_records)

