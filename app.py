from flask import Flask, request, jsonify
import json
from flask_mysqldb import MySQL
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
import pyrebase
import requests
from datetime import timedelta, date

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



app = Flask(__name__)

# mysql-config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "gyaanvanam"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mysql = MySQL(app)
CORS(app)

#firebase config
config = {
  "apiKey": "AIzaSyAPexuYLPwvm5tRSgaNptYSsz3UNVx6WYE",
  "authDomain": "gyaanvanam.firebaseapp.com",
  "projectId": "gyaanvanam",
  "storageBucket": "gyaanvanam.appspot.com",
  "messagingSenderId": "270279882104",
  "appId": "1:270279882104:web:1768d4dc82521dd2ecc48d",
  "serviceAccount": "./keyfile.json"

}

#init firebase app
firebase = pyrebase.initialize_app(config)
#firebase storage
storage = firebase.storage()


# Add a book to the DB
@app.route("/api/addbookpage", methods=["POST"])
def addbook():
 if request.method == "POST":

        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        description = request.form.get("desc")
        cover = request.files["cover"]

        if cover and allowed_files(cover.filename):
            filename = str(uuid.uuid4())
            filename += "."
            filename += cover.filename.split(".")[1]
            #create secure name
            filename_secure = secure_filename(filename)

            cover.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_secure))

            local_filename = "./uploads/"
            local_filename += filename_secure
            firebase_filename = "uploads/"
            firebase_filename += filename_secure

            storage.child(firebase_filename).put(local_filename)

            cover_image = storage.child(firebase_filename).get_url(None)

            cur = mysql.connection.cursor()

            query = "INSERT INTO books (title, author, genre, cover, description) VALUES ('"+ str(title)+"','"+str(author)+"','"+str(genre)+"','"+str(cover_image)+"','"+str(description)+"');"
            cur.execute(query)
            mysql.connection.commit()

            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename_secure))

            return jsonify(data="the post was created successfully")