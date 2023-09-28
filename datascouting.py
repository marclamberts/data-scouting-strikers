import streamlit as st
import pandas as pd
import altair as alt

# Function to read and preprocess the data
@st.cache_data()
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]

    # Calculate percentile ranks for all metrics based on the total dataset and convert to 100.0 scale
    percentile_ranks = pd.DataFrame()
    for col in df.columns[6:]:
        percentile_ranks[f"{col} Percentile Rank"] = df[col].rank(pct=True)

    # Concatenate the percentile ranks DataFrame with the original DataFrame
    df = pd.concat([df, percentile_ranks], axis=1)

    return df

def main():
    st.title("Men strikers 2022-2023")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Choose filters")

    # Set the minimal minutes to 500 using the slider in the sidebar
    min_minutes_played = st.sidebar.slider("Minimum Minutes Played", min_value=0, max_value=2000, value=500, step=100)

    # Load data using the caching function
    file_path = "Complete database.xlsx"
    df = load_and_process_data(file_path)

    # Create a dropdown for the user to select a league in the sidebar
    leagues = ["All Leagues"] + df["League"].unique().tolist()
    selected_league = st.sidebar.selectbox("Select League", leagues)

    # Filter the data based on the selected league
    if selected_league != "All Leagues":
        df = df[df["League"] == selected_league]

    # Create a dropdown for the user to select a team within the selected league in the sidebar
    teams = ["All Teams"] + df["Team within selected timeframe"].unique().tolist()
    selected_team = st.sidebar.selectbox("Select Team", teams)

    # Filter the data based on the selected team
    if selected_team != "All Teams":
        df = df[df["Team within selected timeframe"] == selected_team]

    # Filter the data based on the minimum minutes played
    df = df[df["Minutes played"] >= min_minutes_played]

    # Create a dropdown for the user to select a metric category in the sidebar
    metric_category = st.sidebar.selectbox("Select Metric Category", ["Offensive", "Defensive", "Passing"])

    # Define the full list of offensive metrics
    offensive_metrics = [
        'Goals per 90', 'Non-penalty goals per 90', 'Shots per 90', 'xG per 90', 'Assists per 90', 'xA per 90',
        'Crosses per 90', 'Dribbles per 90', 'Offensive duels per 90', 'Touches in box per 90', 'Progressive runs per 90'
    ]

    # Check if the selected category is Offensive and display the bar chart for offensive metrics
    if metric_category == "Offensive":
        # Calculate the mean percentile rank for each offensive metric
        mean_percentiles = df[offensive_metrics + ['Player']].melt(id_vars=['Player'], var_name='Metric', value_name='Percentile Rank')
        
        # Create a bar chart with percentile rank on the x-axis and metrics on the y-axis
        bar_chart = alt.Chart(mean_percentiles).mark_bar().encode(
            x=alt.X('Percentile Rank:Q', title='Percentile Rank', 
                    axis=alt.Axis(format='%'),  # Format the x-axis as a percentage
                    scale=alt.Scale(domain=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
                   ),
            y=alt.Y('Metric:N', title='Metric', sort=alt.EncodingSortField(field="Percentile Rank", op="mean", order="descending")),
            tooltip=['Metric', alt.Tooltip('Percentile Rank:Q', title='Percentile Rank', format='.0%')]
        ).properties(width=800, height=600, title=f'Mean Percentile Ranks for Offensive Metrics |@ShePlotsFC')

        st.altair_chart(bar_chart)

    # Add a text input for the user to search for a specific player
    search_player = st.text_input("Search Player", "")

    # Filter the data based on the search query and display a bar chart for the selected player
    if search_player:
        filtered_df = df[df["Player"].str.contains(search_player, case=False)]
        if not filtered_df.empty:
            player_name = filtered_df.iloc[0]["Player"]
            player_metrics = filtered_df[offensive_metrics + ['Player']].melt(id_vars=['Player'], var_name='Metric', value_name='Percentile Rank')

            # Create a bar chart for the selected player's offensive metrics
            player_bar_chart = alt.Chart(player_metrics).mark_bar().encode(
                x=alt.X('Percentile Rank:Q', title='Percentile Rank',
                        axis=alt.Axis(format='%'),  # Format the x-axis as a percentage
                        scale=alt.Scale(domain=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
                       ),
                y=alt.Y('Metric:N', title='Metric', sort=alt.EncodingSortField(field="Percentile Rank", op="mean", order="descending")),
                tooltip=['Metric', alt.Tooltip('Percentile Rank:Q', title='Percentile Rank', format='.0%')]
            ).properties(width=800, height=600, title=f'{player_name} - Mean Percentile Ranks for Offensive Metrics |@ShePlotsFC')

            st.altair_chart(player_bar_chart)

    # Add the text at the bottom of the app
    st.markdown("Marc Lamberts @lambertsmarc @ShePlotsFC | Collected at 22-07-2023 | Wyscout")

if __name__ == "__main__":
    main()
