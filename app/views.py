import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory #added required import
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm #added uploadform
from werkzeug.security import check_password_hash #required import


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required #accessed by logged-in users 
def upload():
    # Instantiate your form class
    form = UploadForm()

    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.file.data #gets data
        filename = secure_filename(file.filename) #sanitizes filename
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #defines save location
        file.save(upload_path) #saves file

        flash('File Saved', 'success')
        return redirect(url_for('upload')) # Updated to redirect user to a route that displays all uploaded image files

    return render_template('upload.html', form=form) #render upload template

#New upload route and view function
@app.route('/uploads/<filename>')
def get_image(filename):
    """Return a specific image from the uploads folder."""
    folder_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']) #debug
    print("Serving from:", folder_path)#debug
    return send_from_directory(folder_path, filename)

#New files route
@app.route('/files')
@login_required #accessed by logged-in users
def files():
    """Display uploaded images in an HTML list."""
    images = get_uploaded_images()  #get list of uploaded image filenames
    print("Images found:", images) #debug
    return render_template('files.html', images=images)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Get the username and password values from the form.

        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        #query db for user
        user = UserProfile.query.filter_by(username=username).first()

        #checking if user exists and if password is correct
        if user and check_password_hash(user.password, password):
            # Gets user id, load into session
            login_user(user)
            flash("Login successful!", "success") #flash message
            return redirect(url_for("upload")) #redirect to upload 
        flash("Invalid username or password", "danger") #failed login message

    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

#new logout route
@app.route('/logout')
@login_required
def logout():
    """Log out the user and redirect to home."""
    logout_user()  #log out user
    flash("You have been logged out successfully.", "info")  #flash message
    return redirect(url_for('home'))  #redirect to home page

#helper function to iterate over upload folder content
def get_uploaded_images():
    """Iterate over the uploads folder and return a list of filenames."""
    upload_folder = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])  #defines upload directory
    image_files = [] #list for image filenames

    
    #checks if directory exists
    if os.path.exists(upload_folder):
        for file in os.listdir(upload_folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  #filters image files
                image_files.append(file)

    return image_files  #return list of uploaded images
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
