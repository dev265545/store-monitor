# Store Monitoring FastAPI Project

This project is a FastAPI-based web application that generates reports on store uptime and downtime. It processes store status data, business hours, and timezone information to calculate store activity metrics.

## Features

- Trigger report generation
- Check report status
- Download completed reports
- Background task processing for report generation

## Project Structure

The project consists of the following main components:

- `main.py`: FastAPI application entry point
- `models.py`: SQLAlchemy ORM models
- `database.py`: Database connection setup
- `utils.py`: Utility functions for report generation

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-username/store-monitor.git
   cd store-monitor
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Ensure you have set up your database connection string in `database.py`. The project uses SQLAlchemy, so you can configure it to work with various database backends.

## Usage

1. Start the FastAPI server:

   ```
   uvicorn main:app --reload
   ```

2. Access the API at `http://localhost:8000`

## API Endpoints

### POST /trigger_report

Triggers the generation of a new report.

**Response:**

```json
{
  "report_id": "uuid-of-the-report"
}
```

### GET /get_report/{report_id}

Checks the status of a report.

**Response:**

- If the report is still running:
  ```json
  {
    "status": "Running"
  }
  ```
- If the report is complete:
  ```json
  {
    "status": "Complete",
    "report_url": "/download_report/{report_id}"
  }
  ```

### GET /download_report/{report_id}

Downloads the completed report as a CSV file.

## Data Models

- `Store`: Represents a store with its timezone information
- `StoreStatus`: Represents the status of a store at a given timestamp
- `BusinessHours`: Represents the business hours of a store
- `Report`: Represents a generated report

## Report Generation Process

The report generation process is handled by the `generate_report` function in `utils.py`. It performs the following steps:

1. Fetches all necessary data from the database
2. Converts data to pandas DataFrames for efficient processing
3. Merges and processes the data to calculate uptime and downtime
4. Filters data based on business hours
5. Calculates metrics for different time ranges (last hour, day, and week)
6. Saves the report as a CSV file

## Error Handling

The application includes basic error handling:

- 404 errors for reports not found
- Exception handling for timezone conversion issues
