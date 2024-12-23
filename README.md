# Chattanooga Events Scraper

This project is a web scraper designed to extract event details from multiple websites hosting information about Chattanooga events. It uses Python, Selenium, and BeautifulSoup to fetch, parse, and save event data. The extracted data includes titles, dates, times, locations, image URLs, and event details.

---

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Logs and Debugging](#logs-and-debugging)
- [Planned Improvements](#planned-improvements)
- [License](#license)

---

## Features

- Extracts events from multiple websites, including:
  - Visit Chattanooga
  - CHA Guide Events
  - Chattanooga Pulse
  - Chatt Library
- Debugging utilities:
  - Logs key actions and errors.
  - Supports HTML saving and detailed inspection tools.
- Configurable debugging and output saving options.
- Outputs events as CSV files for further analysis.

---

## Setup

### Prerequisites

- Python 3.8+
- Google Chrome
- Dependencies listed in `requirements.txt`.

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/MacOS
   venv\Scripts\activate     # For Windows
   ```
3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure you have Google Chrome installed and up-to-date.

---

## Usage

1. Run the main script to start scraping:
   ```bash
   python event_scraper6.py
   ```

2. The extracted data will be saved as a CSV file in the `data/` directory:
   - Example: `all_events.csv`

3. Logs will be saved in the `logs/` directory for debugging and insights.

---

## Project Structure

```
├── data/                   # Directory for extracted data
├── debugging_scripts/      # Additional debugging tools and scripts
│   ├── data/               # Sub-directory for debugging data
│   ├── logs/               # Sub-directory for debugging logs
│   ├── date_extraction.py  # Debugging script for date extraction
│   ├── details.py          # Debugging script for event details
│   ├── image_extraction.py # Debugging script for images
│   ├── location.py         # Debugging script for locations
│   └── url_extraction.py   # Debugging script for URLs
├── logs/                   # Log files generated during runtime
├── Chattanooga_events.desktop # Shortcut for the application
└── event_scraper6.py       # Main scraping script
```

---

## Logs and Debugging

- Logging is configured in `event_scraper6.py`. Logs include timestamps, log levels, and detailed messages.
- Debugging options can be toggled in the script using boolean flags:
  - `execute_debugging`: Enable/disable debugging functions.
  - `execute_scroll_page`: Enable/disable page scrolling for JavaScript rendering.
  - `execute_save_html`: Save HTML content of the scraped pages.
  - `execute_save_events_to_csv`: Save events as CSV during scraping.

Logs are saved in the `logs/` directory for easy access.

---

## Planned Improvements

- Add support for price extraction.
- Enhance image extraction to display image previews instead of URLs.
- Refactor code to reduce redundancy in functions.
- Add support for additional event websites.
- Optimize Selenium usage and consider headless browsing.
- Explore containerization or a dedicated environment setup.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

