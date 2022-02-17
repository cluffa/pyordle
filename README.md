# pyordle
A simple command line wordle clone. Scores are saved to a SQL database and leaderboards and game history are printed at the end of a game.  

I created this game to practice Python/SQL and to eventually use for reinforcement learning.  

I have made some game design changes that make it differnt than the official game. There is no special conditions for double letters. For example, the first n in the word runny would be red in the official game. I also decided not to incude a guess limit. I want the focus to be on getting the answer in fewer guesses and not just guessing it. This makes the leaderboards and scoring based on guesses and not win/loss ratio.

See releases for .exe  

| Game      | Game History/Leaderboard |
| ----------- | ----------- |
| ![game](./images/gameplay.png)  | ![stats](./images/stats.png)       |

