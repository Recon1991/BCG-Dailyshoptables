# Original Author: pizzapren
# Editor: Recon1991 and Contributors
# Project: Daily Shop Data Extractor
# Description: This script extracts data from daily shop JSON files for analysis.

import json
import os
from pathlib import Path
import csv
import re
import platform
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

if platform.system() == "Windows":
    home_var = "USERPROFILE"
else:
    home_var = "HOME"

# Load configuration from daily_shop_extract_config.json
with open("daily_shop_extract_config.json", "r") as config_file:
    config = json.load(config_file)

PROJECT_ROOT = Path(__file__).parent.resolve()
COBBLEMON_DIR = Path(os.path.expandvars(config["COBBLEMON_DIR"].replace("${HOME_DIR}", f"${home_var}")))
DAILYSHOP_CONFIG_DIR = COBBLEMON_DIR / "minecraft" / "config" / "dailyshop" / "trade_tables"

OUTPUT_FILE_NAME = config["OUTPUT_FILE_NAME"]
CSV_SEPARATOR = config.get("CSV_SEPARATOR", ",")
COLUMN_NAMES = config["CSV_COLUMNS"]
FUN_MODE = config.get("FUN_MODE", False)

def read_table(table_name: str):
    file_path = DAILYSHOP_CONFIG_DIR / (table_name + ".json")
    try:
        with open(file_path, "r") as fd:
            contents = json.load(fd)
        validate_data(contents, table_name)  # Perform validation after reading data
        if FUN_MODE:
            print(Fore.YELLOW + f" Successfully loaded data for table: {table_name}" + Style.RESET_ALL)
        return contents
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found - {file_path}")
        exit(1)

def validate_data(data, table_name: str):
    """
    Validates the structure of the JSON data to ensure required fields exist and are of expected types.
    """
    # Basic validation for the 'roll' key
    if "roll" not in data:
        print(f"{Fore.RED}Validation Error: 'roll' is missing in the '{table_name}' table.")
        exit(1)

    if "pool" in data:
        if not isinstance(data["pool"], list):
            print(f"{Fore.RED}Validation Error: 'pool' should be a list in the '{table_name}' table.")
            exit(1)

        for pool_entry in data["pool"]:
            if "value" not in pool_entry or "weight" not in pool_entry:
                print(f"{Fore.RED}Validation Error: 'value' or 'weight' missing in an entry of 'pool' in '{table_name}' table.")
                exit(1)

            if not isinstance(pool_entry["weight"], (int, float)):
                print(f"{Fore.RED}Validation Error: 'weight' should be a number in '{table_name}' table.")
                exit(1)

def format_percentage(value: float, decimal_places: int = 2):
    """
    Formats a percentage value to a specified number of decimal places and adds a % symbol.
    """
    return f"{value * 100:.{decimal_places}f}%"

def format_item_name(item_name: str):
    """
    Formats an item name by replacing underscores with spaces and capitalizing each word.
    Additionally, replaces 'Ts.' with 'Tom's'.
    """
    formatted_name = item_name.replace('_', ' ').title()
    return formatted_name.replace('Ts.', "Tom's")

def format_mod_name(mod_name: str):
    """
    Formats a mod name by replacing underscores with spaces and capitalizing each word.
    """
    return mod_name.replace("_", " ").title()

def format_cost(count: int, item: str):
    """
    Formats the cost by combining the count and item name in a readable format.
    """
    return f"{count} x {item.replace('_', ' ').title()}"

def parse_cost(cost: str):
    """
    Parses the cost string into a tuple of (total_emerald_value, original_cost) for sorting purposes.
    """
    match = re.match(r"(\d+) x (.+)", cost)
    if match:
        count = int(match.group(1))
        item = match.group(2).strip()
        # Convert Emerald Block to equivalent Emerald value (assuming 1 Block = 9 Emeralds)
        if item == "Emerald Block":
            total_emerald_value = count * 9
        else:
            total_emerald_value = count
        return total_emerald_value, cost
    return 0, cost

