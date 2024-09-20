import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Union
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def current_driver_standings() -> List[Dict[str, Union[str, int]]]:
    """
    Scrapes the driver standings from the F1 website using BeautifulSoup.

    :return: List of dictionaries containing driver data: position, driver name, nationality, car, and points.
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
                driver_name = columns[1].text.strip()[:-3]
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


def get_current_session(html_content: str) -> str:
    """
    Scrapes the F1 live timing page to determine the session type using BeautifulSoup.

    :param html_content: The HTML content of the live timing page.
    :return: 'race', 'sprint', or 'other' based on the current session type.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    session_element = soup.find('span', class_='stats_session_left')

    if session_element:
        session_text = session_element.get_text().lower()
        print(session_text)
        if "race" in session_text:
            return "race"
        elif "sprint" in session_text:
            return "sprint"
        elif "quali" in session_text:
            return "quali"

    return "other"


def get_html(use_file: bool = False, file_path: str = 'f1_live_data.html') -> str:
    """
    Retrieves HTML content from the F1 live timing page.

    :param use_file: If True, reads HTML from the specified file instead of fetching from the web.
    :param file_path: The path to the local file containing HTML.
    :return: The HTML content as a string.
    """
    if use_file and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            html = file.read()
        print("Loaded HTML from file.")
    else:
        url = 'https://f1.tfeed.net/live'

        # Set up the Selenium WebDriver
        driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()))
        driver.get(url)

        # Wait for the page to load completely
        time.sleep(5)

        html = driver.page_source

        # Save the HTML to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        print("Fetched HTML from the web and saved to file.")

        driver.quit()

    return html


def get_live_race_order(html_content: str) -> List[str]:
    """
    Retrieves the live race order of drivers from the HTML content.

    :param html_content: The HTML content of the live timing page.
    :return: A list of driver names in their current race order.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    driver_data = []

    rows = soup.find_all('div', id=lambda x: x and x.startswith('stats_d_'))

    for row in rows:
        driver_span = row.find('span', id=lambda x: x and x.endswith('_nick'))
        if driver_span:
            driver_name = driver_span.get_text().strip()
            if driver_name:
                driver_data.append(driver_name)

    return driver_data


def apply_race_points(standings_data: List[Dict], race_order: List[str], session_type: str) -> pd.DataFrame:
    """
    Applies race or sprint points to drivers based on their current race order, updates their positions,
    and sorts the drivers based on their total championship points.

    :param standings_data: The list of dictionaries representing driver standings data.
    :param race_order: The list of driver names in their current race order.
    :param session_type: The session type, either 'race' or 'sprint'.
    :return: A DataFrame with the updated standings, new points applied, and positions updated.
    """
    race_points = {
        # Points if race finishes in quali order
        "quali": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
        "race": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],  # Points for a race
        "sprint": [8, 7, 6, 5, 4, 3, 2, 1]  # Points for a sprint race
    }

    points_to_apply = race_points.get(session_type, [])

    if not race_order:
        print("No live race data available.")
        return pd.DataFrame(standings_data)

    # Convert the standings data into a DataFrame
    standings_df = pd.DataFrame(standings_data)

    # Create an 'Original Position' column
    standings_df['Original Position'] = standings_df.index + 1
    standings_df['Points Predicted in Session'] = 0

    # Apply points based on race order
    for i, driver_name in enumerate(race_order):
        if i < len(points_to_apply):
            # Use regex for flexible name matching and avoid encoding issues
            matching_rows = standings_df[standings_df['Driver'].str.contains(
                driver_name, flags=re.IGNORECASE, regex=True)]

            if not matching_rows.empty:
                standings_df.loc[matching_rows.index,
                                 'Points Predicted in Session'] = points_to_apply[i]

    # Calculate the predicted championship points
    standings_df['Predicted Championship Points'] = standings_df['Points'] + \
        standings_df['Points Predicted in Session']

    # Sort by predicted championship points
    standings_df.sort_values(
        by='Predicted Championship Points', ascending=False, inplace=True)

    # Update the position and calculate positions gained/lost
    standings_df['Position'] = range(1, len(standings_df) + 1)
    standings_df['Positions Gained/Lost'] = standings_df['Original Position'] - \
        standings_df['Position']

    return standings_df


if __name__ == "__main__":
    html_content = get_html()

    session_type = get_current_session(html_content)
    print("Current Session Type:", session_type)

    live_race_order = get_live_race_order(html_content)
    print("Live Race Order:", live_race_order)

    standings = current_driver_standings()

    updated_standings_df = apply_race_points(
        standings, live_race_order, session_type)

    # Output the updated standings DataFrame
    print(updated_standings_df[[
          'Position', 'Driver', 'Points', 'Predicted Championship Points', 'Positions Gained/Lost']])

    print(updated_standings_df.describe())
