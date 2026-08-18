# URL Tracer

URL Tracer is a web-based cybersecurity analysis platform for detecting and analyzing suspicious URL activity, cyber attacks, and source IP risk.

The project consists of a React frontend, FastAPI backend, database layer, attack detection modules, IP risk analysis, and machine learning components.

## Features

* URL and request analysis
* Cyber attack detection
* Attack classification
* Severity classification
* Source IP analysis
* IP risk scoring
* Dashboard analytics
* Attack filtering and pagination
* Machine learning based detection
* Data upload
* Data export
* Sample data generation
* REST API
* Interactive API documentation through FastAPI

## Technology Stack

### Frontend

* React 18
* Vite
* React Router
* Tailwind CSS
* Recharts
* Lucide React
* date-fns

### Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* Pandas
* NumPy
* Scikit-learn
* Python-Levenshtein
* aiofiles

## Project Structure

```text
demo-URL-tracer/
│
├── backend/
│   ├── api/
│   │   ├── attacks.py
│   │   ├── dashboard.py
│   │   ├── export.py
│   │   ├── ips.py
│   │   ├── ml.py
│   │   └── upload.py
│   │
│   ├── detection/
│   ├── risk/
│   ├── services/
│   ├── sample_data/
│   ├── utils/
│   │
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── README.md
```

## Architecture

```text
React Frontend
       |
       | HTTP REST API
       |
       v
FastAPI Backend
       |
       +-------------------+
       |                   |
       v                   v
Detection Modules      IP Risk Analysis
       |                   |
       +---------+---------+
                 |
                 v
          Machine Learning
                 |
                 v
             Database
```

## Backend

The backend provides the REST API and handles request processing, detection, database operations, risk analysis, and machine learning functionality.

### Start the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will run on:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

## Frontend

The frontend provides the dashboard and user interface for interacting with the backend.

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The development frontend will normally run on:

```text
http://localhost:5173
```

## Production Build

Create a production frontend build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## API

The backend exposes endpoints for dashboard statistics, attack records, IP analysis, file uploads, exports, and machine learning functionality.

### Dashboard

```http
GET /api/dashboard
```

Provides aggregated security information such as:

* Total requests
* Total attacks
* High-risk IPs
* Critical IPs
* Attack types
* Attack severity
* Top attacking IPs
* Recent detections

### Attacks

List attacks:

```http
GET /api/attacks
```

Supported filters include:

```text
attack_type
severity
result
source_ip
page
page_size
```

Example:

```http
GET /api/attacks?severity=CRITICAL&page=1&page_size=50
```

Retrieve an individual attack:

```http
GET /api/attacks/{attack_id}
```

## Detection

The detection system processes URL and request information and classifies suspicious activity.

Detection records can contain:

* Attack type
* Source IP
* Severity
* Detection result
* Timestamp
* Request information

Supported result classifications include:

```text
ATTEMPT
POTENTIAL_SUCCESS
```

Severity classifications include:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## IP Risk Analysis

The IP analysis component evaluates source IP activity and provides risk-related information.

The system can identify:

* Risk score
* Risk level
* Attack count
* High-risk IP addresses
* Critical IP addresses
* Top attacking IP addresses

## Machine Learning

The project contains a machine learning pipeline using Scikit-learn and NumPy.

The current implementation includes a Random Forest based detection component for classifying URL/request related activity.

The machine learning pipeline is intended as part of the project's detection architecture and can be extended with additional features, models, and training data.

## Data

The current project includes sample and synthetic data for demonstration and development.

The data is used to populate:

* Attack records
* IP information
* Dashboard statistics
* Detection results
* Risk analysis

The project is not currently a live network traffic monitoring system.

## Data Upload and Export

The backend includes functionality for uploading and exporting security-related data.

These components are located under:

```text
backend/api/upload.py
backend/api/export.py
```

## Database

Database access is implemented using SQLAlchemy.

The main database-related files are:

```text
backend/database.py
backend/models.py
backend/schemas.py
```

The database layer is responsible for storing and retrieving application data used by the detection and dashboard components.

## Development Workflow

Start the backend:

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend communicates with the FastAPI backend through REST API requests.

## Deployment

The frontend can be deployed using Vercel or another platform that supports Vite applications.

The backend requires a Python-compatible hosting environment capable of running FastAPI with Uvicorn.

For deployment, the frontend API configuration must point to the deployed backend URL instead of the local development server.

## Current Limitations

* The project uses sample and synthetic data.
* It is not connected to live network traffic.
* IP intelligence is not based on a production threat-intelligence provider.
* The machine learning model is intended for demonstration and development.
* Authentication and authorization are not currently implemented as a complete production security layer.
* Production deployment requires appropriate database, secrets, logging, monitoring, and security configuration.

## Repository

```text
https://github.com/agrawalutkarsh2023-cpu/demo-URL-tracer
```

## License

No license is currently specified in the repository.
