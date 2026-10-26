# House Price Prediction — Machine Learning Web Application

A full-stack, responsive Machine Learning web dashboard designed for residential property valuation using **Python, Flask, Scikit-Learn (Linear Regression), HTML5/CSS3, Chart.js**, and production-grade **AWS EC2 (Gunicorn + Nginx)** deployment architecture.

Developed with clean, transparent engineering principles — ideal for academic evaluation, college capstone defense, and real-world portfolio demonstration.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Technology Stack](#technology-stack)
3. [Project Architecture](#project-architecture)
4. [Machine Learning Details](#machine-learning-details)
5. [Project Directory Structure](#project-directory-structure)
6. [Local Setup & Execution](#local-setup--execution)
7. [Running Unit Tests](#running-unit-tests)
8. [AWS EC2 Deployment Guide (Step-by-Step)](#aws-ec2-deployment-guide-step-by-step)
9. [College Viva & Presentation Guide](#college-viva--presentation-guide)
10. [License](#license)

---

## Key Features

- **Professional Analytics Dashboard**: Clean real-estate aesthetic styled in deep navy blue, crisp white, soft gray, and emerald green.
- **Real Scikit-Learn Model**: Trains a true Ordinary Least Squares (OLS) Linear Regression model; never returns mock or hardcoded numbers.
- **Dynamic Session Metrics**: Real-time tracking of session predictions count, latest price, and average session price in server memory without database bloat.
- **Interactive Chart.js Visualizer**: Dynamic line chart updating with each property prediction to visualize valuation trends.
- **Two-Tier Validation**: Client-side feedback in JavaScript coupled with rigorous server-side verification rejecting negative, non-numeric, or physical outliers.
- **Indian Rupee Formatting**: Clear, readable valuation output formatted in Indian numbering standards (e.g. `₹48,50,000` / `₹48.50 Lakh`).
- **Production-Ready AWS Config**: Pre-built configurations for Gunicorn WSGI, Nginx reverse proxy, and Systemd service automation.

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5, CSS3, Jinja2 | Responsive dashboard layout, cards, and forms |
| **Data Viz** | Chart.js 4.x | Real-time session prediction trend chart |
| **Backend API** | Python 3.10+, Flask 3.x | RESTful endpoints, validation, session state |
| **Machine Learning**| scikit-learn, pandas, numpy | Dataset handling, OLS Linear Regression, metrics |
| **Model Persistence**| Joblib | Serialized model loading (`.joblib`) on Flask startup |
| **Testing** | pytest | Automated unit and integration testing suite |
| **WSGI Server** | Gunicorn | Multi-process WSGI server bound to `127.0.0.1:8000` |
| **Reverse Proxy** | Nginx | Static file serving, gzip compression, HTTP/HTTPS proxy |
| **Cloud Host** | AWS EC2 (AL2023 / Ubuntu) | Elastic Compute Cloud deployment target |

---

## Project Architecture

```
Client Browser (HTML5 / CSS3 / Chart.js)
                 │
                 ▼  [Port 80 HTTP / 443 HTTPS]
┌────────────────────────────────────────────────────────┐
│                      AWS EC2                           │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │               Nginx Reverse Proxy              │   │
│   │   • Serves static assets directly (/static/)   │   │
│   │   • Forwards dynamic requests to port 8000     │   │
│   └──────────────────────┬─────────────────────────┘   │
│                          │                             │
│                          ▼  [Internal Loopback]        │
│   ┌────────────────────────────────────────────────┐   │
│   │            Gunicorn WSGI Server                │   │
│   │   (Managed by Systemd Service)                 │   │
│   │   • Worker 1    • Worker 2    • Worker 3       │   │
│   └──────────────────────┬─────────────────────────┘   │
│                          │                             │
│                          ▼                             │
│   ┌────────────────────────────────────────────────┐   │
│   │               Flask Application                │   │
│   │   • Input Validation (model.py)                │   │
│   │   • Scikit-Learn Model (house_price_model)     │   │
│   │   • In-Memory Session History                  │   │
│   └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## Machine Learning Details

### The Algorithm: Linear Regression (Ordinary Least Squares)

The model predicts the house price $y$ as a linear combination of input features $x_i$:

$$y = \beta_0 + \beta_1(\text{area}) + \beta_2(\text{bedrooms}) + \beta_3(\text{bathrooms}) + \beta_4(\text{floors}) + \beta_5(\text{age}) + \epsilon$$

Where:
- $\beta_0$ is the **Intercept** (the baseline property price offset).
- $\beta_1, \beta_2, \dots, \beta_5$ are the **Regression Coefficients** (weights assigned to each feature).
- $\epsilon$ is the residual error.

### Trained Model Evaluation Metrics

Evaluated on an unseen 20% test partition (500 samples) from 2,500 observations:

| Metric | Measured Value | Meaning |
| :--- | :--- | :--- |
| **$R^2$ Score** | **0.9928** | The model explains 99.28% of variance in house prices. |
| **MAE** | **₹2,30,612** | Mean Absolute Error: average magnitude of prediction difference. |
| **RMSE** | **₹2,91,047** | Root Mean Squared Error: standard deviation of prediction residuals. |

### Learned Weights Breakdown

- **Built-up Area (`area_sqft`)**: `+₹4,814.20 / sq ft`
- **Bedrooms (`bedrooms`)**: `+₹2,59,433.35 / bedroom`
- **Bathrooms (`bathrooms`)**: `+₹1,65,262.69 / bathroom`
- **Floors (`floors`)**: `+₹3,37,967.14 / floor`
- **Age of Property (`age_years`)**: `-₹54,841.87 / year` (depreciation)
- **Base Intercept ($\beta_0$)**: `₹12,27,666.97`

---

## Project Directory Structure

```
house-price-prediction/
├── app.py                         # Flask application & route handlers
├── model.py                       # Predictor class, validation & INR formatting
├── train_model.py                 # Scikit-learn training & metrics generation script
├── requirements.txt               # Pinned Python package dependencies
├── README.md                      # Comprehensive documentation & deployment manual
├── .gitignore                     # Git ignore rules
│
├── templates/
│   └── index.html                 # Jinja2 dashboard template
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom responsive stylesheet
│   └── js/
│       └── dashboard.js           # AJAX handlers, validation & Chart.js logic
│
├── data/
│   ├── README.md                  # Dataset specification & methodology
│   ├── generate_dataset.py        # Benchmark demonstration dataset generator
│   └── housing_data.csv           # 2,500 record demonstration dataset
│
├── models/
│   ├── .gitkeep                   # Preserves directory in git
│   ├── house_price_model.joblib   # Serialized Scikit-Learn model artifact
│   └── metrics.json               # Recorded evaluation metrics & coefficients
│
├── tests/
│   └── test_app.py                # 14 automated unit and integration tests
│
└── deployment/
    ├── gunicorn.conf.py           # Production Gunicorn WSGI configuration
    ├── nginx.conf                 # Nginx reverse proxy configuration
    ├── house-price-prediction.service # Systemd unit service definition
    └── deploy-aws.sh              # One-command AWS EC2 deployment script
```

---

## Local Setup & Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed
- Git installed

### Step 1: Clone or navigate to the project directory
```bash
cd "d:/house prediction"
```

### Step 2: Create and activate a virtual environment
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install required packages
```bash
pip install -r requirements.txt
```

### Step 4: (Optional) Re-generate data and train model
```bash
python data/generate_dataset.py
python train_model.py
```
*(A pre-trained model and dataset are already included in the repository).*

### Step 5: Start the local Flask development server
```bash
python app.py
```
Open your browser and navigate to: `http://localhost:5000`

### Step 6: Test production Gunicorn locally (Linux / macOS / WSL)
```bash
gunicorn --bind 127.0.0.1:8000 app:app
```

---

## Running Unit Tests

Run the complete automated test suite using `pytest`:

```bash
python -m pytest -v
```

All 14 tests verify:
- Model loading and coefficients availability
- Mathematical INR formatting (`₹45,00,000` and `₹45.00 Lakh`)
- Physical boundary validation (negative values, zero area, excessive limits)
- Endpoints `GET /`, `GET /health`, `POST /predict`, and `GET /history`

---

## AWS EC2 Deployment Guide (Step-by-Step)

Deploying a machine learning model on AWS requires a production web architecture: Gunicorn serves the Python WSGI application, while Nginx handles public web requests and passes them to Gunicorn.

---

### Step 1: Launch an AWS EC2 Instance

1. Log into your **AWS Management Console**.
2. Navigate to **EC2** &rarr; **Instances** &rarr; click **Launch Instance**.
3. Configure instance settings:
   - **Name**: `House-Price-Prediction-Server`
   - **AMI (Operating System)**: Choose either:
     - **Amazon Linux 2023 AMI** *(Recommended)* or
     - **Ubuntu Server 22.04 / 24.04 LTS**
   - **Instance Type**: `t2.micro` or `t3.micro` *(AWS Free Tier Eligible)*.
   - **Key Pair**: Select an existing key pair or click **Create new key pair** (e.g. `house-key.pem`). Download the `.pem` file to your computer.

---

### Step 2: Configure EC2 Security Group (Firewall)

Under **Network Settings**, configure the following **Inbound Rules**:

| Type | Protocol | Port Range | Source | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | TCP | `22` | `My IP` (or `0.0.0.0/0`) | Secure terminal access |
| **HTTP** | TCP | `80` | `0.0.0.0/0` (Anywhere) | Public web traffic for Nginx |
| **HTTPS** | TCP | `443` | `0.0.0.0/0` (Anywhere) | Encrypted SSL/TLS traffic |

> **Important**: Do **NOT** open port `5000` or port `8000` to the public internet. Gunicorn will listen only on the internal loopback (`127.0.0.1:8000`), shielded by Nginx.

Click **Launch Instance**.

---

### Step 3: Connect to your EC2 Instance via SSH

Open your terminal or PowerShell:

- **For Amazon Linux 2023**:
  ```bash
  chmod 400 house-key.pem  # On Linux/macOS
  ssh -i "house-key.pem" ec2-user@<YOUR-EC2-PUBLIC-IP>
  ```
- **For Ubuntu**:
  ```bash
  chmod 400 house-key.pem
  ssh -i "house-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
  ```

---

### Step 4: Transfer Code to EC2

You can clone from your Git repository:

```bash
git clone https://github.com/<your-username>/house-price-prediction.git
cd house-price-prediction
```

*Or upload directly via `scp` from your local machine:*
```bash
scp -i "house-key.pem" -r "d:/house prediction" ec2-user@<YOUR-EC2-PUBLIC-IP>:~/house-price-prediction
```

---

### Step 5: Automated Deployment (Fastest Method)

Run the included automated deployment script:

```bash
chmod +x deployment/deploy-aws.sh
sudo ./deployment/deploy-aws.sh
```

The script automatically:
1. Detects whether you are running Amazon Linux 2023 or Ubuntu.
2. Updates system packages and installs Python 3, pip, git, and Nginx.
3. Sets up `/var/www/house-price-prediction` with appropriate non-root ownership.
4. Creates a Python virtual environment and installs dependencies.
5. Trains the model and verifies all 14 tests pass.
6. Installs and enables the Systemd service (`house-price-prediction.service`).
7. Configures and starts Nginx reverse proxy on port 80.
8. Validates the `/health` endpoint.

---

### Step 6: Manual Step-by-Step Deployment (For Detailed Understanding)

If you wish to configure each component manually:

#### A. Install System Packages
- **On Amazon Linux 2023**:
  ```bash
  sudo dnf update -y
  sudo dnf install -y python3 python3-pip git nginx
  ```
- **On Ubuntu**:
  ```bash
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-pip python3-venv git nginx
  ```

#### B. Setup Application Directory & Virtual Environment
```bash
sudo mkdir -p /var/www/house-price-prediction
sudo cp -r ./* /var/www/house-price-prediction/
cd /var/www/house-price-prediction

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
```

#### C. Setup Systemd Service
```bash
sudo cp deployment/house-price-prediction.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable house-price-prediction
sudo systemctl start house-price-prediction
sudo systemctl status house-price-prediction
```

#### D. Configure Nginx Reverse Proxy
- **On Amazon Linux 2023**:
  ```bash
  sudo cp deployment/nginx.conf /etc/nginx/conf.d/house-price-prediction.conf
  sudo nginx -t
  sudo systemctl restart nginx
  sudo systemctl enable nginx
  ```
- **On Ubuntu**:
  ```bash
  sudo cp deployment/nginx.conf /etc/nginx/sites-available/house-price-prediction
  sudo ln -s /etc/nginx/sites-available/house-price-prediction /etc/nginx/sites-enabled/
  sudo rm -f /etc/nginx/sites-enabled/default
  sudo nginx -t
  sudo systemctl restart nginx
  sudo systemctl enable nginx
  ```

---

### Step 7: Verify Live Deployment

1. Open a browser and visit: `http://<YOUR-EC2-PUBLIC-IP>`
2. Test health check: `http://<YOUR-EC2-PUBLIC-IP>/health`
   - Expected JSON response:
     ```json
     {
       "status": "healthy",
       "model_loaded": true,
       "service": "House Price Prediction Service",
       "algorithm": "Linear Regression"
     }
     ```

---

### Step 8: (Optional) Adding a Custom Domain & Free SSL (HTTPS)

1. Point your domain (e.g. `houseprice.yourdomain.com`) to your EC2 Public IP via an **A Record** in your DNS provider (e.g. Route 53, GoDaddy, Cloudflare).
2. Edit `/etc/nginx/conf.d/house-price-prediction.conf` (or `/etc/nginx/sites-available/house-price-prediction`):
   ```nginx
   server_name houseprice.yourdomain.com;
   ```
3. Install **Certbot** for Let's Encrypt:
   ```bash
   # Amazon Linux 2023
   sudo dnf install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d houseprice.yourdomain.com

   # Ubuntu
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d houseprice.yourdomain.com
   ```
4. Certbot will automatically issue the SSL certificate and configure HTTPS redirection on port 443!

---

## College Viva & Presentation Guide

### Quick Answers to Common Examiner Questions

#### Q1: Why did you choose Linear Regression for this project?
> **Answer**: Linear Regression is a fundamental supervised learning algorithm well-suited for predicting continuous numeric variables (house prices). It provides high interpretability, enabling us to examine the exact regression coefficients ($\beta$ weights) for each property feature and explain the business impact of each square foot or bedroom directly to stakeholders.

#### Q2: What is the significance of the $R^2$ score?
> **Answer**: The $R^2$ (coefficient of determination) measures the proportion of variance in the dependent variable (property price) that can be explained by the independent features. Our model achieved an $R^2 \approx 0.99$, indicating that the 5 structural features account for almost all variance in the benchmark dataset.

#### Q3: What is the difference between MAE and RMSE?
> **Answer**:
> - **MAE (Mean Absolute Error)** calculates the average magnitude of absolute errors: $\frac{1}{n}\sum |y_i - \hat{y}_i|$. It treats all errors proportionally.
> - **RMSE (Root Mean Squared Error)** squares errors before taking the root: $\sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$. Because errors are squared, RMSE penalizes large outliers much more severely than MAE.

#### Q4: Why can't we just use the Flask built-in development server in production?
> **Answer**: The default `app.run()` server is single-threaded, not optimized for security, and lacks process management. If an unhandled exception or crash occurs, the whole server goes down. In production, we use **Gunicorn** as a multi-worker WSGI server behind an **Nginx** reverse proxy to handle SSL termination, static file caching, process recovery, and shield against denial-of-service attacks.

#### Q5: How is user session prediction history stored?
> **Answer**: The session history is maintained strictly in Python process memory (`threading.Lock()` protected list). This keeps the application lightweight, zero-dependency, and fast for demonstration purposes without requiring a heavy relational database server like MySQL or PostgreSQL.

---

## License

This project is licensed under the MIT License — open for academic, educational, and commercial evaluation.
