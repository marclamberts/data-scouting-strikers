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
        percentile_ranks[f"{col} Percentile Rank"] = df[col].rank(pct=True) * 100.0

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

    # Create a dropdown for the user to select the first metric for the scatter plot
    selected_metric1 = st.sidebar.selectbox(f"Select {metric_category} Metric 1", relevant_metrics)

    # Create a dropdown for the user to select the second metric for the scatter plot
    selected_metric2 = st.sidebar.selectbox(f"Select {metric_category} Metric 2", relevant_metrics)

    # Sort the DataFrame based on the first selected metric in descending order
    sorted_df = df.sort_values(by=selected_metric1, ascending=False)

    # Add a text input for the user to search for a specific player
    search_player = st.text_input("Search Player", "")

    # Filter the data based on the search query and highlight the data point if found
    if search_player:
        df["Match Search"] = df["Player"].str.contains(search_player, case=False)
        df_highlighted = df[df["Match Search"]]

        # Create the scatter plot with conditional color for the highlighted player
        scatter_plot = alt.Chart(df).mark_circle().encode(
            x=alt.X(selected_metric1, title=selected_metric1),
            y=alt.Y(selected_metric2, title=selected_metric2),
            tooltip=["Player", "Team", "Age", "Minutes played", selected_metric1, selected_metric2,
                     alt.Tooltip(f"{selected_metric1} Percentile Rank:Q", format=".1f"),
                     alt.Tooltip(f"{selected_metric2} Percentile Rank:Q", format=".1f")],
            color=alt.condition(
                alt.datum["Match Search"] == True,
                alt.value("red"),  # Highlighted color (red) for the searched player
                alt.value("steelblue")  # Normal color (steelblue) for other data points
            ),
            size=alt.Size("Minutes played", title="Minutes Played"),
            opacity=alt.value(0.6)
        ).properties(width=800, height=600, title=f"Scatter plot: {selected_metric1} vs. {selected_metric2} |@ShePlotsFC")

        st.altair_chart(scatter_plot)

        # Display the player name, team, and percentile ranks if found in the search
        if not df_highlighted.empty:
            st.markdown(f"Player found: {df_highlighted.iloc[0]['Player']}, Team: {df_highlighted.iloc[0]['Team']}")
            st.write(f"{selected_metric1} Percentile Rank: {df_highlighted.iloc[0][selected_metric1 + ' Percentile Rank']:.1f}")
            st.write(f"{selected_metric2} Percentile Rank: {df_highlighted.iloc[0][selected_metric2 + ' Percentile Rank']:.1f}")

    else:
        # Create the scatter plot without conditional color (no highlighting)
        scatter_plot = alt.Chart(df).mark_circle().encode(
            x=alt.X(selected_metric1, title=selected_metric1),
            y=alt.Y(selected_metric2, title=selected_metric2),
            tooltip=["Player", "Team", "Age", "Minutes played", selected_metric1, selected_metric2,
                     alt.Tooltip(f"{selected_metric1} Percentile Rank:Q", format=".1f"),
                     alt.Tooltip(f"{selected_metric2} Percentile Rank:Q", format=".1f")],
            color=alt.value("steelblue"),  # Normal color (steelblue) for all data points
            size=alt.Size("Minutes played", title="Minutes Played"),
            opacity=alt.value(0.6)
        ).properties(width=800, height=600, title=f"Scatter plot: {selected_metric1} vs. {selected_metric2} |@ShePlotsFC")

        st.altair_chart(scatter_plot)

    # Add the text at the bottom of the app
    st.markdown("Marc Lamberts @lambertsmarc @ShePlotsFC | Collected at 22-07-2023 | Wyscout")

if __name__ == "__main__":
    main()
