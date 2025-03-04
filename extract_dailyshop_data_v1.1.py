import json
import os
from pathlib import Path
import csv
import re
import platform
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Detect home directory
home_var = "USERPROFILE" if platform.system() == "Windows" else "HOME"

# Load configuration from daily_shop_extract_config.json
with open("daily_shop_extract_config.json", "r") as config_file:
    config = json.load(config_file)

PROJECT_ROOT = Path(__file__).parent.resolve()
COBBLEMON_DIR = Path(os.path.expandvars(config["COBBLEMON_DIR"].replace("${HOME_DIR}", f"${home_var}")))
DAILYSHOP_CONFIG_DIR = COBBLEMON_DIR / "minecraft" / "config" / "dailyshop" / "trade_tables"

OUTPUT_EMERALD_FILE = "daily_shop_emeralds.csv"
OUTPUT_COIN_FILE = "daily_shop_coins.csv"
CSV_SEPARATOR = config.get("CSV_SEPARATOR", ",")
COLUMN_NAMES = config["CSV_COLUMNS"]
FUN_MODE = config.get("FUN_MODE", False)

def read_table(table_name: str):
    file_path = DAILYSHOP_CONFIG_DIR / (table_name + ".json")
    try:
        with open(file_path, "r") as fd:
            contents = json.load(fd)
        return contents
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found - {file_path}")
        exit(1)

def format_percentage(value: float, decimal_places: int = 2):
    return f"{value * 100:.{decimal_places}f}%"

def format_item_name(item_name: str):
    return item_name.replace('_', ' ').title()

def format_mod_name(mod_name: str):
    return mod_name.replace("_", " ").title()

def format_cost(count: int, item: str):
    return f"{count} x {item.replace('_', ' ').title()}"

def parse_cost(cost: str):
    match = re.match(r"(\d+) x (.+)", cost)
    if match:
        count = int(match.group(1))
        item = match.group(2).strip()
        return count * 9 if item == "Emerald Block" else count, cost
    return 0, cost

def convert_emerald_to_coins(emerald_count):
    """
    Converts Emeralds to Copper, Iron, and Gold Coins.

    1 Emerald = 4 Copper Coins
    9 Copper = 1 Iron
    9 Iron = 1 Gold (81 Copper)
    """
    copper = emerald_count * 4  
    gold = copper // 81  
    remaining_copper = copper % 81  
    iron = remaining_copper // 9  
    copper = remaining_copper % 9  
    return gold, iron, copper

if __name__ == "__main__":
    if FUN_MODE:
        print(Fore.MAGENTA + " 🎉 Welcome to the Daily Shop Data Extractor! Let's get extracting! ✨" + Style.RESET_ALL)
    else:
        print("Starting Daily Shop Data Extractor...")

    daily_shop = read_table("daily_shop")
    total_weight = sum(entry["weight"] for entry in daily_shop["pool"])
    
    if FUN_MODE:
        print(Fore.CYAN + f"📝 Calculated total shop weight: {total_weight}" + Style.RESET_ALL)
    else:
        print(f"Shop total weight: {total_weight}")

    csv_data_emeralds = [COLUMN_NAMES]  
    csv_data_coins = [COLUMN_NAMES + ["Gold Coins", "Iron Coins", "Copper Coins"]]  

    for entry in daily_shop["pool"]:
        pool_name = entry['value']
        
        if FUN_MODE:
            print(Fore.CYAN + "-" * 10 + f" Extracting from pool: {pool_name} " + "-" * 10 + Style.RESET_ALL)
        else:
            print("-" * 10 + pool_name + "-" * 10)
        
        pool = read_table(pool_name)
        total_item_weight = sum(item["weight"] for item in pool["output"])

        cost_item = pool['input1']['filter'].split(":")[1]  
        cost_count = pool['input1']['count']['count']
        cost = format_cost(cost_count, cost_item)

        total_emerald_value = cost_count * 9 if cost_item == "emerald_block" else cost_count
        gold, iron, copper = convert_emerald_to_coins(total_emerald_value)

        for item in pool['output']:
            mod_name, item_name = item['item'].split(':')
            percentage_in_pool = item["weight"] / total_item_weight
            percentage_in_shop = percentage_in_pool / total_weight

            formatted_item_name = format_item_name(item_name)
            formatted_mod_name = format_mod_name(mod_name)
            formatted_percentage_in_shop = format_percentage(percentage_in_shop, 2)

            if FUN_MODE:
                print(Fore.GREEN + f" 📦 Item: {formatted_item_name} | Mod: {formatted_mod_name} | Chance: {formatted_percentage_in_shop}" + Style.RESET_ALL)
                print(Fore.YELLOW + f" 💰 Emerald Cost: {total_emerald_value} | Gold: {gold}, Iron: {iron}, Copper: {copper}" + Style.RESET_ALL)
            else:
                print(f"{formatted_item_name},{formatted_mod_name},{formatted_percentage_in_shop},{total_emerald_value}")

            csv_data_emeralds.append([formatted_item_name, formatted_mod_name, cost, total_emerald_value, formatted_percentage_in_shop])
            csv_data_coins.append([formatted_item_name, formatted_mod_name, cost, total_emerald_value, formatted_percentage_in_shop, gold, iron, copper])

    header, *rows = csv_data_emeralds
    sorted_rows = sorted(rows, key=lambda x: (parse_cost(x[2]), x[1], x[0]))
    csv_data_emeralds = [header] + sorted_rows

    header_coins, *rows_coins = csv_data_coins
    sorted_rows_coins = sorted(rows_coins, key=lambda x: (parse_cost(x[2]), x[1], x[0]))
    csv_data_coins = [header_coins] + sorted_rows_coins

    with open(OUTPUT_EMERALD_FILE, "w", newline='') as fd:
        writer = csv.writer(fd, delimiter=CSV_SEPARATOR)
        writer.writerows(csv_data_emeralds)

    with open(OUTPUT_COIN_FILE, "w", newline='') as fd:
        writer = csv.writer(fd, delimiter=CSV_SEPARATOR)
        writer.writerows(csv_data_coins)

    if FUN_MODE:
        print(Fore.CYAN + Style.DIM + " 🎊 ==─==──==────== Processing Completed ==─────==──==─==" + Style.RESET_ALL)
        print(Fore.MAGENTA + " ✅ Data Extraction Complete! Output CSV files:" + Style.RESET_ALL)
        print(Fore.GREEN + f"  📜 {OUTPUT_EMERALD_FILE}  " + Style.RESET_ALL)
        print(Fore.GREEN + f"  💰 {OUTPUT_COIN_FILE}  " + Style.RESET_ALL)
        print(Fore.CYAN + Style.DIM + " 🎊 ==─==──==────== Processing Completed ==─────==──==─==" + Style.RESET_ALL)
        print(" ")
        print(Fore.BLUE + "  🎉 Thanks for using the Daily Shop Data Extractor! Have an amazing day! " + Style.RESET_ALL)
    else:
        print(f"✅ Process completed! Emerald CSV: {OUTPUT_EMERALD_FILE}, Coin CSV: {OUTPUT_COIN_FILE}")
