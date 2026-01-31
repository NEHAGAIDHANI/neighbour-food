from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from models import db, User, House, Meal, MealRequest, HouseImage

from config import Config
from flask import session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os,uuid

app = Flask(__name__)
CORS(app) # This allows the browser to connect to the API easily


# Folder to store uploaded images
# Upload folder and allowed extensions
UPLOAD_FOLDER = 'static/images'  # <-- your actual folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
CORS(app) # This allows the browser to connect to the API easily


# This tells us exactly where app.py is sitting






app = Flask(__name__)
app.config.from_object(Config)

# THIS IS THE CORRECT PLACE TO TEST
print(f"DATABASE URL LOADED: {app.config['SQLALCHEMY_DATABASE_URI']}")

db.init_app(app)

with app.app_context():
    db.create_all()

# ------------------- HELPERS -------------------
# ------------------- HELPERS -------------------

def login_required():
    return 'users_id' in session

def cook_required():
    return session.get('role') == 'cook'

from functools import wraps

def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not login_required():
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def require_cook(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not login_required() or not cook_required():
            return redirect(url_for('index_page'))
        return f(*args, **kwargs)
    return decorated

# ------------------- PAGE ROUTES -------------------

@app.route('/')
def home():
    return redirect(url_for('login_page'))



@app.route('/index')
def index_page():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    # Get username from session
    username = session.get('username', 'User')
    return render_template('index.html', username=username)



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cook-form', methods=['GET'])
def cook_form_page():
    print("Cook form route accessed")  # debug
    return render_template('cook_form.html', meal=None)





@app.route('/listings')
def listings_page():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    meals = Meal.query.all()
    return render_template('listings.html', meals=meals)

@app.route('/houses')
def house_listings():
    houses = House.query.all()
    return render_template('house_listings.html', houses=houses)

@app.route('/house/<int:house_id>')
def house_details(house_id):
    house = House.query.get_or_404(house_id)
    meals = Meal.query.filter_by(house_id=house.id).all()

    return render_template(
        'house_details.html',
        house=house,
        meals=meals
    )







@app.route('/details/<int:meal_id>')
@require_login
def details_page(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    return render_template('details.html', meal=meal)




# ------------------- AUTH APIs -------------------

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email').strip().lower()  # normalize email
        password = request.form.get('password')

        # Check if email exists
        if User.query.filter_by(email=email).first():
            return "Email already registered"

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save user in DB
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return "Invalid email or password"

        session.clear()
        session['users_id'] = user.id
        session['username'] = user.username
        session['role'] = getattr(user, "role", "user")  # optional

        # ✅ EVERYONE goes to index.html
        return redirect(url_for('index_page'))

    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/cook-form', methods=['GET', 'POST'])
def cook_form_submit():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        # Example for adding a meal
        house = House.query.filter_by(owner_id=session['users_id']).first()
        if not house:
            return "Please add a house first!"

        image_file = request.files.get('image')
        filename = None
        if image_file:
            from werkzeug.utils import secure_filename
            import os, uuid
            UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(UPLOAD_FOLDER, filename))

        meal = Meal(
            title=request.form['title'],
            description=request.form['description'],
            portions=int(request.form['portions']),
            food_type=request.form['food_type'],
            packaging=request.form.get('packaging'),
            allergies=request.form.get('allergies'),
            ingredients=request.form.get('ingredients'),
            available_till=request.form.get('available_till') or None,
            cook_id=session['users_id'],
            house_id=house.id,
            image=filename
        )

        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('index_page'))

    return render_template('cook_form.html')


# Show the edit form with pre-filled data
@app.route('/meal/edit/<int:meal_id>', methods=['GET'])
def edit_meal_form(meal_id):
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    meal = Meal.query.get_or_404(meal_id)

    if meal.cook_id != session['users_id']:
        return "Unauthorized", 403

    return render_template('cook_form.html', meal=meal)






@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))



