from flask import Flask, request
import DatabaseLibrary as DB
from datetime import datetime
import utils_server


db = DB.Database("main_database.db")

app = Flask(__name__)

"""
FOR FULL DOCUMENTATION SEE DataBaseLibrary.py
"""


@app.route("/get_pending_messages")
def get__pending_messages():
    user_id = request.args.get("user_id")
    messages = db.get_pending_messages(given_user_id=user_id)
    return messages


@app.route("/get_all_messages")
def get_all_messages():
    user_id = request.args.get("user_id")
    messages = db.get_all_messages(given_user_id=user_id)
    return messages


@app.route("/get_sent_messages")
def get_sent_messages():
    user_id = request.args.get("user_id")
    messages = db.get_sent_messages(given_user_id=user_id)
    return messages


@app.route("/get_users")
def get_users():
    users_ids = request.args.get("users_ids")[1:-1].split(", ")
    users_dict = db.get_users(users_ids)
    return users_dict


@app.route("/get_user_name")
def get_user_name():
    requested_user_id = request.args.get("user_id")
    user_name = db.get_user_name(requested_user_id)
    return user_name


@app.route("/get_user_id")
def get_user_id():
    requested_user_name = request.args.get("user_name")
    if db.does_user_exist(requested_user_name):
        user_id = db.get_user_id(requested_user_name)
        return str(user_id)
    return "Invalid user"


@app.route("/send_message", methods=["POST"])
def send_message():
    date = request.form.get("date")
    author_id = request.form.get("author_id")
    addressee_id = request.form.get("addressee_id")
    message = request.form.get("data")
    db.add_message(date=date, author_id=author_id, addressee_id=addressee_id, data=message)
    return db.get_last_sent_message()


@app.route("/register", methods=["PUT"])
def register():
    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    password = request.form.get("password")
    date_joined = datetime.now()
    if db.does_user_exist(name):
        return "User name is already taken"
    db.add_user(name=name, birthdate=birthdate, date_joined=date_joined, password=password)
    return "User added"


@app.route("/login", methods=["PUT"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    user_id = db.is_valid_user(name, password)
    if user_id is not None:
        return f"Valid user id={user_id}"
    else:
        return "Wrong name or password"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
