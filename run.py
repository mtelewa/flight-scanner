import gspread 
from google.oauth2.service_account import Credentials
from pprint import pprint
from colorama import Fore, Back, Style
from prettytable import PrettyTable
import sys

# set scope (lists apis that the program shall access in order to run)
# It is a constant (that's why capital letters)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
# Interaction matrix spreadsheet
INT_SHEET = GSPREAD_CLIENT.open('interaction_matrix')
# Booked flights spreadsheet
BOOK_SHEET = GSPREAD_CLIENT.open('booked_flights')
# define the cities available in the database
cities = INT_SHEET.worksheet("january1").col_values(1)[1:]
months = ["january", "february", "march"]



def display_welcome():
    """
    displays welcome message to the user
    """
    welcome_message = \
        Fore.GREEN + "\033[1m" + "\n" + "********************************".center(40) + \
                                 "\n" + "** Welcome to FLIGHT SCANNER! **".center(40) + \
                                 "\n" + "********************************".center(40) + "\n" + "\033[0m"      # 40 columns will be in deployment terminal center
    print(welcome_message)



def get_city(string):
    """
    fetches user input for the departure and destination questions 
    and validates it through the validate_data function
    
    parameters: string, either "from" or "to"
    returns: int (city_index) and string (city)
    """
    while True:
        ask_city = \
            Fore.YELLOW + "\033[1m" + f"Where are you travelling {string}?" + \
                                      "\n" + "Insert the full city name, first three letters or the number next to the city" + \
                                      "\n" + "example: cairo, cai or 2 for Cairo \n" + "\033[0m"
        print(ask_city)
        
        # display the cities for the user
        for idx, val in enumerate(cities):
            print(idx, val.capitalize())

        # fetch user input
        city = input(Fore.BLUE + "\n" + "\033[1m" + f"I am travelling {string}: \n" + "\033[0m")

        # and validate it
        city_index = validate_data(city, cities)
        if city_index is not None:
            city = cities[city_index]
            print(Fore.BLUE + "\033[1m" + f"You are travelling {string} {city.capitalize()}" + "\033[0m" + "\n")
            break

    return city_index, city



def validate_data(data, data_list):
    """
    checks that data is in the database either the full city name
    or the first three letters or the number

    parameters: 
        data: string, input by the user
        data_list: list, the database entries available
    
    returns:
        idx: integer, index of the data_list where the data input by user was found to be true
    """
    # check if full city name is in database
    if data in data_list:
        idx = data_list.index(data)
        return idx
    elif any(item.startswith(data) for item in data_list):
        for idx, val in enumerate(data_list):
            # check if the substring exists and that the substring is not empty
            if val.startswith(data) and data != "":
                return idx
                break
    else:
        try:
            idx = int(data)
            if idx < len(data_list):
                return idx
            else: 
                print(Fore.RED + "\033[1m" + f"Please choose a value from 0 to {len(data_list)-1} \n" + "\033[0m")
        except ValueError:
            print(Fore.RED + "\033[1m" + f"Invalid data: {data} is not in the database \n" + "\033[0m")
            idx = None


def get_month():
    """
    fetches user input for the month to travel 
    and validates it through the validate_data function
    
    parameters: string, either "from" or "to"
    returns: int (city_index) and string (city)
    """
    while True:
        ask_time = \
            Fore.YELLOW + "\033[1m" + f"When are you travelling?" + \
                                        "\n" + "Insert the full month name, first three letters or the month number" + \
                                        "\n" + "example: january, jan or 0 for January \n" + "\033[0m"
        print(ask_time)

        # display the months for the user
        for idx, val in enumerate(months):
            print(idx, val.capitalize())

        # fetch user input
        month = input(Fore.BLUE + "\n" + "\033[1m" + f"I am travelling in: \n" + "\033[0m")

        # and validate it
        month_index = validate_data(month, months)
        if month_index is not None:
            month = months[month_index]
            print(Fore.BLUE + "\033[1m" + f"You are travelling in {month.capitalize()}" + "\033[0m" + "\n")
            break
    
    return month


def ask_need():
    """
    asks user whether the terminal shall display fastest, cheapest or all flights in the chosen month
    and calls the get_entry function with the chosen option
    """
    while True:
        try:
            choice = int(input(Fore.YELLOW + "\n" + "\033[1m" + f"Check cheapest trip [0] or fastest trip [1], or all trips [2]? \n" + "\033[0m"))
            if choice == 0:
                table = get_entry("cheapest")
                break
            if choice == 1:
                table = get_entry("fastest")
                break
            if choice == 2:
                table = get_entry("all")
                break
            else:
                print(Fore.RED + "\033[1m" + "Please insert a number from 0 to 2" + "\033[0m" + "\n")
        except ValueError:
            print(Fore.RED + "\033[1m" + "Please insert a number from 0 to 2" + "\033[0m" + "\n")

    return table


