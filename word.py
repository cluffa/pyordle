# %%
from turtle import color
from termcolor import colored
from random import sample
from pyfiglet import figlet_format
from datetime import datetime
import os
import psycopg2
import uuid

# load data
from words_lists import words as wordslist, answers as answerslist

clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")

# spacing specs by font
# width, cut off left, cut off right
FONT_DICT = {
    "standard":(12, 0, 0),
    "small":(10, 0, 0),
    "5lineoblique":(15, 0, 1),
    "alphabet":(7, 0, 1),
    "banner":(9, 0, 1),
    "big":(14, 0, 0), # first letter A breaks
    "binary":(9, 0, 1),
    "block":(16, 0, 0),
    "colossal":(13, 0, 1),
    "doh":(43, 0, 0),
    "doom":(8, 0, 0),
    "dotmatrix":(18, 0, 2),
    "roman":(24, 0, 1)
    }

VERT_SEP = "|"
HOR_SEP = "="
FONT = "small"
WORD_LEN = 5
CAN_LOSE = False
NUM_TRYS = 6
GLOBAL_WIDTH, CUT_LEFT, CUT_RIGHT = FONT_DICT[FONT]
SEP_LEN = ((GLOBAL_WIDTH + len(VERT_SEP))*WORD_LEN + len(VERT_SEP)) // len(HOR_SEP) if len(HOR_SEP) != 0 else 0

# setup postgresSQL connection
CONNECTION = psycopg2.connect(
        database="wizozyvz",
        user="wizozyvz",
        password="mvvteKfWqScUK0bWFxMo89x8SKfVP2h-",
        host="kashin.db.elephantsql.com",
        port=None
    )

