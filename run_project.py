import csv
import os
import random
import sys

# always work from the folder where this file is saved
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

# ------------------------------------------------------------
#  SOURCE CODE OF THE MODULES (stored as text)
# ------------------------------------------------------------
MODULE_HELPERS = r'''# helpers.py  (Module 1)
# Small helper functions used by the other files.

def print_line():
    print("-" * 60)


def print_heading(text):
    print()
    print("=" * 60)
    print(text.center(60))
    print("=" * 60)


def get_text(message):
    # keep asking until the user types something
    while True:
        value = input(message).strip()
        if value != "":
            return value
        print("Please type something.")


def get_number(message):
    # keep asking until the user types a valid whole number
    while True:
        value = input(message).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a valid number.")


def get_choice(message, allowed_options):
    # allowed_options is a tuple like ("North", "South")
    while True:
        value = input(message).strip().lower()
        for option in allowed_options:
            if value == option.lower():
                return option
        print("Choose one of:", ", ".join(allowed_options))
'''

MODULE_DATA_HANDLER = r'''# data_handler.py  (Module 2)
# Reads / writes the CSV file and does Add, Display, Search, Update, Delete.
#
# Python data structures used here:
#   1. List        -> all records are stored in a list
#   2. Dictionary  -> every record is a dictionary
#   3. Tuple       -> REGIONS, CATEGORIES (fixed values that never change)
#   4. Set         -> unique customers / regions
#   5. List and dictionary methods -> append, remove, sort, get, keys, items

import csv
from helpers import print_line, get_text, get_number, get_choice

DATA_FILE = "01_data/raw/sales_data.csv"

# tuples (cannot be changed)
REGIONS = ("North", "South", "East", "West")
CATEGORIES = ("Electronics", "Furniture", "Stationery")
PAYMENTS = ("Card", "UPI", "Cash", "NetBanking")


# ---------------- File handling ----------------
def load_data(filename=DATA_FILE):
    # read the CSV file and return a list of dictionaries
    records = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(row)          # list method: append
    return records


def save_data(records, filename=DATA_FILE):
    # write the list of dictionaries back to the CSV file
    columns = list(records[0].keys())
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


# ---------------- Operations ----------------
def show_record(record):
    # print one record nicely
    for key, value in record.items():    # dictionary method: items
        print(key.ljust(16), ":", value)
    print_line()


def display_all(records):
    print("Order  Date        Customer   Region  Product       Qty  Total")
    print_line()
    for r in records:
        print(r["order_id"].ljust(6), r["order_date"].ljust(11), r["customer_name"].ljust(10),
              r["region"].ljust(7), r["product"].ljust(13), r["quantity"].ljust(4), r["total_amount"])
    print_line()
    print("Total records:", len(records))


def add_record(records):
    # new id = last id + 1
    last_id = int(records[-1]["order_id"])
    new_record = {}
    new_record["order_id"] = str(last_id + 1)
    new_record["order_date"] = get_text("Order date (YYYY-MM-DD): ")
    new_record["customer_name"] = get_text("Customer name: ").title()
    new_record["region"] = get_choice("Region " + str(REGIONS) + ": ", REGIONS)
    new_record["product"] = get_text("Product name: ").title()
    new_record["category"] = get_choice("Category " + str(CATEGORIES) + ": ", CATEGORIES)
    quantity = get_number("Quantity: ")
    price = get_number("Unit price: ")
    new_record["quantity"] = str(quantity)
    new_record["unit_price"] = str(price)
    new_record["total_amount"] = str(quantity * price)
    new_record["payment_method"] = get_choice("Payment " + str(PAYMENTS) + ": ", PAYMENTS)
    new_record["rating"] = str(get_number("Rating (1-5): "))

    records.append(new_record)
    save_data(records)
    print("Record added! New order id =", new_record["order_id"])


def find_by_id(records, order_id):
    # return the record with this id, or None if not found
    for r in records:
        if r["order_id"] == str(order_id):
            return r
    return None


def search_record(records):
    order_id = get_number("Enter order id to search: ")
    record = find_by_id(records, order_id)
    if record is None:
        print("No record found with id", order_id)
    else:
        print_line()
        show_record(record)


def update_record(records):
    order_id = get_number("Enter order id to update: ")
    record = find_by_id(records, order_id)
    if record is None:
        print("No record found with id", order_id)
        return
    show_record(record)
    print("1. Quantity   2. Region   3. Payment method   4. Rating")
    choice = get_number("What do you want to update? ")

    if choice == 1:
        record["quantity"] = str(get_number("New quantity: "))
        # total must change too
        record["total_amount"] = str(int(record["quantity"]) * int(record["unit_price"]))
    elif choice == 2:
        record["region"] = get_choice("New region " + str(REGIONS) + ": ", REGIONS)
    elif choice == 3:
        record["payment_method"] = get_choice("New payment " + str(PAYMENTS) + ": ", PAYMENTS)
    elif choice == 4:
        record["rating"] = str(get_number("New rating (1-5): "))
    else:
        print("Invalid choice.")
        return

    save_data(records)
    print("Record updated!")


def delete_record(records):
    order_id = get_number("Enter order id to delete: ")
    record = find_by_id(records, order_id)
    if record is None:
        print("No record found with id", order_id)
        return
    show_record(record)
    sure = input("Are you sure? (yes/no): ").strip().lower()
    if sure == "yes":
        records.remove(record)           # list method: remove
        save_data(records)
        print("Record deleted.")
    else:
        print("Delete cancelled.")


def summary_report(records):
    # uses a set, a dictionary and list methods
    unique_customers = set()
    unique_regions = set()
    sales_by_region = {}                 # dictionary
    total_sales = 0

    for r in records:
        unique_customers.add(r["customer_name"])
        unique_regions.add(r["region"])
        amount = int(r["total_amount"])
        total_sales = total_sales + amount
        region = r["region"]
        sales_by_region[region] = sales_by_region.get(region, 0) + amount   # dict method: get

    all_totals = []
    for r in records:
        all_totals.append(int(r["total_amount"]))
    all_totals.sort(reverse=True)        # list method: sort

    print_line()
    print("Total records       :", len(records))
    print("Unique customers    :", len(unique_customers))
    print("Regions             :", sorted(unique_regions))
    print("Total sales         : Rs.", total_sales)
    print("Biggest order       : Rs.", all_totals[0])
    print("Smallest order      : Rs.", all_totals[-1])
    print("Top 3 orders        :", all_totals[:3])
    print_line()
    print("Sales by region:")
    for region, amount in sales_by_region.items():
        print("  ", region.ljust(6), "Rs.", amount)
    print_line()
'''

