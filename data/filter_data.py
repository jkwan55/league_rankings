import json
import os

wanted_keys = ["participantID", "teamID", "goldStats", "championName", "playerName", "totalGold", "stats", "goldPerSecond"]

def create_filtered_file(filename, idx):
    with open(filename, 'r') as file:
        current_object = ""
        start = 0
        obtain10 = False
        obtain20 = False
        for char in file.read():
            if char == '{':
                start += 1
            elif char == '}':
                start -= 1
            current_object += char
            if start == 0 and len(current_object) < 2:
                current_object = ""
            elif start == 0 :
                obj = json.loads(current_object)
                if obj["eventType"] == "game_end":
                    ge = open(os.path.join(directory, "game" + str(idx) + "_gameend.json", "a"))
                    ge.write(current_object)
                    ge.close()
                    print(filename, "game end created")
                elif not obtain10 and obj["eventType"] == "stats_update" and obj["gameTime"] > 600000:
                    update10 = open(os.path.join(directory, "game" + str(idx) + "_update10.json", "a"))

                    obj = json.load(current_object)
                    p = obj['participants']
                    new_list = []
                    for participant in p:
                        new_dict = {key: participant[key] for key in wanted_keys}
                        new_list.append(new_dict)
                    obj['participants'] = new_list
                    new_obj = json.dumps(obj)

                    update10.write(new_obj)
                    update10.close()
                    obtain10 = True
                    print(filename, "update 10 created")
                elif not obtain20 and obj["eventType"] == "stats_update" and obj["gameTime"] > 1200000:
                    update20 = open(os.path.join(directory, "game" + str(idx) + "_update20.json", "a"))

                    obj = json.load(current_object)
                    p = obj['participants']
                    new_list = []
                    for participant in p:
                        new_dict = {key: participant[key] for key in wanted_keys}
                        new_list.append(new_dict)
                    obj['participants'] = new_list
                    new_obj = json.dumps(obj)

                    update20.write(new_obj)
                    update20.close()
                    obtain20 = True
                    print(filename, "update 20 created")
                current_object = ""

def iterate_games():
    directory = "games"
    for idx, filename in enumerate(os.listdir(directory)):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            create_filtered_file(f, idx)
            os.remove(f)
            print("removing game file: ", filename)

if __name__ == "__main__":
    iterate_games()
