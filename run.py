import gspread
from google.oauth2.service_account import Credentials
from colorama import Fore
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
# format the flight_data worksheet
BOOK_SHEET.worksheet('flight_data').format("A:F",
                                           {"horizontalAlignment": "CENTER"})
# define the cities available in the database
cities = INT_SHEET.worksheet("january1").col_values(1)[1:]
months = ["january", "february", "march"]


def display_welcome():
    """
    displays welcome message to the user
    """
    welcome_message = \
        Fore.GREEN + "\033[1m" + "\n" + ("****************************"
                                         "****").center(40) + \
                                 "\n" + ("** Welcome to FLIGHT"
                                         "SCANNER! **").center(40) + \
                                 "\n" + ("**********************"
                                         "**********").center(40) + \
                                 "\n" + "\033[0m"
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
            Fore.YELLOW + "\033[1m" + f"Where are you travelling {string}?" \
                        + "\n" + "Insert the full city name, first" \
                        + " letters or the number next to the city \n" \
                        + "example: cairo, cai or 2 for Cairo \n" \
                        + "\033[0m"
        print(ask_city)
        # display the cities for the user
        for idx, val in enumerate(cities):
            print(idx, val.capitalize())

        # fetch user input
        city = input(Fore.BLUE + "\033[1m" + f"\nI am travelling {string}"
                               + "\n" + "\033[0m").lower()

        # and validate it
        city_index = validate_data(city, cities)
        if city_index is not None:
            city = cities[city_index]
            print(Fore.GREEN + "\033[1m" + f"\nYou are travelling {string}"
                             + f" {city.capitalize()} \n" + "\033[0m")
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
        idx: integer, index of the data_list where the data input
             by user was found to be true
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
                print(Fore.RED + "\033[1m" + "Please choose a value from 0"
                               + f" to {len(data_list)-1} \n" + "\033[0m")
        except ValueError:
            print(Fore.RED + "\033[1m" + f"Invalid data: {data} is not"
                           + " in the database \n" + "\033[0m")
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
            Fore.YELLOW + "\033[1m" + f"When are you travelling? \n" \
                        + "Insert the full month name, first letters" \
                        + " or the month number \n" \
                        + "example: january, jan or 0 for January \n" \
                        + "\033[0m"
        print(ask_time)

        # display the months for the user
        for idx, val in enumerate(months):
            print(idx, val.capitalize())

        # fetch user input
        month = input(Fore.BLUE + "\n" + "\033[1m"
                                + f"I am travelling in: \n"
                                + "\033[0m").lower()

        # and validate it
        month_index = validate_data(month, months)
        if month_index is not None:
            month = months[month_index]
            print(Fore.GREEN + "\033[1m" + "You are travelling"
                             + f" in {month.capitalize()} \n" + "\033[0m")
            break
    return month


def ask_need():
    """
    asks user whether the terminal shall display fastest,
    cheapest or all flights in the chosen month
    and calls the get_entry function with the chosen option
    """
    while True:
        try:
            choice = int(input(Fore.YELLOW + "\033[1m"
                                           + "\nCheck cheapest trip [0]"
                                           + " or fastest trip [1], or all"
                                           + " trips [2]? \n" + "\033[0m"))
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
                print(Fore.RED + "\033[1m" + "Please insert a number"
                               + " from 0 to 2 \n" + "\033[0m")
        except ValueError:
            print(Fore.RED + "\033[1m" + "Please insert a number"
                           + " from 0 to 2 \n" + "\033[0m")

    return table


