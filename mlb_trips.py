import requests
import json
from datetime import datetime
import pytz
from tabulate import tabulate

def get_mlb_saturday_home_games():
    # Teams you want to check (with their MLB team IDs)
    teams = {
        "Atlanta Braves": 144,
        "Chicago White Sox": 145,
        "Milwaukee Brewers": 158,
        "Minnesota Twins": 142,
        "Washington Nationals": 120,
        "St. Louis Cardinals": 138,
        "Cincinnati Reds": 113,
        "Cleveland Guardians": 114,
        "Colorado Rockies": 115
    }
    
    # Get the current year
    year = 2025
    
    # Initialize a dictionary to store results
    saturday_home_games = {}
    
    # MLB Stats API base URL
    base_url = "https://statsapi.mlb.com/api/v1"
    
    # Eastern timezone for converting game times
    eastern = pytz.timezone('US/Eastern')
    
    # Process each team
    for team_name, team_id in teams.items():
        print(f"Getting schedule for {team_name}...")
        
        # Endpoint for the team's schedule for the specified year
        schedule_url = f"{base_url}/schedule"
        params = {
            "teamId": team_id,
            "season": year,
            "sportId": 1,  # MLB
            "gameType": "R",  # Regular season games
            "hydrate": "team,venue"
        }
        
        # Send the request
        response = requests.get(schedule_url, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error fetching schedule for {team_name}: {response.status_code}")
            continue
        
        # Parse the response
        data = response.json()
        
        # Initialize list to store this team's Saturday home games
        saturday_home_games[team_name] = []
        
        # Go through each date in the schedule
        for date_info in data.get("dates", []):
            for game in date_info.get("games", []):
                # Parse the game date
                game_date_str = game.get("gameDate")
                if not game_date_str:
                    continue
                
                # Convert to datetime object
                game_date = datetime.fromisoformat(game_date_str.replace("Z", "+00:00"))
                game_date_eastern = game_date.astimezone(eastern)
                
                # Check if this is a Saturday game
                if game_date_eastern.weekday() == 5:  # 5 corresponds to Saturday
                    # Check if this team is the home team
                    if game.get("teams", {}).get("home", {}).get("team", {}).get("id") == team_id:
                        # Check if this is a day game (before 5 PM Eastern)
                        is_day_game = game_date_eastern.hour < 17
                        
                        # Format the date for output
                        formatted_date = game_date_eastern.strftime("%Y-%m-%d")
                        
                        # Format the time for output
                        formatted_time = game_date_eastern.strftime("%I:%M %p ET")
                        
                        # Get the away team name
                        away_team = game.get("teams", {}).get("away", {}).get("team", {}).get("name", "Unknown")
                        
                        # Only add day games (before 5 PM Eastern)
                        if is_day_game:
                            saturday_home_games[team_name].append({
                                "date": formatted_date,
                                "time": formatted_time,
                                "opponent": away_team,
                                "venue": game.get("venue", {}).get("name", "Unknown")
                            })
    
    # Return the results
    return saturday_home_games

def print_saturday_home_games(saturday_home_games):
    # Print the results
    for team, games in saturday_home_games.items():
        if games:
            print(f"\n{team} Saturday Afternoon Home Games:")
            
            # Prepare data for tabulate
            table_data = []
            for game in games:
                table_data.append([
                    game["date"],
                    game["time"],
                    game["opponent"],
                    game["venue"]
                ])
                
            # Print the table
            print(tabulate(table_data, headers=["Date", "Time", "Opponent", "Venue"], tablefmt="grid"))
        else:
            print(f"\n{team}: No Saturday afternoon home games found.")

def main():
    saturday_home_games = get_mlb_saturday_home_games()
    print_saturday_home_games(saturday_home_games)
    
    # Also save to a JSON file
    with open("mlb_saturday_afternoon_home_games_2025.json", "w") as f:
        json.dump(saturday_home_games, f, indent=4)
    
    print("\nResults also saved to 'mlb_saturday_afternoon_home_games_2025.json'")

if __name__ == "__main__":
    main()