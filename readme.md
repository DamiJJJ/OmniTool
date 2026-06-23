# **OmniTool**

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-framework-lightgrey.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-utility--first-38B2AC.svg)
![DaisyUI](https://img.shields.io/badge/DaisyUI-components-5A0EF8.svg)
![Docker](https://img.shields.io/badge/Docker-containerized-2496ED.svg)
![MariaDB](https://img.shields.io/badge/Database-MariaDB%2FMySQL-003545.svg)
![OpenWeather](https://img.shields.io/badge/API-OpenWeatherMap-orange.svg)
![YouTube](https://img.shields.io/badge/API-YouTube-red.svg)
![ExchangeRate](https://img.shields.io/badge/API-ExchangeRate-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

OmniTool is a versatile web application built with **Python** and the **Flask** framework, leveraging **Tailwind CSS** and **DaisyUI** for its user interface styling. The project's goal is to create a central hub where users can access various useful tools and services.

## **Table of Contents**

1.  [**Features**](#features)
2.  [**Technologies Used**](#technologies-used)
3.  [**Getting Started Locally**](#getting-started-locally)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [API Keys Configuration](#api-keys-configuration)
    - [Database Migrations](#database-migrations)
    - [Running the Application](#running-the-application)
4.  [**Deployment with Docker**](#deployment-with-docker)
    - [What's in the box](#whats-in-the-box)
    - [Environment variables](#environment-variables)
    - [Quick start with Docker Compose](#quick-start-with-docker-compose)
    - [Build and run manually](#build-and-run-manually)
    - [CI/CD and home-server](#cicd-and-home-server)
5.  [**License**](#license)

---

## **Features**

OmniTool currently offers the following modules and functionalities:

- **User Authentication System**: Full registration, login, and logout functionality. Most modules require user authentication.
- **Landing Page**: A welcoming home page for the application.
- **Weather Module**:
  - Displays current weather conditions and hourly/daily forecasts for a specified city.
  - Daily forecasts are presented in **collapsible sections** for detailed viewing.
  - **Logged users can save their favorite cities** and remove them.
  - **Publicly accessible, no login required.**
  - Utilizes the **OpenWeatherMap API**.
- **Currency Converter Module**:
  - Allows users to convert between different currencies.
  - **Conversion history is personalized** and stored in the database for each user.
  - **Users can save their favorite currency pairs** and also remove them if needed.
  - Uses an external API to fetch exchange rates.
- **File Converter Module**:
  - Allows users to convert **between most popular image formats(JPG, PNG, WEBP, GIF, BMP, TIFF).**
  - **SOON** Documents (PDF, DOCX) conversion.
  - Utilizes the Pillow library for image processing.
- **To-Do List Module**:
  - A simple task management application with options to add, mark as complete/incomplete, edit, and delete tasks.
  - **To-do lists are personalized** and stored in the database for each user.
  - Includes **deadlines and priorities**.
- **YouTube Module**:
  - Integration with the **YouTube Data API** to fetch and display the latest videos from a specific channel.
  - Implements **infinite** scroll for seamless loading of additional videos.
  - Features a **built-in video player** (iframe) that allows users to watch videos without leaving the page.
  - Displays **key video statistics**, including views, likes, and comments.
- **Theme Switcher (Light/Dark Mode)**:
  - Enables dynamic toggling between light and dark themes for the user interface.
  - User preferences are saved in the **server session and browser's localStorage**, effectively preventing "flash of unstyled content" (FOUC) issues.

---

## **Technologies Used**

**Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Gunicorn  
**Frontend:** HTML5, CSS3, JavaScript, Tailwind CSS, DaisyUI  
**Database:** MariaDB / MySQL (via PyMySQL); SQLite for local development  
**Containerization:** Docker, GitHub Actions → GHCR, Watchtower (auto-deploy)  
**APIs:** OpenWeatherMap API, YouTube Data API v3, ExchangeRate-API

---

## **Getting Started Locally**

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

> Prefer containers? Skip to [**Deployment with Docker**](#deployment-with-docker).

### Prerequisites

- **Python 3.8+** (the Docker image uses 3.12)
- **pip**

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/DamiJJJ/OmniTool.git
    cd OmniTool
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### API Keys Configuration

Create a `.env` file in the root directory of your project and add your keys. By default development uses SQLite, so `DATABASE_URL` is optional locally:

```dotenv
SECRET_KEY='your_very_secret_flask_key'

# Database (pick one):
# Development default — SQLite (no DATABASE_URL needed):
DATABASE_URL='sqlite:///site.db'
# MariaDB / MySQL (home-server / production):
# DATABASE_URL='mysql://omnitool:password@mariadb:3306/omnitool?charset=utf8mb4'
# PostgreSQL:
# DATABASE_URL='postgresql://user:password@host:5432/dbname'

OPENWEATHER_API_KEY='your_openweathermap_api_key'
CURRENCY_API_KEY='your_exchangerateapi_api_key'
YOUTUBE_API_KEY='your_youtube_api_key'

# For Local Development Only
FLASK_ENV='development' # or 'production'
FLASK_APP='app.py'
```

- Replace `'your_very_secret_flask_key'` with a unique, strong key.
- The `DATABASE_URL` scheme is auto-normalized: `mysql://` → PyMySQL driver, `postgres://`/`postgresql://` → psycopg. You don't need to spell out the driver yourself.
- You can obtain `OPENWEATHER_API_KEY` from [OpenWeatherMap](https://openweathermap.org/api).
- You can obtain `CURRENCY_API_KEY` from [ExchangeRate-API](https://www.exchangerate-api.com/).
- You can obtain `YOUTUBE_API_KEY` from [Google Cloud Console](https://console.cloud.google.com/).

### Database Migrations

Migrations live in `migrations/` and are committed to the repo. For a fresh database (or after changing the data models) apply them with:

```bash
flask db upgrade
```

- `flask db upgrade` — applies all pending migrations (creates the schema on an empty database).
- `flask db migrate -m "..."` — generate a new migration after you change `models.py`.
- In Docker this runs **automatically** on container start (see below) — no manual step needed.

### Running the Application

Start the Flask development server:

```bash
flask run
```

The application will be accessible at `http://127.0.0.1:5000/`.

For a production-like run locally, use Gunicorn (the same server the container uses):

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

---

## **Deployment with Docker**

OmniTool is fully containerized. The image runs database migrations on startup and then serves the app with Gunicorn.

### What's in the box

- **`Dockerfile`** — based on `python:3.12-slim`, installs `requirements.txt`, copies the app (including `migrations/`).
- **`docker/entrypoint.sh`** — on every start it runs `flask db upgrade` (retrying until the database is reachable, useful on first boot while MariaDB is still coming up), then launches Gunicorn on port **8000**.
- **`.dockerignore`** — keeps secrets (`.env`), the local SQLite DB (`instance/`) and dev cruft out of the image.
- **`.github/workflows/deploy.yml`** — builds the image and pushes it to GHCR on every push to `main`.
- **`deploy/`** — ready-to-use Portainer stacks (`mariadb-stack.yml`, `omnitool-stack.yml`) and a full home-server walkthrough (`WDROZENIE.md`).

The container exposes port **8000** (Gunicorn). Map it to any host port you like.

### Environment variables

| Variable | Required | Example / default | Notes |
|---|---|---|---|
| `FLASK_ENV` | yes | `production` | Selects the production config. |
| `SECRET_KEY` | yes | `python3 -c "import secrets; print(secrets.token_hex(32))"` | App refuses to start in production without it. |
| `DATABASE_URL` | yes | `mysql://omnitool:pass@mariadb:3306/omnitool?charset=utf8mb4` | `mysql://` → PyMySQL, `postgres://` → psycopg (auto). |
| `SESSION_COOKIE_SECURE` | no | `false` | Set `false` when served over plain HTTP (e.g. `http://omnitool.home`), otherwise the session cookie is dropped and login won't persist. Defaults to `true`. |
| `OPENWEATHER_API_KEY` | no | — | Weather module. |
| `CURRENCY_API_KEY` | no | — | Currency module. |
| `YOUTUBE_API_KEY` | no | — | YouTube module. |
| `YOUTUBE_CHANNEL_ID` | no | `UC1uYJszfaKTzbbz7jMiXBFg` | Channel for the YouTube module. |
| `GUNICORN_WORKERS` / `GUNICORN_TIMEOUT` | no | `3` / `120` | Optional tuning. |

### Quick start with Docker Compose

A minimal stack (app + MariaDB) for trying it locally. Save as `docker-compose.yml` and run `docker compose up --build`:

```yaml
services:
  mariadb:
    image: mariadb:11.4
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    environment:
      MARIADB_ROOT_PASSWORD: rootpass
      MARIADB_DATABASE: omnitool
      MARIADB_USER: omnitool
      MARIADB_PASSWORD: omnitoolpass
    volumes:
      - mariadb_data:/var/lib/mysql

  omnitool:
    build: .
    image: omnitool:local
    restart: unless-stopped
    ports:
      - "8082:8000"
    environment:
      FLASK_ENV: production
      SECRET_KEY: change-me-to-a-long-random-value
      DATABASE_URL: "mysql://omnitool:omnitoolpass@mariadb:3306/omnitool?charset=utf8mb4"
      SESSION_COOKIE_SECURE: "false"
      # OPENWEATHER_API_KEY: ...
      # CURRENCY_API_KEY: ...
      # YOUTUBE_API_KEY: ...
    depends_on:
      - mariadb

volumes:
  mariadb_data:
```

The app will be at `http://localhost:8082/`. Tables are created automatically on first start.

### Build and run manually

```bash
# Build
docker build -t omnitool .

# Run (point DATABASE_URL at a reachable MySQL/MariaDB)
docker run -d --name omnitool -p 8082:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -e DATABASE_URL="mysql://omnitool:password@db-host:3306/omnitool?charset=utf8mb4" \
  -e SESSION_COOKIE_SECURE=false \
  omnitool
```

### CI/CD and home-server

- **GitHub Actions** builds the image on push to `main` and publishes it to **GHCR** as `ghcr.io/damijjj/omnitool:latest`.
- On the home-server, **Watchtower** pulls the new image and redeploys the container automatically (the stack carries the `com.centurylinklabs.watchtower.enable=true` label).
- For the complete Portainer + Nginx Proxy Manager + MariaDB setup, follow **[`deploy/WDROZENIE.md`](deploy/WDROZENIE.md)**.

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
