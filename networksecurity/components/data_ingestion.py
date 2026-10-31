
import os
import sys
from pathlib import Path

import certifi
import numpy as np
import pandas as pd
import pymongo

from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from typing import Optional

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact


# --------------------------------------------------
# PROJECT AND MONGODB CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env", override=True)

MONGO_DB_URL = os.getenv("MONGODB_URL_KEY")

if not MONGO_DB_URL:
    raise ValueError(
        "MONGODB_URL_KEY is missing. Please check your project .env file."
    )


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # --------------------------------------------------
    # READ DATA FROM MONGODB
    # --------------------------------------------------

    def export_collection_as_dataframe(self):

        client = None

        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            logging.info("Connecting to MongoDB Atlas")

            client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )

            client.admin.command("ping")

            logging.info("MongoDB Atlas connection successful")

            collection = client[database_name][collection_name]

            records = list(collection.find())

            if not records:
                raise ValueError(
                    f"No records found in {database_name}.{collection_name}"
                )

            df = pd.DataFrame(records)

            if "_id" in df.columns:
                df = df.drop(columns=["_id"])

            df.replace({"na": np.nan}, inplace=True)

            logging.info(
                f"Successfully retrieved {len(df)} records from MongoDB"
            )

            return df

        except Exception as e:
            logging.exception("Error while reading data from MongoDB")
            raise NetworkSecurityException(e, sys)

        finally:
            if client is not None:
                client.close()

    # --------------------------------------------------
    # EXPORT DATA INTO FEATURE STORE
    # --------------------------------------------------

    def export_data_into_feature_store(
        self,
        dataframe: pd.DataFrame
    ):

        try:
            feature_store_file_path = (
                self.data_ingestion_config.feature_store_file_path
            )

            dir_path = os.path.dirname(feature_store_file_path)

            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(
                feature_store_file_path,
                index=False,
                header=True
            )

            logging.info("Feature store file created successfully")

            return dataframe

        except Exception as e:
            logging.exception("Error while exporting feature store")
            raise NetworkSecurityException(e, sys)

    # --------------------------------------------------
    # SPLIT DATA INTO TRAIN AND TEST
    # --------------------------------------------------

    def split_data_as_train_test(
        self,
        dataframe: pd.DataFrame
    ):

        try:
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42
            )

            logging.info("Train-test split completed")

            dir_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )

            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True
            )

            logging.info(
                f"Training records: {len(train_set)}"
            )

            logging.info(
                f"Testing records: {len(test_set)}"
            )

        except Exception as e:
            logging.exception("Error while splitting train and test data")
            raise NetworkSecurityException(e, sys)

    # --------------------------------------------------
    # COMPLETE DATA INGESTION PIPELINE
    # --------------------------------------------------

    def initiate_data_ingestion(self):

        try:
            logging.info("Data ingestion started")

            dataframe = self.export_collection_as_dataframe()

            dataframe = self.export_data_into_feature_store(
                dataframe
            )

            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=(
                    self.data_ingestion_config.training_file_path
                ),
                test_file_path=(
                    self.data_ingestion_config.testing_file_path
                )
            )

            logging.info("Data ingestion completed successfully")

            return data_ingestion_artifact

        except Exception as e:
            logging.exception("Data ingestion pipeline failed")
            raise NetworkSecurityException(e, sys)
