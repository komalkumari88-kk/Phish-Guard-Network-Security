
import os
import sys
import json

import certifi
import pandas as pd
import pymongo

from dotenv import load_dotenv
from pathlib import Path

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

MONGO_DB_URL = os.getenv("MONGODB_URL_KEY")

if not MONGO_DB_URL:
    raise ValueError("MONGODB_URL_KEY is missing from .env")

ca = certifi.where()


class NetworkDataExtract:

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        client = None

        try:
            client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=ca,
                serverSelectionTimeoutMS=10000
            )

            client.admin.command("ping")

            db = client[database]
            collection_obj = db[collection]

            result = collection_obj.insert_many(records)

            logging.info("Dataset uploaded successfully")

            return len(result.inserted_ids)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

        finally:
            if client:
                client.close()


if __name__ == "__main__":

    try:
        FILE_PATH = BASE_DIR / "Network_Data" / "phisingData.csv"

        DATABASE = "KRISHAI"
        COLLECTION = "NetworkData"

        networkobj = NetworkDataExtract()

        records = networkobj.csv_to_json_convertor(
            file_path=FILE_PATH
        )

        print("Total records found:", len(records))

        no_of_records = networkobj.insert_data_mongodb(
            records,
            DATABASE,
            COLLECTION
        )

        print("Successfully uploaded records:", no_of_records)

    except Exception as e:
        raise NetworkSecurityException(e, sys)
