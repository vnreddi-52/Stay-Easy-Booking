import csv 
import sqlite3 as sq
from models import StandardRoom, DeluxeRoom, SuiteRoom, Guest, Booking
from database_access import Queries
from validations import (
      validate_date_format, 
      validate_no_of_guests,
      validate_email,
      validate_name,
      validate_phone_no,
      validate_checkin,
      validate_checkout,
      get_booking_input,
      validate_room_type
    )
import math
from datetime import date, datetime, timedelta
from pricing import calculate_price, full_payment 

ROOM_CAPACITY = {
    "Standard": 2,
    "Deluxe": 3,
    "Suite": 4
}

conn = sq.connect("stay_easy.db")
curr = conn.cursor()

FILE_PATH_ROOMCSV = r"C:\Users\vaishnavi.reddi\Downloads\Booking Application (2)\rooms.csv"
# Loading CSV
def load_rooms_csv():
    try:
        file = open(FILE_PATH_ROOMCSV, "r")
        return csv.reader(file)
    except Exception as e:
        print(e)

def log_errors(errors):
    with open("app.log", "w") as file:
        for i in errors:
            file.write(i)
            file.write("\n")
            
def validate_data(data):
    errors=[]
   
    for line, row in enumerate(data, start=1):
        if line==1:
            continue

        if len(row)!=3:
            errors.append("Missing fields")
            continue

        room_no, room_type, floor = row
        valid = True

        try:
            room_no = int(room_no)
        except ValueError:
            valid = False
            errors.append(f"Line {line} - Room no should be digit")
            continue 

        if room_type.capitalize() not in ("Standard", "Deluxe", "Suite"):
            valid = False
            errors.append(f"Line {line} - Invalid Room Type")
            continue

        if floor not in ("1","2","3"):
            valid = False
            errors.append(f"Line {line} - Invalid Floor")
            continue

        curr.execute(Queries.insert_query_room, (room_no, room_type, floor, 'True'))      
    conn.commit()
    log_errors(errors)

def initialise_databases():
    curr.execute("PRAGMA foreign_keys = OFF")
    # curr.execute("DROP TABLE IF EXISTS Booking")
    # curr.execute("DROP TABLE IF EXISTS Guest")
    # curr.execute("DROP TABLE IF EXISTS Room")
    # print("Dropped succesfully")

    curr.execute(Queries.create_query_room)
    rooms_data = list(load_rooms_csv())
    validate_data(rooms_data)

    curr.execute(Queries.create_query_guest)
    #curr.execute(Queries.insert_query_guest)

    curr.execute(Queries.create_query_booking)
    # curr.execute(Queries.insert_query_booking)

    conn.commit()
    
    curr.execute("PRAGMA foreign_keys = ON")

def display_tables():
    curr.execute(Queries.select_query_room)
    for i in curr.fetchall():
        print(i)

    curr.execute(Queries.select_query_guest)
    for i in curr.fetchall():
        print(i)

    curr.execute(Queries.select_query_booking)
    for i in curr.fetchall():
        print(i) 

def display(obj):
    for i in obj:
        print(i)

#rooms_data = list(load_rooms_csv())
#validate_data(rooms_data)

def get_check_availability():
    room_type = validate_room_type("Enter the type of room needed: ").strip().capitalize()
    check_in = validate_checkin("Enter check_in date: ")
    check_out = validate_checkout(check_in)
    no_of_guests = validate_no_of_guests(room_type)
    return room_type, check_in, check_out, no_of_guests

