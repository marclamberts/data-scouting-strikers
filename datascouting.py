import streamlit as st
import pandas as pd
import altair as alt

# Function to read and preprocess the data
@st.cache
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]

    # Calculate percentile ranks for all metrics based on the total dataset and convert to 100.0 scale
    percentile_ranks = pd.DataFrame()
    for col in df.columns[6:]:
        percentile_ranks[f"{col} Percentile Rank"] = df[col].rank(pct=True) * 100.0

    # Concatenate the percentile ranks DataFrame with the original DataFrame
    df = pd.concat([df, percentile_ranks], axis=1)

    return df

def main():
    st.title("Data scouting app")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Choose filters")

    # Create a button to switch to the "Search Players" page
    search_players_button = st.sidebar.button("Search Players")

    if search_players_button:
        show_search_players_page()
    else:
        show_main_page()

def show_main_page():
    # Set the minimal minutes to 500 using the slider in the sidebar
    min_minutes_played = st.sidebar.slider("Minimum Minutes Played", min_value=0, max_value=2000, value=500, step=100)

    # Load data using the caching function
    file_path = "Scouting database 31-10-2023.xlsx"
    df = load_and_process_data(file_path)

    # Create a dropdown for the user to select a league in the sidebar
    leagues = df["League"].unique()
    selected_league = st.sidebar.selectbox("Select League", leagues)

    # Create a dropdown for the user to select a team within the selected league in the sidebar
    teams_in_selected_league = df[df["League"] == selected_league]["Team within selected timeframe"].unique()
    selected_team = st.sidebar.selectbox("Select Team", teams_in_selected_league, key="team_filter")

    # Calculate percentile ranks for all metrics based on the filtered dataset and convert to 100.0 scale
    filtered_df = df[(df["League"] == selected_league) & (df["Team within selected timeframe"] == selected_team) & (df["Minutes played"] >= min_minutes_played)]

    # Create a dropdown for the user to select a metric category in the sidebar
    metric_category = st.sidebar.selectbox("Select Metric Category", ["Offensive", "Defensive", "Passing"])

    # Determine the relevant metrics based on the selected category
    if metric_category == "Offensive":
        relevant_metrics = [
            'Goals per 90', 'Non-penalty goals per 90', 'Shots per 90', 'xG per 90', 'Assists per 90', 'xA per 90',
            'Crosses per 90', 'Dribbles per 90', 'Offensive duels per 90', 'Touches in box per 90',
            'Progressive runs per 90'
        ]
    elif metric_category == "Defensive":
        relevant_metrics = [
            'Defensive duels per 90', 'Defensive duels won, %', 'Aerial duels per 90', 'Aerial duels won, %', 
            'Shots blocked per 90', 'PAdj Sliding tackles', 'PAdj Interceptions', 'Fouls per 90'
        ]
    else:
        relevant_metrics = [
            'Passes per 90', 'Accurate passes, %', 'Assists per 90', 'xA per 90', 'Second assists per 90',
            'Third assists per 90', 'Key passes per 90', 'Passes to final third per 90', 'Passes to penalty area per 90',
            'Through passes per 90', 'Deep completions per 90', 'Progressive passes per 90'
        ]

    # Sort the filtered DataFrame based on the selected metric in descending order
    selected_metric = st.sidebar.selectbox(f"Select {metric_category} Metric", relevant_metrics)

    sorted_df = filtered_df.sort_values(by=selected_metric, ascending=False)


    # Display the team filter on the left column
    st.sidebar.write(f"Selected Team: {selected_team}")

    # Display the graph for the selected metric category in the main column
    chart_data = sorted_df.head(15)
    chart = alt.Chart(chart_data)

