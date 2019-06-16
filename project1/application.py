import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.context import CryptContext

app = Flask(__name__)

# setup pwd_context
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256"
)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# set secret key
app.secret_key = b'1\x9fe\xb0\xa3\xdc\xdd3\x02.EuZw\x12\xc1'


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():

    # forget any existing user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("error.html", error="username can't be left empty")

        elif not password:
            return render_template("error.html", error="password can't be left empty")

        
        result = db.execute("SELECT * FROM users where username = :username",
                        {"username": username}).fetchone()

        if result == None:
            return render_template("error.html", error="Could not login")
        elif result.rowcount == 0:
            return render_template("error.html", error="User does not exist")

        if username == result.username and pwd_context.verify(password, result.password):
            return redirect(url_for("index"))
        return render_template("error.html", error="Could not login")

        # Log user in
        session["users"] = username
    
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("users") is None:
        session["users"] = []
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        results = db.execute("SELECT username, password FROM users WHERE username = :username",
                    {"username": username}).fetchall()
        for result in results:
            if result is not None and username == result.username:
                return render_template("error.html", error="This Username already exists")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": pwd_context.encrypt(password)})
        session["users"] = username
        db.commit()
        return redirect(url_for("index"))
    
    elif request.method == "GET":
        return render_template("registration.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()

    return redirect(url_for("index"))


