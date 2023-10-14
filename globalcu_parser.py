import argparse
import csv
import datetime
import decimal
import re

def main() -> None:
    args = parse_args()

    csv_data = read_csv(args.file)

    account_entries = csv_data_to_entries(csv_data)

    if args.category:
        display_category(account_entries, args.category)
    else:
        display_summary(account_entries)

        display_categories(account_entries)

        display_unknown_entries(account_entries)


def parse_args():
    parser = argparse.ArgumentParser(
                        prog='python3 globalcu_parser.py',
                        description='''Parses a CSV file of account history from GlobalCU. 
                        Displays a summary of money in, money out. Breaks down
                        expenses by category.''')

    parser.add_argument('file', help="The bank account statement file to process")

    parser.add_argument('-c', '--category', help="Display transactions for specific category") 

    return parser.parse_args()


def read_csv(file) -> list:
    csvfile = open(file)

    data = list(csv.reader(csvfile))

    csvfile.close()
    
    return data


def csv_data_to_entries(csv_data: list) -> list:
    entries = []
    for row in csv_data:
        entry = AccountEntry(row)
        if not entry.is_empty_entry:
            entries.append(entry)
    entries.reverse()
    return entries


class AccountEntry:
    def __init__(self, csv_entry: list) -> None:
        self.parse(csv_entry)
        self.set_matchers()
        self.set_category_type()

    def parse(self, csv_entry: list) -> None:
        if len(csv_entry) != 0:
            self.date = datetime.datetime.strptime(csv_entry[0], "%m/%d/%Y")
            self.description = csv_entry[1]
            self.amount = decimal.Decimal(csv_entry[3])
            if self.amount < 0:
                self.balance_type = "withdrawal"
            else:
                self.balance_type = "deposit"
            self.is_empty_entry = False
        else:
            self.is_empty_entry = True

    def set_matchers(self) -> None:
        self.matchers = [
            { "category": "Groceries", "regex": re.compile(r"COSTCO|SAFEWAY|TARGET|(BROWN JUG)|(WALGREENS)|(ALASKA MILL FEED)|(JOHNNY'S PRODUCE)|(SCHNUCKS)|( CARRS )|(FRED-MEYER)|( FRED MEY )|(NEW SAGAYA)", re.IGNORECASE)},
            { "category": "Income", "regex": re.compile(r"GCI COMMUNICATIO TYPE: DIRECT DEP CO: GCI COMMUNICATIO DATA", re.IGNORECASE)},
            { "category": "Eating Out", "regex": re.compile(r"(MCDONALD)|(FIRE ISLAND)|(DOMINO'S)|(49TH STATE 'CONE-X')|(KRISPY KREME)|(THE BAKE SHOP)|(HOUSE OF BREAD)|(EL JEFE TACO JOINT)|(EL GREEN GO)|(Sushi Ai)|(EL CATRIN)|(GREAT HARVEST BREAD)|(JOURNEY CAFE KAILUA KONA)|(SCOTTISH ARMS)|(KONA BREWING HAWAII)|(SNOW CITY CAFE)|(DISH 3 SEA)|(SPENARD ROADHOUSE)|(FRESH CUP COFFEE)|(YAK & YETI CAFE)|(RAY'S PLACE)|(DENALI PRETZELS)|(Square One Brewery)|(NAMASTE SHANGRI-LA)|(HUDSON ST)|(ROCKWELL BEER COMPANY)|(THE WINE & CHEESE PLAC)|(LA BODEGA)|(BEAR TOOTH)|(MOOSES TOOTH)|KALADI|STARBUCKS|EUROCAFE|PIKE&PINE|HUDSONNEWS|(RECKLESS N)|(MIDNIGHT MOON)|(THE PURPLE MOOSE ESPRESS)|(WILD SCOOPS)", re.IGNORECASE)},
            { "category": "Car Insurance", "regex": re.compile(r"STATE FARM|GEICO", re.IGNORECASE)},
            { "category": "Rent/Mortgage/HOA", "regex": re.compile(r"(Real Estate Solu)|(NEWREZ-SHELLPOIN)|(ROY BRILEY HOA)", re.IGNORECASE)},
            { "category": "Home Goods/Renovation/Maintenance", "regex": re.compile(r"(APPLIANCE PARTS COMPANY)|(VENT DOCTORS OF ALASK)|(ANDYS ACE HDWE)|LOWE'S", re.IGNORECASE)},
            { "category": "Paypal", "regex": re.compile(r"PAYPAL", re.IGNORECASE)},
            { "category": "Global CU Acc Transfer", "regex": re.compile(r"ULTRABRANCH-PC TRANSFER", re.IGNORECASE)},
            { "category": "Bank of America CC Debt", "regex": re.compile(r"BK OF AMER", re.IGNORECASE)},
            { "category": "VISA CC Debt", "regex": re.compile(r"VISA TYPE: PAYMENT CO", re.IGNORECASE)},
            { "category": "Amazon Subscriptions", "regex": re.compile(r"(Amazon Prime)|(AMZN Mktp)|(Prime Video)", re.IGNORECASE)},
            { "category": "Amazon Purchases", "regex": re.compile(r"(Amazon.com)", re.IGNORECASE)},
            { "category": "Utilities", "regex": re.compile(r"(GCI BILLING)|(CHUGACH ELECTRIC)|(CHUGACHELECTRIC)|ENSTAR", re.IGNORECASE)},
            { "category": "Gas/Parking", "regex": re.compile(r"(MCKINLEY PARKING)|(FRED M FUEL)|(HOLIDAY STATIONS)|(SPEEDWAY)|(CHEVRON)", re.IGNORECASE)},
            { "category": "Car Maintenance", "regex": re.compile(r"(CONTINENTAL SUBARU)", re.IGNORECASE)},
            { "category": "Personal", "regex": re.compile(r"Kindle|(EVE ONLINE)|(NORTHERN KNIVES)|(BARNESNOBLE)|(BEST BUY)|BOSCO`S|(FIRST LIGHT BOOKSTORE HONOLULU)|(BESTBUY)|(DIVE ALASKA)|(Nintendo)|(ALASKA ROCK GYM)|( REI )|(AK PARKS PAY STATIONS)|(ST LOUIS ZOO)|(Classic Toys)", re.IGNORECASE)},
            { "category": "Legal", "regex": re.compile(r"ALASKAVITALREC|ROCKETLAW", re.IGNORECASE)},
            { "category": "Pets", "regex": re.compile(r"(VCA ANIMAL HOSP)|PETSMART|PRETTYLITTER|PETCO", re.IGNORECASE)},
            { "category": "Travel", "regex": re.compile(r"(ST. LOUIS ART MUSEUM)|(HAWAII TROPICAL BOTANICAL)|(ANC AIRPORT PARKING)|(ANELAKAI ADVENTURE)|(ALASKA AIR)", re.IGNORECASE)},
            { "category": "Car Payment Debt", "regex": re.compile(r"(TD AUTO FINANCE)", re.IGNORECASE)},
            { "category": "IRS", "regex": re.compile(r"(IRS TREAS)", re.IGNORECASE)},
            { "category": "Baby Stuff", "regex": re.compile(r"BABYBJORN|GROVIA", re.IGNORECASE)},
            { "category": "Student Loans", "regex": re.compile(r"STUDNTLOAN|(STUDENT LN)", re.IGNORECASE)},
        ]

    def set_category_type(self) -> None:
        if not self.is_empty_entry:
            for matcher in self.matchers:
                if matcher["regex"].search(self.description) != None:
                    self.category = matcher["category"]
                    return
            
            self.category = "Unknown"


