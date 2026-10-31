# PhishGuard – Network Security: Phishing Website Detection Using Machine Learning

## 1. Project Overview

PhishGuard is a Machine Learning-based Network Security application designed to detect phishing websites using website security features.

The project uses a trained Machine Learning model to analyze website-related data and classify websites as legitimate or phishing.

The application provides a web interface where users can upload CSV files and receive prediction results.

### Key Features

- Phishing website detection using Machine Learning.
- CSV file upload and prediction.
- Data ingestion and validation.
- Data transformation and preprocessing.
- Machine Learning model training.
- Model evaluation and artifact generation.
- FastAPI backend.
- HTML-based web interface.
- MLflow integration.
- Docker containerization.
- AWS ECR and EC2 deployment configuration.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine Learning |
| FastAPI | Backend API |
| Uvicorn | Application server |
| MongoDB Atlas | Database integration |
| MLflow | Model tracking |
| Docker | Containerization |
| AWS ECR | Docker image storage |
| AWS EC2 | Cloud deployment |
| Git and GitHub | Version control |
| HTML, CSS, Jinja2 | Web interface |

## 3. Project Architecture

The project follows a Machine Learning pipeline:

1. Data Collection
2. Data Ingestion
3. Data Validation
4. Data Transformation
5. Model Training
6. Model Evaluation
7. Model Saving
8. MLflow Tracking
9. FastAPI Application
10. CSV Upload and Prediction
11. Docker Containerization
12. AWS Deployment

## 4. Project Folder Structure

```text
networksecurity/
│
├── .github/
│   └── workflows/
│       └── main.yml
│
├── Artifacts/
│
├── data_schema/
│   └── schema.yaml
│
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
│
├── networksecurity/
│   ├── cloud/
│   ├── components/
│   ├── constant/
│   ├── entity/
│   ├── exception/
│   ├── logging/
│   ├── pipeline/
│   └── utils/
│
├── templates/
│   ├── index.html
│   └── table.html
│
├── app.py
├── main.py
├── integration.py
├── push_data.py
├── test_mongodb.py
├── Dockerfile
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

*Note: Artifacts are generated during training and may be excluded from GitHub.*

## 5. Clone the GitHub Repository

Open PowerShell or your terminal.

```bash
git clone https://github.com/komalkumari88-kk/Phish-Guard-Network-Security.git
```

Move into the project folder:

```bash
cd Phish-Guard-Network-Security
```

## 6. Python Environment Setup

Create a Conda environment:

```bash
conda create -p venv python=3.11 -y
```

Activate the environment:

```bash
conda activate ./venv
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

## 7. Environment Variables

Create a `.env` file in the project root directory.

Example:

```env
MONGODB_URL=your_mongodb_connection_string
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

Replace the example values with your own credentials.

**Security:**
- Never commit `.env` to GitHub.
- Never publish AWS access keys or MongoDB passwords.
- Keep `.env` in `.gitignore`.
- Use GitHub Secrets for CI/CD credentials.

## 8. Running the Application Locally

Start the FastAPI application:

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:8001/
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8001/docs
```

Health endpoint:

```text
http://127.0.0.1:8001/health
```

### Available API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Open the PhishGuard home page |
| `/health` | GET | Check application health |
| `/train` | GET | Trigger the training pipeline |
| `/predict` | POST | Upload a CSV and generate predictions |
| `/docs` | GET | Open Swagger API documentation |

## 9. CSV File Upload and Prediction

1. Open the PhishGuard application.
2. Select the CSV file containing website security features.
3. Click the Analyze CSV File button.
4. The application reads the uploaded CSV.
5. The trained preprocessing and model objects generate predictions.
6. The prediction results are displayed in the web interface.

**Important:** The uploaded CSV must contain the same input features expected by the trained preprocessing pipeline. The `Result` target column should not be included as an input feature.

## 10. Docker Setup

Docker is used to package the application and its dependencies into a container.

Check Docker installation:

```bash
docker --version
```

Build the Docker image:

```bash
docker build -t networkssecurity .
```

Check available Docker images:

```bash
docker images
```

Run the container:

```bash
docker run -d -p 8001:8001 --name phishguard networkssecurity
```

Check running containers:

```bash
docker ps
```

Open:

```text
http://localhost:8001/
```

*The Dockerfile must start the application on `0.0.0.0:8001` for access through the published container port. Verify its startup command before running this step.*

## 11. AWS Setup

The project deployment configuration uses the following AWS services:

### AWS Services

- AWS IAM – Identity and access management.
- AWS ECR – Container image repository.
- AWS EC2 – Virtual machine for application deployment.

### AWS Region

```text
us-east-1
```

### ECR Repository

