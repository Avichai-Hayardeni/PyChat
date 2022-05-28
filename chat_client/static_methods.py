import requests
from datetime import date
import URLs_and_consts as uac
import json
import os


def check_birthday(birthdate):
    """
    Checks for valid birthdate

    :param birthdate: given birthdate
    :type birthdate: (str)
    :return: True if valid, False if not
    :rtype: (bool)
    """

    valid = True
    date_today = date.today().strftime("%Y/%m/%d").split("/")
    year_month_day = birthdate.split("-")
    if int(date_today[0]) - int(year_month_day[0]) < 13:
        valid = False

    elif int(date_today[0]) - int(year_month_day[0]) == 13:
        if int(date_today[1]) < int(year_month_day[1]):
            valid = False
        elif int(date_today[1]) == int(year_month_day[1]):
            if int(date_today[2]) < int(year_month_day[2]):
                valid = False

    return valid


def is_database():
    """"
    :return: True if database exists, False if not
    :rtype: (bool)
    """

    return os.path.isfile('messages.db')


def get_user_name_from_server(user_id):
    """
    Gets a username of a given id via the server

    :param user_id: Given user id
    :type user_id: (int)
    :return: The name of the given user
    :rtype: (str)
    """

    try:
        url = f"{uac.get_user_name_from_server}{user_id}"
        messages_request = requests.get(url=url)  # Makes the request using the /get_user_id method
        request_content = messages_request.content.decode()  # Saves the server reply in a variable
        return request_content
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Server is down!")


def get_user_id_from_server(user_name):
    """
    :param user_name: Requested user's username
    :type user_name: (str)
    :return: Returns the user's id from the server, or an exception if the server is down
    :rtype: (int) or exception
    """

    try:
        url = f"{uac.get_user_id_from_server}{user_name}"
        messages_request = requests.get(url=url)  # Makes the request using the /get_user_id method
        request_content = messages_request.content.decode()  # Saves the server reply in a variable
        return request_content
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Server is down!")


def get_all_users_from_server(users):
    """
    Gets all usernames of the given ids via the server

    :param users: List of all the users
    :rtype: list
    :return: Ids and names of given users
    :rtype: dict
    """
    try:
        url = f"{uac.get_users_from_server}{users}"
        messages_request = requests.get(url=url)  # Makes the request using the /get_user_id method
        request_content = json.loads(messages_request.content.decode())  # Saves the server reply in a variable
        return request_content
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Server is down!")
