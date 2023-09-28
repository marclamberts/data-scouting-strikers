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
            player_metrics = filtered_df.melt(id_vars=['Player'], var_name='Metric', value_name='Value')

            # Create a bar chart for the selected player's metrics
            bar_chart = alt.Chart(player_metrics).mark_bar().encode(
                x=alt.X('Value:Q', title='Value', scale=alt.Scale(domain=[0, 100])),
                y=alt.Y('Metric:N', title='Metric', sort=alt.EncodingSortField(field="Value", op="mean", order="descending")),
                tooltip=['Metric', 'Value']
            ).properties(width=800, height=600, title=f'{player_name} - Metrics |@ShePlotsFC')

            st.altair_chart(bar_chart)
            st.write(player_metrics)

    # Add the text at the bottom of the app
    st.markdown("Marc Lamberts @lambertsmarc @ShePlotsFC | Collected at 22-07-2023 | Wyscout")

if __name__ == "__main__":
    main()
