import json
import os
from pathlib import Path
from fractions import Fraction

COBBLEMON_DIR = Path("~") / "curseforge" / "minecraft" / "instances" / "BigChadGuys Plus (w Cobblemon)"
DAILYSHOP_CONFIG_DIR = COBBLEMON_DIR / "config" / "dailyshop" / "trade_tables"

OUTPUT_FILE_NAME = "daily_shop_data.csv"
CSV_SEPARATOR = ","


def read_table(table_name: str):
    file_path = os.path.expanduser(DAILYSHOP_CONFIG_DIR / table_name) + ".json"
    with open(file_path, "r") as fd:
        contents = json.load(fd)
    return contents


def format_percentage(value: float, decimal_places: int = 4):
    """
    Formats a percentage value to a specified number of decimal places and adds a % symbol.
    """
    return f"{value * 100:.{decimal_places}f}%"


def format_fraction(value: float):
    """
    Formats a value as a fraction.
    """
    return str(Fraction(value).limit_denominator())


if __name__ == "__main__":
    daily_shop = read_table("daily_shop")
    """
        {
            "roll": {
                "type": "constant",
                "count": 24
            },
            "pool": [
                {
                    "value": "1_emerald",
                    "weight": 1.0
                },
                ...
            ]
        }
    """
    total_weight = sum(entry["weight"] for entry in daily_shop["pool"])
    print(f"Shop total weight: {total_weight}")

    csv_data = [
        ["Item name", "Mod name", "Item count", "Cost", "Percentage", "Fraction"]  # Column names
    ]

    for entry in daily_shop["pool"]:
        pool_name = entry['value']
        print("-" * 10 + pool_name + "-" * 10)
        pool = read_table(pool_name)
        """
        {
            "roll": {
                "type": "constant",
                "count": 1
            },
            "input1": {
                "filter": "minecraft:emerald_block",
                "count": { "type": "constant", "count": 48 }
            },
            "output": [
                {
                    "item": "creeperoverhaul:badlands_creeper_spawn_egg",
                    "count": { "type": "constant", "count": 1 },
                    "weight": 1
                },
                ...
            ]
        }
        """
        total_item_weight = sum(item["weight"] for item in pool["output"])
        print(f"\tPool item weights: {total_item_weight}")

        cost_item = pool['input1']['filter'].split(":")[1]  # Ignore minecraft:
        cost_count = pool['input1']['count']['count']
        cost = f"{cost_count} {cost_item}"
        print(f"\tCost: {cost}")

        for item in pool['output']:
            mod_name, item_name = item['item'].split(':')
            item_count = item['count']['count']
            percentage_in_pool = item["weight"] / total_item_weight
            percentage_in_shop = percentage_in_pool / total_weight

            formatted_percentage_in_pool = format_percentage(percentage_in_pool)
            formatted_percentage_in_shop = format_percentage(percentage_in_shop)
            fraction_in_shop = format_fraction(percentage_in_shop)

            print(f"{item_name},{mod_name},{item_count},{formatted_percentage_in_pool},{formatted_percentage_in_shop},{fraction_in_shop}")
            csv_data.append([item_name, mod_name, str(item_count), cost, formatted_percentage_in_shop, fraction_in_shop])

    if os.path.exists(OUTPUT_FILE_NAME):
        os.remove(OUTPUT_FILE_NAME)
    with open(OUTPUT_FILE_NAME, "x") as fd:
        csv_contents = "\n".join([CSV_SEPARATOR.join(line) for line in csv_data])
        fd.write(csv_contents)
