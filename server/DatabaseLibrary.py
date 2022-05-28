import sqlite3
from utils_server import *


class Database:

    def __init__(self, file_name):
        """
        Initiates connection with database, initiates db if does not exist

        :param file_name: Address of database
        :type file_name: (str)
        """

        self.conn = sqlite3.connect(file_name, check_same_thread=False)
        self.init_messages_table()
        self.init_users_table()
        self.init_user()
        self.init_message()

    def init_users_table(self):
        """
        Initiates table of users in database
        """

        self.conn.execute('''CREATE TABLE IF NOT EXISTS user_list
        (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT NOT NULL,
        date_joined TEXT NOT NULL,
        birthdate TEXT NOT NULL,
        password TEXT NOT NULL)
        ''')

    def init_messages_table(self):
        """
        Initiates table of messages in database
        """

        self.conn.execute('''CREATE TABLE IF NOT EXISTS message_list
        (message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        date TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        addressee_id INTEGER NOT NULL,      
        is_pending INTEGER NOT NULL,
        data TEXT NOT NULL)
        ''')

    def init_user(self):
        """
        Initiates demo user to start counting users from 1 and not from 0
        """

        cursor = self.conn.cursor()
        sql1_to_execute = "SELECT * FROM user_list WHERE user_id = 0"
        cursor.execute(sql1_to_execute)
        if not len(cursor.fetchall()) > 0:
            sql2_to_execute = "INSERT INTO user_list(user_id, name, date_joined, birthdate, password) VALUES(?,?,?,?,?)"
            record = (0, "Dohnny", "2022-03-31 19:57:51", "2004-09-15 00:00:00", hash_password("123"))
            cursor.execute(sql2_to_execute, record)
            self.conn.commit()

    def init_message(self):
        """
        Initiates demo messages to start counting messages from 1 and not from 0
        """

        cursor = self.conn.cursor()
        sql1_to_execute = "SELECT * FROM message_list WHERE message_id = 0"
        cursor.execute(sql1_to_execute)
        if not len(cursor.fetchall()) > 0:
            sql2_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_pending, data) VALUES(?,?,?,?,?,?)"
            record = (0, "2004-09-15 00:00:00", 0, 0, 0, "hello")
            cursor.execute(sql2_to_execute, record)
            self.conn.commit()

    def add_user(self, name, date_joined, birthdate, password):
        """
        Adds new user to database

        :param name: Name of user
        :type name: (str)
        :param date_joined: Date of registering
        :type date_joined: (str)
        :param birthdate: Date of birth
        :type birthdate: (str)
        :param password: Password of user
        :type password (str)
        """

        if isinstance(password, int):
            password = str(password)
        user_id = self.create_new_id("user_list") + 1
        user_name = name

        cursor = self.conn.cursor()
        sql_to_execute = "INSERT INTO user_list(user_id, name, date_joined, birthdate, password) VALUES(?,?,?,?,?)"
        record = (user_id, user_name, date_joined, birthdate, hash_password(password))
        cursor.execute(sql_to_execute, record)
        self.conn.commit()

    def create_new_id(self, list_type):
        """
        Gets last id of table

        :param list_type: Requested table (users or messages)
        :type list_type: (str)
        :return: Returns new id to set user or message with
        :rtype: (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = "SELECT * FROM sqlite_sequence where name = ?"
        cursor.execute(sql_to_execute, (list_type, ))
        current_id = cursor.fetchall()[0][1]
        return current_id

    def add_message(self, date, author_id, addressee_id, data):
        """
        Adds new message to database

        :param date: Date of said message
        :type date: (str)
        :param author_id: Id of the author of the message
        :type author_id: (int)
        :param addressee_id: Id of the addressee_id of the message
        :type addressee_id: (int)
        :param data: The message itself
        :type data: (str)
        """

        message_id = self.create_new_id("message_list") + 1
        cursor = self.conn.cursor()
        sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_pending, data) VALUES(?,?,?,?,?,?)"
        record = (message_id, date, author_id, addressee_id, 1, data)
        cursor.execute(sql_to_execute, record)
        self.conn.commit()

    def remove_user(self, given_user_id):
        """
        Used in development. Deletes a user from the users table.
        :param given_user_id: User id to remove
        :type given_user_id: (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = "DELETE FROM user_list WHERE user_id = ?"
        record = (given_user_id,)
        cursor.execute(sql_to_execute, record)
        self.conn.commit()

    def clear_user_list(self):
        """
        Used in development. Clears out the entire user list.
        """

        cursor = self.conn.cursor()
        sql_to_execute = "DELETE FROM user_list"
        cursor.execute(sql_to_execute)
        self.conn.commit()
        self.update_sqlite_sequence("user_list")
        self.init_user()

    def clear_message_list(self):
        """
        Used in development. Clears out the entire message list.
        """

        cursor = self.conn.cursor()
        sql_to_execute = "DELETE FROM message_list"
        cursor.execute(sql_to_execute)
        self.conn.commit()
        self.update_sqlite_sequence("message_list")
        self.init_message()

    def update_sqlite_sequence(self, list_type):
        """
        Updates the sqlite_sequence table to given list type (users or messages)

        :param list_type: Requested list type to update
        :type list_type: (str)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{list_type}'"
        cursor.execute(sql_to_execute)
        self.conn.commit()

    def get_pending_messages(self, given_user_id):
        """
        Returns pending messages of given user

        :param given_user_id: Id of requested user
        :type given_user_id: (int)
        :return: All pending messages of user in a dictionary, in format {message_id: [date, author_id, data]}
        :rtype: (dict)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE addressee_id = {given_user_id} AND is_pending = 1"
        cursor.execute(sql_to_execute)
        message_list = cursor.fetchall()
        message_dict = {}
        for message in message_list:
            message_dict[message[0]] = [message[1], message[2], message[5]]
        self.set_messages_not_pending(given_user_id)
        return message_dict

    def set_messages_not_pending(self, given_user_id):
        """
        After sending pending messages to user, sets the messages to not being pending

        :param given_user_id: Id of requested user
        :type given_user_id: (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"UPDATE message_list SET is_pending = 0 WHERE addressee_id = {given_user_id}"
        cursor.execute(sql_to_execute)
        self.conn.commit()

    def get_all_messages(self, given_user_id):
        """
        Returns all the messages of a given user. This method takes place after a user logins from a new device.

        :param given_user_id: Id of requested user
        :type given_user_id: (int)
        :return: All messages of user in a dictionary, in format {message_id: [date, author_id, data]}
        :rtype: (dict)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE addressee_id = {given_user_id}"
        cursor.execute(sql_to_execute)
        message_list = cursor.fetchall()
        message_dict = {}
        for message in message_list:
            message_dict[message[0]] = [message[1], message[2], message[5]]
        self.set_messages_not_pending(given_user_id)
        return message_dict

    def get_sent_messages(self, given_user_id):
        """
        Return all the messages a given user has sent. This method takes place after a user logins from a new device.

        :param given_user_id: Id of requested user
        :type given_user_id: (int)
        :return: All sent messages of user in a dictionary, in format {message_id: [date, addressee_id, data]}
        :rtype: (dict)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE author_id = {given_user_id}"
        cursor.execute(sql_to_execute)
        message_list = cursor.fetchall()
        message_dict = {}
        for message in message_list:
            message_dict[message[0]] = [message[1], message[3], message[5]]
        self.set_messages_not_pending(given_user_id)
        return message_dict

    def is_valid_user(self, given_user_name, given_user_password):
        """
        Used in the log-in process.

        :param given_user_name: Name of the requested user
        :type given_user_name: (str)
        :param given_user_password: Password of the requested user
        :type given_user_password: (str)
        :return: Returns "None" if user does not exists and their id if they do.
        :rtype: (None) or (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM user_list WHERE name = '{given_user_name}'"
        cursor.execute(sql_to_execute)
        user = cursor.fetchall()
        if not user:
            return None
        else:
            if check_password(user[0][-1], given_user_password):
                return user[0][0]
        return None

    def get_user_name(self, user_id):
        """
        Returns name of user by their id. Used after a user got a message from a new user for the first time.

        :param user_id: Id of requested user
        :type user_id: (int)
        :return: Name of requested user
        :rtype: (str)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM user_list WHERE user_id = {user_id}"
        cursor.execute(sql_to_execute)
        user_name = cursor.fetchall()[0][1]
        return user_name

    def get_users(self, user_ids):
        """
        Returns all the names of users by their ids. Used after a user logins from a new device.

        :param user_ids: List of all the ids of users the client has chatted with.
        :type: user_ids: (list)
        :return: Returns a dictionary of all their names, in format {user_id: user_name}
        :rtype: (dict)
        """

        cursor = self.conn.cursor()
        users_dict = {}
        for user_id in user_ids:
            user_id = int(user_id)
            sql_to_execute = f"SELECT * FROM user_list WHERE user_id = {user_id}"
            cursor.execute(sql_to_execute)
            user_name = cursor.fetchall()[0][1]
            users_dict[user_id] = user_name
        return users_dict

    def does_user_exist(self, name):
        """
        Used in the register process. Used to avoid duplicates in names of users.

        :param name: Name user had entered
        :type name: (str)
        :return: True if name was taken, False if not
        :rtype: (bool)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM user_list WHERE name = '{name}'"
        cursor.execute(sql_to_execute)
        user = cursor.fetchall()
        if user:
            return True
        return False

    def get_last_sent_message(self):
        """
        :return: Returns last sent message by a user in format {message_id: [date, addressee_id, data]}. Used after /send_message was called.
        :rtype: (dict)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list ORDER BY message_id DESC LIMIT 1"
        cursor.execute(sql_to_execute)
        message_dict = {}
        message = cursor.fetchall()[0]
        message_dict[message[0]] = [message[1], message[3], message[5]]
        return message_dict

    def get_user_id(self, user_name):
        """
        Returns id of user by their name. Used when client clicked on "add new chat" button.

        :param user_name: Name of requested user
        :type user_name: (str)
        :return: Id of requested user
        :rtype: (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM user_list WHERE name = '{user_name}'"
        cursor.execute(sql_to_execute)
        user_id = cursor.fetchall()[0][0]
        return user_id
