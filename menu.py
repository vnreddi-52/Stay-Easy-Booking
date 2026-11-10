
from main import (check_availability, initialise_databases,
                   display_tables, alternative_rooms,create_booking, get_check_availability,
                   check_in_booking, check_out_booking, cancel_booking, view_booking_details,
                   guest_stay_history, occupancy_report, revenue_report, export_bookings, booking_filter_status)
from validations import get_check_availability

def display_list(list_type):
    if not list_type:
        print("No values to return")
        return []
    else:
        for i in list_type:
            print(i)

def menu():
    initialise_databases()
    display_tables()

    while True:
        print("""
              1. Search room availability
              2. Create Booking
              3. Check in
              4. CHeck out
              5. Cancel Booking
              6. View booking details
              7. Guest stay history 
              8. Occupancy report
              9. Revenue report
              10. Export all bookings to CSV
              11. Exit 

              12: booking_filter_status
            """)
        choice = int(input("Enter your choice: "))
        match choice:
            case 1:
                room_type, check_in, check_out, no_of_guests = get_check_availability()
                # curr.execute("SELECT * FROM ROOM WHERE room_type = 'Standard'")
                data = check_availability(room_type, check_in, check_out, no_of_guests)
                if data:
                    print(f"Available {room_type} Rooms is: {data}")
                else:
                    print("No rooms avaliable of your type")
                    data2 = alternative_rooms(room_type, check_in, check_out, no_of_guests)
                    if data2:
                        print("Other room types are")
                        for r_type, rooms in data2.items():
                            print(f"{r_type}: {rooms}")
                    else:
                        print("Sorry bro no rooms available at all")
            case 2:
                create_booking()
            case 3:
                check_in_booking()
            case 4:
                check_out_booking()
            case 5:
                cancel_booking()
            case 6:
                view_booking_details()
            case 7:
                guest_stay_history()
            case 8:
                occupancy_report()
            case 9:
                revenue_report()
            case 10:
                export_bookings()
            case 11:
                print("Exiting")
                return
            case 12:
                booking_filter_status()


menu()