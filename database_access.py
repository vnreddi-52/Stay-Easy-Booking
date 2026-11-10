
class Queries:
    # Queries for Room
    create_query_room = """CREATE TABLE IF NOT EXISTS ROOM(
                        room_no INT PRIMARY KEY,
                        room_type TEXT NOT NULL CHECK(room_type in ('Standard','Deluxe','Suite')),
                        floor INT NOT NULL CHECK(floor BETWEEN 1 AND 3),
                        is_available BOOL NOT NULL CHECK(is_available in ('True','False'))
                        )
                        """
    insert_query_room = """INSERT OR IGNORE INTO ROOM VALUES (?,?,?,?)"""
    select_query_room = """SELECT * FROM ROOM"""

    # Quesries for Guests 
    create_query_guest = """CREATE TABLE IF NOT EXISTS GUEST (
                        phone_no INT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL
                        )"""

    insert_query_guest2 = """
    INSERT OR IGNORE INTO Guest (phone_no, name, email)
    VALUES (?, ?, ?)
    """

    select_query_guest = """SELECT * FROM GUEST"""

    # QUeries for Booking
    create_query_booking = """ CREATE TABLE IF NOT EXISTS Booking (
                            bid INTEGER PRIMARY KEY AUTOINCREMENT,
                            guest INT NOT NULL REFERENCES GUEST(phone_no),
                            room INT NOT NULL REFERENCES ROOM(room_no),
                            check_in DATE NOT NULL ,
                            check_out DATE NOT NULL ,
                            no_of_guests INT NOT NULL,
                            status TEXT NOT NULL,
                            price REAL NOT NULL,
                            cancelled_date DATE,
                            cancellation_amount REAL
                            )"""
    insert_query_booking= """INSERT OR IGNORE INTO Booking
                            (guest, room, check_in, check_out,
                            no_of_guests, status, price, cancelled_date, cancellation_amount)
                            VALUES(?,?,?,?,?,?,?,NULL, NULL)"""


    
    select_query_booking = """SELECT * FROM BOOKING"""

    room_availability_query = """
                SELECT r.room_no
                from Room r
                where r.room_type = ?
                AND r.room_no NOT IN (
                SELECT b.room 
                from booking b
                where b.status in ('CONFIRMED', 'CHECKED_IN') AND
                 ? < b.check_out AND
                ? > b.check_in
                )
                ORDER BY r.room_no ASC
                """

    select_guest_by_phone = """
    SELECT * FROM GUEST
    WHERE phone_no = ?
    """

    completed_stays_query = """
    SELECT COUNT(*)
    from booking
    where guest = ? AND status = 'CHECKED_OUT'
    """
    # added thesee
    select_booking_by_id = """SELECT * from Booking where bid = ?"""
    update_booking_status = """UPDATE Booking 
                                SET status = ?
                                WHERE bid = ?"""
    select_room_by_id="""SELECT room_no, room_type, floor
                        from ROOM where room_no=?"""

    update_cancellation = """UPDATE Booking
    SET status = ?, cancelled_date = ?, cancellation_amount = ?
    WHERE bid = ?"""

    guest_booking_history = """SELECT * FROM Booking
    WHERE guest= ?"""

    occupied_rooms_query = """SELECT COUNT(DISTINCT room)
    FROM Booking
    WHERE status IN ('CONFIRMED', 'CHECKED_IN')
    AND check_in <= ?
    AND check_out > ?"""

    total_rooms_query = """SELECT COUNT(*) FROM Room"""
