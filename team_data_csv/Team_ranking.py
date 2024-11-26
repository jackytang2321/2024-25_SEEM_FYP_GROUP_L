import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

csv_directory = os.getcwd()
features_columns = [
    'teamkda', 'dragons&barons', 'damagetochampions', 'visionscore', 'earnedgold'
]

def clean_data(df, feature_columns):
    for col in feature_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=feature_columns + ['result'])
    return df

def calculate_team_scores(csv_directory, features_columns):
    all_data = []
    team_names = []
    for filename in os.listdir(csv_directory):
        if filename.endswith('.csv'):
            team_name = os.path.splitext(filename)[0]
            print(f"Processing file: {filename}")
            team_data = pd.read_csv(os.path.join(csv_directory, filename))
            team_names.append(team_name)
            feature_columns = [col for col in features_columns if col in team_data.columns]
            if not feature_columns:
                print(f"No valid features in {filename}. Skipping.")
                continue
            if 'result' not in team_data.columns:
                print(f"'result' column missing in {filename}. Skipping.")
                continue
            team_data = clean_data(team_data, feature_columns)
            if team_data.empty:
                print(f"No valid data after cleaning {filename}. Skipping.")
                continue
            team_data['team'] = team_name
            all_data.append(team_data)
    if not all_data:
        print("No valid data found. Check your CSV files and highlighted columns.")
        return []
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"Combined Data Shape: {combined_data.shape}")
    x = combined_data[features_columns]
    y = combined_data['result']
    teams = combined_data['team']
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    model = LogisticRegression()
    model.fit(x_scaled, y)
    combined_data['score'] = model.predict_proba(x_scaled)[:, 1]
    team_scores = combined_data.groupby('team')['score'].mean().reset_index()
    team_scores = team_scores.sort_values(by='score', ascending=False)
    return team_scores

team_scores = calculate_team_scores(csv_directory, features_columns)
print("Team Rankings Based on Performance Scores:")
if not team_scores.empty:
    for rank, row in team_scores.iterrows():
        print(f"{rank + 1}. {row['team']} - Score: {row['score']:.2f}")
else:
    print("No rankings to display.")