def check_availability(room_type, check_in, check_out, no_of_guests):
    capacity = ROOM_CAPACITY[room_type]
    #required_rooms = math.ceil(no_of_guests/capacity)

    curr.execute(Queries.room_availability_query, (room_type, check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d")))
    available_rooms = curr.fetchall()
    if available_rooms:
        return available_rooms[0][0]
    return []

def get_existing_guest(phone_no):
    curr.execute(Queries.select_guest_by_phone,(phone_no,))
    return curr.fetchone()

def alternative_rooms(room_type, check_in, check_out, no_of_guests):
    alternatives = {}
    for r_type, r_capacity in ROOM_CAPACITY.items():
        if r_type == room_type or r_capacity < no_of_guests:
            continue
        # required_rooms = required_rooms = math.ceil(no_of_guests/r_capacity)
        curr.execute(Queries.room_availability_query, (r_type, check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d")))
        available_rooms = [row[0] for row in curr.fetchall()]
        if available_rooms:
            alternatives[r_type] = available_rooms
    return alternatives
     
def create_booking():
    # collect all inputs
    phone_no, name , email, no_of_guests, check_in,check_out, room_type = get_booking_input()

    available_room = check_availability(room_type, check_in, check_out, no_of_guests)

    if available_room:
        allocated_room = available_room
    else:
        print("No rooms available for your type")
        alternatives = alternative_rooms(room_type, check_in, check_out, no_of_guests)
        if not alternatives:
            print("No suitable alternative rooms are available")
            return
        print("Available alternative rooms are: ")
        for r_type, room_no in alternatives.items():
            print(f"{r_type}: {room_no}")

        choice = input("Would you like to choose an alternative room?").strip().lower()
        if choice != "yes":
            print("Booking cancelled.")
            return

        selected_type = validate_room_type("Enter the alternative room type: ")
        if selected_type not in alternatives:
            print("Selected room type is not available.")
            return

        room_type = selected_type
        allocated_room = alternatives[selected_type][0]
    print("Allocated room is:", allocated_room)

    # GUest objects creation
    existing_guest=get_existing_guest(phone_no)
    if existing_guest:
        print("Existing guest found bro")
        g = Guest(existing_guest[1], existing_guest[0], existing_guest[2])
    else:
        g = Guest(name, phone_no, email)

    # ROom objecs creation
    curr.execute("""
                SELECT room_no, room_type, floor
                from ROOM
                WHERE room_no = ?""", (allocated_room,))

    room_data = curr.fetchone()
    if not room_data:
        print("Room details not found0")
        return
    if room_type.capitalize() == "Standard":
        # room_obj = StandardRoom(*room_data)
        r = StandardRoom(room_data[0], room_data[1], room_data[2])
    elif room_type.capitalize() == "Deluxe":
        r = DeluxeRoom(room_data[0], room_data[1], room_data[2])
    else:
        r = SuiteRoom(room_data[0], room_data[1], room_data[2])

    include_breakfast = False
    if room_type.capitalize() == "Standard":
        while True:
            breakfast_choice = input(
                "Bro.. breakfast for 350 per guest per night ok? "
            ).strip().lower()
            if breakfast_choice in ("yes"):
                include_breakfast = True
                break
            if breakfast_choice in ("no"):
                break

    # for loyalty discount
    curr.execute(Queries.completed_stays_query, (phone_no,))
    completed_stays = curr.fetchone()[0]
    # final booking price
    price_details = calculate_price(
        r, check_in, check_out, no_of_guests, completed_stays,
        include_breakfast
    )

    print("Price details are: ")
    print("Room charges:", price_details["room_charges"])
    print("Extra guest charges:", price_details["extra_charges"])
    print("Breakfast charges:", price_details["breakfast_charges"])
    print("7 night discount:", price_details["stay_discount"])
    print("Loyalty discount:", price_details["loyalty_discount"])
    print("GST:", price_details["gst"])
    print("Total:", price_details["total"])

    price = price_details["total"]
    if not full_payment(price):
        print("Booking cancelled.")
        return
    
    # guest, room, check_in, check_out, no_of_guests, status, price, cancelled_date, cancellation_amount
    booking = Booking(g, r, check_in, check_out, no_of_guests, "CONFIRMED", price)

    try:
        booking.bid = save_booking(booking)
        print("Booking successfull0")
        print(g)
        print(booking)
    except Exception as e:
        print("Error while saving file")

def save_booking(booking):
    try:
        check_in = booking.check_in.strftime("%Y-%m-%d")
        check_out = booking.check_out.strftime("%Y-%m-%d")
        curr.execute(Queries.insert_query_guest2,(booking.guest.phone, booking.guest.name, booking.guest.email))
        curr.execute(Queries.insert_query_booking,
            (booking.guest.phone,
                booking.room.room_no,
                check_in,
                check_out,
                booking.no_of_guests,
                booking.status,
                booking.price,))
        booking_id = curr.lastrowid        
        conn.commit()
        return booking_id

    except Exception as e:
        conn.rollback()
        print(e)

def check_in_booking():
    bid = input("ENter booking id: ").strip()
    curr.execute(Queries.select_booking_by_id, (bid))
    booking = curr.fetchone()
    if not booking:
        print("No such Boking found")
        return
    status = booking[6]
    checkin_date = date.fromisoformat(booking[3])

    if date.today() != checkin_date:
        print("Check in allowed only on the date which u have entered while booking ...")
        return
    
    curr.execute(Queries.update_booking_status, ("CHECKED_IN", bid))
    conn.commit()
    print("Guest successfully check in")

FILE_PATH_INVOICES= r"C:\Users\vaishnavi.reddi\Downloads\Booking Application (2)\Booking Application\invoices"

def generate_invoice(bid, guest_data, r, check_in, check_out, guests, price_details):
        invoice_id = "BK" + str(bid).zfill(4) #BK0001 bekuu adke
        filename = FILE_PATH_INVOICES + "\\" + invoice_id + ".txt"

        file = open(filename, "w")
        file.write("===============StayEasy Hotel============")
        file.write("Booking ID: "+invoice_id + "\n")
        file.write("Guest Name: "+guest_data[1] + "\n")
        file.write("Phone: "+str(guest_data[0]) + "\n")
        file.write("Email: "+ guest_data[2] + "\n")
        file.write("Room Number: "+str(r.room_no) + "\n")
        file.write("Room Type: "+r.room_type + "\n")
        file.write("Check-in: "+str(check_in) + "\n")
        file.write("Check-out: "+str(check_out) + "\n")
        file.write("Number of Guests: "+str(guests) + "\n")

        file.write("="*10 + "NIGHT " + "="*10)
        for night in price_details["nightly_breakdown"]:
            file.write("\nDate: " + str(night["date"])+"\n")
            file.write("Room Tariff: " + str(night["room_tariff"]) + "\n")
            file.write("Extra Guest Charge: " + str(night["extra_guest_charge"]) + "\n")
            file.write("GST Rate: "+str(night["gst_rate"] * 100) + "%\n")
            file.write("GST: "+str(night["gst"]) + "\n")

        file.write("="*10 + "BILL" + "="*10)
        file.write("Room Charges: "+str(price_details["room_charges"]) + "\n")
        file.write("Extra Charges: "+str(price_details["extra_charges"]) + "\n")
        file.write("7 Night Discount: "+str(price_details["stay_discount"]) + "\n")
        file.write("Loyalty Discount: "+str(price_details["loyalty_discount"]) + "\n")
        file.write("GST: "+str(price_details["gst"]) + "\n")
        file.write("TOTAL AMOUNT: "+str(price_details["total"]) + "\n")
        file.close()
        print("Invoice generated successfully...bro..")


def check_out_booking():
    bid = input("ENter booking id: ").strip()
    curr.execute(Queries.select_booking_by_id, (bid))
    booking = curr.fetchone()
    if not booking:
        print("No such Boking found")
        return

    phone_no = booking[1]
    room_no = booking[2]
    check_in = date.fromisoformat(booking[3])
    check_out = date.fromisoformat(booking[4])
    guests = booking[5]
    status = booking[6]
    if status.upper()!="CHECKED_IN":
        print("Guest didn't check in bro..")
        return
    # FEtching guest details
    curr.execute(Queries.select_guest_by_phone, (phone_no,))
    guest_data = curr.fetchone()

    # fteching room details
    curr.execute(Queries.select_room_by_id, (room_no,))
    room_data = curr.fetchone()
    
    if not room_data:
            print("Room details not found0")
            return
    room_type = room_data[1]
    if room_type.capitalize() == "Standard":
        # room_obj = StandardRoom(*room_data)
        r = StandardRoom(room_data[0], room_data[1], room_data[2])
    elif room_type.capitalize() == "Deluxe":
        r = DeluxeRoom(room_data[0], room_data[1], room_data[2])
    else:
        r = SuiteRoom(room_data[0], room_data[1], room_data[2])

    # for loyalty discount
    curr.execute(Queries.completed_stays_query, (phone_no,))
    completed_stays = curr.fetchone()[0]
    # final booking price
    price_details = calculate_price(r, check_in, check_out, guests, completed_stays)

    try:
        curr.execute(Queries.update_booking_status, ("CHECKED_OUT", bid))
        conn.commit()
    except Exception as e:
        print(e)
        return

    generate_invoice(bid, guest_data, r, check_in, check_out, guests, price_details)
    print("Guest checked out successfully")
def cancel_booking():

    booking_id = input("Enter Booking ID: ").strip()

    # FEtch booking
    curr.execute(Queries.select_booking_by_id,(booking_id,))
    booking = curr.fetchone()

    if not booking:
        print("Booking not found!")
        return

    check_in = date.fromisoformat(booking[3])
    status = booking[6]
    price = booking[7]

    # CHeck status
    if status != "CONFIRMED":
        print("Only confirmed bookings can be cancelled.")
        return

    # CAlculate refund
    days_remaining = (check_in - date.today()).days
    if days_remaining >= 7:
        refund = price
    elif days_remaining >= 2:
        refund = price * 0.50
    else:
        refund = 0

    cancellation_amount = price - refund

    # DIsplay details
    print("\nCancellation details:")
    print("Booking ID:", booking_id)
    print("Original amount:", price)
    print("Days before checkin:", days_remaining)
    print("Refund amount:", round(refund, 2))
    print("Amount retained:", round(cancellation_amount, 2))

    choice = input("Confirm cancellation? ").strip().lower()

    if choice != "yes":
        print("Cancellation stoped bro")
        return

    # UPdate database
    try:
        curr.execute(Queries.update_cancellation,
            ("CANCELLED",
            date.today().isoformat(),
            cancellation_amount,
            booking_id))

        conn.commit()

        print("\nBooking cancelled successfully!")
        print("Refund:", round(refund, 2))
        print("Amount retained:", round(cancellation_amount, 2))

    except Exception as e:
        print("Cancellation failed:", e)

def view_booking_details():
    bid = input("ENter booking id: ").strip()
    curr.execute(Queries.select_booking_by_id, (bid,))
    booking = curr.fetchone()
    if not booking:
        print("No such Boking found")
        return
    print("="*10 + "Booking Deatils" + "="*10)
    print("Booking ID:",booking[0])
    print("Guest Phone:",booking[1])
    print("Room Number:",booking[2])
    print("Check-in:",booking[3])
    print("Check-out:",booking[4])
    print("Number of Guests:",booking[5])
    print("Booking Status:",booking[6])
    print("Total Price: ",booking[7])
    print("Cancelled Date: ",booking[8])
    print("Cancellation Amount:",booking[9])

def guest_stay_history():
    phone_no = input("Enter guest mobile number: ").strip()
    existing_guest = get_existing_guest(phone_no)
    if not existing_guest:
        print("Guest not found bro..")
        return
    print("========Guest Details========")
    print("Name:", existing_guest[1])
    print("Phone:", existing_guest[0])
    print("Email:", existing_guest[2])
    curr.execute(Queries.guest_booking_history,(phone_no,))
    bookings=curr.fetchall()
    if not bookings:
        print("No booking found broo")
        return
    print("======Guest Stay History========")
    for booking in bookings:
        print("\nBooking ID:",booking[0])
        print("Room Number:", booking[2])
        print("Check-in:", booking[3])
        print("Check-out:",booking[4])
        print("Guests:",booking[5])
        print("Status:",booking[6])
        print("Price: Rs.", booking[7])

def booking_filter_status():
    status_list = [
    "ALL",
    "CONFIRMED",
    "CHECKED_IN",
    "CHECKED_OUT",
    "CANCELLED"]
    while True:
        status = input("Enter status u wanna filter by(ALL / CONFIRMED / CHECKED_IN / CHECKED_OUT / CANCELLED): ")
        if status.upper() in status_list:
            break
        else:
            print("Invalid status entered brooo...")
    if status.upper()=="ALL":
        curr.execute("Select room from Booking")
        for i in curr.fetchall():
            print(i)
    else:
        curr.execute("Select room from Booking where status =?",(status.upper(),))
        res = curr.fetchall()
        print(res)

def occupancy_report():
    try:
        s_date = input("Enter start date: ").strip()
        format_sdate = datetime.strptime(s_date, "%d-%m-%Y").date()
        e_date = input("Enter end date: ").strip()
        format_edate = datetime.strptime(e_date,"%d-%m-%Y").date()
    except ValueError:
        print("Invalid date format")
        return
    if format_edate <= format_sdate:
        print("End date must be after start date broo")
        return

    curr.execute(Queries.total_rooms_query)
    total_rooms = curr.fetchone()[0]

    if total_rooms==0:
        print("No roms available broo")
        return

    current_date = format_sdate
    occupancy = 0
    nights = 0

    while current_date<format_edate:
        day = current_date.strftime("%Y-%m-%d")
        curr.execute(Queries.occupied_rooms_query, (day, day))

        occupied_rooms = curr.fetchone()[0]
        percentage = (occupied_rooms / total_rooms) * 100
        print("\nDate:", current_date)
        print("Occupied Rooms:", occupied_rooms)
        print("Total Rooms:", total_rooms)
        print("Occupancy:", round(percentage, 2))
        occupancy += percentage
        nights+= 1
        current_date += timedelta(days=1)
       
    average = occupancy/nights
    print("Average Occupancy:", round(average, 2))

def revenue_report():
    curr.execute(Queries.select_query_room)
    records = curr.fetchall()

    curr.execute(Queries.select_query_booking)
    bookings = curr.fetchall()
    room_types = ["Standard", "Deluxe", "Suite"]
    total_stays = 0
    total_revenue = 0
    total_gst = 0
    total_cancellation = 0
    for room_type in room_types:
        completed_stays = 0
        room_revenue = 0
        gst_collected = 0
        cancellation_amount = 0
        for booking in bookings:
            for room in records:
                if room[0]!= booking[2]:
                    continue
                if room[1].lower()!=room_type.lower():
                    break
                if booking[6]=="CHECKED_OUT":
                    completed_stays += 1
                    if room[1] == "Standard":
                        r = StandardRoom(room[0], room[1], room[2])
                    elif room[1] == "Deluxe":
                        r = DeluxeRoom(room[0], room[1], room[2])
                    else:
                        r = SuiteRoom(room[0], room[1], room[2])

                    bill = calculate_price(r,datetime.strptime(booking[3], "%Y-%m-%d").date(),
                                           datetime.strptime(booking[4], "%Y-%m-%d").date(),booking[5],0)
                    gst_collected += bill["gst"]
                    room_revenue += booking[7] - bill["gst"]
                elif booking[6]== "CANCELLED":
                    cancellation_amount += booking[9] or 0
                break
        print("--------------------")
        print("Room Type:", room_type)
        print("Completed Stays:",completed_stays)
        print("Room Revenue:",round(room_revenue,2))
        print("GST Collected:",round(gst_collected,2))
        print("Amount Kept From Cancellations:",round(cancellation_amount,2))
        total_stays += completed_stays
        total_revenue += room_revenue
        total_gst += gst_collected
        total_cancellation += cancellation_amount
    print("==========Total Summaryh==========")
    print("Total Completed Stays:", total_stays)
    print("Total Room Revenue:", round(total_revenue,2))
    print("Total GST Collected:", round(total_gst,2))
    print("Total Cancellation Amount Kept:", round(total_cancellation,2))

def export_bookings():
    curr.execute(Queries.select_query_booking)
    bookings=curr.fetchall()
    if not bookings:
        print("No booking found broo")
        return
    try:
        with open("bookings_export.csv", "w", newline="") as file:
            writer = csv.writer(file)
            for booking in bookings:
                writer.writerow(booking)
            print("Boking exported succesfully")
    except OSError:
        print("Error while writing csv file brooo")