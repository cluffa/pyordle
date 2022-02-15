# %%
from termcolor import colored
from random import sample
from pyfiglet import figlet_format
from datetime import date
import os
import urllib.parse as up
import psycopg2
import uuid

clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
clearConsole()     

# load data
words = []
with open("./wordle-allowed-guesses.txt") as f:
    for line in f:
        words.append(line.rstrip())
                
answers = []
with open("./wordle-answers-alphabetical.txt") as f:
    for line in f:
        answers.append(line.rstrip())
        
words = words + answers

# game
class pyordle():
    def __init__(self, answer:str = None):
        if answer == None:
            self.answer = sample(answers, 1)[0]
        else:
            self.answer = answer
            
        self.guess_letters = dict(
            zip(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
                ["white"]*26)
            )
            
        self.guesses = []
        self.colors = []
        self.global_width = 0
        self.name = ""
        
        self.play_game()
    
    def play_game(self):
        print("Game Started, Type Guess...")
        
        # input loop
        while True:
            guess = input("").lower()
            
            if guess == "":
                print("the word was", self.answer)
                self.view_history()
                print("exiting...")
                return ""

            if len(guess) != 5:
                print("must be 5 letters")
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
                    return
                
                # lose condition
                #if len(self.guesses) == 6:
                #    print("You Lose!!!")
                #    self.view_history()
                #    return
        
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
    
    # doesnt work
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
                letter = figlet_format(char, "small").split("\n")
                
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
                colored_letter = [colored(char, colors[i]) for char in letter]
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
        self.name = input("Enter Name To Save Stats: ").lower()
        if self.name == "":
            return
        
        data = (
            self.name,
            date.today().strftime('%Y-%m-%d %H:%M:%S'),
            self.answer,
            len(self.guesses),
            uuid.getnode()
        )
        
        url = "postgres://wizozyvz:mvvteKfWqScUK0bWFxMo89x8SKfVP2h-@kashin.db.elephantsql.com/wizozyvz"
        up.uses_netloc.append("postgres")
        url = up.urlparse(url)
        connection = psycopg2.connect(database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        
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
        if connection == None:
            url = "postgres://wizozyvz:mvvteKfWqScUK0bWFxMo89x8SKfVP2h-@kashin.db.elephantsql.com/wizozyvz"
            up.uses_netloc.append("postgres")
            url = up.urlparse(url)
            connection = psycopg2.connect(database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
        
        clearConsole()
        cursor = connection.cursor()
        if self.name == "":
            self.name = input("Enter name to view history: ")
            if self.name != "":
                cursor.execute("select to_char(date, 'MM-DD-YYYY'), word, guesses from stats where name=%s", (self.name,))
                records = cursor.fetchall()
                total_guesses = 0
                for row in records:
                    total_guesses += row[2]
                print("Your Average: ", total_guesses/len(records))
                print("Your History:")
                print("{: >12} {: >5} {: >8}".format("DATE", "WORD", "GUESSES"))
                for row in records:
                    print("{: >12} {: >5} {: >8}".format(*row))
            
        cursor.execute("select name, to_char(date, 'MM-DD-YYYY'), word, guesses from stats where name != 'test'")
        records = cursor.fetchall()
        print("\nAll History:")
        print("{: >10} {: >12} {: >10} {: >10}".format("NAME", "DATE", "WORD", "GUESSES"))
        for row in records:
            print("{: >10} {: >12} {: >7} {: >8}".format(*row))
            
        cursor.execute("""
            select 
                name,
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
        print("{: >10} {: >10} {: >10} {: >10}".format("NAME", "AVG_GUESSES", "MIN_GUESSES", "MAX_GUESSES"))
        for row in records:
            print("{: >10} {: >10} {: >10} {: >10}".format(row[0], str(round(row[1], 2)), row[2], row[3]))
            
        cursor.close()

# %%
if __name__ == '__main__':
    pyordle()
# %%