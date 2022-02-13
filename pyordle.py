# %%
from termcolor import colored
from random import sample
from pyfiglet import figlet_format
import os

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
clearConsole()     

words = []
with open('./wordle-allowed-guesses.txt') as f:
    for line in f:
        words.append(line.rstrip())
                
answers = []
with open('./wordle-answers-alphabetical.txt') as f:
    for line in f:
        answers.append(line.rstrip())
        
words = words + answers

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
        while(True):
            guess = input("")
            
            if guess == "":
                print("exiting...")
                return ""

            if(len(guess) != 5):
                print("must be 5 letters")
            elif(guess not in words):
                print("not a word")
            else:
                self.guesses.append(guess)
                self.colors.append(self.color_guess(guess))
                self.print_guesses()
                if self.colors[-1] == ['green']*5:
                    print("You Won!!!")
                    return ""
        
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
                

        
        
    def print_guesses(self):
        clearConsole()
        print("Game Started, Type Guess...")
        #self.print_keyboard()
        for word, colors in zip(self.guesses, self.colors):
            word = word.upper()
            word_out = []
            for i, char in enumerate(word):
                # lsit of letter rows
                letter = figlet_format(char).strip().split("\n")
                
                # color each row
                colored_letter = [colored(char, colors[i]) for char in letter]
                
                # finding max length row in letter
                max_len = 0
                for line in colored_letter:
                    l = len(line)
                    if l > max_len:
                        max_len = l
                        
                # standardize row length
                for idx, line in enumerate(colored_letter):
                    add = max_len - len(line)
                    if idx == 0:
                        colored_letter[idx] = " "*add + line
                    else:
                        colored_letter[idx] = line + " "*add
                
                word_out.append(colored_letter)
            
            # add rows for words
            sep = "|"
            colored_word = [i+sep+j+sep+k+sep+l+sep+m for i,j,k,l,m in zip(*word_out)]
            
            # join lines
            out = '\n'
            print(out.join(colored_word))


# %%
pyordle()