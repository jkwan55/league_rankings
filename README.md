# league_rankings
website: ~~http://ec2-54-193-47-8.us-west-1.compute.amazonaws.com/~~
## Inspiration
  Hackathon to rank league of legends teams. I feel like I have worked on something similar and worked toward the same approach.
## What it does
  Use data given from json files to rank league of legends teams base on varaibles like totalGold advantage and structure advantages.
## How we built it
  Grab the big json files and filter out the needed information and make them smaller json files. Load the new json files and average out the variables per player and average the values for each team. Change weights based on previous winners.
## Challenges we ran into
  Virtual Machine memory when reading large JSON files. To solve this, I read the JSON file character by character to figure out when an object in the array ends and load one object at a time. Save the new object if needed into new file and remove the file when done. This allows me to save space and read it much quicker. Lastly, the amount of games are huge and each file takes a good amount of space, so the VM used ran out of space quickly and I could only do 2 tournaments, I chose lcs 2022 and 2023.
## Accomplishments that we're proud of
  The project was very interesting and made me think about the solution constantly. The ideas kept coming in about what approach to do, do we use ML to get the weights, which variables to grab from the JSON, and many more. I am proud with the limited time I had and the process it took to figure out how to use the JSON files, how to get the varibles, and how to figure out the weights for the calculations.
## What we learned
  Python JSON loads the files right away which runs into VM memory problems. Packages like ijson does not work because the json given is an array of objects in one line, so you cannot go one line at a time. 
## What's next for League Team Rankings
  The next possible advancement I can think of is adding new variables that are given from the JSON and figuring out their importance in ranking the teams. 
