import gspread 
from google.oauth2.service_account import Credentials
from pprint import pprint
from colorama import Fore, Back, Style
from prettytable import PrettyTable

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
SHEET = GSPREAD_CLIENT.open('interaction_matrix')


def display_welcome():
    """
    displays welcome message to the user
    """
    welcome_message = \
        Fore.GREEN + "\033[1m" + "\n" + "********************************".center(40) + \
                                 "\n" + "** Welcome to FLIGHT SCANNER! **".center(40) + \
                                 "\n" + "********************************".center(40) + "\n" + "\033[0m"      # 40 columns will be in deployment terminal center
    print(welcome_message)


# define the cities available in the database
cities = SHEET.worksheet("january1").col_values(1)[1:]
months = ["january", "february", "march"]



def get_city(string):
    """
    fetches user input for the departure and destination questions 
    and validates it through validate_city function
    
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


def reject_same_city():
    """
    rejects user input if destination is same as departure, if so ask for new city input
    """
    print(Fore.RED + "\033[1m" + f"Departure and Destination cities cannot be the same!" + "\n" + "\033[0m")


                


def get_month():
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
                get_entry("cheapest")
                break
            if choice == 1:
                get_entry("fastest")
                break
            if choice == 2:
                get_entry("all")
                break
            else:
                print(Fore.RED + "\033[1m" + "Please insert a number from 0 to 2" + "\033[0m" + "\n")
        except ValueError:
            print(Fore.RED + "\033[1m" + "Please insert a number from 0 to 2" + "\033[0m" + "\n")



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
            prices.append(SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(",")[0])
    
        min_price = prices.index(min(prices))
        table.add_row(SHEET.worksheet(f"{month}{min_price+1}").cell(departure_city_index+2, destination_city_index+2).value.split(","))
        print(table)

    if choice == "fastest":
        print(Fore.BLUE + "\033[1m" + f"Searching fastest flight in {month.capitalize()} .." + "\033[0m" + "\n")
        for i in range(1,sheets_per_month+1):
            durations.append(SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(",")[1])

        min_duration = durations.index(min(durations))
        table.add_row(SHEET.worksheet(f"{month}{min_duration+1}").cell(departure_city_index+2, destination_city_index+2).value.split(","))
        print(table)

    if choice == "all":
        print(Fore.BLUE + "\033[1m" + f"Searching all flights in {month.capitalize()} .." + "\033[0m" + "\n")
        for i in range(1,sheets_per_month+1):
            table.add_row(SHEET.worksheet(f"{month}{i}").cell(departure_city_index+2, destination_city_index+2).value.split(","))
        print(table)

    return table





if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()
    
    # get the indeces of the cities from the user input and validate the input
    departure_city_index = get_city("from")[0]
    destination_city_index = get_city("to")[0]

    # check that the departure is not the same as destination
    while True:
        if departure_city_index == destination_city_index:
            reject_same_city()
            departure_city_index = get_city("from")[0]
            destination_city_index = get_city("to")[0]
        else:
            break

    month = get_month()

    ask_need()

    



