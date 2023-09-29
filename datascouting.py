import streamlit as st
import pandas as pd
import altair as alt

# Define the list of offensive metrics
offensive_metrics = [
    'Goals per 90', 'Non-penalty goals per 90', 'Shots per 90', 'xG per 90', 'Assists per 90', 'xA per 90',
    'Crosses per 90', 'Dribbles per 90', 'Offensive duels per 90', 'Touches in box per 90', 'Progressive runs per 90'
]

# Function to read and preprocess the data
@st.cache_data()
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]

    return df

def calculate_percentile_ranks(data, metrics):
    # Calculate percentile ranks for the specified metrics based on all players' data and convert to 100.0 scale
    percentile_ranks = pd.DataFrame()
    for col in metrics:
        percentile_ranks[f"{col} Percentile Rank"] = data[col].rank(pct=True, method='min') * 100.0

    return percentile_ranks

def main():
    st.title("Men strikers 2022-2023")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Choose filters")

    # Load data using the caching function
    file_path = "Complete database.xlsx"
    df = load_and_process_data(file_path)

    # Create a filter to select the specific league
    selected_league = st.sidebar.selectbox("Select League", ["All Leagues"] + df["League"].unique().tolist())

    # Filter the data based on the selected league
    if selected_league != "All Leagues":
        df = df[df["League"] == selected_league]

    # Create a filter to select the specific team
    selected_team = st.sidebar.selectbox("Select Team", ["All Teams"] + df["Team within selected timeframe"].unique().tolist())

    # Filter the data based on the selected team
    if selected_team != "All Teams":
        df = df[df["Team within selected timeframe"] == selected_team]

    # Calculate percentile ranks for the selected data and metrics
    percentile_ranks_df = calculate_percentile_ranks(df, offensive_metrics)

    # Melt the DataFrame for visualization
    melted_df = pd.melt(percentile_ranks_df, var_name='Metric', value_name='Percentile Rank')

    # Create a filter to select the specific player
    selected_player = st.sidebar.selectbox("Select Player", ["All Players"] + df["Player"].unique().tolist())

    # Filter the data based on the selected player
    if selected_player != "All Players":
        melted_df = melted_df[melted_df["Player"] == selected_player]

    # Create a bar chart for the selected player's offensive metrics
    bar_chart = alt.Chart(melted_df).mark_bar().encode(
        x=alt.X('Percentile Rank:Q', title='Percentile Rank', axis=alt.Axis(format='%')),
        y=alt.Y('Metric:N', title='Metric', sort=alt.EncodingSortField(field="Percentile Rank", op="mean", order="descending")),
        tooltip=['Metric', 'Percentile Rank']
    ).properties(width=800, height=600, title=f'Mean Percentile Ranks for Offensive Metrics |@ShePlotsFC')

    # Display the bar chart
    st.altair_chart(bar_chart)

    # Add the text at the bottom of the app
    st.markdown("Marc Lamberts @lambertsmarc @ShePlotsFC | Collected at 22-07-2023 | Wyscout")

if __name__ == "__main__":
    main()
