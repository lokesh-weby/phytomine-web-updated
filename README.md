# Phytomine

**Phytomine** is a Django-based web application built for a modular data processing pipeline. The platform supports staged workflows for cultivation, accumulation, extraction, and sustained data operations.

## What it does

Phytomine is designed to process and analyze data through multiple stages while enforcing validation, traceability, and pipeline control.

Key capabilities:
- Modular Django apps for distinct pipeline phases
- Role-based administration and workflow control
- Data validation, analysis, and extraction
- Local development and Docker deployment support

## Core Django apps

- **Admins**: system administration, user management, and global configuration
- **Cultivator**: initial data intake and cultivation processing
- **Accumulator**: analysis and validation before passing data onward
- **Extractor**: insight extraction and processed data generation
- **Sustainer**: ongoing maintenance, storage, and sustained operations

## Technology stack

- **Backend**: Python, Django
- **Database**: SQLite (default development configuration)
- **Frontend**: HTML, CSS, JavaScript with Django templates
- **Deployment**: Docker / docker-compose

## Prerequisites

- Python 3.10+ installed
- `pip` available
- `git` for cloning
- Docker and Docker Compose if using containerized deployment

## Local setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Phytomine
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate   # macOS / Linux
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the repository root if one is required.
   - Add any required settings such as `SECRET_KEY`, database configuration, and debug flags.

5. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. (Optional) Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

Open the app in your browser at `http://127.0.0.1:8000/`.

## Running tests

Use Django's test runner to verify the application:

```bash
python manage.py test
```

## Docker

Run the app using Docker Compose:

```bash
docker-compose up --build
```

This builds the image and starts the application using the configuration in `docker-compose.yml`.

## Notes

- This project currently uses SQLite for development by default.
- Keep confidential keys and sensitive configuration out of version control.

## License

This project is proprietary and confidential. Unauthorized copying of this file, via any medium, is strictly prohibited.
