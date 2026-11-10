import re
from datetime import date, datetime, timedelta
import sqlite3 as sq

conn = sq.connect("stay_easy.db")
curr = conn.cursor()

phone_no_pattern = r"^[6-9]\d{9}$"
email_pattern = r"^[a-zA-Z0-9]+@gmail\.com$"
guest_pattern = r"\d+"

ROOM_CAPACITY = {
    "Standard": 2,
    "Deluxe": 3,
    "Suite": 4
}

def validate_phone_no():
    while True:
        phone_no = input("Enter phone number: ")
        if re.fullmatch(phone_no_pattern, phone_no):
            return phone_no
        print("Invalid phone no entered ")

def validate_name():
    while True:
        name = input("Enter your name: ").strip()
        if name and name.isalpha():
            return name
        print("Invalid name entered ")

def validate_email():
    while True:
        email = input("Enter your email: ")
        if re.fullmatch(email_pattern, email):
            return email
        print("Invalid email entered")

def get_check_availability():
    room_type = validate_room_type("Enter the room type: ")
    guests = validate_no_of_guests(room_type)
    check_in = validate_checkin("Enter check in date: ")
    check_out = validate_checkout(check_in)
    return room_type, check_in, check_out, guests

def validate_no_of_guests(room_type):
    maximum = ROOM_CAPACITY[room_type]
    while True:
        no_of_guests = input("Enter no of guests: ")
        if re.fullmatch(guest_pattern, no_of_guests):
            guests = int(no_of_guests)
            if 1 <= guests <= maximum:
                return guests
        print("Enter a valid no of guests")
    

def validate_room_type(msg):
    while True:
        type = input(msg).strip()
        if type.lower() in ("standard", "deluxe", "suite"):
            return type.capitalize()
        print("Invalid Room type")

def validate_date_format(msg):
    while True:
        try:
            i_date = input(msg)
            parsed_date = datetime.strptime(i_date, "%d-%m-%Y")
            return parsed_date
        except ValueError:
            print("Invalid date entered")

def validate_checkin(msg):
    while True:
        check_in = validate_date_format(msg)
        check_in = check_in.date()
        today = date.today()
        max_date = today+ timedelta(days = 180)   
        if today <= check_in <= max_date:
            return check_in
        print("Check in must be between today and next 180 days")

def validate_checkout(check_in):
    while True:
        check_out = validate_date_format("Enter check out date: ").date()
        nights = (check_out - check_in).days
        if 1<= nights <=30:
            return check_out

        print("Stay must be between 1-30 days")

def get_booking_input():
    phone = validate_phone_no()
    name = validate_name()
    email = validate_email()

    check_in = validate_checkin("Enter check in date: ")
    check_out = validate_checkout(check_in)
    room_type = validate_room_type("Enter room type: ")
    guests = validate_no_of_guests(room_type)

    return phone, name, email, guests, check_in, check_out, room_type


    