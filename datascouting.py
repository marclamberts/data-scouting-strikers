import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import math
from mplsoccer import PyPizza, add_image
import matplotlib.pyplot as plt

# Function to read and preprocess the data
@st.cache
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]
    # Filter and rename columns
    metrics_to_keep = ['Player','Team', 'Position', 'Age', 'Matches played', 'Minutes played','Goals per 90', 'xG per 90', 'Shots on target, %', 'Dribbles per 90', 'Progressive runs per 90',
                      'Defensive duels won, %', 'Aerial duels won, %', 'PAdj Sliding tackles', 'PAdj Interceptions', 'Shots blocked per 90',
                      'xA per 90', 'Key passes per 90', 'Passes to final third per 90', 'Passes to penalty area per 90', 'Through passes per 90', 'Progressive passes per 90']
    filtered_df = df[metrics_to_keep]
    filtered_df.rename(columns={
        'Goals per 90': 'Goals',
        'xG per 90': 'xG',
        'Dribbles per 90': 'Dribbles',
        'Progressive runs per 90': 'Prog. runs',
        'Defensive duels won, %': 'Def. duels%',
        'Aerial duels won, %': 'Aerial duels %',
        'PAdj Sliding tackles': 'PAdj tackles',
        'Shots blocked per 90': 'Shots blocked',
        'xA per 90': 'xA',
        'Key passes per 90': 'Key passes',
        'Passes to final third per 90': 'Passes final 3rd',
        'Passes to penalty area per 90': 'Passes to box',
        'Through passes per 90': 'Through pass',
        'Progressive passes per 90': 'Prog. passes'
    }, inplace=True)
    return filtered_df

def main():
    st.title("Data Scouting App")

    # Create a sidebar column on the left for filters
    st.sidebar.title("Search")

    # Load data using the caching function
    file_path = "Database Men.xlsx"
    df = load_and_process_data(file_path)

    # Create a dropdown menu for the user to select a league
    league = st.sidebar.selectbox("Select League", options=df['League'].unique())

    # Create a dropdown menu for the user to select a team based on the selected league
    teams_in_league = df[df['League'] == league]['Team'].unique()
    team_name = st.sidebar.selectbox("Select Team", options=teams_in_league)

    # Create a text input for the user to enter a player name
    player_name = st.sidebar.text_input("Search Player by Name")

    if player_name:
        # Search for the player in the DataFrame and display their information
        player_info = df[df['Player'].str.contains(player_name, case=False, na=False)]
        if not player_info.empty:
            st.write(player_info[['Player', 'Age', 'Team', 'Position', 'Minutes played', 'Goals', 'Assists', 'xG', 'xA']])
            generate_pizza_chart(df, player_name)
        else:
            st.write("Player not found")

    if team_name:
        # Search for the team in the DataFrame and display all players from that team
        players_in_team = df[df['Team'].str.contains(team_name, case=False, na=False)]
        if not players_in_team.empty:
            st.write(players_in_team[['Player', 'Age', 'Team', 'Position', 'League', 'Minutes played', 'Goals', 'Assists', 'xG', 'xA']])
        else:
            st.write("Team not found")

def generate_pizza_chart(df, player_name):
    # Filter based on minutes played and position
    df = df[df['Minutes played'] >= 300]
    positions_to_filter = ['CF']
    filtered_df = df[df['Position'].isin(positions_to_filter)]

    # Drop unnecessary columns and reset index
    df = df.drop(['Team', 'Position', 'Age', 'Matches played', 'Minutes played'], axis=1).reset_index()

    # Create a parameter list
    params = list(df.columns)
    params = params[2:]

    # Select the player and get their data
    player_df = df.loc[df['Player'] == player_name].reset_index()
    if player_df.empty:
        st.write("Player data not available for pizza chart.")
        return
    player = list(player_df.loc[0])

    # Drop the first 3 items from the player list to align with params
    player = player[3:]

    # Calculate percentile values
    values = []
    for x in range(len(params)):   
        values.append(math.floor(stats.percentileofscore(df[params[x]], player[x])))

    # Ensure no value is exactly 100
    values = [99 if v == 100 else v for v in values]

    # Initialize PyPizza
    baker = PyPizza(
        params=params,                  # list of parameters
        straight_line_color="white",    # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=1,               # linewidth of last circle
        other_circle_lw=1,              # linewidth for other circles
        other_circle_ls="-."            # linestyle for other circles
    )

    # Color for the slices and text
    slice_colors = ["#003f5c"] * 5 + ["#ff6361"] * 5 + ["#ffa600"] * 6
    text_colors = ["#000000"] * 8 + ["white"] * 5

    # Load logo image
    logo_image = plt.imread('/Users/marclambertes/Downloads/Outswinger FC (3).png')

    # Plot pizza
    fig, ax = baker.make_pizza(
        values,              # list of values
        figsize=(10, 10),    # adjust figsize according to your need
        param_location=110,  # where the parameters will be added
        color_blank_space="same",
        slice_colors=slice_colors,
        kwargs_slices=dict( 
            edgecolor="white",
            zorder=2, linewidth=1
        ),                   # values to be used when plotting slices
        kwargs_params=dict(
            color="white", fontsize=12,
            va="center", alpha=.8
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="white", fontsize=12,
            zorder=3,
            bbox=dict(
                edgecolor="white", facecolor="#000000",
                boxstyle="round,pad=0.2", lw=1
            )
        )                    # values to be used when adding parameter-values
    )
    add_image(logo_image, fig, left=0.001, bottom=1, width=0.2, height=0.1, zorder=15)

    fig.text(
        0.515, 0.97, f"{player_name}\n\n", size=35,
        ha="center", color="white"
    )

    fig.text(
        0.515, 0.932,
        f"Per 90 Percentile Rank for position 23-24\n\n",
        size=15,
        ha="center", color="white"
    )

    fig.text(
        0.03, 0.005, "Minimal 300 minutes", color="white"
    )

    # Add credits
    notes = '@lambertsmarc'
    CREDIT_1 = "by Marc Lamberts | @lambertsmarc \ndata: Wyscout\nAll units per 90"
    CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

    fig.text(
        0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        color="white",
        ha="right"
    )

    # Add text
    fig.text(
        0.34, 0.935, "Attacking            Defending         Key passing                ", size=14, color="white"
    )

    # Add rectangles
    fig.patches.extend([
        plt.Rectangle(
            (0.31, 0.9325), 0.025, 0.021, fill=True, color="#003f5c",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.475, 0.9325), 0.025, 0.021, fill=True, color="#ff6361",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.632, 0.9325), 0.025, 0.021, fill=True, color="#ffa600",
            transform=fig.transFigure, figure=fig
        ),
    ])

    # Save the figure
    plt.savefig(f'{player_name}.png', dpi=750, bbox_inches='tight', facecolor='#051650')
    
    # Display the pizza chart in Streamlit
    st.pyplot(fig)

if __name__ == "__main__":
    main()
