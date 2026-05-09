# Phytomine

Welcome to the **Phytomine** web application project. This is a Django-based platform designed with a multi-modular data processing pipeline.

## Overview

Phytomine is architected to handle complex data workflows, focusing on stages such as cultivation, extraction, and accumulation. The platform ensures data is properly validated, analyzed, and passed through various pipeline stages to maintain high data integrity and flow control.

## Project Modules

The application is structured around several core Django apps, each handling a distinct phase of the data pipeline:

- **Admins**: Handles overall system administration, user management, and global configurations.
- **Cultivator**: Responsible for the initial data processing and cultivation stage.
- **Accumulator**: Analyzes data and acts as an intermediary step, ensuring only successfully analyzed data progresses.
- **Extractor**: Extracts actionable insights and processed data from the accumulator stage.
- **Sustainer**: Manages ongoing data maintenance, storage, or sustained operations.

## Technology Stack

- **Backend**: Python, Django
- **Database**: SQLite (default for development/production on current setup)
- **Frontend**: HTML, CSS, JavaScript (Vanilla/Django Templates)
- **Deployment**: Docker, AWS (CI/CD via GitHub Actions)

## Setup & Installation

Follow these steps to run the project locally:

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Phytomine
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory based on `.env.example` (if available) and configure your database and secret keys.

5. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   The application will be accessible at `http://127.0.0.1:8000/`.

## Running with Docker

Alternatively, you can run the project using Docker:

```bash
docker-compose up --build
```

## License

This project is proprietary and confidential. Unauthorized copying of this file, via any medium, is strictly prohibited.
