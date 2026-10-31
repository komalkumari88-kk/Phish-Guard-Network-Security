
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get MongoDB URL from .env
uri = os.getenv("MONGODB_URL_KEY")

if not uri:
    raise ValueError("MONGODB_URL_KEY not found in .env")

# Connect to MongoDB Atlas
client = MongoClient(
    uri,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000
)

try:
    client.admin.command("ping")
    print("Pinged your deployment.")
    print("Successfully connected to MongoDB Atlas!")

except Exception as e:
    print("Connection failed:", e)

finally:
    client.close()
