from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from customtkinter import *
import customtkinter
from PIL import ImageTk, Image
import requests
from datetime import date, datetime
import sqlite3
import os.path
import json
from customtkinter import CTkButton


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("custom_style.json")  # Installs custom background


def get_user_name_from_server(user_id):  # Gets a username of a given id via the server
    url = f"http://localhost:8000/get_user_name?user_id={user_id}"
    messages_request = requests.get(url=url)  # Makes the request using the /get_user_id method
    request_content = messages_request.content.decode()  # Saves the server reply in a variable
    return request_content


def get_all_users_from_server(users):  # Gets all usernames of the given ids via the server
    url = f"http://localhost:8000/get_users?users_ids={users}"
    messages_request = requests.get(url=url)  # Makes the request using the /get_user_id method
    request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable
    return request_content


class TkApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('--insert_name--')  # Title
        self.iconbitmap('heart.ico')  # Icon
        self.geometry(str(self.winfo_screenwidth()) + "x" + str(self.winfo_screenheight()))  # Setting size to full screen
        self.resizable(width=0, height=0)  # Disabling resizing the __window.
        self.state('zoomed')  # Maximizing __window
        self.overrideredirect(False)

        self.frames = {}  # Initializes frames dict
        self.__chats = {0}  # Initializes users set
        self.__chats.remove(0)
        self.__messages = []  # Initializes messages list

        self.__is_logged_in = self.is_database()  # Checks whether user is logged in by looking for the database of messages
        if self.__is_logged_in:  # If the user is logged in, does the following actions:
            self.conn = sqlite3.connect("messages.db", check_same_thread=False)
            with open("user_id.txt", "r") as file:
                self.__user_id = file.read()  # Gets the user id from the client files

            self.__chatters = self.get_chatters()  # Gets the chatters names and ids
            for key in self.__chatters.keys():
                self.__chats.add(key)

        else:  # Will force user to log in or register
            self.__user_id = None
            self.__chatters = {}

    def is_database(self):  # Returns True if database exists, False if not
        if os.path.isfile('messages.db'):
            return True
        return False

    def is_logged_in(self):  # Returns True if the user is logged in, False if not
        return self.__is_logged_in

    # def user_id(self):   # Only used in development
        # return self.__user_id

    def get_chatters(self):  # Returns chatters dictionary from the database
        cursor = self.conn.cursor()
        sql_to_execute = "SELECT * FROM chatters_list"
        cursor.execute(sql_to_execute)
        users = cursor.fetchall()
        user_dict = {}
        for user in users:
            user_dict[user[0]] = user[1]
        return user_dict

    def register_or_login(self):  # Creates a register button
        global register_button
        global login_button

        register_button = CTkButton(self, text="Click to register", command=self.register_window, bg_color="MediumOrchid3")
        register_button.pack()
        login_button = CTkButton(self, text="Click to login", command=self.login_window, bg_color="MediumOrchid3")
        login_button.pack()

    def register_window(self):  # Manages registry
        global register_window

        register_window = CTkToplevel()  # Opens a register __window
        register_window.geometry("650x420")
        register_window.configure(bg="MediumOrchid3")
        lbl_name = CTkLabel(register_window, text="Enter your name: ", bg_color="MediumOrchid3").grid(row=0)  # Name
        entry_name = CTkEntry(register_window, bg_color="MediumOrchid3")  # Name input field
        entry_name.grid(row=1)
        lbl_birthdate = CTkLabel(register_window, text="Enter your birthdate (year-month-day): ", bg_color="MediumOrchid3").grid(row=2)  # Birthdate
        entry_birthdate = CTkEntry(register_window, bg_color="MediumOrchid3")  # Birthdate input field
        entry_birthdate.grid(row=3)
        lbl_password = CTkLabel(register_window, text="Enter your password: ", bg_color="MediumOrchid3").grid(row=4)  # Password
        entry_password = CTkEntry(register_window, bg_color="MediumOrchid3")  # Password input field
        entry_password.grid(row=5)
        btn_entered_data = CTkButton(register_window, text="Enter", bg_color="MediumOrchid3", command=lambda: self.server_register(client_name=entry_name.get(), client_birthdate=entry_birthdate.get(), client_password=entry_password.get()))  # Button when finished
        btn_entered_data.grid(row=6)

    def server_register(self, client_name, client_birthdate, client_password):  # Registers using the server
        global register_button
        global register_window

        # Checks for valid birthdate, name and password. If invalid, opens a text message that has "Wrong date or user is not old enough" on it
        if not self.check_birthdate(client_birthdate) or client_name.strip() == "" or client_password.strip == "":
            messagebox.showerror(message="Wrong date or user is not old enough")
            register_window.destroy()
            self.register_window()

        # If user details are valid, registers using the server method /register
        else:
            data = {
                "name": client_name,
                "birthdate": client_birthdate,
                "password": client_password
            }
            register_url = "http://localhost:8000/register"
            register_request = requests.put(url=register_url, data=data)
            if register_request.content.decode() == "User added":  # Finishes registry process
                register_window.destroy()
                register_button.destroy()

    def check_birthdate(self, birthdate):  # Checks whether the birthdate is valid
        x = birthdate
        if len(x) != 10:  # Valid birthdate is in ****-**-** form
            return False
        if x[4] != "-" and x[7] != "-":  # Must include two '-' in the right places
            return False
        year, month, day = x.split('-')
        try:
            int(x[:4])
            int(x[5:7])
            int(x[8:])
            datetime(int(year), int(month), int(day))
        except ValueError:
            return False
        date_today = date.today().strftime("%d/%m/%Y")
        date_today = date_today[:6] + str(int(date_today[6:]) - 13)  # Makes sure user is at least 13
        today = datetime.strptime(date_today, "%d/%m/%Y").date()
        birthdate = datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y").date()
        if today < birthdate:
            return False
        return True

    def login_window(self):  # Manages login
        global login_window

        login_window = CTkToplevel()  # Opens a register __window
        login_window.geometry("650x420")
        lbl_name = CTkLabel(login_window, bg_color="MediumOrchid3", text="Enter your name: ").grid(row=0)  # Name
        entry_name = CTkEntry(login_window, bg_color="MediumOrchid3")  # Name input field
        entry_name.grid(row=1)
        lbl_password = CTkLabel(login_window, bg_color="MediumOrchid3", text="Enter your password: ").grid(row=2)  # Password
        entry_password = CTkEntry(login_window, bg_color="MediumOrchid3")  # Password input field
        entry_password.grid(row=3)
        btn_entered_data = CTkButton(login_window, text="Enter", bg_color="MediumOrchid3", command=lambda: self.server_login(client_name=entry_name.get(), client_password=entry_password.get()))  # Button when finished
        btn_entered_data.grid(row=4)

    def server_login(self, client_name, client_password):  # Logins using the server
        global register_button
        global login_button

        data = {
            "name": client_name,
            "password": client_password
        }
        login_url = "http://localhost:8000/login"
        login_request = requests.put(url=login_url, data=data)  # Sends the request using the /login method
        request_content = login_request.content.decode()  # Saves the server reply in a variable

        # If user is valid, destroys the unnecessary widgets, saves the user id and initializes database
        if request_content[:10] == "Valid user":
            login_window.destroy()
            try:  # Some bugs came up as the program migrated to customtkinter. This seemed to have solved the problem
                register_button.destroy()
            except ValueError:
                pass
            login_button.destroy()
            self.__is_logged_in = True
            self.__user_id = request_content.split("=")[-1]
            with open("user_id.txt", "w") as file:
                file.write(self.__user_id)

            self.initialize_database()  # Initialize client

        else:  # If user is not valid, forces the client to login again
            messagebox.showerror(message="Wrong name or password")
            login_window.destroy()
            self.login_window()

    def initialize_database(self):  # Initializes database with the columns message_id, date, author_id, type, data and is_read
        # Used in case of a new device log in
        # Creates user_id and user_name columns
        self.conn = sqlite3.connect("messages.db", check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS message_list
                (message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date TEXT NOT NULL,
                author_id INTEGER NOT NULL,      
                type INTEGER NOT NULL,
                data TEXT NOT NULL,
                is_read INTEGER NOT NULL)
                ''')  # If read = 1, message has been read
        self.conn.execute('''CREATE TABLE IF NOT EXISTS chatters_list
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_name TEXT NOT NULL)
                ''')
        self.get_all_messages()  # Calls the next method to receive messages from server

    def get_all_messages(self):  # Gets all the user's messages from the server
        url = f"http://localhost:8000/get_all_messages?user_id={self.__user_id}"
        messages_request = requests.get(url=url)  # Makes the request using the /get_all_messages method
        request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable

        users_ids = []  # Initializes all of the users' ids list

        for key in request_content.keys():  # Variable "key" is the message's id
            message_info = request_content[key]  # That's one message

            cursor = self.conn.cursor()
            sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, type, data, is_read) VALUES(?,?,?,?,?,?)"
            record = (key, message_info[0], message_info[1], message_info[2], message_info[3], 0)
            cursor.execute(sql_to_execute, record)
            self.conn.commit()  # Adds message the the database

            if message_info[1] not in self.__chats:  # Adds new users to list and to self.__chats
                users_ids.append(message_info[1])
                self.__chats.add(message_info[1])

        users_dict = get_all_users_from_server(users_ids)  # Prepares to add all the users to the database using the server

        for key in users_dict.keys():
            cursor = self.conn.cursor()
            sql_to_execute = "INSERT INTO chatters_list(user_id, user_name) VALUES(?,?)"
            record = (int(key), users_dict[key])
            cursor.execute(sql_to_execute, record)
            self.conn.commit()  # Adds user to the database
        self.__chatters = self.get_chatters()  # Updates chatters dictionary

        self.open_chat_frames()  # Calls the next method to show chats on __window

    def get_pending_messages(self):  # Gets the user's pending messages from server
        url = f"http://localhost:8000/get_pending_messages?user_id={self.__user_id}"
        messages_request = requests.get(url=url)  # Makes the request using the /get_pending_messages method
        request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable

        for key in request_content.keys(): # Variable "key" is the message's id
            message_info = request_content[key]  # That's one message

            cursor = self.conn.cursor()
            sql_to_execute = "INSERT INTO message_list(message_id, date, author_id, type, data, is_read) VALUES(?,?,?,?,?,?)"
            record = (key, message_info[0], message_info[1], message_info[2], message_info[3], 0)
            cursor.execute(sql_to_execute, record)
            self.conn.commit()  # Adds message to the database

            if message_info[1] not in self.__chatters.keys():  # If message's author is a new one, adds user to the database
                self.add_user_to_database(message_info[1])

        self.open_chat_frames()  # Calls the next method to show chats on __window

    def open_chat_frames(self):  # Opens all the chats in order, each chat on one frame
        self.destroy_screen()
        list_of_dicts_of_chat_messages = []  # List of all the messages in form of {author1 id: [messages], author2 id: [messages]...}
        dict_of_order = {}  # Dictionary of all the chatters with their last message id, in form of {chatter id: last message id}

        for chat in self.__chats:
            response_tuple = self.get_all_chat_messages(chat)
            list_of_dicts_of_chat_messages.append({list(response_tuple[1].keys())[0]: response_tuple[0]})
            dict_of_order.update(response_tuple[1])

        self.__messages = list_of_dicts_of_chat_messages
        list_of_chats_ordered = []  # List of all the chats that should be displayed, in order

        while not list(dict_of_order.keys()) == []:  # Loops until the list is complete
            first = list(dict_of_order.keys())[0]
            for key in dict_of_order.keys():
                if dict_of_order[key] > dict_of_order[first]:
                    first = key
            dict_of_order.pop(first)
            list_of_chats_ordered.append(first)

        # The Following lines were used in development:
        # self.frames["destroy_button"] = CTkFrame(self)  # Adds destroy button
        # self.frames["destroy_button"].pack()
        # btn = CTkButton(self.frames["destroy_button"], text="click to destroy", bg_color="MediumOrchid3", command=self.destroy_screen)
        # btn.pack()

        buttons_dict = {}  # Initializes button dictionary

        self.frames["main_frame"] = Frame(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())  # Creates a main frame to hold everything
        self.frames["main_frame"].place(x=0, y=0)

        self.frames["canvas"] = Canvas(self.frames["main_frame"], width=self.winfo_screenwidth(), height=self.winfo_screenheight())  # Creates a Canvas
        self.frames["canvas"].place(x=0, y=0)

        self.frames["scrollbar"] = ttk.Scrollbar(self.frames["main_frame"], orient=VERTICAL, command=self.frames["canvas"].yview)  # Adds a Scrollbar to the Canvas
        self.frames["scrollbar"].place(x=self.winfo_screenwidth() - 15, y=0, height=self.winfo_screenheight())

        self.frames["canvas"].configure(yscrollcommand=self.frames["scrollbar"].set)  # Configures the Canvas
        self.frames["canvas"].bind('<Configure>', lambda e: self.frames["canvas"].configure(scrollregion=self.frames["canvas"].bbox("all")))

        def _on_mouse_wheel(event):  # Adds a key bind to mousewheel
            self.frames["canvas"].yview_scroll(-1 * int((event.delta / 120)), "units")

        self.frames["canvas"].bind_all("<MouseWheel>", _on_mouse_wheel)

        self.frames["second_frame"] = Frame(self.frames["canvas"], width=self.winfo_screenwidth(), height=self.winfo_screenheight())  # Creates another frame inside the Canvas
        self.frames["second_frame"].place(x=0, y=0)

        self.frames["canvas"].create_window((0, 0), window=self.frames["second_frame"], anchor="nw")  # Adds that new frame to a Window in the Canvas

        pos_y = 0

        for user_id in list_of_chats_ordered:
            user_name = self.__chatters[user_id]  # Gets username
            buttons_dict[user_id] = UserButton(user_id, user_name, self, pos_y).place(x=0, y=pos_y)  # Adds user button
            self.frames["second_frame"].configure(height=pos_y)  # Changes the height of the second_frame every time a button is added

            pos_y += 100

        self.frames["second_frame"].configure(height=pos_y+26)  # Changes the height of the second_frame for the last time

    def get_all_chat_messages(self, chatter_id):  # Returns all the messages sent from a user using the database
        cursor = self.conn.cursor()
        sql_to_execute = f"SELECT * FROM message_list WHERE author_id = {chatter_id}"
        cursor.execute(sql_to_execute)
        messages = cursor.fetchall()
        return messages, {messages[-1][2]: messages[-1][0]}  # Response is in form (messages, {author id: last message's id})

    def add_user_to_database(self, user_id):  # Adds user to database
        cursor = self.conn.cursor()
        sql_to_execute = "INSERT INTO chatters_list(user_id, user_name) VALUES(?,?)"
        record = (user_id, get_user_name_from_server(user_id))
        cursor.execute(sql_to_execute, record)
        self.conn.commit()  # Adds user to the database
        self.__chatters = self.get_chatters()  # Updates chatters dictionary
        for key in self.__chatters.keys():
            self.__chats.add(key)  # Updates chatters' ids set

    def open_chat(self, user_id):
        self.destroy_screen()

        self.frames["go_back"] = CTkFrame(self)  # Adds go back key to the chats menu
        self.frames["go_back"].pack()
        btn = CTkButton(self.frames["go_back"], text="click to go back", bg_color="MediumOrchid3", command=self.open_chat_frames)  # Creates a button for each message
        btn.pack()  # Packs the button

        user_messages = []  # All of one user's messages
        for chat in self.__messages:
            if user_id in chat.keys():
                user_messages = chat[user_id]
        for message in user_messages:
            message_id = message[0]

            self.frames[message_id] = CTkFrame(self)  # Adds a frame to each message
            self.frames[message_id].pack()

            lbl = CTkLabel(self.frames[message_id], text=message[4], bg_color="MediumOrchid3", fg_color="LightCyan1")
            lbl.pack()

    def destroy_screen(self):  # Destroys screen
        for key in self.frames.keys():
            try:  # Some bugs came up as the program migrated to customtkinter. This seemed to have solved the problem
                self.frames[key].destroy()
            except ValueError:
                pass


class UserButton(CTkButton):  # Class to easily create a button to each user in the users menu
    def __init__(self, id, text, app, posY):
        super().__init__(app.frames["second_frame"], text=text, fg_color="SkyBlue1", bg_color="HotPink3", command=lambda: app.open_chat(id), width=app.winfo_screenwidth(), height=100)
        self.place(x=50, y=posY)


