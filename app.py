import streamlit as st
from scraper import scrape_f1_driver_data, get_current_session, apply_race_points


def display_f1_standings():
    st.title("Live Driver Standings")

    # Scrape current driver standings
    standings_data = scrape_f1_driver_data()

    # Get the current session type (race, sprint, or other)
    session_type = get_current_session()

    if session_type in ["race", "sprint"]:
        st.write(f"Session Type: {session_type.capitalize()} in progress.")
        # Apply race points if it's a race or sprint session
        standings_data = apply_race_points(standings_data, session_type)
    else:
        st.write("No points-awarding session in progress.")

    # Display the standings in a table
    if standings_data:
        st.table(standings_data)
    else:
        st.write("No live data available.")


if __name__ == "__main__":
    display_f1_standings()