```text
networkssecurity
```

### ECR Login URI

```text
788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity
```

## 12. Configure GitHub Repository Secrets

Open your GitHub repository:

Settings → Secrets and variables → Actions → New repository secret.

Add the following secrets:

| Secret Name | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key |
| `AWS_REGION` | `us-east-1` |
| `AWS_ECR_LOGIN_URI` | `788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity` |
| `ECR_REPOSITORY_NAME` | `networkssecurity` |

**Important:**
- Enter the actual AWS credentials only in GitHub Secrets.
- Do not paste credentials into this README.
- Use an IAM identity with only the permissions required for ECR and deployment.
- Rotate any AWS credentials that have accidentally been exposed.

## 13. Docker Installation on AWS EC2

Launch an Ubuntu EC2 instance and connect to it using SSH.

### Step 1: Update the packages

```bash
sudo apt-get update -y
```

### Step 2: Upgrade the packages

```bash
sudo apt-get upgrade -y
```

### Step 3: Download the Docker installation script

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
```

### Step 4: Install Docker

```bash
sudo sh get-docker.sh
```

### Step 5: Verify Docker installation

```bash
sudo docker --version
```

### Step 6: Start Docker

```bash
sudo systemctl start docker
```

Enable Docker at startup:

```bash
sudo systemctl enable docker
```

Check Docker service:

```bash
sudo systemctl status docker
```

## 14. AWS ECR Deployment

Authenticate Docker with Amazon ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 788614365622.dkr.ecr.us-east-1.amazonaws.com
```

Build the Docker image:

```bash
docker build -t networkssecurity .
```

Tag the Docker image:

```bash
docker tag networkssecurity:latest 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity:latest
```

Push the Docker image to ECR:

```bash
docker push 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity:latest
```

These commands assume that the ECR repository already exists and the AWS identity has the required permissions.

## 15. Pull and Run the Image on EC2

After configuring AWS CLI credentials or an EC2 IAM role with ECR permissions, authenticate on the EC2 instance:

```bash
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 788614365622.dkr.ecr.us-east-1.amazonaws.com
```

Pull the image:

```bash
sudo docker pull 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity:latest
```

Run the application:

```bash
sudo docker run -d -p 8001:8001 --name phishguard 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity:latest
```

Check the running container:

```bash
sudo docker ps
```

View container logs:

```bash
sudo docker logs phishguard
```

Open the application using:

```text
http://YOUR_EC2_PUBLIC_IP:8001/
```

Make sure the EC2 security group allows inbound TCP traffic on port 8001 from the intended users. For production, use HTTPS through a reverse proxy or load balancer rather than exposing the application directly.

## 16. GitHub Actions CI/CD

The project contains a GitHub Actions workflow:

```text
.github/workflows/main.yml
```

The workflow can be configured to:

1. Check out the GitHub repository.
2. Set up Python.
3. Install dependencies.
4. Build the Docker image.
5. Authenticate with AWS ECR using GitHub Secrets.
6. Push the Docker image to ECR.
7. Deploy the updated image to EC2.

The actual deployment steps depend on the contents of `main.yml` and the EC2 deployment method. GitHub Secrets must be referenced through the workflow's secrets context, not hardcoded.

## 17. Troubleshooting

| Problem | Possible solution |
|---|---|
| Python package installation error | Check Python version and dependencies |
| MongoDB connection error | Verify MongoDB URL and network access |
| Model file not found | Check `final_model/` paths |
| CSV feature mismatch | Compare uploaded CSV columns with the trained schema |
| Docker command not found | Install and start Docker |
| ECR login failure | Check AWS region, IAM permissions and credentials |
| EC2 connection failure | Check SSH access and security group |
| Application not accessible | Check container status, logs and port mapping |
| GitHub Actions failure | Check workflow configuration and repository secrets |

## 18. Future Improvements

- Improve phishing detection accuracy.
- Add more website security features.
- Improve model evaluation and monitoring.
- Add user authentication.
- Add prediction history.
- Implement HTTPS and secure production deployment.
- Improve CI/CD automation.
- Add automated model retraining.

## 19. Conclusion

PhishGuard demonstrates an end-to-end Machine Learning application for phishing website detection.

The project combines data ingestion, data validation, preprocessing, model training, model evaluation, FastAPI, Docker, MLflow and AWS deployment concepts.

It provides practical experience in Machine Learning, backend development, MLOps, cloud infrastructure and deployment automation.

## 20. Project Links

**GitHub Repository:**

https://github.com/komalkumari88-kk/Phish-Guard-Network-Security

**Local Application:**

http://127.0.0.1:8001/

**API Documentation:**

http://127.0.0.1:8001/docs
