import json
import os

def edit_filtered_file(filename):
    if 'update' in filename:
        with open(filename, 'r+') as file:
            obj = json.load(file)
            p = obj['participants']
            wanted_keys = ["participantID", "teamID", "goldStats", "championName", "playerName", "totalGold", "stats", "goldPerSecond"]
            new_list = []
            for participant in p:
                new_dict = {key: participant[key] for key in wanted_keys}
                new_list.append(new_dict)
            obj['participants'] = new_list
            new_obj = json.dumps(obj)
            file.seek(0)
            file.truncate()
            file.write(new_obj)

def iterate_games():
    directory = "games"
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            edit_filtered_file(f)
            print('Updated: ', f)

if __name__ == "__main__":
    iterate_games()
