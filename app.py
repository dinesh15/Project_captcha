from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from uuid import uuid4
from flask_migrate import Migrate
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/mycaptchadatabase'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)
app.config['DEBUG'] = True
app.config['RECAPTCHA_SITE_KEY'] = "6LdHzQ8pAAAAAJ-xu-QslvYliAQVQYBj9csMmyzn"
app.config['RECAPTCHA_SECRET_KEY'] = " 6LdHzQ8pAAAAAM8tJ-jyVr429s905NR9yn6aMc9g"

recaptcha = ReCaptcha(app)

# Set up Flask-Migrate
migrate = Migrate(app, db)

# Models
class UserTest(db.Model):
    __tablename__ = 'user_test'
    id = db.Column(db.Integer, primary_key=True)
    unique_key = db.Column(db.String(120), nullable=False)  
    user_id = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    captcha_type = db.Column(db.String(50), nullable=False)


class CaptchaResult(db.Model):
    __tablename__ = 'captcha_result'
    id = db.Column(db.Integer, primary_key=True)
    user_test_id = db.Column(db.Integer, db.ForeignKey('user_test.id'), nullable=False)
    time_taken = db.Column(db.Float, nullable=False)  # Store time in seconds
    captcha_type = db.Column(db.String(120), nullable=False)

# Flask CLI command for initializing the database
@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    print('Initialized the database.')

@app.route('/')
def index():
    app.logger.debug("Session Data: %s", session)
    return redirect(url_for('enter_key'))

@app.route('/enter_key', methods=['GET', 'POST'])
def enter_key():
    print("Session Data:", session)
    if request.method == 'POST':
        unique_key = request.form.get('unique_key')
        # You can add validation for the unique key here
        session['unique_key'] = unique_key
        return redirect(url_for('start_captcha'))

    return render_template('enter_key.html')

@app.route('/start_captcha')
def start_captcha():
    if 'unique_key' not in session:
    # Redirect to enter_key if unique key is not set
        return redirect(url_for('enter_key'))
    unique_key = session['unique_key']
    user_id = str(uuid4())  # Generate a unique user_id for each test
    captcha_type = "text"  # Determine captcha type here

    # Create a new UserTest instance
    new_test = UserTest(
        unique_key=unique_key, 
        user_id=user_id, 
        captcha_type=captcha_type,
        start_time=datetime.utcnow()
    )
    db.session.add(new_test)
    db.session.commit()

    # Store the user_test_id in the session
    session['user_test_id'] = new_test.id
    # Store the current time as start_time in the session
    session['start_time'] = datetime.utcnow().isoformat()

    # Generate and store CAPTCHA text
    captcha_text = generate_captcha_text()
    session['captcha_text'] = captcha_text
    image_data = create_captcha_image(captcha_text)
    captcha_image = base64.b64encode(image_data).decode('ascii')

    # Render the CAPTCHA in the HTML template
    return render_template('show_captcha.html', captcha_image=captcha_image)

@app.route('/verify_captcha', methods=['POST'])
def verify_captcha():
    print(f"Start time from session: {session.get('start_time')}")
    print(f"End time from form: {request.form.get('end_time')}")
    # Check if the user_test_id is stored in the session
    if 'user_test_id' not in session:
        return jsonify({'error': 'User test ID is missing from the session.'}), 400

    user_test_id = session['user_test_id']
    
    # Retrieve the start_time from the session
    start_time_str = session.get('start_time')
    if not start_time_str:
        return jsonify({'error': 'Start time is missing from the session.'}), 400
    
    # Parse the start time from the session
    start_time = datetime.fromisoformat(start_time_str)
    
    # Retrieve the end_time from the submitted form data
    end_time_str = request.form.get('end_time')
    if not end_time_str:
        return jsonify({'error': 'End time is missing from the request.'}), 400

    # Parse the end time from the form data
    try:
        end_time = datetime.fromisoformat(end_time_str.rstrip('Z'))
    except ValueError:
        return jsonify({'error': 'Invalid end time format.'}), 400
    
    # Calculate the time taken as the difference between end time and start time
    time_taken = (end_time - start_time).total_seconds()

    captcha_response = request.form.get('captcha_response')
    captcha_type = request.form.get('captcha_type')
    print(f"Time taken: {time_taken} seconds")
    # Validate the received data
    if not captcha_response or not captcha_type:
        return jsonify({'error': 'Missing data in the request.'}), 400
    
    # Check the captcha response
    captcha_is_valid = check_captcha(captcha_response)

    if captcha_is_valid:
        captcha_result = CaptchaResult(
            user_test_id=user_test_id,
            time_taken=time_taken,
            captcha_type=captcha_type
        )
        # Set the end_time in the UserTest model if needed
        user_test = UserTest.query.get(user_test_id)
        user_test.end_time = end_time
        db.session.add(captcha_result)
        db.session.commit()

        db.session.add(captcha_result)
        try:
            db.session.commit()
            # Clear the start_time from the session
            session.pop('start_time', None)
            return jsonify({'message': 'Captcha verified successfully.'}), 200
        except Exception as e:
            db.session.rollback()
            # Log the exception for debugging
            app.logger.error(f"An error occurred: {e}")
            return jsonify({'error': 'Failed to save captcha result.'}), 500
    else:
        return jsonify({'error': 'Captcha verification failed.'}), 400


def check_captcha(captcha_response):
    correct_captcha = session.get('captcha_text')
    return captcha_response.lower() == correct_captcha.lower()

# Function to generate CAPTCHA text
def generate_captcha_text(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def create_captcha_image(captcha_text):
    # Size of the image
    width, height = 200, 100
    
    # Create a new image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use a truetype font
    font = ImageFont.truetype("arial.ttf", 42)
    
    # Calculate width and height of the text to be inserted
    text_width, text_height = draw.textsize(captcha_text, font=font)
    
    # Calculate x, y position of the text
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Add text to image
    draw.text((x, y), captcha_text, font=font, fill='black')
    
    # Save the image to a stream
    image_io = io.BytesIO()
    image.save(image_io, 'PNG')
    image_io.seek(0)
    
    # Return the image data in a format that can be sent to the client
    return image_io.getvalue()

if __name__ == '__main__':
    app.debug = True
    app.run()

