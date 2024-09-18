import streamlit as st
import pandas as pd
from scraper import scrape_f1_driver_data, get_current_session, apply_race_points


def display_f1_standings():
    st.title("Live Driver Standings")

    # Scrape current driver standings
    updated_standings = scrape_f1_driver_data()

    # Get the current session type (race, sprint, or other)
    session_type = get_current_session()

    if session_type in ["race", "sprint"]:
        st.write(f"Session Type: {session_type.capitalize()} in progress.")
        # Apply race points if it's a race or sprint session
        updated_standings = apply_race_points(updated_standings, session_type)
    else:
        st.write("No points-awarding session in progress.")

    # Display the standings in a table
    if updated_standings:
        df = pd.DataFrame(updated_standings)

        columns_to_display = [
            'Position', 'Driver', 'Current Championship Points', 'Points Predicted in Session',
            'Predicted Championship Points', 'Positions Gained/Lost'
        ]

        st.table(df[columns_to_display].style.hide(axis='index'))
    else:
        st.write("No live data available.")


if __name__ == "__main__":
    display_f1_standings()
