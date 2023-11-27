# CAPTCHA User Study: Setup and Execution Guide

This document provides a comprehensive guide on setting up and running the CAPTCHA User Study project developed using Flask, a Python web framework.

## Prerequisites:
- Python installed on the system (Python 3.x recommended).
- Basic knowledge of Python and Flask.
- MySQL or any SQL-based database server installed and running.
- An IDE or text editor for editing Python and HTML files.

## Setup Steps:
1. **Install Required Libraries**: Open your terminal or command prompt and navigate to your project directory. Run the following command to install necessary Python packages:
   ```
   pip install Flask Flask-SQLAlchemy Pillow pymysql
   ```

2. **Database Setup**:
   - Launch MySQL or your SQL server.
   - Create a new database for the project (e.g., `mycaptchadatabase`).

3. **Configuration**: Open the `app.py` file in your project directory. Modify the following lines as per your database setup:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/mycaptchadatabase'
   ```
   Replace `root`, `admin`, and `mycaptchadatabase` with your database username, password, and database name, respectively.

4. **Initialize the Database**: Run your Flask app once to initialize the database using the Flask CLI command:
   ```
   flask run
   ```
   Then, in a new terminal window, while the Flask app is running, execute:
   ```
   flask initdb
   ```
   This will create the necessary tables in your database.

5. **Running the Application**:
   - After initializing the database, stop the Flask server (`Ctrl + C`) and run it again with:
     ```
     flask run
     ```
   - Open a web browser and navigate to `http://127.0.0.1:5000/`.

6. **Using the Application**:
   - The initial page will prompt for a unique key. Enter any key (or a predefined one if you have specific keys for users).
   - After submitting the key, you'll be directed to the CAPTCHA challenge.
   - Solve the CAPTCHA and submit your response.
   - The application records the time taken to solve the CAPTCHA and stores the result in the database.

## Files and Their Roles:
- `app.py`: The main Flask application file containing all routes and logic.
- `show_captcha.html`: HTML template to display the CAPTCHA challenge.
- `enter_key.html`: HTML template for entering the unique key.
- `templates/`: Folder containing all HTML templates.
- `static/`: (If applicable) Folder containing static files like CSS, JS, and images.

## Additional Notes:
- Ensure the Flask server is running whenever you want to use the application.
- The database must be accessible and running to store and retrieve data.
- Modify HTML templates to improve the user interface as per your requirements.

## Troubleshooting:
- If you encounter database connection issues, verify your database credentials and connection string in `app.py`.
- For errors related to missing packages, ensure all required packages are installed with `pip`.
- For template rendering issues, check the HTML files for syntax errors and ensure they are located in the correct directory (`templates/`).
