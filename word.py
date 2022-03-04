"""
copy of wordle
use WordPy.play_game()
"""
# %%
import uuid
import time
import os
from random import sample
from datetime import datetime

import psycopg2
from termcolor import colored
from pyfiglet import figlet_format

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
class WordPy:
    """
    Copy of Wordle
    """
    def __init__(self, answer:str = None, name:str = None):
        self.guesses = []
        self.colors = []
        self.win = False
        self.all_output = HOR_SEP*SEP_LEN
        self.start_time = time.time()
        self.time_between = []
        self.answer = ""

        self.guess_letters = dict(zip(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
            "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
            ["white"]*26
            ))

        self.given_answer = answer

        if name is None:
            self.name = ""
        else:
            self.name = name
        self.game_setup()

    def game_setup(self):
        """
        sets variables to default
        """
        self.guesses = []
        self.colors = []
        self.win = False
        self.all_output = HOR_SEP*SEP_LEN
        self.start_time = time.time()
        self.time_between = []

        # randomly pick word for answer
        if self.given_answer is None:
            self.answer = sample(answerslist, 1)[0]
        else:
            self.answer = self.given_answer

        # keeps track of "keyboard" colors
        self.guess_letters = dict(zip(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
            "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
            ["white"]*26
            ))

    def play_game(self):
        """
        initiates interactive command line game
        """
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
                self.time_between.append(round(time.time() - self.start_time, 2))
                self.start_time = time.time()
                self.update_output()
                self.refresh_game_state()

                # win condition
                if guess == self.answer:
                    self.win = True
                    if CAN_LOSE:
                        print("You Won!!!")
                    else:
                        print("You Got It!!!")
                    self.save_stats()
                    self.view_history()
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
        """
        initaites quit or restart prompt
        """
        ans = input("\nDo you want to restart (y/n)? ")
        if ans.lower() == "y":
            self.game_setup()
            self.play_game()
        elif ans.lower() == "n":
            pass


    # check guess for validity
    def valid_input(self, guess:str, length:int = 5, print_error:bool = True) -> bool:
        """checks guess validity

        Args:
            guess (str): word
            length (int, optional): length of word (only 5 now). Defaults to 5.
            print_error (bool, optional): print error to console. Defaults to True.

        Returns:
            bool: true if valid
        """
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
    def color_guess(self, guess:str) -> list:
        """color guess according to answer

        Args:
            guess (str): word

        Returns:
            list: list of colors as strings
        """
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
        """prints colored alphabet based on current progress in game
        """
        print(" ".join([colored(letter.upper(), self.guess_letters[letter], attrs=["bold"])
            for letter in self.guess_letters]))

    # colors the figlet and adds separators
    def colored_figlet(self, word:str, colors:list) -> str:
        """colors figlet ascii art

        Args:
            word (str): word
            colors (list): list of colors, same length as word

        Returns:
            str: colored word as ascii art
        """
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
            colored_letter_rows = [
                colored(row, colors[i], attrs=["bold"]) for row in letter_rows_trimmed]

            # add list of letter rows
            word_out_array.append(colored_letter_rows)

        # combine rows of each letter & add hor, vert lines
        colored_word_rows = [
            VERT_SEP+VERT_SEP.join(zipped)+VERT_SEP for zipped in zip(*word_out_array)]
        colored_word_rows.append(HOR_SEP*SEP_LEN)
        colored_word_rows[-1] = colored_word_rows[-1]
        colored_word = "\n".join(colored_word_rows)
        return colored_word

    # adds output to existing output with guess in colors
    def update_output(self) -> None:
        """adds colored word to end of console output
        """
        self.all_output += "\n" + self.colored_figlet(self.guesses[-1], self.colors[-1])

    # updates current game state
    def refresh_game_state(self) -> None:
        """refreses console with current game state
        """
        clearConsole()
        self.print_alpha()
        print(self.all_output)

    # saves game stats to database
    def save_stats(self) -> None:
        """prompts player for info and saves all stats to database
        """
        # enter name or nothing to skip
        if self.name == "" or self.name is None:
            self.name = input("Enter name to save stats or press return to skip: ").lower()
            if self.name == "":
                self.name = None
                return

        # data to be saved
        data = (
            self.name,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            self.answer,
            len(self.guesses),
            uuid.getnode(),
            # na if over max varchar length
            str(self.guesses) if len(str(self.guesses)) < 512 else "NA",
            CAN_LOSE,
            WORD_LEN,
            NUM_TRYS,
            # na if over max varchar length
            str(self.time_between) if len(str(self.time_between)) < 512 else "NA"
        )

        # save and commit game stats
        cursor = CONNECTION.cursor()
        cursor.execute(
            """
            INSERT INTO
                stats(
                    NAME,
                    date,
                    word,
                    guesses,
                    uuid,
                    words_guessed,
                    can_lose,
                    word_length,
                    trys_lose,
                    time_between
                )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            data)
        cursor.close()
        CONNECTION.commit()

    # prints personal, global history, and leaderboards
    def view_history(self) -> None:
        """prompts user for info and prints leaderboards/history
        """
        clearConsole()
        cursor = CONNECTION.cursor()

        # get name if not called from save stats
        if self.name == "":
            cursor.execute("""
                SELECT
                    DISTINCT NAME
                FROM
                    stats
                """)
            valid_names = cursor.fetchall()
            valid_names = [name[0] for name in valid_names]

            self.name = input("Enter name to view history or press return to skip: ").lower()
            while (self.name not in valid_names) & (self.name != ""):
                print("Name does not match any records")
                self.name = input("Enter name to view history or press return to skip: ").lower()

        # print top player stats
        cursor.execute("""
            SELECT
                rank() OVER (
                    ORDER BY
                        avg(guesses)
                ) rank,
                NAME,
                count(NAME) AS count,
                avg(guesses) AS avg_guesses,
                min(guesses) AS min_guesses,
                max(guesses) AS max_guesses
            FROM
                stats
            WHERE
                NAME != 'test'
            GROUP BY
                NAME
            ORDER BY
                avg_guesses
            """)
        leaderboard = cursor.fetchall()
        print("\nTop Players:")
        print(f"{'RANK': >4} {'NAME': >12} {'NGAMES': >8} {'AVG': >8} {'MIN': >8} {'MAX': >8}")
        for row in leaderboard:
            print(f"{row[0]: >4} {row[1]: >12} {row[2]: >8} {str(round(row[3], 2)): >8} {row[4]: >8} {row[5]: >8}")

        # print personal stats if name is given
        if self.name != "" and self.name is not None:
            cursor.execute("""
                SELECT
                    to_char(date, 'YYYY-MM-DD HH24:MI') AS fdate,
                    word,
                    guesses
                FROM
                    stats
                WHERE
                    NAME = %s
                ORDER BY
                    fdate DESC
                LIMIT
                    10
                """,
                (self.name,)
            )
            personal_records = cursor.fetchall()

        # get and print all history
        cursor.execute("""
            SELECT
                NAME,
                to_char(date, 'YYYY-MM-DD HH24:MI') AS fdate,
                word,
                guesses
            FROM
                stats
            WHERE
                NAME != 'test'
                AND NAME != %s
            ORDER BY
                fdate DESC
            LIMIT
                10
            """,
            (self.name,)
            )
        records = cursor.fetchall()

        if self.name != "" and self.name is not None:
            print(f"\n{'Recent Games Played By Others': <51}|| {'Personal History (last 10)': <35}")
            print(f"{'NAME': >10} {'DATETIME': >18} {'WORD': >9} {'GUESSES': >8}   ||  {'DATETIME': >18} {'WORD': >9} {'GUESSES': >8}")
            print("===================================================||========================================")
            records += [["-"]*len(records[0])]*(max(len(records), len(personal_records))-len(records))
            personal_records += [["-"]*len(personal_records[0])]*(max(len(records), len(personal_records))-len(personal_records))
            for row1, row2 in zip(records, personal_records):
                print(f"{row1[0]: >10} {row1[1]: >18} {row1[2]: >9} {row1[3]: >8}", f"  ||  {row2[0]: >18} {row2[1]: >9} {row2[2]: >8}")
        else:
            print("\nRecent Games Played")
            print(f"{'NAME': >10} {'DATETIME': >18} {'WORD': >9} {'GUESSES': >8}")
            print("================================================")
            for row1 in records:
                print(f"{row1[0]: >10} {row1[1]: >18} {row1[2]: >9} {row1[3]: >8}")

        # close cursor
        cursor.close()

#### functions for outside simulation
    # manual input returns true if valid input
    def manual_input(self, guess:str, update_output = False) -> bool:
        """make guess through function instead of playing game

        Args:
            guess (str): word
            update_output (bool, optional): true to update output used by refresh game. Defaults to False.

        Returns:
            bool: returns true if guess is correct
        """
        if self.valid_input(guess, print_error = False):
            colors = self.color_guess(guess)
            self.guesses.append(guess)
            self.colors.append(colors)
            self.time_between.append(round(time.time() - self.start_time, 2))
            self.start_time = time.time()
            if update_output:
                self.update_output()
            self.win = (guess == self.answer) or (self.win)
            return True
        else:
            return False

    # prints game summary
    def simple_print_game(self) -> None:
        """prints a simplified game state
        """
        out = []
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            out.append("".join([colored(char, color, attrs=["bold"]) for char, color in zip(word, colors)]))
        print("\n".join(out))

# %%
if __name__ == "__main__":
    WordPy().play_game()