MODULE_ANALYSIS = r'''# analysis.py  (Module 3)
# NumPy and Pandas analysis of the sales dataset.

import numpy as np
import pandas as pd
from helpers import print_line, print_heading

DATA_FILE = "01_data/raw/sales_data.csv"
CLEAN_FILE = "01_data/processed/sales_clean.csv"


# ---------------- NumPy ----------------
def numpy_demo():
    print_heading("NUMPY DEMO")

    # 1D array
    df = pd.read_csv(DATA_FILE)
    amounts = np.array(df["total_amount"])
    print("1D array (first 10 totals):", amounts[:10])

    # 2D array (quantity, unit_price, total)
    table = np.array(df[["quantity", "unit_price", "total_amount"]])
    print("\n2D array shape:", table.shape, "(rows, columns)")
    print("First 3 rows:")
    print(table[:3])

    # indexing and slicing
    print_line()
    print("First amount          :", amounts[0])
    print("Last amount           :", amounts[-1])
    print("Amounts 5 to 9        :", amounts[5:10])
    print("Row 2, column 3       :", table[2, 2])
    print("All quantities (col 0), first 8:", table[:8, 0])

    # statistics
    print_line()
    print("Sum                   :", np.sum(amounts))
    print("Mean                  :", round(np.mean(amounts), 2))
    print("Maximum               :", np.max(amounts))
    print("Minimum               :", np.min(amounts))
    print("Standard deviation    :", round(np.std(amounts), 2))


# ---------------- Pandas ----------------
def pandas_demo():
    print_heading("PANDAS DEMO")

    # create a DataFrame from a dictionary
    small = pd.DataFrame({
        "product": ["Laptop", "Phone", "Pen Pack"],
        "price": [55000, 20000, 80],
    })
    print("A small DataFrame we created:")
    print(small)

    # read the CSV
    df = pd.read_csv(DATA_FILE)
    print_line()
    print("Dataset shape (rows, columns):", df.shape)

    # selected rows and columns
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nSelected columns (customer, product, total) for rows 0-4:")
    print(df.loc[0:4, ["customer_name", "product", "total_amount"]])

    # filtering
    print_line()
    big_orders = df[df["total_amount"] > 100000]
    print("Orders above Rs.100000:", len(big_orders))
    print(big_orders[["order_id", "product", "total_amount"]].head())

    north_electronics = df[(df["region"] == "North") & (df["category"] == "Electronics")]
    print("\nNorth region + Electronics orders:", len(north_electronics))

    # sorting
    print_line()
    print("Top 5 orders by total amount:")
    print(df.sort_values("total_amount", ascending=False).head(5)[["order_id", "customer_name", "product", "total_amount"]])

    # missing values
    print_line()
    print("Missing values in each column:")
    print(df.isnull().sum())
    df["rating"] = df["rating"].fillna(df["rating"].mean())      # fill with average
    df["payment_method"] = df["payment_method"].fillna("Unknown")
    print("\nMissing values after cleaning:", df.isnull().sum().sum())
    df.to_csv(CLEAN_FILE, index=False)
    print("Clean data saved to", CLEAN_FILE)

    # groupby
    print_line()
    print("Total sales by region:")
    print(df.groupby("region")["total_amount"].sum())
    print("\nAverage rating by category:")
    print(df.groupby("category")["rating"].mean().round(2))

    # statistical analysis
    print_line()
    print("Statistics of numeric columns:")
    print(df[["quantity", "unit_price", "total_amount", "rating"]].describe().round(2))
    print("\nCorrelation between quantity and total_amount:",
          round(df["quantity"].corr(df["total_amount"]), 2))


def insights():
    print_heading("KEY INSIGHTS")
    df = pd.read_csv(CLEAN_FILE)

    best_region = df.groupby("region")["total_amount"].sum().idxmax()
    best_product = df.groupby("product")["total_amount"].sum().idxmax()
    best_customer = df.groupby("customer_name")["total_amount"].sum().idxmax()
    top_payment = df["payment_method"].value_counts().idxmax()
    best_category = df.groupby("category")["total_amount"].sum().idxmax()
    avg_order = np.mean(df["total_amount"])

    print("1. Best performing region   :", best_region)
    print("2. Highest revenue product  :", best_product)
    print("3. Highest revenue category :", best_category)
    print("4. Top customer             :", best_customer)
    print("5. Most used payment method :", top_payment)
    print("6. Average order value      : Rs.", round(avg_order, 2))
    print("7. Average customer rating  :", round(df["rating"].mean(), 2), "/ 5")

    # monthly sales
    df["month"] = pd.to_datetime(df["order_date"]).dt.month
    monthly = df.groupby("month")["total_amount"].sum()
    print("8. Best month (number)      :", monthly.idxmax())
    print_line()
'''

