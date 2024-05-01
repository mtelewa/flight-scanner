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

def get_departure_city():
    while True:
        print(Fore.YELLOW + "\033[1m" + "Where are you travelling from?" + "\033[0m")
        print("Insert the full city name, first three letters or the number next to the city")
        print("example: cairo, cai or 2 for Cairo \n")
        for idx, val in enumerate(cities):
            print(idx, val)
        departure_city = input(Fore.BLUE + "\n" + "\033[1m" + "I am travelling from: \n" + "\033[0m")


        if validate_city(departure_city):
            city_chosen = cities[validate_city(departure_city)]
            print(f"You chose {upper(city_chosen)}")
            break


def validate_city(city):
    """
    checks that city is in the database either the full city name
    or the first three letters or the number
    """
    if city in cities:
        idx = cities.index(city)
        return idx
    elif any(item.startswith(city) for item in cities):
        print('ne')
    else:
        try:
            idx = int(city)
            return idx
        except ValueError:
            print('Invalid city: city is not in database \n')
            return False

    # else:
    #     raise ValueError('Invalid city: city is not in database \n')
    #     return False


if __name__ == '__main__':
    """
    Run all program functions
    """
    display_welcome()
    get_departure_city()



# a = SHEET.worksheet("jan1").get_all_values()

# pprint(a[2][1])

# price = a[2][1].split(",")[0]
# print(price)

# duration = a[2][1].split(",")[1]
# print(duration)


