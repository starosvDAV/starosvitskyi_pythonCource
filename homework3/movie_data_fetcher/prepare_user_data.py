import argparse
import csv
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import requests
import zipfile
from collections import defaultdict, Counter
import pytz
import json

# ---------- Logging ----------
def setup_logger(log_level):
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), "INFO"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("process.log"),
            logging.StreamHandler()
        ]
    )

# ---------- CLI Arguments ----------
def parse_arguments():
    parser = argparse.ArgumentParser(description="Prepare user data")
    parser.add_argument("--destination", required=True, help="Destination folder")
    parser.add_argument("--filename", default="output", help="CSV filename without extension")
    parser.add_argument("--gender", choices=["male", "female"], help="Filter by gender")
    parser.add_argument("--number", type=int, help="Number of rows to keep")
    parser.add_argument("log_level", nargs="?", default="INFO", help="Optional log level")
    return parser.parse_args()

# ---------- Data Download ----------
def download_data(filename):
    logging.info("Downloading user data...")
    url = "https://randomuser.me/api/?results=5000&format=csv"
    response = requests.get(url)
    path = Path(f"{filename}.csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write(response.text)
    logging.info(f"Saved raw data to {path}")
    return path

# ---------- Data Processing ----------
def process_data(input_path, args):
    logging.info("Processing CSV file...")
    out_rows = []
    with open(input_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if args.gender and row.get("gender") != args.gender:
                continue
            if args.number and len(out_rows) >= args.number:
                break

            # Global index
            row["global_index"] = str(len(out_rows) + 1)

            # Current time from timezone
            try:
                tz_offset = int(row.get("location.timezone.offset", "+0").replace(":", ""))
                current_time = datetime.utcnow()
                row["current_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                row["current_time"] = ""

            # Title mapping
            mapping = {"Mrs": "missis", "Ms": "miss", "Mr": "mister", "Madame": "mademoiselle"}
            row["name.title"] = mapping.get(row["name.title"], row["name.title"])

            # Date of birth
            try:
                dob = datetime.strptime(row["dob.date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                row["dob.date"] = dob.strftime("%m/%d/%Y")
                row["dob.year"] = dob.year
            except:
                row["dob.date"] = ""
                row["dob.year"] = 0

            # Registered date
            try:
                reg = datetime.strptime(row["registered.date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                row["registered.date"] = reg.strftime("%m-%d-%Y, %H:%M:%S")
                row["registered.year"] = reg.year
            except:
                row["registered.date"] = ""
                row["registered.year"] = 0

            out_rows.append(row)
    logging.info(f"Filtered and processed {len(out_rows)} rows")
    return out_rows

# ---------- Data Grouping ----------
def group_data_by_decade_country(rows):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        year = int(row.get("dob.year", 0))
        if year < 1960:
            continue
        decade = f"{year // 10 * 10}-th"
        country = row.get("location.country", "Unknown")
        grouped[decade][country].append(row)
    return grouped

# ---------- Save Grouped Data ----------
def save_grouped_data(grouped, base_path):
    logging.info("Saving grouped data to folders...")
    for decade, countries in grouped.items():
        decade_path = base_path / decade
        decade_path.mkdir(parents=True, exist_ok=True)
        for country, users in countries.items():
            country_path = decade_path / country
            country_path.mkdir(parents=True, exist_ok=True)

            ages = [int(u.get("dob.age", 0)) for u in users]
            reg_years = [datetime.now().year - int(u.get("registered.year", 0)) for u in users]
            ids = [u.get("id.name", "") for u in users if u.get("id.name")]
            max_age = max(ages, default=0)
            avg_reg = int(sum(reg_years) / len(reg_years)) if reg_years else 0
            popular_id = Counter(ids).most_common(1)[0][0] if ids else "none"

            file_name = f"max_age_{max_age}_avg_registered_{avg_reg}_popular_id_{popular_id}.csv"
            file_path = country_path / file_name

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=users[0].keys())
                writer.writeheader()
                writer.writerows(users)
            logging.info(f"Saved: {file_path}")

# ---------- Log Folder Structure ----------
def log_folder_structure(path: Path, prefix=""):
    if path.is_dir():
        logging.info(f"{prefix}[DIR] {path.name}")
        for item in sorted(path.iterdir()):
            log_folder_structure(item, prefix + "    ")
    else:
        logging.info(f"{prefix}[FILE] {path.name}")

# ---------- Main ----------
def main():
    args = parse_arguments()
    setup_logger(args.log_level)

    destination = Path(args.destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    os.chdir(destination)

    raw_file = download_data(args.filename)
    shutil.move(str(raw_file), destination / raw_file.name)

    rows = process_data(destination / raw_file.name, args)
    grouped = group_data_by_decade_country(rows)
    save_grouped_data(grouped, destination)

    log_folder_structure(destination)

    # Archive
    zip_path = destination.with_suffix(".zip")
    logging.info(f"Archiving folder to {zip_path}")
    shutil.make_archive(str(destination), "zip", root_dir=destination)
    logging.info("✅ Done!")


if __name__ == "__main__":
    main()
