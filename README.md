# NAVAREA-1 Web Scraper & Parser

This repository contains a Python-based Web Scraper and Parser designed to fetch and structure active "NAVAREA I" radio navigational warnings from the Admiralty Maritime Data Solutions website.

It was built utilizing the powerful **Scrapling** library.

## Features

- **Scraper (`navarea_scraper.py`)**: Fetches the main index page, extracts verification tokens, seamlessly emulates form submission for "Show selection", and downloads the unformatted NAVAREA I warnings into `navarea_1_warnings.txt`.
- **Parser (`navarea_parser.py`)**: Reads the unformatted text and uses regex to deterministically extract `warning_id`, `coordinates`, `title`, `issued_text`, and `cancellation_text`, outputting a structured `parsed_warnings.json` payload mapped to standard maritime database schemas.

## Usage

1. **Install Dependencies**
   Since this repository includes the Scrapling source code, you can install the dependencies directly:
   ```bash
   pip install -e .[all]
   ```
2. **Run the Scraper**
   ```bash
   python navarea_scraper.py
   ```
3. **Run the Parser**
   ```bash
   python navarea_parser.py
   ```

---

## Acknowledgments & Credits

**Scrapling Library**  
This repository is originally a fork of [Scrapling](https://github.com/D4Vinci/Scrapling), an adaptive web scraping framework for the modern web. 

All credit for the underlying scraping framework, fetcher engines, and DOM selectors goes to the original creator **Karim Shoair (D4Vinci)** and the contributors to the Scrapling project.

* [Scrapling GitHub Repository](https://github.com/D4Vinci/Scrapling)
* [Scrapling Documentation](https://scrapling.readthedocs.io)
