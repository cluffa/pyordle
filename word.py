# %%
from termcolor import colored
from random import sample
from pyfiglet import figlet_format
from datetime import datetime
import pyfiglet.fonts
import pyfiglet.fonts
import os
import psycopg2
import uuid

clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")

# load data
from words_lists import words, answers

# game
class wordpy():
    def __init__(self, quick_start = True, answer:str = None):
        # randomly pick word for answer
        if answer == None:
            self.answer = sample(answers, 1)[0]
        else:
            self.answer = answer
        
        # TODO finish setup prompts
        if quick_start:
            # default settings
            self.can_lose = False
        else:
            # prompts for settings
            self.setup_game()
            
        self.guess_letters = dict(
            zip(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
                ["white"]*26)
            )
            
        self.guesses = []
        self.colors = []
        self.global_width = 0
        self.name = ""
        self.win = False
    
    def play_game(self):
        clearConsole()
        print("Game started... \nType a 5 letter word or press return to give up and view stats...")
        
        # input loop
        while True:
            guess = input("").lower()
            
            if guess == "":
                print("the word was", self.answer)
                self.view_history()
                input("\nPress return to exit...")
                return 

            if len(guess) != 5:
                print("word must be 5 letters")
            elif guess not in words:
                print("not a word")
            else:
                self.guesses.append(guess)
                self.colors.append(self.color_guess(guess))
                self.print_guesses()
                
                # win condition 
                if guess == self.answer:
                    print("You Won!!!")
                    self.save_stats()
                    input("\nPress return to exit...")
                    return
                
                
                # lose condition
                if self.can_lose:
                    if len(self.guesses) == self.num_trys:
                        print("You Lose!!!")
                        print("The word was", self.answer)
                        self.view_history()
                        return
    
    def manual_input(self, guess):
        self.guesses.append(guess)
        self.colors.append(self.color_guess(guess))
        self.win = (guess == self.answer) or (self.win)
        
    # TODO prompts and sets game settings
    def setup_game(self):
        self.can_lose = True
        self.num_trys = 6
        
    # defines color for each letter of a guess
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
    def print_keyboard(self):
        print(" ".join([colored(letter.upper(), self.guess_letters[letter], attrs=["bold"]) for letter in self.guess_letters]))
        print("_"*(self.global_width*5 + 6))
        
    # prints current game state
    def print_guesses(self):
        clearConsole()
        reset_output = False
        self.print_keyboard()
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            word_out = []
            for i, char in enumerate(word):
                # list of letter rows
                letter = figlet_format(char).split("\n") # , "small"
                
                # updating global letter width
                for line in letter:
                    if len(line) > self.global_width:
                        self.global_width = len(line)
                        reset_output = True
                        
                # standardize row length
                for idx, line in enumerate(letter):
                    add = self.global_width - len(line)
                    add_sides = add // 2
                    add_extra = add - add_sides*2
                    letter[idx] = " "*add_sides + line + " "*add_sides + " "*add_extra
                
                # color each row
                colored_letter = [colored(char, colors[i], attrs=["bold"]) for char in letter]
                colored_letter = colored_letter[0:4]
                
                # add list of letter lines to list of letters as lines
                word_out.append(colored_letter)
            
            # add rows for words
            sep = "|"
            colored_word = [sep+i+sep+j+sep+k+sep+l+sep+m+sep for i,j,k,l,m in zip(*word_out)]
            colored_word.append("_"*(self.global_width*5 + 6))
            
            # join lines, no output if output width changes
            out = "\n"
            if reset_output:
                pass
            else:
                print(out.join(colored_word))
                
        # rerun if output width changed
        if reset_output:
            self.print_guesses()
            
    def save_stats(self):
        # setup postgresSQL connection
        connection = psycopg2.connect(
            database="wizozyvz",
            user="wizozyvz",
            password="mvvteKfWqScUK0bWFxMo89x8SKfVP2h-",
            host="kashin.db.elephantsql.com",
            port=None
        )
        
        # enter name or nothing to skip
        self.name = input("Enter name to save stats or press return to skip: ").lower()
        if self.name == "":
            self.name = None
            self.view_history(connection)
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
        cursor = connection.cursor()
        cursor.execute(
            'insert into stats(name, date, word, guesses, uuid) values(%s, %s, %s, %s, %s)',
            data)
        cursor.close()
        connection.commit()
        
        print("History:")
        self.view_history(connection)
        #print("Data Saved:", data)
            
        
    def view_history(self, connection = None):
        
        # setup connection if called from outside save_stats
        if connection == None:
            connection = psycopg2.connect(
                database="wizozyvz",
                user="wizozyvz",
                password="mvvteKfWqScUK0bWFxMo89x8SKfVP2h-",
                host="kashin.db.elephantsql.com",
                port=None
            )
        
        clearConsole()
        cursor = connection.cursor()
        
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
                """,
                (self.name,)
            )
            records = cursor.fetchall()
            total_guesses = 0
            for row in records:
                total_guesses += row[2]
            print("Your Average:", total_guesses/len(records))
            print("Your History:")
            print("{: >18} {: >9} {: >8}".format("DATETIME", "WORD", "GUESSES"))
            for row in records:
                print("{: >18} {: >9} {: >8}".format(*row))
        
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
        records = cursor.fetchall()
        print("\nTop Players:")
        print("{: >4} {: >12} {: >8} {: >8} {: >8} {: >8}".format("RANK", "NAME", "NGAMES", "AVG", "MIN", "MAX"))
        for row in records:
            print("{: >4} {: >12} {: >8} {: >8} {: >8} {: >8}".format(row[0], row[1], row[2], str(round(row[3], 2)), row[4], row[5]))
        
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
            limit 25
            """)
        records = cursor.fetchall()
        print("\nAll History (limit 25):")
        print("{: >10} {: >18} {: >9} {: >8}".format("NAME", "DATETIME", "WORD", "GUESSES"))
        for row in records:
            print("{: >10} {: >18} {: >9} {: >8}".format(*row))
        
        # close cursor
        cursor.close()
        
    def print_game(self):
        out = []
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            out.append("".join([colored(char, color) for char, color in zip(word, colors)]))
        print("\n".join(out))
            
                
        
# %%
if __name__ == "__main__":
    wordpy().play_game()