import pandas as pd
import requests
from bs4 import BeautifulSoup


def ball_by_ball_score(json_data, match_no, innings):
    data = []
    for cl_node in json_data['commentary']:
        each_ball = cl_node['commentaryList']
        for row in each_ball:
            if 'overNumber' in row:
                over = row['overNumber']
                bowler = row['commText'].split('to')[0].strip()
                batter = row['commText'].split(',')[0].split('to')[1]
                batTeamScore = row['batTeamScore']

                runs = row['commText'].split(',')
                if runs[1].strip().endswith('byes') and not runs[2].isalnum():
                    runs = runs[2].strip()
                else:
                    runs = runs[1].strip().split(' ')[0]

                if runs.strip() == 'B0$':
                    runs = row['commentaryFormats']['bold']['formatValue'][0].upper()

                data.append([match_no, innings, over, batter, bowler, runs])

    # Create dataframe
    df = pd.DataFrame(data, columns=['Match No', 'Innings', 'Over', 'Batter', 'Bowler', 'Actions'])
    return df

url = 'https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches'
api_url ='https://www.cricbuzz.com/api/cricket-match/'
webpage = requests.get(url)
main_soup = BeautifulSoup(webpage.content,'html.parser')
match_links = main_soup.find_all('a',attrs={'class':'text-hvr-underline'})

all_match_dfs = []

for i in range(74):
    match_id = match_links[i].get('href').split('/')[2]
    first_inn = api_url + match_id + '/full-commentary/1'
    second_inn = api_url + match_id + '/full-commentary/2'
    json_data1, json_data2 = requests.get(first_inn).json(), requests.get(second_inn).json()
    df1 = ball_by_ball_score(json_data1, match_no=i + 1, innings=1)
    df2 = ball_by_ball_score(json_data2, match_no=i + 1, innings=2)

    # Append dataframes for both innings to the list
    all_match_dfs.append(df1)
    all_match_dfs.append(df2)

# Concatenate all dataframes in the list into a single dataframe
all_matches_df = pd.concat(all_match_dfs, ignore_index=True)

all_matches_df.head()

df = all_matches_df.sort_values(by=['Match No', 'Innings', 'Over']).copy(deep=True)
df.reset_index(drop=True, inplace=True)


df.loc[[9742, 52,10335, 9534, 8549, 1514, 1493, 1513, 1509, 52, 1545, 1544, 1543, 1540, 1516, 1539, 1538, 1534, 1526, 1521,1524,1543], 'Actions'] = 1
df.loc[[1582, 1580, 1572, 1568, 1567, 1566, 1564, 1563, 1562, 1561,5062, 7913,1597,8623,1592,1585,1590,5119,8017], 'Actions'] = 1
df.loc[[1493,1589,1588,1613], 'Actions'] = 2
df.loc[[1507,1584,1599,10293], 'Actions'] = 'SIX'
df.loc[1507, 'Actions'] = 1
df.loc[[1507, 1522, 1519, 1518, 1517], 'Actions'] = [1, 'SIX', 'no', 2, 2]
df.loc[[1523,1583,8623,9594,9633] , 'Actions']= 'FOUR'
df.loc[1541, 'Actions'] = 'WIDE'
df.loc[[1519,1611,1499,1587,1593,76,1495], 'Actions'] = 'no'

df['Actions'].unique()

def map_actions(action):
    if action in ('WIDE','WIDE,'):
        return 'Extra_W', 1
    elif action in ['3 WIDES', '2 WIDES', '5 WIDES']:
        return 'Extras_W', int(action.split()[0])
    elif action == 'NO BALL':
        return 'Extras_N', 1
    elif action in ['FOUR', 4]:
        return 'Boundary', 4
    elif action in ['SIX', 6,'6']:
        return 'Six', 6
    elif action == '5':
        return 'Extras_O', 5
    elif action in ['1', 1,'1 run']:
        return 'Single', 1
    elif action in ['2', 2,'2 runs']:
        return 'Double', 2
    elif action in ['3', '3 runs']:
        return 'Triple', 3
    elif action == 'no':
        return 'Dot',0
    elif action in('OUT','Wicket'):
        return 'Wicket',0
    else:
        return action,action


df['Action'], df['Runs'] = zip(*df['Actions'].apply(map_actions))

df.drop(columns=['Actions'], inplace=True)
