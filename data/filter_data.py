import json
import os

def create_filtered_file(filename):
    with open('filename', 'r') as file:
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
                    ge = open(filename[:-5] + "_gameend" + filename[-5:], "a")
                    ge.write(current_object)
                    ge.close()
                elif not obtain10 and obj["eventType"] == "stats_update" and obj["gameTime"] > 600000:
                    update10 = open(filename[:-5] + "_update10" + filename[-5:], "a")
                    update10.write(current_object)
                    update10.close()
                    obtain10 = True
                elif not obtain20 and obj["eventType"] == "stats_update" and obj["gameTime"] > 1200000:
                    update20 = open(filename[:-5] + "_update20" + filename[-5:], "a")
                    update20.write(current_object)
                    update20.close()
                    obtain20 = True
                current_object = ""

def iterate_games():
    directory = "games"
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            create_filtered_file(f)
            os.remove(f)

if __name__ == "__main__":
    iterate_games()
