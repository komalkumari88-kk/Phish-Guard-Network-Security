
import sys
from pathlib import Path

import numpy as np
import mlflow
import mlflow.sklearn

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ClassificationMetricArtifact
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_object


class ModelTrainer:

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # STEP 1: Define machine learning models and parameters

    def get_models_and_params(self):

        models = {
            "Random Forest": RandomForestClassifier(random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(random_state=42),
            "AdaBoost": AdaBoostClassifier(random_state=42),
            "Logistic Regression": LogisticRegression(max_iter=1000)
        }

        params = {
            "Random Forest": {
                "n_estimators": [50, 100],
                "max_depth": [None, 10]
            },
            "Decision Tree": {
                "max_depth": [5, 10, None]
            },
            "Gradient Boosting": {
                "n_estimators": [50, 100],
                "learning_rate": [0.05, 0.1]
            },
            "AdaBoost": {
                "n_estimators": [50, 100],
                "learning_rate": [0.5, 1.0]
            },
            "Logistic Regression": {
                "C": [0.1, 1.0, 10.0]
            }
        }

        return models, params

    # STEP 2: Calculate classification metrics

    def calculate_metrics(self, model, X, y):

        predictions = model.predict(X)

        return ClassificationMetricArtifact(
            f1_score=float(
                f1_score(y, predictions, zero_division=0)
            ),
            precision_score=float(
                precision_score(y, predictions, zero_division=0)
            ),
            recall_score=float(
                recall_score(y, predictions, zero_division=0)
            )
        )

    # STEP 3: Track model and metrics using MLflow

    def track_mlflow(self, best_model, metrics, accuracy):

        try:

            project_dir = Path(__file__).resolve().parents[2]
            mlflow_db = project_dir / "mlflow.db"

            tracking_uri = f"sqlite:///{mlflow_db.as_posix()}"

            mlflow.set_tracking_uri(tracking_uri)

            mlflow.set_experiment(
                "Network-Security-Phishing-Detection"
            )

            with mlflow.start_run():

                mlflow.log_metric(
                    "accuracy",
                    float(accuracy)
                )

                mlflow.log_metric(
                    "f1_score",
                    float(metrics.f1_score)
                )

                mlflow.log_metric(
                    "precision",
                    float(metrics.precision_score)
                )

                mlflow.log_metric(
                    "recall",
                    float(metrics.recall_score)
                )

                # IMPORTANT:
                # Use cloudpickle to avoid the skops
                # untrusted sklearn.tree._tree.Tree error.

                mlflow.sklearn.log_model(
                    sk_model=best_model,
                    artifact_path="model",
                    serialization_format="cloudpickle"
                )

            logging.info(
                "MLflow tracking completed successfully"
            )

        except Exception as e:

            logging.exception(
                "MLflow tracking failed"
            )

            raise NetworkSecurityException(e, sys)

    # STEP 4: Main model training method

    def initiate_model_trainer(self) -> ModelTrainerArtifact:

        logging.info("Starting model training")

        try:

            # Load transformed file paths

            train_file_path = (
                self.data_transformation_artifact.transformed_train_file_path
            )

            test_file_path = (
                self.data_transformation_artifact.transformed_test_file_path
            )

            # Load NumPy arrays

            train_arr = np.load(train_file_path)
            test_arr = np.load(test_file_path)

            logging.info(
                f"Training array shape: {train_arr.shape}"
            )

            logging.info(
                f"Testing array shape: {test_arr.shape}"
            )

            # Separate input features and target

            X_train = train_arr[:, :-1]
            y_train = train_arr[:, -1].astype(int)

            X_test = test_arr[:, :-1]
            y_test = test_arr[:, -1].astype(int)

            logging.info(
                "Features and target separated successfully"
            )

            # Get models and hyperparameters

            models, params = self.get_models_and_params()

            best_model = None
            best_model_name = None
            best_cv_score = -1

            # Train and compare all models

            for model_name, model in models.items():

                logging.info(
                    f"Training model: {model_name}"
                )

                grid_search = GridSearchCV(
                    estimator=model,
                    param_grid=params[model_name],
                    cv=3,
                    scoring="f1",
                    n_jobs=-1,
                    verbose=1
                )

                grid_search.fit(
                    X_train,
                    y_train
                )

                logging.info(
                    f"{model_name} best CV score: "
                    f"{grid_search.best_score_}"
                )

                if grid_search.best_score_ > best_cv_score:

                    best_cv_score = grid_search.best_score_
                    best_model = grid_search.best_estimator_
                    best_model_name = model_name

            if best_model is None:

                raise Exception(
                    "No model was successfully trained"
                )

            logging.info(
                f"Best model selected: {best_model_name}"
            )

            # Calculate training and testing accuracy

            train_predictions = best_model.predict(X_train)
            test_predictions = best_model.predict(X_test)

            train_accuracy = accuracy_score(
                y_train,
                train_predictions
            )

            test_accuracy = accuracy_score(
                y_test,
                test_predictions
            )

            # Calculate classification metrics

            train_metric_artifact = self.calculate_metrics(
                best_model,
                X_train,
                y_train
            )

            test_metric_artifact = self.calculate_metrics(
                best_model,
                X_test,
                y_test
            )

            logging.info(
                f"Training accuracy: {train_accuracy}"
            )

            logging.info(
                f"Testing accuracy: {test_accuracy}"
            )

            logging.info(
                f"Testing F1 score: {test_metric_artifact.f1_score}"
            )

            logging.info(
                f"Testing precision: "
                f"{test_metric_artifact.precision_score}"
            )

            logging.info(
                f"Testing recall: {test_metric_artifact.recall_score}"
            )

            # Check minimum model accuracy

            if test_accuracy < 0.60:

                raise Exception(
                    "Model accuracy is below the expected minimum of 0.60"
                )

            # Save trained model in Artifacts folder

            model_file_path = Path(
                self.model_trainer_config.trained_model_file_path
            )

            model_file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            save_object(
                str(model_file_path),
                best_model
            )

            logging.info(
                f"Trained model saved at: {model_file_path}"
            )

            # Save final model for prediction

            project_dir = Path(__file__).resolve().parents[2]

            final_model_dir = project_dir / "final_model"

            final_model_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            final_model_path = final_model_dir / "model.pkl"

            save_object(
                str(final_model_path),
                best_model
            )

            logging.info(
                f"Final model saved at: {final_model_path}"
            )

            # Track experiment using MLflow

            self.track_mlflow(
                best_model,
                test_metric_artifact,
                test_accuracy
            )

            # Create model trainer artifact

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=str(model_file_path),
                train_metric_artifact=train_metric_artifact,
                test_metric_artifact=test_metric_artifact
            )

            logging.info(
                "Model training completed successfully"
            )

            return model_trainer_artifact

        except Exception as e:

            logging.exception(
                "Error occurred during model training"
            )

            raise NetworkSecurityException(e, sys)
