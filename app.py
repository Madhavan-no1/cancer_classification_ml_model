from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from main import getPrediction
import os

# Save images to the 'static' folder as Flask serves images from this directory
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create an app object using the Flask class
app = Flask(__name__, static_folder="static")

# Set secret key for session encryption
app.secret_key = "secret key"

# Define the upload folder to save images uploaded by the user
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the home route
@app.route('/')
def index():
    return render_template('index.html')

# Add Post method to the decorator to allow for form submission
@app.route('/', methods=['POST'])
def submit_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Get prediction from model
            label = getPrediction(filename)
            full_filename = url_for('static', filename='images/' + filename)  # Correct URL path
            
            flash(label)  # Flash the diagnosis label
            flash(full_filename)  # Flash the image path
        except Exception as e:
            flash(f'Error processing the image: {str(e)}')
            return redirect(request.url)
        
        return redirect(url_for('index'))
    else:
        flash('Allowed file types are png, jpg, jpeg')
        return redirect(request.url)

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Define port so we can map container port to localhost
    app.run(host='0.0.0.0', port=port)  # Define 0.0.0.0 for Docker
