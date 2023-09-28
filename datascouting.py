import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.stats import rankdata

# Function to read and preprocess the data
@st.cache
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    df = df[df['Position'].notna()]  # Exclude rows with empty values in the "Position" column
    df = df[df['Position'].str.contains('CF')]
    df = df[df['Minutes played'] >= 500]
    df.reset_index(drop=True, inplace=True)
    return df

def main():
    st.title("Player Percentile Ranks")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Choose a Player")

    # Load data using the caching function
    file_path = "Complete database.xlsx"
    df = load_and_process_data(file_path)

    # Create a dropdown for the user to select a player in the sidebar
    players = ["Select a Player"] + df["Player"].unique().tolist()
    selected_player = st.sidebar.selectbox("Select Player", players)

    if selected_player != "Select a Player":
        # Filter data for the specific player
        player_df = df[df['Player'] == selected_player]

        # Define the desired order of metrics
        metrics = ['Goals per 90', 'Non-penalty goals per 90', 'xG per 90', 'Head goals per 90', 'Shots per 90', 'Shots on target, %',
                   'Assists per 90', 'xA per 90', 'Crosses per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Offensive duels won, %',
                   'Touches in box per 90', 'Progressive runs per 90']

        # Calculate percentile ranks for each metric
        percentile_ranks = {}
        for metric in metrics:
            percentile_ranks[metric] = rankdata(df[metric], method='average') / len(df) * 99

        # Define colors and create a colormap
        colors = ['red', 'orange', 'green']
        cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors)

        # Create a bar graph
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='#424242')
        ax.set_facecolor('#424242')

        for i, metric in enumerate(metrics):
            metric_value = player_df[metric].values[0]
            percentile_rank = percentile_ranks[metric][player_df.index[0]]
            color = cmap(percentile_rank / 99)  # Assign color based on percentile rank
            bar = ax.barh(i, percentile_rank, alpha=0.7, color=color)
            ax.text(
                bar[0].get_width() + 2, bar[0].get_y() + bar[0].get_height() / 2, f'{int(percentile_rank)}', va='center', ha='left',
                color='white'  # Set the text color to white
            )

        ax.axvline(50, color='lightgrey', linestyle='--', label='50th Percentile Rank')

        ax.set_ylim(len(metrics) - 0.5, -0.5)
        ax.set_yticks(range(len(metrics)))
        ax.set_yticklabels(metrics, color='white')  # Set the tick labels color to white

        max_percentile_rank = max([max(percentile_ranks[metric]) for metric in metrics])
        ax.set_xlim(0, max_percentile_rank + 10)

        ax.set_xlabel('Percentile Ranks', color='white')
        ax.set_ylabel('Metrics', color='white')
        ax.set_yticklabels(metrics, color='white')  # Set the tick labels color to white

        team_name = player_df['Team within selected timeframe'].values[0]
        ax.set_title(f'Player: {selected_player} ({team_name})', fontsize=35, color='white')

        ax.legend().remove()

        ax.text(
            -0.15,
            -0.10,
            'Percentile ranks calculated against CF | Primeira 2022-2023 | @lambertsmarc - Marc Lamberts | Wyscout',
            transform=ax.transAxes,
            fontsize=15,
            color='white'  # Set the text color to white
        )

        ax.spines['top'].set_visible(False)  # Hide the top spine
        ax.spines['right'].set_visible(False)  # Hide the right spine
        ax.spines['bottom'].set_visible(False)  # Hide the bottom spine
        ax.spines['left'].set_visible(False)  # Hide the left spine

        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='x', colors='white')

        plt.subplots_adjust(left=0.2)

        # Save the plot as PNG with transparent background
        plt.savefig(f'{selected_player}.png', dpi=500, facecolor="#424242")

        # Display the plot in Streamlit
        st.pyplot(fig)
    else:
        st.write("Please select a player from the sidebar.")

if __name__ == "__main__":
    main()