def display_summary(account_entries: list) -> None:
    delta = 0
    withdrawals = 0
    desposits = 0

    for entry in account_entries:
        delta += entry.amount
        if entry.amount < 0:
            withdrawals += entry.amount
        else:
            desposits += entry.amount

    print("----------SUMMARY----------")
    print("Account period start:".ljust(30), account_entries[0].date.strftime("%m/%d/%Y"))
    print("Account period end:".ljust(30), account_entries[len(account_entries) - 1].date.strftime("%m/%d/%Y"))
    print("Balance over account period:".ljust(30), delta)
    print("Total withdrawals:".ljust(30), withdrawals)
    print("Total deposits:".ljust(30), desposits)
    print()


def display_categories(account_entries: list) -> None:
    amounts_by_categories = {}

    for entry in account_entries:
        if entry.category in amounts_by_categories:
            amounts_by_categories[entry.category] += entry.amount
        else:
            amounts_by_categories[entry.category] = entry.amount

    print("----------CATEGORIES----------")

    for category in dict(sorted(amounts_by_categories.items())):
        print((category + ":").ljust(40) + str(amounts_by_categories[category]))

    print()


def display_unknown_entries(account_entries: list) -> None:
    print("----------UNKNOWN ENTRIES----------")
    for entry in account_entries:
        if entry.category == "Unknown":
            print("Date:".ljust(8), entry.date.strftime("%m/%d/%Y"), "Description:".ljust(14), entry.description.ljust(144), "Amount:".ljust(10), entry.amount)
            

def display_category(account_entries: list, category: str) -> None:

    print("----------CATEGORY {} ENTRIES----------".format(category))

    for entry in account_entries:
        if entry.category.lower() == category.lower():
            print("Date:".ljust(8), entry.date.strftime("%m/%d/%Y"), "Description:".ljust(14), entry.description.ljust(144), "Amount:".ljust(10), entry.amount)


if __name__ == '__main__':
    main()

