import streamlit as st
import pandas as pd

# Function to read and preprocess the data
@st.cache
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def main():
    st.title("Data scouting app")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Search")

    # Load data using the caching function
    file_path = "Scouting database 31-10-2023.xlsx"
    df = load_and_process_data(file_path)

    # Create a text input for the user to enter a player name
    player_name = st.sidebar.text_input("Search Player by Name")

    # Create a text input for the user to enter a team name
    team_name = st.sidebar.text_input("Search Team by Name")

    if player_name:
        # Search for the player in the DataFrame and display their information
        player_info = df[df['Player'].str.contains(player_name, case=False, na=False)]
        if not player_info.empty:
            st.write(player_info[['Player', 'Age', 'Team', 'Minutes played', 'Goals', 'Assists', 'xG', 'xA']])
        else:
            st.write("Player not found")

    if team_name:
        # Search for the team in the DataFrame and display all players from that team
        players_in_team = df[df['Team'].str.contains(team_name, case=False, na=False)]
        if not players_in_team.empty:
            st.write(players_in_team[['Player', 'Age', 'Team', 'League', 'Minutes played', 'Goals', 'Assists', 'xG', 'xA']])
        else:
            st.write("Team not found")

if __name__ == "__main__":
    main()