def get_entry(choice):
    """
    fetch entry(ies) from the spread sheat based on user input
    of "fastest", "cheapest" or all flights
    parameters:
        choice: string, user choice from "fastest", "cheapest" or "all"
    returns:
        table: prettytable object, flight details
        (price, duration, date, time)
    """
    table = PrettyTable(['Price ($)', 'Duration (min)',
                         'Date', 'Departure time'])
    sheets_per_month = 2

    prices, durations = [], []
    if choice == "cheapest":
        print(Fore.BLUE + "\033[1m" + "Searching cheapest flight"
                                     + f" in {month.capitalize()} .. \n"
                                     + "\033[0m")
        for i in range(1, sheets_per_month+1):
            cell = INT_SHEET.worksheet(f"{month}{i}").cell(
                                       departure_city_index+2,
                                       destination_city_index+2).value
            price = cell.split(",")[0]
            prices.append(price)

        min_price = prices.index(min(prices))
        table.add_row(INT_SHEET.worksheet(f"{month}{min_price+1}").cell(
                      departure_city_index+2,
                      destination_city_index+2).value.split(","))

    if choice == "fastest":
        print(Fore.BLUE + "\033[1m" + "Searching fastest flight"
                                     + f" in {month.capitalize()} ..\n"
                                     + "\033[0m")
        for i in range(1, sheets_per_month+1):
            cell = INT_SHEET.worksheet(f"{month}{i}").cell(
                                       departure_city_index+2,
                                       destination_city_index+2).value
            duration = cell.split(",")[1]
            durations.append(duration)

        min_duration = durations.index(min(durations))
        table.add_row(INT_SHEET.worksheet(f"{month}{min_duration+1}").cell(
                      departure_city_index+2,
                      destination_city_index+2).value.split(","))

    if choice == "all":
        print(Fore.BLUE + "\033[1m" + "Searching all flights in"
                                     + f" {month.capitalize()} ..\n"
                                     + "\033[0m")
        for i in range(1, sheets_per_month+1):
            table.add_row(INT_SHEET.worksheet(f"{month}{i}").cell(
                          departure_city_index+2,
                          destination_city_index+2).value.split(","))

    return table


def validate_name(string):
    """
    checks if user full name has numbers
    parameters:
        string, name
    returns:
        boolean (True or False)
    """
    return any(char.isdigit() for char in string) or \
        any(not c.isalnum() for c in string) or not string


def get_name():
    """
    fetches name from user input and validates it
    by calling validate_name function
    """
    while True:
        name = input(Fore.YELLOW + "\033[1m" + f"Please enter your full name\n"
                                 + "example: Alex Mustermann\n"
                                 + "Please note that if you entered more than"
                                 + " two names, \nonly the first two are"
                                 + " considered\n"
                                 + "\033[0m")

        # split name to first and last names and check that
        # at least two names are input
        first_name = name.split(" ")[0]
        try:
            last_name = name.split(" ")[1]
        except IndexError:
            last_name = first_name
            print(Fore.RED + "\033[1m" + "Please enter your full name as"
                           + " shown in the example\n" + "\033[0m")

        if validate_name(first_name):
            print(Fore.RED + "\033[1m" + "Invalid first name. Please enter"
                           + " your full name as shown in the example\n"
                           + "\033[0m")
        elif validate_name(last_name):
            print(Fore.RED + "\033[1m" + "Invalid last name. Please enter"
                           + " your full name as shown in the example\n"
                           + "\033[0m")
        else:
            name = first_name + " " + last_name
            print(Fore.GREEN + "\033[1m" + "Your name is"
                             + f" {first_name.capitalize()}"
                             + f" {last_name.capitalize()}\n"
                             + "\033[0m")
            break
    return name


