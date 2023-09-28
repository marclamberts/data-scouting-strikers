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

    # Calculate percentile ranks for the specified offensive metrics based on the total dataset and convert to 100.0 scale
    percentile_ranks = pd.DataFrame()
    for col in offensive_metrics:
        percentile_ranks[f"{col} Percentile Rank"] = df[col].rank(pct=True) * 100.0

    # Concatenate the percentile ranks DataFrame with the original DataFrame
    df = pd.concat([df, percentile_ranks], axis=1)

    return df

def main():
    st.title("Men strikers 2022-2023")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Choose filters")

    # Load data using the caching function
    file_path = "Complete database.xlsx"
    df = load_and_process_data(file_path)

    # Add a text input for the user to search for a specific player
    search_player = st.text_input("Search Player", "")

    # Filter the data based on the search query and display a bar chart for the selected player
    if search_player:
        filtered_df = df[df["Player"].str.contains(search_player, case=False)]
        if not filtered_df.empty:
            player_name = filtered_df.iloc[0]["Player"]
            player_metrics = filtered_df[offensive_metrics + ['Player']].melt(id_vars=['Player'], var_name='Metric', value_name='Percentile Rank')

            # Create a bar chart for the selected player's offensive metrics
            bar_chart = alt.Chart(player_metrics).mark_bar().encode(
                x=alt.X('Percentile Rank:Q', title='Percentile Rank',
                        axis=alt.Axis(
                            format='0%',
                            values=[i * 0.1 for i in range(11)]  # Custom tick values from 0 to 1 (0% to 100%)
                        ),
                        scale=alt.Scale(domain=[0, 100])  # Limit the x-axis domain to 0-100
                       ),
                y=alt.Y('Metric:N', title='Metric', sort=alt.EncodingSortField(field="Percentile Rank", op="mean", order="descending")),
                tooltip=['Metric', 'Percentile Rank']
            ).properties(width=800, height=600, title=f'{player_name} - Mean Percentile Ranks for Offensive Metrics |@ShePlotsFC')

            st.altair_chart(bar_chart)
            st.write(player_metrics)

    # Add the text at the bottom of the app
    st.markdown("Marc Lamberts @lambertsmarc @ShePlotsFC | Collected at 22-07-2023 | Wyscout")

if __name__ == "__main__":
    main()