# ------------------- HOUSE API -------------------
@app.route('/house/create', methods=['GET', 'POST'])
def create_house():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    # Get username from session to pre-fill owner_name
    username = session.get('username', '')

    if request.method == 'POST':
        house = House(
            owner_id=session['users_id'],
            owner_name=request.form['owner_name'],  # comes from form
            description=request.form['description'],
            address=request.form['address'],
            city=request.form['city'],
            breakfast_time=request.form['breakfast_time'],
            lunch_time=request.form['lunch_time'],
            dinner_time=request.form['dinner_time'],
            pickup_time=request.form['pickup_time']
        )

        db.session.add(house)
        db.session.commit()  # commit to get house.id

        # ---------------- IMAGE UPLOAD ----------------
        image_files = request.files.getlist('images')
        UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'house_images')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for image_file in image_files:
            if image_file and allowed_file(image_file.filename):
                unique_name = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
                image_path = os.path.join(UPLOAD_FOLDER, unique_name)
                image_file.save(image_path)

                house_image = HouseImage(
                    house_id=house.id,
                    image=unique_name
                )
                db.session.add(house_image)

        db.session.commit()
        return redirect(url_for('house_listings'))

    # Pass username to template
    return render_template('house_form.html', username=username)







# ------------------- MEALS API -------------------

@app.route('/meals', methods=['POST'])
def api_create_meal():
    if not login_required() or not cook_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.form
    image = request.files.get('image')

    filename = None
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    house = House.query.filter_by(user_id=session['users_id']).first()
    meal = Meal(
        dish_name=data['dish_name'],
        description=data['description'],
        portions_available=int(data['quantity']),
        image=filename,
        house_id=house.id if house else None
    )

    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Meal added"}), 201

@app.route('/api/meals')
def api_get_meals():
    meals = Meal.query.all()
    return jsonify([
        {
            "id": m.id,
            "dish_name": m.dish_name,
            "image": m.image,
            "cook": m.house.owner_name if m.house else "Unknown"
        } for m in meals
    ])

@app.route('/api/meals/<int:meal_id>')
def api_meal_details(meal_id):
    m = Meal.query.get_or_404(meal_id)
    return jsonify({
        "dish_name": m.dish_name,
        "description": m.description,
        "portions": m.portions_available,
        "image": m.image,
        "cook": m.house.owner_name if m.house else "Unknown",
        "city": m.house.city if m.house else ""
    })

# ------------------- REQUEST FOOD (CUSTOMER) -------------------

# API route to request a meal (decrease portions)
@app.route('/api/request/<int:meal_id>', methods=['POST'], endpoint='api_request_meal')
def api_request_food(meal_id):
    meal = Meal.query.get_or_404(meal_id)

    if meal.portions <= 0:
        return redirect(url_for('details_page', meal_id=meal.id))

    meal.portions -= 1
    db.session.commit()

    return redirect(url_for('details_page', meal_id=meal.id))


# Page route for a user to request a meal
@app.route('/meal/<int:meal_id>/request', methods=['POST'], endpoint='request_meal_page')
def request_meal(meal_id):
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    req = MealRequest(
        meal_id=meal_id,
        requester_id=session['users_id']
    )

    db.session.add(req)
    db.session.commit()

    return redirect(url_for('listings_page'))


# Accept a meal request (by cook)
@app.route('/request/<int:req_id>/accept', methods=['POST'], endpoint='accept_request')
def accept_request(req_id):
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    req = MealRequest.query.get_or_404(req_id)

    req.status = 'accepted'
    req.pickup_date = request.form['pickup_date']
    req.pickup_time = request.form['pickup_time']

    db.session.commit()

    return redirect(url_for('view_requests'))


# View all requests for the logged-in cook
@app.route('/requests', endpoint='view_requests')
def view_requests():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    requests = MealRequest.query.join(Meal)\
        .filter(Meal.cook_id == session['users_id'])\
        .all()

    return render_template('requests.html', requests=requests)

@app.route('/my-requests')
def my_requests():
    if 'users_id' not in session:
        return redirect(url_for('login_page'))

    # Get all requests made by the current user
    requests = MealRequest.query.join(Meal)\
        .filter(MealRequest.requester_id == session['users_id'])\
        .all()

    return render_template('my_requests.html', requests=requests)









if __name__ == "__main__":
    # This block makes sure we are inside the Flask "App Context"
    with app.app_context():
        db.create_all()  # INDENTED with 1 Tab
        print("Tables created successfully!") # INDENTED with 1 Tab

    # This starts the actual web server
    app.run(debug=True)
    
