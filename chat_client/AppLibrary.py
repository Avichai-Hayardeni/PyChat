from threading import Thread
import PySimpleGUI as sg
import sqlite3
from datetime import datetime
from pyautogui import size
import time
import gc
from PIL import ImageFont
from static_methods import *
import requests


sg.theme('DarkBlue13')


class SgAPP:
    """
    This class is pretty much the entire client. It has all the necessary methods to run (apart from some static functions).
    """

    def __init__(self):
        """
        Initiates all the class properties. Checks if the user is logged in.
        If not, start the login process. If user is logged in, opens main app screen.
        """

        self.__chats = {0}  # Initializes users set
        self.__chats.remove(0)
        self.__layout = [[]]  # Initializes app layout
        self.__list_of_chats_column = [[]]  # Initializes the left side of the main screen
        self.__chat_column = sg.Column([[]])  # Initializes the right side of the main screen
        self.__current_chat_layout = [[]]  # Initializes current chat layout
        self.__message_input = []  # Initializes user input
        self.__current_chat = None
        font = ImageFont.truetype("GARABD.TTF", 20)
        self.__average_size_of_char = font.getsize("a")
        self.__size_in_pixels = (size()[0], size()[1])
        self.__char_length = self.__size_in_pixels[0] / self.__average_size_of_char[0]
        self.__server_down = False
        self.__new_messages = False
        self.__thread_pending = None
        self.__close_thread = False

        self.__is_logged_in = is_database()  # Checks whether user is logged in by looking for the database of messages
        if self.__is_logged_in:  # If the user is logged in, does the following actions:

            self.__window = sg.Window("", [[]])
            self.conn = sqlite3.connect("messages.db", check_same_thread=False)
            with open("user_id.txt", "r") as file:
                self.__user_id = file.read()  # Gets the user id from the client files

            self.__chatters = self.get_chatters()  # Gets the chatters names and ids
            for key in self.__chatters.keys():
                self.__chats.add(key)  # Updates users set
            self.get_pending_messages()  # Gets pending messages
            self.open_chat_frames()  # Starts main screen

        else:  # Will force user to log in or register
            self.__layout = [
                [sg.VPush()],
                [sg.Text("You are not logged in!", font=("Garamond", 40, "bold"), key="-LOGIN-")],
                [sg.Button("Click to register", visible=True, size=(20, 3), font=("Garamond", 20, "bold"))],
                [sg.Button("Click to login", visible=True, size=(20, 3), font=("Garamond", 20, "bold"))],
                [sg.VPush()],
                [sg.VPush()]
            ]

            self.__window = sg.Window('Register and login', self.__layout, element_justification="center", icon="PyChat1.ico").Finalize()  # Opens register and login window
            self.__window.Maximize()

            self.register_and_login()
            self.__user_id = None
            self.__chatters = {}

    def is_logged_in(self):
        """
        :return: True if the user is logged in, False if not
        :rtype: (bool)
        """

        return self.__is_logged_in

    # def user_id(self):   # Only used in development
    # return self.__user_id

    def get_chatters(self):
        """
        :return: chatters dictionary from the database
        :rtype: dict
        """

        cursor = self.conn.cursor()
        sql_to_execute = "SELECT * FROM chatters_list"
        cursor.execute(sql_to_execute)
        users = cursor.fetchall()
        user_dict = {}
        for user in users:
            user_dict[user[0]] = user[1]
        return user_dict

    def register_and_login(self):
        """
        Opens register and login windows accordingly
        """

        while True:
            event, values = self.__window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes __window or clicks cancel
                break
            if event == 'Click to register':
                self.open_register_window()
            if event == 'Click to login':
                self.open_login_window()

        self.__window.close()

    def open_register_window(self):
        """
        Opens register window
`       Closes it automatically when user registers via the server
        """

        layout = [
            [sg.Text("Enter your name: "), sg.InputText(key="-NAME-")],
            [
                sg.Text("Enter your birthdate: "),
                sg.CalendarButton('Calendar', target="-BIRTHDATE-", key="-CALENDAR-", format='%d/%m/%Y'),
                sg.Text("", key="-BIRTHDATE-")
            ],
            [sg.Text("Enter password: "), sg.InputText(key="-PASSWORD-")],
            [sg.Submit(key="-SUBMIT-"), sg.Text(key="-ERRORS-")]
        ]
        window1 = sg.Window("Register", layout, icon="PyChat1.ico")
        while True:
            event, values = window1.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "-SUBMIT-":
                birthdate = window1["-BIRTHDATE-"].get()[6:] + "-" + window1["-BIRTHDATE-"].get()[3:5] + "-" + window1["-BIRTHDATE-"].get()[:2]

                if len(values["-NAME-"].replace(" ", "")) < 2:  # Checks if name is longer than 1 char
                    window1["-ERRORS-"].update("Name must be at least 2 characters long")

                elif len(values["-PASSWORD-"].replace(" ", "")) < 5:  # Checks if password is longer than 4 chars
                    window1["-ERRORS-"].update("Password must be at least 5 characters long")

                elif not check_birthday(birthdate):  # Checks birthdate using the static methods file
                    window1["-ERRORS-"].update("You must be at least 13 years old to use this app")

                else:
                    try:
                        data = {
                            "name": values["-NAME-"],
                            "birthdate": birthdate,
                            "password": values["-PASSWORD-"]
                        }
                        register_url = uac.register

                        register_request = requests.put(url=register_url, data=data)  # Makes the register request using the server
                        if register_request.content.decode() == "User name is already taken":
                            window1["-ERRORS-"].update(register_request.content.decode())
                        else:
                            self.__window["Click to register"].update(visible=False)
                            break
                    except requests.exceptions.ConnectionError:
                        window1.close()
                        self.server_down_before_logged_in("before")
        window1.close()

    def open_login_window(self):
        """
        Opens login window
        Closes it automatically once the user logged in via the server
        """

        layout = [
            [sg.Text("Enter your name: "), sg.InputText(key="-NAME-")],
            [sg.Text("Enter password: "), sg.InputText(key="-PASSWORD-")],
            [sg.Submit(key="-SUBMIT-"), sg.Text(key="-ERRORS-")]
        ]
        window1 = sg.Window("Login", layout, icon="PyChat1.ico")
        while True:
            event, values = window1.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "-SUBMIT-":  # Checks for errors. If there are none, attempts to log in using the server
                if len(values["-NAME-"]) < 2:  # Checks if name is longer than 1 char
                    window1["-ERRORS-"].update("Name must be at least 2 characters long")

                elif len(values["-PASSWORD-"]) < 5:  # Checks if password is longer than 4 chars
                    window1["-ERRORS-"].update("Password must be at least 5 characters long")
                else:
                    try:
                        data = {
                            "name": values["-NAME-"],
                            "password": values["-PASSWORD-"]
                        }
                        login_url = uac.login
                        login_request = requests.put(url=login_url, data=data)

                        response = login_request.content.decode()
                        if response[:5] != "Valid":  # Checks for a confirmation in the response
                            window1["-ERRORS-"].update("Wrong name or password")
                        else:
                            with open("user_id.txt", "w") as file:
                                id = response.split("=")[-1]
                                file.write(id)
                                self.__user_id = id
                                self.__is_logged_in = True
                            self.__window["Click to login"].update(visible=False)
                            self.__window["-LOGIN-"].update("Loggin in...")
                            break
                    except requests.exceptions.ConnectionError:
                        window1.close()
                        self.server_down_before_logged_in("before")
        window1.close()
        if self.__is_logged_in:
            self.initialize_database()

    def initialize_database(self):
        """
        Initializes database with the columns message_id, date, author_id, type, data and is_read
        Used in case of a new device log in
        Creates user_id and user_name columns
        """

        self.conn = sqlite3.connect("messages.db", check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS message_list
                (message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date TEXT NOT NULL,
                author_id INTEGER NOT NULL,      
                addressee_id INTEGER NOT NULL,
                is_sent INTEGER NOT NULL, 
                data TEXT NOT NULL,
                is_read INTEGER NOT NULL)
                ''')
        # If is_sent = 1, message has been sent by the client
        # If is_read = 1, message has been read
        self.conn.execute('''CREATE TABLE IF NOT EXISTS chatters_list
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_name TEXT NOT NULL)
                ''')
        self.get_all_messages()  # Calls the next method to receive messages from server

    def get_all_messages(self):
        """
        Gets all the user's messages from the server
        Calls upon login from a new device
        Adds them all to messages table
        Adds all users to user table
        """

        try:
            url = f"{uac.get_all_messages}{self.__user_id}"
            messages_request = requests.get(url=url)  # Makes the request using the /get_all_messages method
            request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable

            users_ids = []  # Initializes all the users' ids list

            for key in request_content.keys():  # Variable "key" is the message's id
                message_info = request_content[key]  # That's one message

                cursor = self.conn.cursor()
                sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_sent, data, is_read) VALUES(?,?,?,?,?,?,?)"
                record = (key, message_info[0], message_info[1], self.__user_id, 0, message_info[2], 0)
                cursor.execute(sql_to_execute, record)
                self.conn.commit()  # Adds message to the database

                if message_info[1] not in self.__chats:  # Adds new users to list and to self.__chats
                    users_ids.append(message_info[1])
                    self.__chats.add(message_info[1])

            if not users_ids == []:
                users_dict = get_all_users_from_server(users_ids)  # Prepares to add all the users to the database using the server

            else:
                users_dict = {}

            for key in users_dict.keys():
                cursor = self.conn.cursor()
                sql_to_execute = "INSERT INTO chatters_list(user_id, user_name) VALUES(?,?)"
                record = (int(key), users_dict[key])
                cursor.execute(sql_to_execute, record)
                self.conn.commit()  # Adds user to the database
            self.__chatters = self.get_chatters()  # Updates chatters dictionary

            self.get_sent_messages()

        except requests.exceptions.ConnectionError:
            self.server_down_before_logged_in("mid")

    def get_sent_messages(self):
        """
        Gets all the user's sent messages from the server
        Calls upon login from a new device
        Adds them all to messages table
        Adds all users to user table
        """

        try:
            url = f"{uac.get_sent_messages}{self.__user_id}"
            messages_request = requests.get(url=url)  # Makes the request using the /get_sent_messages method
            request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable

            users_ids = []

            for key in request_content.keys():  # Variable "key" is the message's id
                message_info = request_content[key]  # That's one message

                cursor = self.conn.cursor()
                sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_sent, data, is_read) VALUES(?,?,?,?,?,?,?)"
                record = (key, message_info[0], self.__user_id, message_info[1], 1, message_info[2], 1)
                cursor.execute(sql_to_execute, record)
                self.conn.commit()  # Adds message to the database

                if message_info[1] not in self.__chats:  # Adds new users to list and to self.__chats
                    self.__chats.add(message_info[1])
                    users_ids.append(message_info[1])

            if not users_ids == []:
                users_dict = get_all_users_from_server(users_ids)  # Prepares to add all the users to the database using the server

            else:
                users_dict = {}

            for key in users_dict.keys():
                cursor = self.conn.cursor()
                sql_to_execute = "INSERT INTO chatters_list(user_id, user_name) VALUES(?,?)"
                record = (int(key), users_dict[key])
                cursor.execute(sql_to_execute, record)
                self.conn.commit()  # Adds user to the database
            self.__chatters = self.get_chatters()  # Updates chatters dictionary

            self.open_chat_frames()  # Calls the next method to show chats on __window
        except requests.exceptions.ConnectionError:
            self.server_down_before_logged_in("mid")

    def get_pending_messages(self, running=False):
        """
        Gets the user's pending messages from server

        :param running: True if GUI was opened already
        :type running: (bool)
        :return: Returns 1 if running is set to True
        :rtype: (int)
        """

        url = f"{uac.get_pending_messages}{self.__user_id}"
        try:
            messages_request = requests.get(url=url)  # Makes the request using the /get_pending_messages method
            request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable
            if request_content != {}:
                for key in request_content.keys():  # Variable "key" is the message's id
                    message_info = request_content[key]  # That's one message

                    cursor = self.conn.cursor()
                    sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_sent, data, is_read) VALUES(?,?,?,?,?,?,?)"
                    record = (key, message_info[0], message_info[1], self.__user_id, 0, message_info[2], 0)
                    cursor.execute(sql_to_execute, record)
                    self.conn.commit()  # Adds message to the database

                    if message_info[1] not in self.__chatters.keys():  # If message's author is a new one, adds user to the database
                        try:
                            self.add_user_to_database(message_info[1])
                        except ConnectionError:
                            self.__server_down = True
                self.__server_down = False
                if running:
                    return 1

            if running:
                self.__server_down = False
                return 0
            self.open_chat_frames()
        except requests.exceptions.ConnectionError:
            self.__server_down = True
            if running:
                return 0
            self.open_chat_frames()  # Calls the next method to show chats on __window

    def get_all_chat_messages(self, chatter_id):
        """
        Returns all the messages sent from a user using the database

        :param chatter_id: Id of given user
        :type chatter_id: (int)
        :return: All the messages of the given user plus the last message's id
        :rtype: tuple
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE author_id = {chatter_id} OR addressee_id = {chatter_id}"
        cursor.execute(sql_to_execute)
        messages_list_of_tuples = cursor.fetchall()
        messages_list_of_lists = []
        for single_message in messages_list_of_tuples:
            messages_list_of_lists.append(list(single_message))
        max_char_length = int(self.__size_in_pixels[0] * 3 / 64)

        for i in range(len(messages_list_of_lists)):  # If a message is longer than 80 chars, breaks that into lines
            if len(messages_list_of_lists[i][5]) >= max_char_length:
                message_chars = list(messages_list_of_lists[i][5])
                final_message = []
                while len(message_chars) > max_char_length:
                    broken = False
                    for j in range(max_char_length - 10, max_char_length + 1):
                        if message_chars[j] == " " and not broken:
                            final_message += message_chars[:j + 1]
                            final_message.append("\n")
                            message_chars = message_chars[j + 1:]
                            broken = True
                            break
                    if not broken:
                        final_message += message_chars[0:max_char_length + 1]
                        final_message.append("\n")
                        message_chars = message_chars[max_char_length + 1:]

                final_message += message_chars + list((max_char_length - len(message_chars)) * " ")
                message = "".join(final_message)
                messages_list_of_lists[i][5] = message

        return messages_list_of_lists, {messages_list_of_lists[-1][2]: messages_list_of_lists[-1][0]}  # Response is in form (messages, {author id: last message's id})

    def get_last_message_id(self, chatter_id):
        """
        :param chatter_id: Id of given user
        :type chatter_id: (int)
        :return: Returns a dictionary of {user_id: last_message_id}
        :rtype: dict
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE author_id = {chatter_id} ORDER BY message_id DESC LIMIT 1"
        cursor.execute(sql_to_execute)
        message1 = cursor.fetchall()
        if message1:  # Checks if there are any messages from that user
            id1 = message1[0][0]
        else:
            id1 = 0
        sql_to_execute = f"SELECT * FROM message_list WHERE addressee_id = {chatter_id} ORDER BY message_id DESC LIMIT 1"
        cursor.execute(sql_to_execute)
        message2 = cursor.fetchall()
        if message2:  # Checks if there are any messages sent to that user
            id2 = message2[0][0]
        else:
            id2 = 0
        if id1 > id2:
            return {message1[0][2]: id1}
        else:
            return {message2[0][3]: id2}

    def add_user_to_database(self, user_id):
        """
        Adds user to database

        :param user_id: Given user id
        :type user_id: (int)
        """

        cursor = self.conn.cursor()
        sql_to_execute = "INSERT INTO chatters_list(user_id, user_name) VALUES(?,?)"
        try:
            name = get_user_name_from_server(user_id)  # Gets name via the server
            record = (user_id, name)
            cursor.execute(sql_to_execute, record)
            self.conn.commit()  # Adds user to the database
            self.__chatters = self.get_chatters()  # Updates chatters dictionary
            for key in self.__chatters.keys():
                self.__chats.add(key)  # Updates chatters' ids set
        except ConnectionError:
            raise ConnectionError("Server is down!")

    def get_chats_ordered(self):
        """
        :return: Returns the order in which the chats should be shown
        :rtype: list

        """
        dict_of_order = {}  # Dictionary of all the chatters with their last message id, in form of {chatter id: last message id}
        for chat in self.__chats:
            author_and_message_id = self.get_last_message_id(chat)
            dict_of_order.update(author_and_message_id)

        list_of_chats_ordered = []  # List of all the chats that should be displayed, in order

        while not list(dict_of_order.keys()) == []:  # Loops until the list is complete
            first = list(dict_of_order.keys())[0]
            for key in dict_of_order.keys():
                if dict_of_order[key] > dict_of_order[first]:
                    first = key
            dict_of_order.pop(first)
            list_of_chats_ordered.append(first)
        return list_of_chats_ordered

    def open_chat_frames(self):
        """
        Opens all the chats in order
        Runs a function that calls for get_pending_messages on a different thread
        This is the main app window
        """

        self.__window.close()
        if self.__layout:
            list_of_chats_ordered = self.get_chats_ordered()
            list_box_strings = []
            for user_id in list_of_chats_ordered:
                user_name = self.__chatters[user_id]  # Gets username
                list_box_strings.append(user_name)
                if self.__current_chat == user_id:
                    list_box_strings.append("^" * (len(user_name) - 3))  # ^^^ to mark current chat
                else:
                    list_box_strings.append("")

            # Left column
            self.__list_of_chats_column = sg.Column(
                [
                    [
                        sg.Button("Click to add new chat", key="-ADD_NEW_CHAT-", font=("Garamond", 20, "bold"))  # Add chat button
                    ],
                    [
                        sg.Listbox(list_box_strings, key="-CHAT_LIST-", font=("Garamond", 20, "bold"), text_color="white",
                                   background_color="Turquoise4", expand_x=True, expand_y=True, enable_events=True)  # ListBox of all chat
                    ]
                ],
                background_color="DarkCyan", expand_y=True, expand_x=True, key="-LIST_OF_CHATS-")

            # Right column
            self.__chat_column = sg.Column(self.__current_chat_layout,
                                           size=(size()[0] * 2 / 3, size()[1] - size()[1]/5.5),
                                           key="-CHAT_COLUMN-", scrollable=True, vertical_scroll_only=True,
                                           justification="right", pad=(0, 0))
            self.__message_input = sg.InputText(key="-INPUT-", justification="center",
                                                size=(int(self.__char_length / 2), 20))
            headline = ""
            visible = False
            if self.__current_chat is not None:
                headline = self.__chatters[self.__current_chat]
                visible = True
            self.__layout = [
                [self.__list_of_chats_column,
                 sg.Column([
                     [sg.Text(headline, font=("Garamond", 30, "bold"), background_color="DeepPink4", pad=10, border_width=10, visible=visible)],
                     [self.__chat_column],
                     [sg.Push(), self.__message_input, sg.Push()]  # Text input field
                 ])
                 ]
            ]
            self.__window = sg.Window("Main app window", self.__layout, icon="PyChat1.ico").Finalize()  # Opens window
            self.__window['-INPUT-'].bind("<Return>", "_Enter")
            self.__window["-CHAT_COLUMN-"].Widget.canvas.yview_moveto(1)
            self.__window.Maximize()
            self.__new_messages = False

            def running_thread():  # Gets pending messages from server every 3 seconds
                while True:
                    if self.__close_thread:
                        break
                    elif self.get_pending_messages(running=True) == 0:
                        time.sleep(3)
                    else:
                        self.__new_messages = True

            if self.__thread_pending is None:  # Opens the function on a different thread
                self.__thread_pending = Thread(target=running_thread)
                self.__thread_pending.start()

            while True:  # Main app event loop
                event, values = self.__window.read(300)
                if event == sg.WIN_CLOSED or event == 'Cancel':
                    break

                elif self.__new_messages:
                    self.open_chat("")

                elif event == "-CHAT_LIST-":
                    if not values["-CHAT_LIST-"][0] == "" and not values["-CHAT_LIST-"][0][0] == "^":
                        self.open_chat(values["-CHAT_LIST-"][0])

                elif event == "-ADD_NEW_CHAT-":
                    self.add_chat()

                elif event == "-INPUT-" + "_Enter":
                    if self.__current_chat is None:
                        self.__window["-INPUT-"].update("Click on a chat to send messages")
                    else:
                        if not values["-INPUT-"].split() == []:
                            self.send_message(values["-INPUT-"])
                            try:
                                self.__window["-INPUT-"].update("")
                            except:  # Fixed an error in running
                                pass

                        else:
                            self.__window["-INPUT-"].update("")
            self.__layout = []
            self.__window.close()
            self.__close_thread = True

    def open_chat(self, user_name):
        """
        Opens chat

        :param user_name: Given user name
        :type user_name: (str)
        """

        self.__window.close()
        user_id = 0
        layout = [[sg.Text("a" * int((self.__char_length*0.5)), font=("Garamond", 20, "bold"), text_color="#203562")]]  # Fixes alignment issues
        if not user_name == "" and not user_name[0] == "^":
            for key in self.__chatters:
                if self.__chatters[key] == user_name:
                    user_id = key

            self.__current_chat = user_id

            self.set_messages_read()  # Changed property of chat to being read
        user_messages = self.get_all_chat_messages(self.__current_chat)[0]
        for message in user_messages:
            message_id = message[0]
            if message[4] == 1:  # If message is sent by the user
                layout.append([sg.Push(), sg.Text(message[5], key=message_id, font=("Garamond", 20, "bold"), background_color="SteelBlue3", pad=10, border_width=10)])
            else:  # If message was sent to the user
                layout.append([sg.Text(message[5], key=message_id, font=("Garamond", 20, "bold"), background_color="SpringGreen4", justification="left", border_width=10, pad=10)])
        self.__current_chat_layout = layout
        self.open_chat_frames()  # Reopens main app frame

    def set_messages_read(self):
        """
        Sets messages of current chat to be read
        """

        cursor = self.conn.cursor()
        sql_to_execute = f"UPDATE message_list SET is_read = 1 WHERE author_id = {self.__current_chat}"
        cursor.execute(sql_to_execute)
        self.conn.commit()

    def send_message(self, message):
        """
        Sends a message using the server
        If got confirmation, adds the message to the database

        :param message: Given user input
        :type message: (str)
        """

        if not self.__server_down:
            try:
                send_message_url = uac.send_message
                data = {
                    "date": datetime.today(),
                    "author_id": self.__user_id,
                    "addressee_id": self.__current_chat,
                    "data": message
                }

                send_message_request = requests.post(url=send_message_url, data=data)  # Makes the request using the server
                messages = json.loads(send_message_request.content.decode())

                for key in messages:
                    message_info = messages[key]
                    cursor = self.conn.cursor()
                    sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_sent, data, is_read) VALUES(?,?,?,?,?,?,?)"
                    record = (key, message_info[0], self.__user_id, message_info[1], 1, message_info[2], 1)
                    cursor.execute(sql_to_execute, record)
                    self.conn.commit()  # Adds message to the database

                    self.open_chat(self.__chatters[message_info[1]])
            except requests.exceptions.ConnectionError:
                self.server_down()
        else:
            self.server_down()

    def server_down_before_logged_in(self, time_of_crash):
        """
        Handles GUI in case of the server being down before the user could login

        :param time_of_crash: Whether server crashed mid-login or before
        :type time_of_crash: (str)
        """

        self.__window.close()
        if time_of_crash == "before":
            text = "Server is currently down. Try to login or register later."
        else:
            text = "Server went down before login was complete. Try again later"
            self.conn.close()
            del self.conn
            gc.collect(2)  # Empties garbage collector to be able to delete database
            os.remove("messages.db")
            os.remove("user_id.txt")

        self.__layout = [
            [sg.VPush()],
            [sg.Push(), sg.Text(text, font=("Garamond", 40, "bold"), justification="center", key="-TEXT-", enable_events=True), sg.Push()],
            [sg.VPush()]
        ]
        self.__window = sg.Window("Server Went Down Before Logged In", self.__layout, icon="PyChat1.ico", finalize=True)
        self.__window.maximize()

        while True:

            event, values = self.__window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel' or "-TEXT-":
                break
        self.__window.close()

    def add_chat(self):
        """
        Adds chat after user clicked the add user button
        If got confirmation from the server, adds message to database
        """

        if self.__server_down:
            self.server_down()
        else:
            layout = [
                [sg.Text("Enter name: ")],
                [sg.Input(key="-INPUT-")],
                [sg.Text("Enter first message: ")],
                [sg.Input(key="-MESSAGE-")],
                [sg.Text("", key="-ERROR-")]
            ]
            window1 = sg.Window("Add new chat", layout, icon="PyChat1.ico", finalize=True)
            window1['-MESSAGE-'].bind("<Return>", "_Enter")
            window1['-INPUT-'].bind("<Return>", "_Enter")
            while True:
                event, values = window1.read()
                if event == "Exit" or event == sg.WIN_CLOSED:
                    break
                if event == "-MESSAGE-" + "_Enter" or "-INPUT-" + "_Enter":  # Checks for errors
                    if len(values["-INPUT-"].replace(" ", "")) < 2:
                        window1["-ERROR-"].update("Name must be at least 2 chars long")
                    elif len(values["-MESSAGE-"].replace(" ", "")) == 0:
                        window1["-ERROR-"].update("You must send an initial message")
                    else:
                        user_id = get_user_id_from_server(values["-INPUT-"])
                        if user_id == "Invalid user":
                            window1["-ERROR-"].update(user_id)
                        elif int(user_id) in self.__chats:
                            window1["-ERROR-"].update("You already chat with this person!")
                        else:
                            user_id = int(user_id)
                            try:
                                data = {
                                    "date": datetime.now(),
                                    "author_id": self.__user_id,
                                    "addressee_id": user_id,
                                    "data": values["-MESSAGE-"]
                                }

                                send_message_url = uac.send_message
                                send_message_request = requests.post(url=send_message_url, data=data)  # Sends the initial message using the server
                                messages = json.loads(send_message_request.content.decode())

                                for key in messages:
                                    message_info = messages[key]
                                    cursor = self.conn.cursor()
                                    sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, addressee_id, is_sent, data, is_read) VALUES(?,?,?,?,?,?,?)"
                                    record = (key, message_info[0], self.__user_id, message_info[1], 1, message_info[2], 1)
                                    cursor.execute(sql_to_execute, record)
                                    self.__current_chat = message_info[1]
                                    self.add_user_to_database(message_info[1])
                                    self.conn.commit()  # Adds the massage to the database

                                break
                            except requests.exceptions.ConnectionError:
                                window1["-ERROR-"].update("Server is currently down. Try again later.")

            window1.close()
            self.open_chat(self.__chatters[self.__current_chat])  # Reopens chat

    def server_down(self):
        """
        Handles add new chat and send message actions in case the server is down
        Pop an alert
        """

        sg.Popup("Server went down. Try again later.", title="Server went down", icon="PyChat1.ico")
        self.__server_down = True
