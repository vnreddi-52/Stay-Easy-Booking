from abc import ABC, abstractmethod
from datetime import date
import re

DAYS = ["Friday", "Saturday"]

class Room(ABC):
    def __init__(self, room_no, room_type, floor):
        self.room_no = int(room_no)
        self.room_type = room_type.capitalize()
        self.floor = int(floor)
        
    @abstractmethod
    def tariff(self, day):
        pass
    @abstractmethod
    def extra_guest(self, guests):
        pass
    @abstractmethod
    def breakfast(self, guests = 1, include = False):
        pass

    def __str__(self):
        return f"Room: {self.room_no} | Type: {self.room_type} | Floor: {self.floor}"
    
class StandardRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
        self.base_rate = 2500
        self.max_guests=2
        
    def tariff(self, day):
        if day.weekday() in (4,5):
            return 2500*1.20
        return 2500
    def extra_guest(self, guests):
        return 0
    def breakfast(self,guests=1, include=False ):
        if include:
            return guests * 350
        return 0

class DeluxeRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
        self.base_rate = 4000
        self.max_guests=3

    def tariff(self, day):
        if day.weekday() in (4,5):
            return 4000 * 1.20
        return 4000
    
    def extra_guest(self, guests):
        return max(0, guests - 2)*800

    def breakfast(self, guests=1, include=False):
        return 0

    def __str__(self):
        return f"{self.room_no} {self.room_type} {self.floor}"
    
class SuiteRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
        self.base_rate = 7500
        self.max_guests=4

    def tariff(self, day):
        if day.weekday() in (4, 5):
            return 7500 * 1.20
        return 7500
    
    def extra_guest(self, guests):
        return max(0, guests - 2) * 800

    def breakfast(self, guests=1, include=False):
        return 0

    def __str__(self):
        return f"{self.room_no} {self.room_type} {self.floor}"

class Guest:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        return f"Guest: {self.name} | Phone: {self.phone} | Email: {self.email}"
    
class Booking:
    STATUSES = {
        "CONFIRMED",
        "CHECKED_IN",
        "CHECKED_OUT",
        "CANCELLED"
    }
    def __init__(self, guest, room, check_in, check_out, no_of_guests, status, price):
        if not isinstance(guest, Guest):
            raise ValueError("Invalid guest object")

        if not isinstance(room, Room):
            raise ValueError("Invalid room object")

        dates = [check_in, check_out]
        for i in dates:
            if not isinstance(i, date):
                raise ValueError("Invalid Date")

        if price<0:
            raise ValueError("Incorrect price")

        self.bid=None
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.no_of_guests = no_of_guests
        self.status = "CONFIRMED"
        self.price = price
        self.cancelled_date = None
        self.cancellation_amount =0

    def check_in_guest(self):
        if self.status != "CONFIRMED":
            raise ValueError("Only confirmed bookings can check in bro..")
        if date.today() != self.check_in:
            raise ValueError("Checkin is allowed only on the checkin date")
        self.status = "CHECKED_IN"

    def check_out_guest(self):
        if self.status != "CHECKED_IN":
            raise ValueError("Guest has not checkedin")
        self.status = "CHECKED_OUT"

    def cancel_booking(self):
        if self.status not in ("CONFIRMED",):
            raise ValueError("Booking cannot be cancelled its not confirmed initially bro..")
        self.status = "CANCELLED"
        self.cancelled_date = date.today()
        
    def __str__(self):
        return (
            f"""Booking ID: {self.bid} | 
            Guest: {self.guest.name} | 
            Room: {self.room.room_no} | 
            Check-in: {self.check_in} | 
            Check-out: {self.check_out} | 
            Guests: {self.no_of_guests} | 
            Price: {self.price:.2f} | 
            Status: {self.status}"""
    )