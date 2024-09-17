import requests
from bs4 import BeautifulSoup


def scrape_f1_driver_data():
    """
    Scrapes the driver standings from the F1 website using BeautifulSoup.
    """
    url = 'https://www.formula1.com/en/results/2024/drivers'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from F1 website: Status Code {
              response.status_code}")
        return []

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table that contains driver standings
    table = soup.find('table', class_='f1-table')
    standings_data = []

    if table:
        # Find all rows in the table
        rows = table.find_all('tr')

        # Extract driver standings (skip the first row which is the header)
        for row in rows[1:]:
            columns = row.find_all('td')
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
                    'Points': int(points)
                })
    else:
        print("No table found on the page.")

    return standings_data


def get_current_session():
    """
    Scrapes the F1 live timing page to determine the session type using BeautifulSoup.
    Returns 'race', 'sprint', or 'other'.
    """
    url = 'https://www.formula1.com/en/timing/f1-live-lite'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching session data from F1 website: Status Code {
              response.status_code}")
        return "other"

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the session type (this is just an example, you need to inspect the page for the actual HTML structure)
    session_type = 'other'
    session_element = soup.find('h2', class_='f1-heading')

    if session_element:
        session_text = session_element.text.lower()
        if "race" in session_text:
            session_type = "race"
        elif "sprint" in session_text:
            session_type = "sprint"

    return session_type


def get_live_race_order():
    """
    Scrapes the F1 live timing page to get the current race order.
    """
    url = 'https://www.formula1.com/en/timing/f1-live-lite'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching live timing page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the table that contains the race order
    try:
        table = soup.find('table', class_='f1-table')
        rows = table.find_all('tr')

        # List to store the current race order
        race_order = []

        # Loop through the rows, assuming driver names are in the second column
        for row in rows[1:]:  # Skipping header row
            columns = row.find_all('td')
            if len(columns) > 1:
                # Assuming the driver name is in the 2nd column
                driver_name = columns[1].text.strip()
                race_order.append(driver_name)

        return race_order

    except Exception as e:
        print(f"Error parsing the race order: {e}")
        return []


def apply_race_points(standings_data, session_type):
    """
    Applies race or sprint points to drivers based on their current race order.
    """
    race_points = {
        "race": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],  # Points for a race
        "sprint": [8, 7, 6, 5, 4, 3, 2, 1]  # Points for a sprint race
    }

    # Get the relevant points system based on session type
    points_to_apply = race_points.get(session_type, [])

    # Get the live race order by scraping the F1 live timing page
    race_order = get_live_race_order()

    if not race_order:
        print("No live race data available.")
        return standings_data

    # Apply the points to drivers in the current standings based on their race order
    for i, driver_name in enumerate(race_order):
        for driver in standings_data:
            if driver['Driver'] == driver_name:
                if i < len(points_to_apply):  # Ensure we're within the points range
                    driver['Points'] += points_to_apply[i]

    return standings_data


if __name__ == "__main__":
    driver_standings = scrape_f1_driver_data()
    for standing in driver_standings:
        print(standing)

    print(get_current_session())