def book_flight(table):
    """
    updates the booked_flights spreadsheet
    """
    print(Fore.BLUE + "\033[1m" + f"\nBooking flight ..\n" + "\033[0m")
    worksheet = BOOK_SHEET.worksheet('flight_data')

    while True:
        name = get_name()

        # get the pretty table row
        row = table[0]
        row.border = False
        row.header = False

        # and the table data
        price = row.get_string(fields=["Price ($)"]).strip()
        date = row.get_string(fields=["Date"]).strip()
        time = row.get_string(fields=["Departure time"]).strip()

        # data list
        data = [name, departure_city, destination_city, price, date, time]

        # final data checks with the user
        data_check = print(Fore.YELLOW + "\033[1m"
                                       + "Please check your details before"
                                       + " finalizing the booking\n"
                                       + "\033[0m")

        table.add_column("Name", [name.capitalize()])
        print(table)
        table.del_column("Name")

        is_data_correct = input(Fore.YELLOW + "\033[1m" + "Is data correct?\n"
                                            + "Please enter (yes/Y/y) or"
                                            + "(no/N/n)\n"
                                            + "Any other value is considered"
                                            + " a 'No'\n"
                                            + "\033[0m")

        if is_data_correct == 'y' or is_data_correct == 'Y' \
                or is_data_correct == 'yes':
            # append the data to the flight_data worksheet
            # in the booked_flights spreadsheet
            worksheet.append_row(data)
            print(Fore.GREEN + "\033[1m" + f"Congratulations! Your flight"
                             + " reservation was added to our database\n"
                             + "Our customer service will get back to you"
                             + " shortly to finalize the payment!\n"
                             + "\033[0m")
            break


if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()

    # loop over the whole program if user wants to book additional flights
    while True:

        # check that the departure is not the same as destination
        while True:
            # get the indeces of the cities from the user input
            # and validate the input
            depart_city = get_city("from")
            destin_city = get_city("to")

            if depart_city[0] == destin_city[0]:
                print(Fore.RED + "\033[1m" + f"Departure and Destination"
                               + " cities cannot be the same!\n" + "\033[0m")

            else:
                departure_city_index = depart_city[0]
                departure_city = depart_city[1]
                destination_city_index = destin_city[0]
                destination_city = destin_city[1]
                break

        # ask user what they are looking for
        # (cheapest, fastest or all flights in a certain month)
        month = get_month()
        table = ask_need()
        print(table)

        # check if table has more than 1 row i.e. if more than
        # one flight is displayed, user has to choose one
        while True:
            if len(table.rows) > 1:
                try:
                    flight_choice = int(input(Fore.YELLOW + "\033[1m"
                                        + "\nWhich flight would you"
                                        + " like to book?"
                                        + "\nPlease choose a value from"
                                        + f" 0 to {len(table.rows)-1}"
                                        + "\nFirst flight is 0 and last"
                                        + f" flight is {len(table.rows)-1}\n"
                                        + "\033[0m"))
                    table = table[flight_choice]
                    print(Fore.GREEN + "\033[1m"
                                    + "You chose the following trip\n"
                                    + "\033[0m")
                    print(table)
                    break
                except (ValueError, IndexError) as e:
                    print(Fore.RED + "\033[1m" + "Please insert a number"
                                   + f" from 0 to {len(table.rows)-1}\n"
                                   + "\033[0m")
            else:
                break

        # book flight or exit program
        while True:
            try:
                book_or_exit = int(input(Fore.YELLOW + "\033[1m"
                                   + "\nBook flight [0] or change month [1]"
                                   + " or exit program [2]?\n"
                                   + "\033[0m"))
                if book_or_exit == 0:
                    book_flight(table)
                    break
                if book_or_exit == 1:
                    month = get_month()
                    table = ask_need()
                    print(table)
                if book_or_exit == 2:
                    sys.exit()
                else:
                    print(Fore.RED + "\033[1m"
                                + "Please insert a number from 0 to 2\n"
                                + "\033[0m")                    

            except (ValueError, IndexError) as e:
                print(Fore.RED + "\033[1m"
                               + "Please insert a number from 0 to 2\n"
                               + "\033[0m")

        rerun_program = input(Fore.YELLOW + "\033[1m"
                              + "\nWould you like to book additional flights?"
                              + "\nPlease enter (yes/Y/y) or (no/N/n)"
                              + "\nAny other value is considered a 'No'\n"
                              + "\033[0m")

        if rerun_program != 'y' and rerun_program != 'Y' \
                and rerun_program != 'yes':
            print(Fore.GREEN + "\033[1m" + "Thank you! Have a nice trip!\n"
                             + "\033[0m")
            break
