# Uber Eligible Cars Scraper

This Python script scrapes Uber's eligible vehicle data for a specified city and allows for advanced filtering based on car brands and Uber service categories. It outputs the results both to the console and to a JSON file.

## Features

- **City selection**: Scrape eligible vehicles for any supported Uber city.
- **Brand filtering**: Filter results by one or more specific car brands.
- **Category filtering**: Require or exclude specific Uber service categories (e.g., Comfort, Green, Black).
- **Structured output**: Results are printed in a readable format and saved to a JSON file with a descriptive filename.
- **Robust scraping**: Uses HTTP retries and browser-like headers for reliability.

## Requirements

- Python 3.7+
- Packages: `requests`, `beautifulsoup4`

Install dependencies with:

```sh
pip install requests beautifulsoup4
```

## Usage

```sh
python scrape_uber_vehicles.py [--city CITY] [--brands BRAND1,BRAND2,...] [--required-categories CAT1,CAT2,...] [--excluded-categories CAT3,CAT4,...]
```

### Arguments

- `--city`: Uber city to scrape (default: `porto`).
- `--brands`: Comma-separated list of car brands to include (e.g., `Audi,BMW,Tesla`).
- `--required-categories`: Comma-separated list of categories that must be present (e.g., `Comfort,Green`).
- `--excluded-categories`: Comma-separated list of categories to exclude (e.g., `Black,UberXL`).

### Example Commands

- List all eligible cars for Lisbon:
  ```sh
  python scrape_uber_vehicles.py --city lisbon
  ```
- Only BMW and Tesla cars in Porto, excluding "Black" category:
  ```sh
  python scrape_uber_vehicles.py --city porto --brands BMW,Tesla --excluded-categories Black
  ```
- Cars that must have both Comfort and Green, but not Black:
  ```sh
  python scrape_uber_vehicles.py --city lisbon --required-categories Comfort,Green --excluded-categories Black
  ```

## Output

- Results are printed to the console, grouped by brand and model.
- Filtered results are saved as a JSON file named like:
  ```
  uber_eligible_vehicles_lisbon_brands-BMW-Tesla_required-Comfort-Green_excluded-Black.json
  ```

## Notes

- Please visit the [Uber Eligible Cars](https://www.uber.com/global/en/eligible-vehicles) site for your location to see the available categories for your city.
- The script only considers a predefined set of mainstream car brands by default. Use the `--brands` argument to override this filter.
- If you encounter HTTP errors or missing data, try again as Uber's site may change or temporarily block requests.

## License

MIT License. See [LICENSE](LICENSE) for details.
