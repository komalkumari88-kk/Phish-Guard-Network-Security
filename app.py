

import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Request,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run


# --------------------------------------------------
# 1. PROJECT PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv(dotenv_path=BASE_DIR / ".env")


# --------------------------------------------------
# 3. PROJECT IMPORTS
# --------------------------------------------------

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


# --------------------------------------------------
# 4. CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="PhishGuard - Network Security",
    description="Machine Learning Based Phishing Website Detection",
    version="1.0.0"
)


# --------------------------------------------------
# 5. CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# 6. HTML TEMPLATE CONFIGURATION
# --------------------------------------------------

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# --------------------------------------------------
# 7. HOME ROUTE
# --------------------------------------------------

@app.get("/", tags=["Home"])
async def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


# --------------------------------------------------
# 8. HEALTH CHECK ROUTE
# --------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():

    return {
        "status": "success",
        "message": "PhishGuard application is running"
    }


# --------------------------------------------------
# 9. TRAINING ROUTE
# --------------------------------------------------

@app.get("/train", tags=["Training"])
async def train_route():

    try:

        logging.info("Training pipeline started")

        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()

        logging.info("Training pipeline completed successfully")

        return Response(
            content="Training completed successfully",
            media_type="text/plain",
            status_code=200
        )

    except Exception as e:

        logging.exception("Training pipeline failed")

        raise NetworkSecurityException(e, sys)


# --------------------------------------------------
# 10. PREDICTION ROUTE
# --------------------------------------------------

@app.post("/predict", tags=["Prediction"])
async def predict_route(
    request: Request,
    file: UploadFile = File(...)
):

    try:

        logging.info("Prediction started")

        # Validate uploaded file
        if (
            not file.filename
            or not file.filename.lower().endswith(".csv")
        ):

            raise HTTPException(
                status_code=400,
                detail="Please upload a valid CSV file."
            )

        # Read CSV file
        df = pd.read_csv(file.file)

        if df.empty:

            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV file is empty."
            )

        logging.info(f"Uploaded CSV shape: {df.shape}")

        # --------------------------------------------------
        # REMOVE TARGET COLUMN
        # --------------------------------------------------

        # Result is the target column, not an input feature.
        # Remove it before passing data to the trained model.

        if "Result" in df.columns:
            df = df.drop(columns=["Result"])

            logging.info(
                "Removed Result column from uploaded CSV"
            )

        # --------------------------------------------------
        # CHECK MODEL FILES
        # --------------------------------------------------

        preprocessor_path = (
            BASE_DIR / "final_model" / "preprocessor.pkl"
        )

        model_path = (
            BASE_DIR / "final_model" / "model.pkl"
        )

        if not preprocessor_path.exists():

            raise FileNotFoundError(
                "Preprocessor not found. Please train the model first."
            )

        if not model_path.exists():

            raise FileNotFoundError(
                "Model not found. Please train the model first."
            )

        # --------------------------------------------------
        # LOAD TRAINED MODEL AND PREPROCESSOR
        # --------------------------------------------------

        preprocessor = load_object(str(preprocessor_path))

        final_model = load_object(str(model_path))

        # Initialize prediction model
        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=final_model
        )

        # --------------------------------------------------
        # GENERATE PREDICTIONS
        # --------------------------------------------------

        y_pred = network_model.predict(df)

        # Add prediction column
        df["predicted_column"] = y_pred

        # --------------------------------------------------
        # SAVE PREDICTION RESULTS
        # --------------------------------------------------

        output_dir = BASE_DIR / "prediction_output"

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = output_dir / "output.csv"

        df.to_csv(
            output_file,
            index=False
        )

        logging.info(
            f"Prediction output saved to: {output_file}"
        )

        # --------------------------------------------------
        # CONVERT RESULTS TO HTML
        # --------------------------------------------------

        table_html = df.to_html(
            classes="table table-striped",
            index=False,
            border=0
        )

        logging.info("Prediction completed successfully")

        # Display prediction results
        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={
                "request": request,
                "table": table_html
            }
        )

    except HTTPException:

        raise

    except Exception as e:

        logging.exception("Prediction failed")

        raise NetworkSecurityException(e, sys)

    finally:

        await file.close()


# --------------------------------------------------
# 11. RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app_run(
        app,
        host="127.0.0.1",
        port=8001
    )
