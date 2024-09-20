import streamlit as st
import pandas as pd
from scraper import current_driver_standings, get_current_session, apply_race_points, get_html, get_live_race_order


def display_f1_standings():
    st.title("Live Driver Standings (if they finish in the current order)")

    # Scrape current driver standings
    standings = current_driver_standings()

    # Check if standings were successfully fetched
    if not standings:
        st.write("No driver standings available.")
        return

    # Get HTML content to determine session type and live race order
    html_content = get_html()

    # Get the current session type (race, sprint, or other)
    session_type = get_current_session(html_content)

    # Display session type
    if session_type in ["race", "sprint", "qualifying"]:
        st.write(f"Session Type: {session_type.capitalize()} in progress.")

        # Get live race order
        live_race_order = get_live_race_order(html_content)

        # Apply race points if it's a race or sprint session
        updated_standings_df = apply_race_points(
            standings, live_race_order, session_type)

        # Display the updated standings
        if not updated_standings_df.empty:
            columns_to_display = [
                'Position', 'Driver', 'Points', 'Points Predicted in Session',
                'Predicted Championship Points', 'Positions Gained/Lost'
            ]

            # Render the table in Streamlit
            st.table(updated_standings_df[columns_to_display])
        else:
            st.write("No live race data available to update standings.")
    else:
        st.write("No points-awarding session in progress.")
        # Display the standings without points update
        standings_df = pd.DataFrame(standings)
        st.table(standings_df[['Position', 'Driver', 'Points']])


if __name__ == "__main__":
    display_f1_standings()