def get_entry(choice):
    """
    fetch entry(ies) from the spread sheat based on user input of "fastest", "cheapest" or all flights
    
    parameters: 
        choice: string, user choice from "fastest", "cheapest" or "all"

    returns:
        table: prettytable object, flight details (price, duration, date, time)
    """
    table = PrettyTable(['Price ($)', 'Duration (min)', 'Date', 'Departure time'])
    sheets_per_month = 2

    prices, durations = [], []
    if choice == "cheapest":
        print(Fore.BLUE + "\033[1m" + f"Searching cheapest flight in {month.capitalize()} .." + "\033[0m" + "\n")
        for i in range(1,sheets_per_month+1):
            prices.append(INT_SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(",")[0])
    
        min_price = prices.index(min(prices))
        table.add_row(INT_SHEET.worksheet(f"{month}{min_price+1}").cell(departure_city_index+2, destination_city_index+2).value.split(","))
        
    if choice == "fastest":
        print(Fore.BLUE + "\033[1m" + f"Searching fastest flight in {month.capitalize()} .." + "\033[0m" + "\n")
        for i in range(1,sheets_per_month+1):
            durations.append(INT_SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(",")[1])

        min_duration = durations.index(min(durations))
        table.add_row(INT_SHEET.worksheet(f"{month}{min_duration+1}").cell(departure_city_index+2, destination_city_index+2).value.split(","))

    if choice == "all":
        print(Fore.BLUE + "\033[1m" + f"Searching all flights in {month.capitalize()} .." + "\033[0m" + "\n")
        for i in range(1,sheets_per_month+1):
            table.add_row(INT_SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(","))

    return table


def validate_name(string):
    """
    checks if user full name has numbers
    source: https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
    """
    return any(char.isdigit() for char in inputString)


def get_name():
    """
    fetches name from user input and validates it by calling validate_name function
    """
    while True:
        name = input(Fore.YELLOW + "\033[1m" + f"Please enter your full name" + \
                                    "\n" + "example: Alex Mustermann" +
                                    "\n" + "please note that if you entered more than two names," 
                                    "\n" + "only the first two are considered" + "\033[0m" + "\n")

        # split name to first and last names and check that at least two names are input
        first_name = name.split(" ")[0]
        try:
            last_name = name.split(" ")[1]
        except IndexError:
            print(Fore.RED + "\033[1m" + "Please enter your full name as shown in the example" + "\033[0m" + "\n")

        if validate_name(first_name):
            print(Fore.RED + "\033[1m" + "Invalid first name. Please enter your full name as shown in the example" + "\033[0m" + "\n")
        elif validate_name(last_name):
            print(Fore.RED + "\033[1m" +  "Invalid last name. Please enter your full name as shown in the example" + "\033[0m" + "\n")
        else:
            name = first_name + " " + last_name
            print(Fore.BLUE + "\033[1m" + f"Your name is {first_name} {last_name}" + "\033[0m" + "\n")
            break
    
    return name


def book_flight():
    """
    updates the booked_flights spreadsheet
    """

    print(Fore.YELLOW + "\033[1m" + f"Booking flight .." + "\033[0m" + "\n")
    worksheet = BOOK_SHEET.worksheet('flight_data')
    
    name = get_name()

    data = [name, depa]
    worksheet.append_row(data)
        




if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()
    
    # get the indeces of the cities from the user input and validate the input
    depart_city = get_city("from")
    destin_city = get_city("to")
    departure_city_index, departure_city = depart_city[0], depart_city[1]
    destination_city_index, destination_city = destin_city[0], destin_city[1]

    # check that the departure is not the same as destination
    while True:
        if departure_city_index == destination_city_index:
            print(Fore.RED + "\033[1m" + f"Departure and Destination cities cannot be the same!" + "\n" + "\033[0m")
            depart_city = get_city("from")
            destin_city = get_city("to")
            departure_city_index, departure_city = depart_city[0], depart_city[1]
            destination_city_index, destination_city = destin_city[0], destin_city[1]
        else:
            break

    # ask user what they are looking for (cheapest, fastest or all flights in a certain month)
    month = get_month()
    table = ask_need()
    print(table)

    while True:
        try:
            proceed = int(input(Fore.YELLOW + "\n" + "\033[1m" + f"Book flight [0] or change month [1] or exit program [2]? \n" + "\033[0m"))
            if proceed == 0:
                book_flight()
                break
            if proceed == 1:
                month = get_month()
                table = ask_need()
                print(table)
            if proceed == 2:
                sys.exit()

        except ValueError:
            print(Fore.RED + "\033[1m" + "Please insert a number from 0 to 2" + "\033[0m" + "\n")


    



