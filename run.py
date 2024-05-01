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
    welcome_message = Fore.GREEN + '\033[1m' + "Wecome to Flight Scanner!".center(40) + '\033[0m'      # 40 columns will be in deployment terminal center
    print(welcome_message)


display_welcome()

a = SHEET.worksheet("jan1").get_all_values()

pprint(a[2][1])

price = a[2][1].split(",")[0]
print(price)

duration = a[2][1].split(",")[1]
print(duration)