MODULE_ORGANIZER = r'''# organizer.py  (Module 4)
# The "File Organizer" part of the project.
# It looks inside the 00_inbox folder and moves each file to the right folder
# based on its extension. Moves are saved in a log file.

import os
import shutil
from datetime import datetime
from helpers import print_line

INBOX = "00_inbox"
LOG_FILE = "04_docs/organizer_log.csv"

# dictionary: extension -> destination folder
FOLDER_RULES = {
    ".csv": "01_data/raw",
    ".xlsx": "01_data/raw",
    ".parquet": "01_data/raw",
    ".sql": "02_scripts/sql",
    ".py": "02_scripts/python_r",
    ".ipynb": "02_scripts/notebooks",
    ".png": "03_outputs/charts",
    ".svg": "03_outputs/charts",
    ".pdf": "03_outputs/reports",
    ".pptx": "03_outputs/reports",
    ".pbix": "03_outputs/bi_files",
    ".twbx": "03_outputs/bi_files",
    ".md": "04_docs",
    ".txt": "04_docs",
}


def clean_name(filename):
    # lowercase, no spaces -> machine readable name
    name = filename.lower().replace(" ", "_")
    return name.replace("(", "").replace(")", "")


def make_unique_name(folder, filename):
    # if the file already exists add _v1, _v2 ...
    name, ext = os.path.splitext(filename)
    new_name = filename
    version = 1
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = name + "_v" + str(version) + ext
        version = version + 1
    return new_name


def write_log(entries):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as log:
        if not file_exists:
            log.write("time,original_name,new_location,size_bytes\n")
        for e in entries:                       # e is a tuple
            log.write(",".join(str(x) for x in e) + "\n")


def organize_files():
    if not os.path.exists(INBOX):
        print("Inbox folder not found.")
        return

    files = os.listdir(INBOX)
    if len(files) == 0:
        print("Inbox is empty. Nothing to organize.")
        return

    log_entries = []
    moved = 0
    skipped = 0
    for filename in files:
        path = os.path.join(INBOX, filename)
        if os.path.isdir(path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in FOLDER_RULES:
            print("Skipped (no rule):", filename)
            skipped += 1
            continue

        destination = FOLDER_RULES[ext]
        new_name = make_unique_name(destination, clean_name(filename))
        size = os.path.getsize(path)
        shutil.move(path, os.path.join(destination, new_name))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entries.append((now, filename, destination + "/" + new_name, size))
        print("Moved:", filename.ljust(28), "->", destination + "/" + new_name)
        moved += 1

    if len(log_entries) > 0:
        write_log(log_entries)
    print_line()
    print("Files moved:", moved, "| Skipped:", skipped)
    print("Log saved in", LOG_FILE)


def archive_old_files(days=90):
    # move raw files older than 'days' days into the archive folder
    folder = "01_data/raw"
    count = 0
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        age_days = (datetime.now().timestamp() - os.path.getmtime(path)) / 86400
        if os.path.isfile(path) and age_days > days:
            shutil.move(path, os.path.join("01_data/archive", filename))
            print("Archived:", filename)
            count += 1
    print("Files archived:", count)
'''

