# Daily Shop Data Extractor

## Author

This script was originally authored by pizzaspren

## Overview

The **Daily Shop Data Extractor** is a Python-based tool that extracts data from Minecraft Daily Shop mod JSON files, specifically focusing on daily shop trade tables. This tool processes the extracted data and generates a detailed CSV file, useful for further analysis or modification.

## Features

- Extracts data from daily shop JSON files.
- Outputs the extracted data into a well-formatted CSV file.
- Configurable settings through a JSON configuration file.
- "Fun Mode" for engaging terminal outputs with colorful messages.

## Requirements

- Python 3.6+
- `colorama` library for colorful terminal output.

To install `colorama`, run:

```sh
pip install colorama
```

## Usage

### 1. Clone the Repository

Clone the repository to your local machine using the following command:

```sh
git clone https://github.com/your-username/daily-shop-extractor.git
cd daily-shop-extractor
```

### 2. Install Dependencies

Ensure that Python 3.6 or above is installed. Install the necessary Python package with:

```sh
pip install colorama
```

### 3. Configuration

Update the `daily_shop_extract_config.json` file to set the appropriate paths:

```json
{
  "COBBLEMON_DIR": "${USERPROFILE}/AppData/Roaming/PrismLauncher/instances/BigChadGuys_Plus_Cobblemon",
  "OUTPUT_FILE_NAME": "daily_shop_data.csv",
  "CSV_SEPARATOR": ",",
  "CSV_COLUMNS": ["Item name", "Mod name", "Cost", "Total Emerald", "Chance"],
  "FUN_MODE": true
}
```

- **COBBLEMON\_DIR**: Set this to the directory containing your Minecraft daily shop mod data.
- **FUN\_MODE**: Set to `true` for colorful output.

### 4. Run the Extractor

Execute the Python script to extract data and generate a CSV:

```sh
python extract_dailyshop_data.py
```

## Fun Mode

**Fun Mode** adds color and style to terminal outputs, making the process more enjoyable. To enable it, ensure `"FUN_MODE": true` is set in the configuration file.

## Example Output

Running the extractor will generate a CSV file (`daily_shop_data.csv`) containing details of shop items, including their names, mods, costs, and more.

## License

This project is licensed under the Mozilla Public License, Version 2.0. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## Contact

For any questions, please reach out by opening an issue in the repository.

