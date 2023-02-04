from flask import Flask, render_template, session, redirect, url_for, g
from database import get_db, close_db
from forms import regForm, loginForm, profileSetupForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from functools import wraps


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "greenGoblinMondaysAreTheWorst"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#checks if user is signed in at the start of every request
@app.before_request
def load_logged_in_user():
    #creates a global user before loading page. allows me to show a different nav when logged in vs. logged out.
    g.user = session.get("user_id", None)


#checks if a user is logged in to see weather they can view certain pages or not.
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        #if user isnt logged in, redirect to login page when trying to access restricted pages.
        if g.user is None:
            return redirect( url_for("login"))
        return view(**kwargs)
    return wrapped_view


#redirects to index when / is visited.
@app.route("/")
def index():
    return render_template("index.html")


#registration page. account creation, age verification and the updating of userbase in the database.
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = regForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password1.data
        age = form.age.data
        db = get_db()
        #checking for already existing user names in database
        possible_clashing_user = db.execute("""SELECT * FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if possible_clashing_user is not None:
            form.user_id.errors.append("User ID Already Taken, Please Try Another.")
        else:
            #if its not taken, inserts info into users database.
            db.execute("""INSERT INTO users (user_id, password, age) VALUES (?, ?, ?);""", (user_id, generate_password_hash(password), age))
            db.commit()
            db.execute("""INSERT INTO userProfile (user_id, icon, first_name, gender, bio) VALUES (?, ?, ?, ?, ?);""", (user_id, "", "", "", ""))
            db.commit()
            return redirect( url_for("login") )
    return render_template ("registerForm.html", form=form)


#login page. using registration details, logs one into an account and updates session to show as logged in.
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        #checks database for the login username inputted
        existing_user = db.execute("""SELECT * FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if existing_user is None:
            #if not in database, outputs error message.
            form.user_id.errors.append("User ID Not Found.")
        elif not check_password_hash(existing_user["password"], password ):
            #if the password doesn't match, outputs error message
            form.password.errors.append("Incorrect Password.")
        else:
            #add user to the session so we can keep track whether they are logged in or not and redirect to homepage.
            session["user_id"] = user_id
            return redirect( url_for("index") )
    return render_template ("loginForm.html", form=form)


#route for logging out. clears user_id from session.
@app.route("/logout")
@login_required
def logout():
    session["user_id"] = None
    return redirect ( url_for("login") )


#route for seeing your own profile. Only accessible if logged in.
@app.route("/profileSetup", methods=['GET', 'POST'])
@login_required
def profileSetup():
    form = profileSetupForm()
    if form.validate_on_submit():
        user_id = session["user_id"]
        icon = form.icon.data
        first_name = form.first_name.data
        gender = form.gender.data
        bio = form.bio.data
        db = get_db()
        #updates userProfile db with new profile info from form so now others can see your account on matches page.
        db.execute("""UPDATE userProfile 
                        SET icon =?, first_name =?, gender=?, bio=?
                        WHERE user_id = ?;""", (icon, first_name, gender, bio, user_id))
        db.commit()
        return redirect( url_for("index") )
    return render_template ("profile.html", form=form)

#Page for viewing available subscription services, see details button links to next route.
@app.route("/subscriptions")
@login_required
def subscriptions():
    #gets all subscriptions form the database for display for user
    db = get_db()
    subscriptions = db.execute("""SELECT * FROM subscriptions;""").fetchall()
    return render_template("subscriptions.html", subscriptions = subscriptions)

#Page that shows details for a specific subscription pack once clicked on or by visiting the link using subscriptions id.
@app.route("/subscription/<int:pack_id>")
@login_required
def subscription(pack_id):
    db= get_db()
    subscription = db.execute("""SELECT * FROM subscriptions
                                    WHERE pack_id = ?;""", (pack_id,)).fetchone()
    return render_template("subscription.html", subscription=subscription)

#page that shows others accounts at a glance. Including info such as their icon, name, gender and bio.
@app.route("/matches")
@login_required
def matches():
    db = get_db()
    matches= db.execute("""SELECT icon, first_name, gender, bio 
                            FROM userProfile
                            WHERE user_id <> ?;""", (session["user_id"],)).fetchall()
    return render_template("matches.html", matches = matches)

#route for viewing your own profile, bio, picture, name, gender as well as past purchases
@app.route("/myProfile")
@login_required
def myProfile():
    db = get_db()
    myProfile= db.execute("""SELECT user_id, icon, first_name, gender, bio 
                            FROM userProfile
                            WHERE user_id = ?;""", (session["user_id"],)).fetchone()
    myPurchases = db.execute("""SELECT *
                            FROM purchases
                            WHERE user_id = ?;""", (session["user_id"],)).fetchall()
    return render_template("myProfile.html", myProfile=myProfile, myPurchases= myPurchases)

#cart route creates a cart for user session and shows added items to cart.
@app.route("/cart")
@login_required
def cartFunc():
    if "cart" not in session:
        session["cart"]= {}
    return render_template("cart.html", cart=session["cart"])

#This route adds a subscription pack to cart using subscription packs id.
@app.route("/add_to_cart/<int:pack_id>")
@login_required
def add_to_cart(pack_id):
    if "cart" not in session:
        session["cart"]= {}
    if pack_id not in session["cart"]:
        session["cart"][pack_id] = 0
    session["cart"][pack_id] = session["cart"][pack_id] +1
    return redirect( url_for("cartFunc"))

#This route is for the - button in the cart, and removes one of that item form your cart.
@app.route("/remove_from_cart/<int:pack_id>")
@login_required
def remove_from_cart(pack_id):
    #if the number of things in cart is greater than 0, we can minus one when the button is pushed, stops from going into minus numbers.
    if session["cart"][pack_id] > 0:
        session["cart"][pack_id] = session["cart"][pack_id] - 1
        return redirect( url_for("cartFunc"))
    return redirect( url_for("cartFunc"))

#route that provides a button to clear ones cart
@app.route("/clear_cart")
@login_required
def clearCart():
    #sets cart to empty, erasing any previously stored items
    session["cart"]= {}
    return redirect( url_for("cartFunc"))

#route to purchase the items in your cart, adds purchase to a database so you can view past purchases on your profile
@app.route("/purchase")
@login_required
def purchase():
    #for every item in cart, execute a db query to upload each purchase, for later use to be displayed on view profile page.
    for pack_id in session["cart"]:
        db = get_db()
        for item in session["cart"]:
            db.execute("""INSERT INTO purchases
                            VALUES
                                (?, ?);""", (session["user_id"], session["cart"][pack_id]))
    
    db.commit()
    session["cart"]= {}
    return redirect( url_for("purchaseConfirmation"))

#route for purchase confirmation page!
@app.route("/purchaseConfirmation")
@login_required
def purchaseConfirmation():
    #getting user id to use to display in a thank you message on the order confirmation page
    user_id = session["user_id"]
    return render_template("purchaseConfirmation.html", user_id = user_id)