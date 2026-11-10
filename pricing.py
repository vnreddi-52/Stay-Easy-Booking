from datetime import timedelta

def gst(nightly_breakdown):
    total_gst = 0
    for night in nightly_breakdown:
        tariff = night["room_tariff"]
        extra_guest_charge = night["extra_guest_charge"]
        tax_amt = tariff+extra_guest_charge
        if tariff <= 7500:
            rate = 0.12
        # only in case of suite on fri sat , room tarruff 9k, 
        else:
            rate = 0.18
        gst = tax_amt*rate
        night["gst_rate"] = rate
        night["gst"] = gst
        total_gst += gst

    return total_gst

def calculate_price(room, check_in, check_out, guests, completed_stays,include_breakfast=False):
    nights = (check_out - check_in).days
    room_charges=0
    extra_charges=0
    breakfast_charges=0
    nightly_breakdown=[]
    current_date = check_in

    # loop from start date to end date last day of stay bro
    while current_date < check_out:
        # from upper methods
        tariff = room.tariff(current_date)
        extra_charge = room.extra_guest(guests)
        breakfast_charge = room.breakfast(guests, include_breakfast)

        room_charges+=tariff
        extra_charges+=extra_charge
        breakfast_charges+=breakfast_charge

        nightly_breakdown.append({
            "date": current_date,
            "room_tariff": tariff,
            "extra_guest_charge": extra_charge,
            "breakfast_charge": breakfast_charge})

        current_date += timedelta(days=1)
    # seven days
    if 7<=nights<=9:
        stay_discount=room_charges * 0.10
    elif 10<=nights<=14:
        stay_discount=room_charges * 0.15
    elif nights>=15:
        stay_discount=room_charges * 0.2
    elif nights<7:
        stay_discount=0

    # loyalty discount
    if completed_stays >= 3:
        loyalty_discount=room_charges*0.05
    else:
        loyalty_discount=0
    
    discounted_room_charges = room_charges - stay_discount - loyalty_discount
    
    # now apply gst
    gst_total = gst(nightly_breakdown)
    total = (discounted_room_charges + extra_charges + breakfast_charges+ gst_total)

    return {
        "nights": nights,
        "room_charges": round(room_charges, 2),
        "extra_charges": round(extra_charges, 2),
        "breakfast_charges": round(breakfast_charges, 2),
        "stay_discount": round(stay_discount, 2),
        "loyalty_discount": round(loyalty_discount, 2),
        "gst": round(gst_total, 2),
        "total": round(total, 2),
        "nightly_breakdown": nightly_breakdown
    }

def full_payment(total):
    print(f"Full payment due: Rs {total:.2f}")
    choice = input("Confirm booking and payment?(yes or no) ").strip().lower()
    return choice == "yes"