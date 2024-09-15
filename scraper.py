from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def scrape_f1_driver_data():
    # Initialize WebDriver and load F1 drivers standings page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = 'https://www.formula1.com/en/results/2024/drivers'
    driver.get(url)

    # Locate the table containing driver standings
    standings_data = []
    try:
        # Locate the specific table by class name
        table = driver.find_element(By.CLASS_NAME, 'f1-table')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Loop through table rows and extract driver info (position, name, points)
        for row in rows[1:]:  # Skip the header row
            columns = row.find_elements(By.TAG_NAME, 'td')
            if len(columns) > 1:
                position = columns[0].text.strip()
                driver_name = columns[1].text.strip()
                nationality = columns[2].text.strip()
                car = columns[3].text.strip()
                points = columns[-1].text.strip()
                standings_data.append({
                    'Position': position,
                    'Driver': driver_name,
                    'Nationality': nationality,
                    'Car': car,
                    'Points': points
                })

    except Exception as e:
        print(f"Error scraping F1 driver data: {e}")
    finally:
        driver.quit()

    return standings_data


if __name__ == "__main__":
    driver_standings = scrape_f1_driver_data()
    for standing in driver_standings:
        print(standing)