if __name__ == "__main__":
    if FUN_MODE:
        print(Fore.MAGENTA + " Welcome to the Daily Shop Data Extractor! Let's get extracting! ✨" + Style.RESET_ALL)
    else:
        print("Starting Daily Shop Data Extractor...")

    daily_shop = read_table("daily_shop")
    total_weight = sum(entry["weight"] for entry in daily_shop["pool"])
    if FUN_MODE:
        print(Fore.CYAN + f"📝 Calculated total shop weight: {total_weight}" + Style.RESET_ALL)
    else:
        print(f"Shop total weight: {total_weight}")

    csv_data = [COLUMN_NAMES]  # Column names loaded from daily_shop_extract_config.json

    for entry in daily_shop["pool"]:
        pool_name = entry['value']
        if FUN_MODE:
            print(Fore.CYAN + "-" * 10 + f" Extracting from pool: {pool_name} " + "-" * 10 + Style.RESET_ALL)
        else:
            print("-" * 10 + pool_name + "-" * 10)

        pool = read_table(pool_name)
        total_item_weight = sum(item["weight"] for item in pool["output"])
        if FUN_MODE:
            print(Fore.YELLOW + f" Pool item weights calculated: {total_item_weight}" + Style.RESET_ALL)
        else:
            print(f"\tPool item weights: {total_item_weight}")

        cost_item = pool['input1']['filter'].split(":")[1]  # Ignore minecraft:
        cost_count = pool['input1']['count']['count']
        cost = format_cost(cost_count, cost_item)
        if FUN_MODE:
            print(Fore.GREEN + f" Cost of items: {cost}" + Style.RESET_ALL)
        else:
            print(f"\tCost: {cost}")

        # Calculate total emerald value for the cost
        if cost_item == "emerald_block":
            total_emerald_value = cost_count * 9
        else:
            total_emerald_value = cost_count

        for item in pool['output']:
            mod_name, item_name = item['item'].split(':')
            percentage_in_pool = item["weight"] / total_item_weight
            percentage_in_shop = percentage_in_pool / total_weight

            formatted_item_name = format_item_name(item_name)
            formatted_mod_name = format_mod_name(mod_name)
            formatted_percentage_in_shop = format_percentage(percentage_in_shop, 2)

            if FUN_MODE:
                print(Fore.GREEN + f" Item: {formatted_item_name}, Mod: {formatted_mod_name}, Chance: {formatted_percentage_in_shop}, Total Emerald Value: {total_emerald_value}" + Style.RESET_ALL)
            else:
                print(f"{formatted_item_name},{formatted_mod_name},{formatted_percentage_in_shop},{total_emerald_value}")

            csv_data.append([formatted_item_name, formatted_mod_name, cost, total_emerald_value, formatted_percentage_in_shop])

    # Sort csv_data by total emerald value, then Mod name, then Item name
    header, *rows = csv_data
    sorted_rows = sorted(rows, key=lambda x: (parse_cost(x[2]), x[1], x[0]))
    csv_data = [header] + sorted_rows

    if os.path.exists(OUTPUT_FILE_NAME):
        os.remove(OUTPUT_FILE_NAME)
    with open(OUTPUT_FILE_NAME, "w", newline='') as fd:
        writer = csv.writer(fd, delimiter=CSV_SEPARATOR)
        writer.writerows(csv_data)

    if FUN_MODE:
        print(Fore.CYAN + Style.DIM + "     ==─==──==────== Processing Completed ==─────==──==─==" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"  Process completed successfully! Output CSV file: {OUTPUT_FILE_NAME} " + Style.RESET_ALL)
        print(Fore.CYAN + "  Thanks for using the Daily Shop Data Extractor! Have a great day! " + Style.RESET_ALL)
    else:
        print(f"Process completed successfully. Output CSV file: {OUTPUT_FILE_NAME}")
