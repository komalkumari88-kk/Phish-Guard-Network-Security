
import os
import sys

import pandas as pd
from scipy.stats import ks_2samp

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)

from networksecurity.entity.config_entity import DataValidationConfig

from networksecurity.exception.exception import NetworkSecurityException

from networksecurity.logging.logger import logging

from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH

from networksecurity.utils.main_utils.utils import (
    read_yaml_file,
    write_yaml_file
)


class DataValidation:

    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig
    ):

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config

            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

            logging.info("Data validation initialized successfully")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:

        try:
            logging.info(f"Reading dataset: {file_path}")

            dataframe = pd.read_csv(file_path)

            logging.info(
                f"Dataset loaded successfully. Shape: {dataframe.shape}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_expected_columns(self):

        try:
            schema = self._schema_config

            if not isinstance(schema, dict):
                raise ValueError("Schema must be a dictionary")

            columns = schema.get("columns")

            if isinstance(columns, dict):
                expected_columns = list(columns.keys())

            elif isinstance(columns, list):

                expected_columns = []

                for item in columns:

                    if isinstance(item, dict):
                        expected_columns.extend(item.keys())

                    elif isinstance(item, str):
                        expected_columns.append(item)

                    else:
                        raise ValueError(
                            f"Invalid column definition: {item}"
                        )

            else:
                raise ValueError(
                    "Schema columns must be a list or dictionary"
                )

            if not expected_columns:
                raise ValueError("No expected columns found in schema")

            if len(expected_columns) != len(set(expected_columns)):
                raise ValueError("Duplicate columns found in schema")

            logging.info(
                f"Total expected columns: {len(expected_columns)}"
            )

            return expected_columns

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(
        self,
        dataframe: pd.DataFrame
    ) -> bool:

        try:
            expected_columns = self.get_expected_columns()

            actual_columns = list(dataframe.columns)

            logging.info(
                f"Expected number of columns: {len(expected_columns)}"
            )

            logging.info(
                f"Actual number of columns: {len(actual_columns)}"
            )

            # Check column count
            if len(actual_columns) != len(expected_columns):

                logging.error("Column count validation failed")

                return False

            # Check exact column names
            missing_columns = (
                set(expected_columns) - set(actual_columns)
            )

            extra_columns = (
                set(actual_columns) - set(expected_columns)
            )

            if missing_columns or extra_columns:

                logging.error(
                    f"Missing columns: {missing_columns}"
                )

                logging.error(
                    f"Extra columns: {extra_columns}"
                )

                return False

            logging.info("Column validation successful")

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold: float = 0.05
    ) -> bool:

        try:
            status = True

            report = {}

            logging.info("Dataset drift detection started")

            # Check each column
            for column in base_df.columns:

                d1 = base_df[column].dropna()
                d2 = current_df[column].dropna()

                # Numerical column drift detection
                if (
                    pd.api.types.is_numeric_dtype(d1)
                    and pd.api.types.is_numeric_dtype(d2)
                ):

                    if len(d1) == 0 or len(d2) == 0:

                        p_value = 0.0
                        drift_detected = True

                    else:

                        test_result = ks_2samp(d1, d2)

                        p_value = float(test_result.pvalue)

                        drift_detected = p_value < threshold

                else:

                    # Categorical distribution comparison
                    distribution_1 = (
                        d1.value_counts(normalize=True)
                    )

                    distribution_2 = (
                        d2.value_counts(normalize=True)
                    )

                    all_categories = (
                        distribution_1.index.union(
                            distribution_2.index
                        )
                    )

                    distribution_1 = distribution_1.reindex(
                        all_categories,
                        fill_value=0
                    )

                    distribution_2 = distribution_2.reindex(
                        all_categories,
                        fill_value=0
                    )

                    drift_detected = not distribution_1.equals(
                        distribution_2
                    )

                    p_value = None

                if drift_detected:
                    status = False

                report[column] = {
                    "p_value": p_value,
                    "drift_status": drift_detected
                }

                logging.info(
                    f"Column: {column}, "
                    f"Drift detected: {drift_detected}, "
                    f"P-value: {p_value}"
                )

            # Create drift report directory
            drift_report_file_path = (
                self.data_validation_config.drift_report_file_path
            )

            os.makedirs(
                os.path.dirname(drift_report_file_path),
                exist_ok=True
            )

            # Save drift report
            write_yaml_file(
                file_path=drift_report_file_path,
                content=report
            )

            logging.info(
                f"Drift report saved: {drift_report_file_path}"
            )

            logging.info(
                f"Dataset drift detection completed. No drift: {status}"
            )

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:

        try:

            logging.info("Data validation started")

            # Get training and testing dataset paths
            train_file_path = (
                self.data_ingestion_artifact.trained_file_path
            )

            test_file_path = (
                self.data_ingestion_artifact.test_file_path
            )

            # Read datasets
            train_dataframe = DataValidation.read_data(
                train_file_path
            )

            test_dataframe = DataValidation.read_data(
                test_file_path
            )

            # Validate training dataset
            train_status = self.validate_number_of_columns(
                dataframe=train_dataframe
            )

            if not train_status:

                raise ValueError(
                    "Training dataset does not contain expected columns"
                )

            # Validate testing dataset
            test_status = self.validate_number_of_columns(
                dataframe=test_dataframe
            )

            if not test_status:

                raise ValueError(
                    "Testing dataset does not contain expected columns"
                )

            # Check column order
            if list(train_dataframe.columns) != list(
                test_dataframe.columns
            ):

                raise ValueError(
                    "Training and testing columns are not in the same order"
                )

            # Detect dataset drift
            drift_status = self.detect_dataset_drift(
                base_df=train_dataframe,
                current_df=test_dataframe
            )

            # Create output directories
            train_output_path = (
                self.data_validation_config.valid_train_file_path
            )

            test_output_path = (
                self.data_validation_config.valid_test_file_path
            )

            os.makedirs(
                os.path.dirname(train_output_path),
                exist_ok=True
            )

            os.makedirs(
                os.path.dirname(test_output_path),
                exist_ok=True
            )

            # Save validated training data
            train_dataframe.to_csv(
                train_output_path,
                index=False
            )

            # Save validated testing data
            test_dataframe.to_csv(
                test_output_path,
                index=False
            )

            logging.info(
                "Validated training and testing datasets saved"
            )

            # Create validation artifact
            data_validation_artifact = DataValidationArtifact(

                validation_status=drift_status,

                valid_train_file_path=train_output_path,

                valid_test_file_path=test_output_path,

                invalid_train_file_path=(
                    self.data_validation_config.invalid_train_file_path
                ),

                invalid_test_file_path=(
                    self.data_validation_config.invalid_test_file_path
                ),

                drift_report_file_path=(
                    self.data_validation_config.drift_report_file_path
                )
            )

            logging.info(
                f"Data validation artifact: {data_validation_artifact}"
            )

            logging.info(
                "Data validation completed successfully"
            )

            return data_validation_artifact

        except Exception as e:

            logging.exception("Data validation failed")

            raise NetworkSecurityException(e, sys)
