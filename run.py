import gspread 
from google.oauth2.service_account import Credentials
from pprint import pprint
from colorama import Fore, Back, Style

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
cities = SHEET.worksheet("jan1").col_values(1)[1:]
months = ["january", "february", "march"]



def get_city(string):
    """
    fetches user input for the departure and destination questions 
    and validates it through validate_city function
    
    parameters: string, either "from" or "to"
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

    return city



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
    if data in data_list:
        idx = data_list.index(data)
        return idx
    elif any(item.startswith(data) for item in data_list):
        for idx, val in enumerate(data_list):
            if val.startswith(data):
                return idx
                break
    else:
        try:
            idx = int(data)
            if idx < len(data_list):
                return idx
            else: 
                print(Fore.RED + "\033[1m" + f"Please choose a value from 0 to {len(data_list)} \n" + "\033[0m")
        except ValueError:
            print(Fore.RED + "\033[1m" + f"Invalid data: {data} is not in the database \n" + "\033[0m")
            idx = None


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







if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()
    departure_city = get_city("from")
    destination_city = get_city("to")
    month = get_month()



# a = SHEET.worksheet("jan1").get_all_values()

# pprint(a[2][1])

# price = a[2][1].split(",")[0]
# print(price)

# duration = a[2][1].split(",")[1]
# print(duration)


