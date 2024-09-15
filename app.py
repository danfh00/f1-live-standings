import streamlit as st
from scraper import scrape_f1_driver_data

# Streamlit app


def display_f1_standings():
    st.title("Live Driver Standings")

    # Fetch the data using the scraper
    standings_data = scrape_f1_driver_data()

    if standings_data:
        # Display the standings in a table
        st.table(standings_data)
    else:
        st.write("No live data available.")


if __name__ == "__main__":
    display_f1_standings()
