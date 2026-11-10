# Go to menu
# create all the tables - 

initialise database() - validate romm cdata and store in room 
- create guest - insert values
- create booking - insert booking values 

# next test cases for check availability

# in booking 
1. collect guest details - name mobile , email, no of guests

2. validate all of them

3. collect stay details - room type , check in , check out

4. validate all of them

5. check room availability - function

6. allocate a room

7. calculate booking price
if 4 guests are there then , and its for standard - and available rooms are 3 , then for each room separate booking like guest 1 info should not be used for all of them , or is it fine for my low level projects ??? us ethe same guest info to all the rooms he gets allocated ??

8. display booking summary
9. confirm payment
20. save booking to push booking database
11. display booking confirmtion msg - booking id 



#### available rooms = check_availabilty 

if available ----- use them 
else find for alternative_rooms

now i have list of rooms or no rooms

1. list of rooms

required ko check karna haii , like 5 guests will have 2,2,1

create guest object

loop through allocated rooms
 and create room objesct
 calculate room price 
 create booking obj
 display booking summary
 ask for user confirmation
 yes - push to database
 no - cancel operation
 