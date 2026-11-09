

class MasterBookingException(Exception):
    pass
class RoomUnavailable(MasterBookingException):
    pass
class InvalidDate(MasterBookingException):
    pass
class InvalidStatusChange(MasterBookingException):
    pass
class BookingNotFound(MasterBookingException):
    pass