MODULES = {
    "helpers.py": MODULE_HELPERS,
    "data_handler.py": MODULE_DATA_HANDLER,
    "analysis.py": MODULE_ANALYSIS,
    "organizer.py": MODULE_ORGANIZER,
}

FOLDERS = [
    "00_inbox",
    "01_data/raw", "01_data/interim", "01_data/processed", "01_data/archive",
    "02_scripts/sql", "02_scripts/python_r", "02_scripts/notebooks",
    "03_outputs/charts", "03_outputs/reports", "03_outputs/bi_files",
    "04_docs",
]


# ------------------------------------------------------------
#  SETUP FUNCTIONS
# ------------------------------------------------------------
def create_module_files():
    # write each module to a .py file (only if it is not there yet)
    for filename, code in MODULES.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(code)
            print("Module created:", filename)


def create_folders():
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)


def create_dataset(filename):
    # creates 60 sales records and saves them in a CSV file
    random.seed(42)  # same data every time

    customers = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Anjali", "Karan",
                 "Neha", "Rahul", "Pooja", "Amit", "Divya"]
    regions = ["North", "South", "East", "West"]
    products = [
        ("Laptop", "Electronics", 55000),
        ("Phone", "Electronics", 20000),
        ("Headphones", "Electronics", 2500),
        ("Office Chair", "Furniture", 7000),
        ("Desk", "Furniture", 9500),
        ("Notebook", "Stationery", 120),
        ("Pen Pack", "Stationery", 80),
    ]
    payments = ["Card", "UPI", "Cash", "NetBanking"]

    rows = []
    for i in range(1, 61):
        product = random.choice(products)
        quantity = random.randint(1, 5)
        month = random.randint(1, 10)
        day = random.randint(1, 28)
        row = {
            "order_id": 1000 + i,
            "order_date": "2026-" + str(month).zfill(2) + "-" + str(day).zfill(2),
            "customer_name": random.choice(customers),
            "region": random.choice(regions),
            "product": product[0],
            "category": product[1],
            "quantity": quantity,
            "unit_price": product[2],
            "total_amount": quantity * product[2],
            "payment_method": random.choice(payments),
            "rating": random.randint(1, 5),
        }
        rows.append(row)

    # a few missing values on purpose (to practise handling them later)
    rows[4]["rating"] = ""
    rows[17]["rating"] = ""
    rows[33]["rating"] = ""
    rows[48]["payment_method"] = ""
    rows[55]["rating"] = ""

    columns = list(rows[0].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print("Dataset created with", len(rows), "records ->", filename)


# ------------------------------------------------------------
#  STEP 1 : set everything up, THEN import our own modules
# ------------------------------------------------------------
create_module_files()
create_folders()

import helpers
import data_handler
import analysis
import organizer

if not os.path.exists(data_handler.DATA_FILE):
    create_dataset(data_handler.DATA_FILE)


# ------------------------------------------------------------
#  STEP 2 : menu
# ------------------------------------------------------------
def make_sample_inbox_files():
    # creates a few messy files so we can test the organizer
    samples = ["Q4 Churn Cohort (Final).csv", "Revenue Query.sql", "clean_script.py",
               "Sales Dashboard.pbix", "meeting notes.txt", "photo.jpg"]
    for name in samples:
        path = os.path.join("00_inbox", name)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("sample file\n")
    print("Sample messy files added to 00_inbox/")


def show_menu():
    helpers.print_heading("DATA ANALYST FILE ORGANIZER")
    print(" 1. Display all records")
    print(" 2. Add a new record")
    print(" 3. Search a record")
    print(" 4. Update a record")
    print(" 5. Delete a record")
    print(" 6. Summary report")
    print(" 7. NumPy demo")
    print(" 8. Pandas demo")
    print(" 9. Key insights")
    print("10. Organize files in inbox")
    print("11. Add sample messy files to inbox")
    print("12. Archive old raw files (90+ days)")
    print(" 0. Exit")


def main():
    records = data_handler.load_data()
    print("Loaded", len(records), "records from", data_handler.DATA_FILE)

    while True:
        show_menu()
        choice = helpers.get_number("Enter your choice: ")

        if choice == 1:
            data_handler.display_all(records)
        elif choice == 2:
            data_handler.add_record(records)
        elif choice == 3:
            data_handler.search_record(records)
        elif choice == 4:
            data_handler.update_record(records)
        elif choice == 5:
            data_handler.delete_record(records)
        elif choice == 6:
            data_handler.summary_report(records)
        elif choice == 7:
            analysis.numpy_demo()
        elif choice == 8:
            analysis.pandas_demo()
        elif choice == 9:
            if not os.path.exists(analysis.CLEAN_FILE):
                analysis.pandas_demo()   # creates the clean file first
            analysis.insights()
        elif choice == 10:
            organizer.organize_files()
        elif choice == 11:
            make_sample_inbox_files()
        elif choice == 12:
            organizer.archive_old_files()
        elif choice == 0:
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


main()
