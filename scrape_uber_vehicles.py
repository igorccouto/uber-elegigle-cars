import re
import json
import argparse
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def select_cars_by_category(car_data_dict, required_categories=None, excluded_categories=None):
    result = {}
    for brand, cars in car_data_dict.items():
        filtered_cars = []
        for car in cars:
            categories = set(car['categories'])
            if required_categories and not all(req in categories for req in required_categories):
                continue
            if excluded_categories and any(ex in categories for ex in excluded_categories):
                continue
            filtered_cars.append(car)
        if filtered_cars:
            result[brand] = filtered_cars
    return result

# --- Command-line argument parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description="Scrape Uber eligible vehicles for a given city.")
    parser.add_argument('--city', type=str, default='porto', help='Uber city (default: porto)')
    parser.add_argument('--required-categories', type=str, default='', help='Comma-separated categories that must be present (e.g. Comfort,Green)')
    parser.add_argument('--excluded-categories', type=str, default='', help='Comma-separated categories that must NOT be present (e.g. Black,UberXL)')
    parser.add_argument('--brands', type=str, default='', help='Comma-separated car brands to filter (e.g. Audi,BMW,Tesla)')
    return parser.parse_args()

def create_session():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update(headers)
    return session

args = parse_args()
city = args.city.strip().lower()

required_categories = [c.strip() for c in args.required_categories.split(',') if c.strip()] if args.required_categories else None
excluded_categories = [c.strip() for c in args.excluded_categories.split(',') if c.strip()] if args.excluded_categories else None
brands_filter = [b.strip() for b in args.brands.split(',') if b.strip()] if args.brands else None

url = f"https://www.uber.com/global/pt-pt/eligible-vehicles/?city={city}"

session = create_session()

try:
    response = session.get(url, timeout=15)
    response.raise_for_status()
    html_content = response.text
    # --- Extract car info from the HTML in memory ---
    soup = BeautifulSoup(html_content, 'html.parser')
    car_data = defaultdict(list)  # {brand: [ { 'model': ..., 'year': ..., 'categories': [...] }, ... ]}

    # Find all accordion sections (brands)
    for brand_div in soup.find_all('div', {'data-testid': re.compile(r'^accordion-header$')}):
        brand_name = brand_div.get_text(strip=True)
        # Remove 'Down Small' if present (from SVG title)
        brand_name = brand_name.replace('Down Small', '').strip()
        # Find the next sibling with car list
        content_div = brand_div.find_next('div', {'data-testid': re.compile(r'^accordion-content-')})
        if not content_div:
            continue
        ul = content_div.find('ul')
        if not ul:
            continue
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            # Example: 'A4 - 2018 (Comfort, UberX, Store Pickup, ...)' or 'A3 - 2018 (UberX, ...)' 
            match = re.match(r"([\w\s\-\.]+)\s*-\s*(\d{4})\s*\(([^)]+)\)", text)
            if match:
                model = match.group(1).strip()
                year = match.group(2)
                categories = [c.strip() for c in match.group(3).split(',')]
                car_data[brand_name].append({
                    'model': model,
                    'year': year,
                    'categories': categories
                })

    # Filter to keep only specified brands (default list)
    brands_to_keep = [
        "Audi", "BMW", "BYD", "Chevrolet", "Citroën", "Dacia", "Fiat", "Ford", "Honda", "Hyundai", "Jeep", "Kia", "MG", "Mercedes-Benz", "Mitsubishi", "Nio", "Nissan", "Opel", "Peugeot", "Renault", "Seat", "Skoda", "Tesla", "Toyota", "Volkswagen"
    ]
    # If --brands is provided, override brands_to_keep
    if brands_filter:
        brands_to_keep = brands_filter
    filtered_car_data = {brand: cars for brand, cars in car_data.items() if brand in brands_to_keep}

    filtered_cars = select_cars_by_category(filtered_car_data, required_categories=required_categories, excluded_categories=excluded_categories)

    # Print in a format of table
    for brand, cars in filtered_cars.items():
        print(f"{brand}: {len(cars)} cars")
        for car in cars:
            print(f" - {car['model']} - {car['year']}")

    # Build output filename based on filters
    def filter_part(label, items):
        if not items:
            return ''
        return f"_{label}-" + "-".join([c.replace(' ', '_') for c in items])
    filter_str = f"{filter_part('brands', brands_filter)}{filter_part('required', required_categories)}{filter_part('excluded', excluded_categories)}"
    json_filename = f'uber_eligible_vehicles_{city}{filter_str}.json'
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(filtered_cars, json_file, ensure_ascii=False, indent=2)
    print(f"\nFiltered car data saved to '{json_filename}' for city '{city}'")

except requests.RequestException as e:
    print(f"Failed to fetch the page: {e}")

