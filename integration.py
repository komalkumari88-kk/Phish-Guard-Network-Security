
import os
import sys
import certifi

from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

from networksecurity.pipeline.training_pipeline import TrainingPipeline

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def test_mongodb_connection():
    print("\nSTEP 1: Checking MongoDB connection...")

    mongo_url = os.getenv("MONGODB_URL_KEY")

    if not mongo_url:
        raise ValueError("MONGODB_URL_KEY is missing in .env")

    client = MongoClient(
        mongo_url,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")
        print("SUCCESS: MongoDB connected!")
    finally:
        client.close()


def run_training_pipeline():
    print("\nSTEP 2: Starting training pipeline...")

    pipeline = TrainingPipeline()
    pipeline.run_pipeline()

    print("SUCCESS: Training pipeline completed!")


if __name__ == "__main__":
    try:
        test_mongodb_connection()
        run_training_pipeline()

        print("\nINTEGRATION TEST COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print("\nINTEGRATION TEST FAILED!")
        print("Error:", e)
        raise
