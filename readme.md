# **OmniTool**

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-framework-lightgrey.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

OmniTool is a versatile web application built with **Python** and the **Flask** framework, leveraging **Bootstrap 5** for its user interface styling. The project's goal is to create a central hub where users can access various useful tools and services.

## **Table of Contents**

1.  [**Features**](#features)
2.  [**Technologies Used**](#technologies-used)
3.  [**Getting Started Locally**](#getting-started-locally)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [API Keys Configuration](#api-keys-configuration)
    * [Database Migrations](#database-migrations)
    * [Running the Application](#running-the-application)
4.  [**Upcoming Enhancements**](#upcoming-enhancements)
5.  [**License**](#license)

---

## **Features**

OmniTool currently offers the following modules and functionalities:

* **User Authentication System**: Full registration, login, and logout functionality. Most modules require user authentication.
* **Landing Page**: A welcoming home page for the application.
* **Weather Module**:
    * Displays current weather conditions and hourly/daily forecasts for a specified city.
    * Daily forecasts are presented in **collapsible sections** for detailed viewing.
    * **Publicly accessible, no login required.**
    * Utilizes the **OpenWeatherMap API**.
* **Currency Converter Module**:
    * Allows users to convert between different currencies.
    * **Conversion history is personalized** and stored in the **SQLite (SQLAlchemy)** database for each user.
    * Uses an external API to fetch exchange rates.
* **To-Do List Module**:
    * A simple task management application with options to add, mark as complete/incomplete, and delete tasks.
    * **To-do lists are personalized** and stored in the **SQLite (SQLAlchemy)** database for each user.
* **Theme Switcher (Light/Dark Mode)**:
    * Enables dynamic toggling between light and dark themes for the user interface.
    * User preferences are saved in the **server session and browser's localStorage**, effectively preventing "flash of unstyled content" (FOUC) issues.

---

## **Technologies Used**

* **Backend**: Python, Flask
* **Database**: SQLAlchemy (ORM), SQLite
* **Authentication**: Flask-Login, Werkzeug Security
* **Forms**: Flask-WTF, WTForms
* **Database Migrations**: Flask-Migrate (Alembic)
* **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
* **Environment Management**: `python-dotenv`
* **API Integrations**: `requests` (OpenWeatherMap, ExchangeRate-API)

---

## **Getting Started Locally**

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:

* **Python 3.x** (Python 3.9+ recommended)
* **pip** (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/DamiJJJ/OmniTool.git](https://github.com/DamiJJJ/OmniTool.git)
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

Create a `.env` file in the root directory of your project and add your API keys:

```dotenv
SECRET_KEY='your_very_secret_flask_key'
DATABASE_URL='sqlite:///site.db' # You can use a different path or database, e.g., postgresql://user:password@host:port/dbname
OPENWEATHER_API_KEY='your_openweathermap_api_key'
CURRENCY_API_KEY='your_exchangerateapi_api_key'
```

* Replace `'your_very_secret_flask_key'` with a unique, strong key.
* You can obtain `OPENWEATHER_API_KEY` from [OpenWeatherMap](https://openweathermap.org/api).
* You can obtain `CURRENCY_API_KEY` from [ExchangeRate-API](https://www.exchangerate-api.com/).

### Database Migrations

For the first time running the project, or after making changes to your data models, run database migrations:

```bash
flask db init
flask db migrate -m "Initial migration with User, CurrencyLog, Todo models"
flask db upgrade
```
* `flask db init` - Initializes the Alembic environment (one-time setup).
* `flask db migrate -m "..."` - Creates a migration script based on changes in `models.py`.
* `flask db upgrade` - Applies the migrations to the database.

### Running the Application

Start the Flask application:

```bash
flask run
```
The application will be accessible at `http://127.0.0.1:5000/`.

---

## **Upcoming Enhancements**

Plans are to continue developing OmniTool, including:

* **YouTube Module:** Integration with the YouTube API for searching, displaying and playing videos.
* **Containerization (Docker):** Packaging the application for easier deployment and scalability.
* **Chat Module:** Implementing real-time chat functionality between users.
* **Testing:** Writing comprehensive unit and integration tests for all modules.
* **Deployment:** Deploying the application to a free hosting platform.

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.