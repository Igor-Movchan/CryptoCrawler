import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.options import Options

def get_chrome_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--user-data-dir=/tmp/chrome-user-data')
    return webdriver.Chrome(options=options)

def scrape_page(driver, global_rank_start):
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.cmc-table tbody tr'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.select('table.cmc-table tbody tr')
    records = []

    for idx, row in enumerate(rows, start=0):
        cols = row.find_all('td')
        if len(cols) < 7:
            continue

        try:
            rank = str(global_rank_start + idx)

            name_col = cols[2]
            name_tag = name_col.select_one('a.cmc-link')
            symbol_tag = name_col.select_one('p.coin-item-symbol')

            name = name_tag.get_text(strip=True) if name_tag else 'N/A'
            symbol = symbol_tag.get_text(strip=True) if symbol_tag else 'N/A'

            price = cols[3].get_text(strip=True)
            change_24h = cols[4].get_text(strip=True)

            market_cap_tag = cols[7].select_one('span') if len(cols) > 7 else None
            market_cap = market_cap_tag.get_text(strip=True) if market_cap_tag else 'N/A'

            records.append({
                'Rank': rank,
                'Name': name,
                'Symbol': symbol,
                'Price (USD)': price,
                '24h % Change': change_24h,
                'Market Cap (USD)': market_cap
            })
        except Exception as e:
            print(f"Skipping a row due to error: {e}")
            continue

    return records

def fetch_json_data(start, limit=20):
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing'
    params = {
        'start': start,
        'limit': limit,
        'sortBy': 'market_cap',
        'sortType': 'desc',
        'convert': 'USD'
    }
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['data']['cryptoCurrencyList']

def scrape_json():
    start_time = time.time()
    csv_filename = 'coinmarketcap_data_json.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Rank', 'Name', 'Symbol', 'Price (USD)', '24h % Change', 'Market Cap (USD)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for start in range(1, 101, 20):
            data = fetch_json_data(start=start, limit=20)

            for coin in data:
                quote = coin.get('quotes', [{}])[0]
                writer.writerow({
                    'Rank': coin['cmcRank'],
                    'Name': coin['name'],
                    'Symbol': coin['symbol'],
                    'Price (USD)': f"{quote.get('price', 0):.2f}",
                    '24h % Change': f"{quote.get('percentChange24h', 0):.2f}",
                    'Market Cap (USD)': f"${quote.get('marketCap', 0):,.2f}"
                })

            print(f"Fetched coins {start}–{start + 19}")

    elapsed = time.time() - start_time
    print(f"Scraped 100 entries in {elapsed:.2f} seconds (~{100 / elapsed:.2f} req/s)")

def main():
    # Web scraping
    start_time = time.time()

    driver = get_chrome_driver()

    base_url = 'https://coinmarketcap.com/'

    csv_filename = 'coinmarketcap_data.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Rank', 'Name', 'Symbol', 'Price (USD)', '24h % Change', 'Market Cap (USD)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        global_rank = 1
        for page_num in range(1, 6):
            driver.get(base_url + (f'?page={page_num}' if page_num > 1 else ''))
            page_records = scrape_page(driver, global_rank)
            writer.writerows(page_records)
            global_rank += len(page_records)
            print(f'Page {page_num} scraped.')

    driver.quit()
    elapsed = time.time() - start_time
    print(f"Scraped 100 entries in {elapsed:.2f} seconds (~{100 / elapsed:.2f} req/s)")


    # JSON scraping
    start_time = time.time()
    csv_filename = 'coinmarketcap_data_json.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Rank', 'Name', 'Symbol', 'Price (USD)', '24h % Change', 'Market Cap (USD)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for start in range(1, 101, 20):
            data = fetch_json_data(start=start, limit=20)

            for coin in data:
                quote = coin.get('quotes', [{}])[0]
                writer.writerow({
                    'Rank': coin['cmcRank'],
                    'Name': coin['name'],
                    'Symbol': coin['symbol'],
                    'Price (USD)': f"{quote.get('price', 0):.2f}",
                    '24h % Change': f"{quote.get('percentChange24h', 0):.2f}",
                    'Market Cap (USD)': f"${quote.get('marketCap', 0):,.2f}"
                })

            print(f"Fetched coins {start}–{start + 19}")

    elapsed = time.time() - start_time
    print(f"Scraped 100 entries in {elapsed:.2f} seconds (~{100 / elapsed:.2f} req/s)")

if __name__ == "__main__":
    main()
