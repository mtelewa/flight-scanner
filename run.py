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

def get_city(string):
    """
    fetches user input for the departure and destination questions 
    and validates it through validate_city function
    
    parameters: string with either "from" or "to"
    """
    while True:
        ask_departure = \
            Fore.YELLOW + "\033[1m" + f"Where are you travelling {string}?" + \
                                      "\n" + "Insert the full city name, first three letters or the number next to the city" + \
                                      "\n" + "example: cairo, cai or 2 for Cairo \n" + "\033[0m"
        print(ask_departure)
        
        # display the cities for the user
        for idx, val in enumerate(cities):
            print(idx, val.capitalize())

        # fetch user input
        city = input(Fore.BLUE + "\n" + "\033[1m" + f"I am travelling {string}: \n" + "\033[0m")

        # and validate it
        city_index = validate_city(city)
        if city_index is not None:
            city = cities[city_index]
            print(Fore.BLUE + "\033[1m" + f"You are travelling {string} {city.capitalize()}" + "\033[0m" + "\n")
            break


    return city



def validate_city(city):
    """
    checks that city is in the database either the full city name
    or the first three letters or the number
    """
    if city in cities:
        idx = cities.index(city)
        return idx
    elif any(item.startswith(city) for item in cities):
        for idx, val in enumerate(cities):
            if val.startswith(city):
                return idx
                break
    else:
        try:
            idx = int(city)
            if idx < len(cities):
                return idx
            else: 
                print(Fore.RED + "\033[1m" + 'Please choose a value from 0 to 5 \n' + "\033[0m")
        except ValueError:
            print(Fore.RED + "\033[1m" + f"Invalid city: {city} is not a city in the database \n" + "\033[0m")
            idx = None









if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()
    departure_city = get_city("from")
    destination_city = get_city("to")



# a = SHEET.worksheet("jan1").get_all_values()

# pprint(a[2][1])

# price = a[2][1].split(",")[0]
# print(price)

# duration = a[2][1].split(",")[1]
# print(duration)