# game
class wordpy():
    def __init__(self, answer:str = None):
        self.game_setup(answer)

    def game_setup(self, answer:str = None):
        self.guesses = []
        self.colors = []
        self.name = ""
        self.win = False
        self.all_output = HOR_SEP*SEP_LEN

        # randomly pick word for answer
        if answer == None:
            self.answer = sample(answerslist, 1)[0]
        else:
            self.answer = answer
        
        # keeps track of "keyboard" colors 
        self.guess_letters = dict(zip(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
            "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
            ["white"]*26
            ))
    
    def play_game(self):
        clearConsole()
        print("Game started... \nType a 5 letter word or press return to give up and view stats...")
        
        # input loop
        while True:
            guess = input("").lower()

            # exit condition
            if guess == "":
                print("the word was", self.answer)
                self.view_history()
                self.quit_or_restart()
                return 
            
            # check valid input
            if self.valid_input(guess):
                self.guesses.append(guess)
                colors = self.color_guess(guess)
                self.colors.append(colors)
                self.update_output()
                self.update_game_state()
                
                # win condition 
                if guess == self.answer:
                    self.win = True
                    if CAN_LOSE:
                        print("You Won!!!")
                    else:
                        print("You Got It!!!")
                    self.save_stats()
                    self.quit_or_restart()
                    return

                # lose condition
                elif CAN_LOSE:
                    if len(self.guesses) == NUM_TRYS:
                        print("You Lose!!!")
                        print("The word was", self.answer)
                        self.view_history()
                        self.quit_or_restart()
                        return
    
    def quit_or_restart(self):
        ans = input("\nDo you want to restart (y/n)? ")
        if ans.lower() == "y":
            self.game_setup()
            self.play_game()
        elif ans.lower() == "n":
            pass


    # check guess for validity
    def valid_input(self, guess, length = 5, print_error = True):
        if len(guess) != length:
            if print_error:
                print("must be", length, "letters")
            return False
        elif guess not in wordslist:
            if print_error:
                print("not a word")
            return False
        else:
            return True

    # defines color for each letter of a guess, updates value for alphabet color dict
    def color_guess(self, guess):
        colors = []
        for i, char in enumerate(guess):
            if char == self.answer[i]:
                colors.append("green")
                self.guess_letters[char] = "green"
            elif char in self.answer:
                colors.append("yellow")
                if self.guess_letters[char] != "green":
                    self.guess_letters[char] = "yellow"
            else:
                colors.append("red")
                self.guess_letters[char] = "red"
        return colors
    
    # prints colored alphabet
    # TODO change format or location, not visible in long games
    def print_alpha(self):
        print(" ".join([colored(letter.upper(), self.guess_letters[letter], attrs=["bold"]) for letter in self.guess_letters]))

    # colors the figlet and adds separators
    def colored_figlet(self, word, colors):
        word = word.upper()
        word_out_array = []

        # iterate over each letter in each word
        for i, plainletter in enumerate(word):
            # split character into list of rows of ascii word art
            letter_rows = figlet_format(plainletter, FONT).split("\n")
                    
            # standardize row length for each row in letter
            letter_rows_trimmed = []
            for row in letter_rows:
                row = row[CUT_LEFT:-CUT_RIGHT] if CUT_RIGHT != 0 else row[CUT_LEFT:]
                # only return row if not whitespace
                if (not row.isspace()) and (len(row) != 0):
                    add = GLOBAL_WIDTH - len(row)
                    add_sides = add // 2
                    add_extra = add - add_sides*2
                    letter_rows_trimmed.append(" "*add_sides + row + " "*(add_sides + add_extra))
            
            # color each row of letter individually
            colored_letter_rows = [colored(row, colors[i], attrs=["bold"]) for row in letter_rows_trimmed]
            
            # add list of letter rows
            word_out_array.append(colored_letter_rows)             
        
        # combine rows of each letter & add hor, vert lines
        colored_word_rows = [VERT_SEP+VERT_SEP.join(zipped)+VERT_SEP for zipped in zip(*word_out_array)]
        colored_word_rows.append(HOR_SEP*SEP_LEN)
        colored_word_rows[-1] = colored_word_rows[-1]
        colored_word = "\n".join(colored_word_rows)
        return colored_word

    # adds output to existing output with guess in colors
    def update_output(self):
        self.all_output += "\n" + self.colored_figlet(self.guesses[-1], self.colors[-1])
        
    # updates current game state
    def update_game_state(self, add_last=True):
        clearConsole()
        self.print_alpha()            
        print(self.all_output)
    
    # saves game stats to database
    def save_stats(self):
        # enter name or nothing to skip
        self.name = input("Enter name to save stats or press return to skip: ").lower()
        if self.name == "":
            self.name = None
            self.view_history()
            return
        
        # data to be saved
        data = (
            self.name,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            self.answer,
            len(self.guesses),
            uuid.getnode()
        )
        
        # save and commit game stats
        cursor = CONNECTION.cursor()
        cursor.execute(
            'insert into stats(name, date, word, guesses, uuid) values(%s, %s, %s, %s, %s)',
            data)
        cursor.close()
        CONNECTION.commit()
        
        print("History:")
        self.view_history()
        #print("Data Saved:", data)
            
    # prints personal, global history, and leaderboards
    def view_history(self):
        clearConsole()
        cursor = CONNECTION.cursor()
        
        # get name if not called from save stats
        if self.name == "":
            cursor.execute("""
                select distinct name
                from stats
                """)
            valid_names = cursor.fetchall()
            valid_names = [name[0] for name in valid_names]
            
            self.name = input("Enter name to view history or press return to skip: ").lower()
            while (self.name not in valid_names) & (self.name != ""):
                print("Name does not match any records")
                self.name = input("Enter name to view history or press return to skip: ").lower()
            
        # print top player stats
        cursor.execute("""
            select 
                rank() over (
                    order by avg(guesses)
                ) rank,
                name,
                count(name) as count,
                avg(guesses) as avg_guesses,
                min(guesses) as min_guesses,
                max(guesses) as max_guesses
            from 
                stats
            where
                name != 'test'
            group by
                name
            order by
                avg_guesses
            """)
        leaderboard = cursor.fetchall()
        print("\nTop Players:")
        print("{: >4} {: >12} {: >8} {: >8} {: >8} {: >8}".format("RANK", "NAME", "NGAMES", "AVG", "MIN", "MAX"))
        for row in leaderboard:
            print("{: >4} {: >12} {: >8} {: >8} {: >8} {: >8}".format(row[0], row[1], row[2], str(round(row[3], 2)), row[4], row[5]))
        
        # print personal stats if name is given
        if self.name != "" and self.name != None:
            cursor.execute("""
                select
                    to_char(date, 'YYYY-MM-DD HH24:MI') as fdate,
                    word,
                    guesses
                from stats
                where name=%s
                order by fdate desc
                limit 10
                """,
                (self.name,)
            )
            personal_records = cursor.fetchall()
        
        # get and print all history
        cursor.execute("""
            select
                name,
                to_char(date, 'YYYY-MM-DD HH24:MI') as fdate,
                word,
                guesses
            from stats
            where name != 'test'
            order by fdate desc
            limit 10
            """)
        records = cursor.fetchall()

        if self.name != "" and self.name != None:
            print("\nAll History (last 10):                             || Personal History (last 10):")
            print("{: >10} {: >18} {: >9} {: >8}".format("NAME", "DATETIME", "WORD", "GUESSES"), "  ||  {: >18} {: >9} {: >8}".format("DATETIME", "WORD", "GUESSES"))
            print("=============================================================================================")
            for row1, row2 in zip(records, personal_records):
                print("{: >10} {: >18} {: >9} {: >8}".format(*row1), "  ||  {: >18} {: >9} {: >8}".format(*row2))
        else:
            print("\nAll History (last 10):")
            print("{: >10} {: >18} {: >9} {: >8}".format("NAME", "DATETIME", "WORD", "GUESSES"))
            print("================================================")
            for row1 in records:
                print("{: >10} {: >18} {: >9} {: >8}".format(*row1))

        # close cursor
        cursor.close()

#### functions for outside simulation
    # manual input returns true if correct
    def manual_input(self, guess):
        if self.valid_input(guess, print_error = False):
            colors = self.color_guess(guess)
            self.guesses.append(guess)
            self.colors.append(colors)
            self.win = (guess == self.answer) or (self.win)
            return False
        else:
            return True
    
    # prints game summary
    def simple_print_game(self):
        out = []
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            out.append("".join([colored(char, color, attrs=["bold"]) for char, color in zip(word, colors)]))
        print("\n".join(out))
            
                
        
# %%
if __name__ == "__main__":
    wordpy().play_game()