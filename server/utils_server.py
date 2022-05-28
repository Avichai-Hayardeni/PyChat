from datetime import datetime
from random import randint
import bcrypt


def get_fake_users(db, user_id):
    """
    Adds fake users and messages for the next user that registes.
    Clears database on the way

    :param db: Database
    :type db: Instance of class Database
    :param user_id: Fake users will be created up to this number
    :type user_id: (int)
    :return: Returns "Invalid database" if it's so
    :rtype: (str)
    """

    with open("utils files/words.txt", "r") as f:
        list_of_words = f.read().split("\n")
    with open("utils files/names.txt", "r") as f:
        list_of_names = f.read().split("\n")
    try:
        db.clear_user_list()
        db.clear_message_list()
        g = 0
        for i in range(user_id - 1):
            db.add_user(list_of_names[g], datetime.now(), datetime.now(), 123)
            g += 1
        db.clear_message_list()
        for i in range((user_id - 1) * 30):
            db.add_message(datetime.now(), randint(1, user_id - 1), user_id, list_of_words[randint(0, 149)])

        for i in range((user_id - 1) * 10):
            db.add_message(datetime.now(), user_id, randint(1, user_id - 1), list_of_words[randint(0, 149)])
    except AttributeError:
        return "invalid database"


def clear_database(db):
    """
    Clears a database

    :param db: Database
    :type db: Instance of class Database
    :return: Returns "Invalid database" if it's so
    :rtype: (str)
    """

    try:
        db.clear_user_list()
        db.clear_message_list()
    except AttributeError:
        return "invalid database"


def hash_password(password):
    """
    Hashes password using the library

    :param password: given password
    :type password: (str)
    :return: Hashed password
    :rtype: (bytes)
    """

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(hashed_password, password):
    """
    Checks if password matches the hashed password

    :param hashed_password: given hashed password
    :type hashed_password: (bytes)
    :param password: given password
    :type password: (str)
    :return: True if they match, False if not
    :rtype: (bool)
    """

    return bcrypt.checkpw(password.encode(), hashed_password)
