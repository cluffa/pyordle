# %%
from termcolor import colored
from random import sample
from pyfiglet import figlet_format
import os

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
clearConsole()     

# load data
words = []
with open('./wordle-allowed-guesses.txt') as f:
    for line in f:
        words.append(line.rstrip())
                
answers = []
with open('./wordle-answers-alphabetical.txt') as f:
    for line in f:
        answers.append(line.rstrip())
        
words = words + answers

# game
class pyordle():
    def __init__(self, answer = None):
        if answer == None:
            self.answer = sample(answers, 1)[0]
        else:
            self.answer = answer
            
        self.guesses = []
        self.colors = []
        
        self.play_game()
    
    def play_game(self):
        print("Game Started, Type Guess...")
        
        # input loop
        while True:
            guess = input("")
            
            if guess == "":
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
                    return ""
                
                # lose condition
                if len(self.guesses) == 6:
                    print("You Lose!!!")
                    return ""
        
    # defines color for each letter of a guess
    def color_guess(self, guess):
        colors = []
        for i, char in enumerate(guess):
            if char ==self.answer[i]:
                colors.append('green')
            elif char in self.answer:
                colors.append('yellow')
            else:
                colors.append('red')
        return colors
    
    # doesnt work
    def print_keyboard(self):
        alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        alphabet = [letter.upper for letter in alphabet]
        in_answer = [letter in self.answer for letter in alphabet]
        all_letter_guesses = "".join(self.guesses)
        all_letter_guesses = (char for char in all_letter_guesses)
        for letter in alphabet:
            if letter in all_letter_guesses:
                if letter in self.answer:
                    print(colored(letter, "yellow"))
                else:
                    print(colored(letter, "red"))
            else:
                print(letter)
                
    # prints current game state
    def print_guesses(self, sep = "|"):
        clearConsole()
        print("Game Started, Type Guess...")
        #self.print_keyboard()
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            word_out = []
            for i, char in enumerate(word):
                # list of letter rows
                letter = figlet_format(char).split("\n")
                
                # color each row
                colored_letter = [colored(char, colors[i]) for char in letter]
                colored_letter = colored_letter[0:5]
                
                # finding max length row in letter
                max_len = 18
                for line in colored_letter:
                    l = len(line)
                    if l > max_len:
                        max_len = l
                        
                # standardize row length
                for idx, line in enumerate(colored_letter):
                    add = max_len - len(line)
                    colored_letter[idx] = " " + line + " " + " "*add
                
                word_out.append(colored_letter)
            
            # add rows for words
            colored_word = [i+sep+j+sep+k+sep+l+sep+m for i,j,k,l,m in zip(*word_out)]
            colored_word.append("__________________________________________________________")
            
            # join lines
            out = '\n'
            print(out.join(colored_word))


# %%
pyordle()