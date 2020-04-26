import random
import os
import turtle
from threading import Timer

# Fixed Variables:
NUMBER_OF_PLAYERS = 3
VOWELS = ["A", "E", "I", "O", "U"]

# Fixed Positions
TITLE_POSITION = (0, 350)

# Display Asthethics:
FONT = "Calibri"
BACKGROUND_COLOR = "#ffc4e4"
ARROW_COLOR = "#090057"

# Window Set Up
wn = turtle.Screen()
wn.title("Wheel Of Fortune")
wn.setup(width=1.0, height=1.0)
wn.bgcolor(BACKGROUND_COLOR)

# Application Functions
def load_phrases(file):
    phrases = []
    phrases_file = open(file=file, mode="r")
    for line in phrases_file:
        line = line.rstrip("\n")
        if line != "":
            phrases.append(line)
    return phrases

def is_a_vowel(alphabet):
    return alphabet.upper() in VOWELS

def findnth(haystack, needle, n):
    parts = haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def display_title():
    title = turtle.Turtle()
    title.speed(0)
    title.penup()
    title.pencolor("white")
    title.setpos(TITLE_POSITION)
    title.write("WHEEL OF FORTUNE", align="center", font=(FONT, 30, "bold"))
    title.hideturtle()


# Objects For Wheel Of Fortune
class Game:
    def __init__(self):
        self.current_player_number = 1
        self.phrases = load_phrases(os.path.join(os.getcwd(), "WofFPhrases.txt"))
        self.players = []
        self.puzzle = None
        self.results = turtle.Turtle()
        self.results.speed(0)
        self.results.hideturtle()
        self.wheel = Wheel(radius=250)

    def display_game_results(self):
        x_pos, y_pos = 400, 350
        self.results.reset()
        self.results.penup()
        self.results.color("black")
        for player in self.players:
            self.results.goto(x_pos,y_pos)
            self.results.write("{0} - ${1}".format(player.name, player.money), font=(FONT, 20, 'bold'))
            y_pos -= 30
        self.results.hideturtle()

    def game_results(self):
        self.display_game_results()
        for player in self.players:
            print("{0} - ${1}".format(player.name, player.money))

    def get_player(self, player_number):
        return list(filter(lambda player: player.player_number == player_number, self.players))[0]
    
    def next_player(self):
        if self.current_player_number == NUMBER_OF_PLAYERS: 
            self.current_player_number = 1
        else:
            self.current_player_number += 1
    
    def play(self):
        self.puzzle = Puzzle(random.choice(self.phrases))
        while not self.puzzle.is_solved():
            player = self.get_player(self.current_player_number)
            self.puzzle.display()
            print()
            self.game_results()
            print("\n{}'s Turn\n".format(player.name))
            print("\nSpinning...\n")
            outcome = self.wheel.spin()

            if outcome == "Bankrupt":
                print("\n{} got bankrupt!\n".format(player.name))
                player.money = 0
                self.next_player()
            elif outcome == "Lose A Turn":
                print("\n{} loses a turn!\n".format(player.name))
                self.next_player()
            else:
                print("${}".format(outcome))
                timer = Timer(10.0, print, ['Times up! You lost your turn.'])
                timer.start()
                letter = ""
                valid_input = False
                while not valid_input:
                    letter = input("Guess a letter, you have 10 seconds: ")
                    if timer.is_alive():
                        if letter == "":
                            print("Letter cannot be empty!")
                        elif len(letter) > 1:
                            print("You entered more than one letters.")
                        else:
                            if letter.isalpha():
                                if letter in self.puzzle.list_form:
                                    print("{} already found in the puzzle!".format(letter))
                                else:   
                                    if is_a_vowel(letter):
                                        if outcome == "Free Play":
                                            print("{0} used Free Play for the vowel '{1}'".format(player.name, letter.upper()))
                                            valid_input = True
                                        else:
                                            if player.money < 250:
                                                print("Not enough money to buy a vowel.")
                                            else:
                                                print("{0} bought the vowel '{1}'".format(player.name, letter.upper()))
                                                player.money -= 250
                                                valid_input = True
                                    else:
                                        valid_input = True
                            else:
                                print("Please enter a valid alphabet!")
                    else:
                        valid_input = True
                timer.cancel()
                
                if timer.is_alive():
                    del timer 
                    if self.puzzle.check_letter_exists(letter):
                        occurrences = self.puzzle.count_letter_occurrence(letter)
                        print("You've guessed it! There are {0} '{1}'(s)".format(occurrences, letter))
                        if not outcome == "Free Play" and not is_a_vowel(letter):
                            player.money += (occurrences * outcome)
                        self.puzzle.fill(letter)
                        self.puzzle.display()
                        self.game_results()
                        if not self.puzzle.is_solved():
                            valid_input = False
                            want_to_solve = ""
                            while not valid_input:
                                want_to_solve = input("\nWould you like to solve the puzzle ? (Y/N): ")
                                if want_to_solve == "Y" or want_to_solve == "N":
                                    valid_input = True
                                else:
                                    print("Please enter only 'Y' or 'N'.")
                            if want_to_solve == "Y":
                                solve_attempt = input("Solve the puzzle: ")
                                self.puzzle.solve(solve_attempt)
                                if self.puzzle.is_solved():
                                    self.puzzle.list_form = list(self.puzzle.phrase)
                                    self.puzzle.display()
                                    print("Congratulations! {} solved the puzzle!".format(player.name))
                                    for p in self.players:
                                        if p != player:
                                            p.money = 0
                                else:
                                    print("Sorry {}, your answer is incorrect!".format(player.name))
                                    self.next_player()
                    else:
                        print("\nSorry the puzzle does not contain the letter {}.\n".format(letter.upper()))
                        if not outcome == "Free Play":
                            self.next_player()
                else:
                    del timer
                    self.next_player()
        print("\nFinal Results")
        self.game_results()

    def setup(self):
        print("\nPlayers, please enter your name.\n")
        for count in range(NUMBER_OF_PLAYERS):
            player_number = count + 1
            valid_input = False
            name = ""
            while not valid_input:
                print("Player {}:".format(player_number))
                name = input("Enter your name: ")
                if name != "":
                    valid_input = True
                else:
                    print("Name cannot be empty!")
            self.players.append(Player(name, player_number))

    def start(self):
        print("Welcome To Wheel Of Fortune!")
        self.setup()
        self.play()
        

class Wheel:
    def __init__(self,  radius):
        self.radius = radius
        self.current_sector = 0
        self.arrow = turtle.Turtle()
        self.sectors = [550, 800, 300, 700, 900, 500, 5000, 'Bankrupt',
                        300, 500, 450, 500, 800, 'Lose A Turn', 700, 'Free Play',
                        650, 'Bankrupt', 600, 500, 350, 600, 500, 400]
        self.colors = ['#d40ae1', '#ffa700', '#32d0ff', '#ff4141', '#fdff0d', '#5cc30c', '#dedede', '#000000', 
                       '#ffa700', '#5cc30c', '#ff79bc', '#d40ae1', '#ff4141', '#ffffff', '#32d0ff', '#009619',
                       '#d40ae1', '#000000', '#ff79bc', '#5cc30c', '#32d0ff', '#ff4141', '#ff79bc', '#fdff0d']
        self.x_adjustments = [-40, -45, -50, -50, -50, -50, -45, -50, -30, -20, -10, 0,
                              10, 10, 25, 15, 20, 10, 15, 10, 5, -5, -20, -30]
        self.y_adjustments = [20, 15, 10, 0, -10, -20, -30, -35, -40, -45, -45, -45,
                              -40, -30, -25, -10, -10, 0, 10, 20, 20, 25, 30, 30]
        self.arrow.speed(0)
        self.arrow.hideturtle()
        self.display_on_screen()

    def display_on_screen(self, center=(0, 80)):
        wheel_turtle = turtle.Turtle()
        wheel_turtle.speed(0)

        sector_text = turtle.Turtle()
        sector_text.speed(0)
        sector_text.penup()

        slice_angle = 360 / len(self.sectors)
        heading, position = 90, (center[0] + self.radius, center[1])

        for count, color in enumerate(self.colors):
            wheel_turtle.color(color)
            wheel_turtle.penup()
            wheel_turtle.goto(position)
            wheel_turtle.setheading(heading)
            wheel_turtle.pendown()
            wheel_turtle.begin_fill()
            sector_text.setposition(position[0] + self.x_adjustments[count], position[1] + self.y_adjustments[count])
            sector_text.pencolor("black")
            if isinstance(self.sectors[count], int):
                sector_text.write("${}".format(self.sectors[count]), font=(FONT, 10, "bold"))
            else:
                if self.sectors[count] == "Bankrupt" or self.sectors[count] == "Free Play":
                     sector_text.pencolor("white")
                sector_text.write(self.sectors[count], font=(FONT, 10, "bold"))

            wheel_turtle.circle(self.radius, extent=slice_angle)
            heading, position = wheel_turtle.heading(), wheel_turtle.position()
            wheel_turtle.penup()
            sector_text.penup()
            wheel_turtle.goto(center)
            wheel_turtle.end_fill()
    
        wheel_turtle.hideturtle()
        sector_text.hideturtle()
    
        self.spin_to(self.current_sector)

    def spin(self):
        index = random.randrange(0, len(self.sectors))
        self.spin_to(index)
        return self.sectors[index] 

    def spin_to(self, target, center=(0,80)):
        slice_angle = 360 / len(self.sectors)
        if target < self.current_sector:
            number_of_rotations = (len(self.sectors) - self.current_sector) + target
            current = self.current_sector
            for count in range(number_of_rotations):
                current += 1
                self.arrow.reset()
                self.arrow.speed(0)
                self.arrow.penup()
                self.arrow.goto(center)
                self.arrow.left((0.5*slice_angle) + (current%24)*slice_angle)
                self.arrow.color(ARROW_COLOR)
                self.arrow.pensize(8)
                self.arrow.pendown()
                self.arrow.forward(self.radius - 75)
                self.arrow.penup()
                self.arrow.hideturtle()
        else:
            for count in range(self.current_sector, target+1):
                self.arrow.reset()
                self.arrow.speed(0)
                self.arrow.penup()
                self.arrow.goto(center)
                self.arrow.left((0.5*slice_angle) + count*slice_angle)
                self.arrow.color(ARROW_COLOR)
                self.arrow.pensize(10)
                self.arrow.pendown()
                self.arrow.forward(self.radius - 75)
                self.arrow.penup()
                self.arrow.hideturtle()
        self.current_sector = target

class Puzzle:
    def __init__(self, phrase):
        self.phrase = phrase
        self.solved = False
        self.list_form = []
        self.turtles = []
        self.generate_list_form()

    def count_letter_occurrence(self, alphabet):
        count = 0
        for letter in self.phrase:
            if letter == alphabet.upper():
                count += 1
        return count

    def check_letter_exists(self, alphabet):
        return alphabet.upper() in self.phrase
    
    def display(self):
        self.display_on_screen()
        print("".join(self.list_form))

    def display_on_screen(self):
        self.turtles = []
        x_pos, y_pos = -650, -200
        space_count =  0
        for count, character in enumerate(self.list_form):
            if character == " ":
                space_count += 1
                next_space = findnth(self.phrase," ",space_count)
                word = ""
                if next_space == -1:
                    word = self.phrase[findnth(self.phrase," ",space_count-1):]
                else:
                    word = self.phrase[findnth(self.phrase," ",space_count-1):next_space]
                if x_pos + (len(word) * 50) + 30 >= 650:
                    x_pos = -650
                    y_pos -= 60
                if x_pos > -650:
                    x_pos += 30
            else:
                letter_turtle = turtle.Turtle()
                letter_turtle.speed(0)
                letter_turtle.penup()
                letter_turtle.goto(x_pos, y_pos)
                letter_turtle.color("black")
                letter_turtle.pensize(5)
                letter_turtle.pendown()
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.penup()
                if character.isalpha():
                    letter_turtle.forward(20)
                    letter_turtle.right(90)
                    letter_turtle.forward(35)
                    letter_turtle.color("black")
                    letter_turtle.write(character, align="center", font=(FONT, 20, "bold"))
                    letter_turtle.hideturtle()
                letter_turtle.hideturtle()
                self.turtles.append(letter_turtle)
                x_pos += 50
            if x_pos >= 650:
                x_pos = -650
                y_pos -= 60

    def fill(self, alphabet):
        for count, letter in enumerate(self.phrase):
            if alphabet.upper() == letter:
                self.list_form[count] = letter
        if "".join(self.list_form) == self.phrase:
            self.solved = True

    def is_solved(self):
        return self.solved

    def generate_list_form(self):
        for character in self.phrase:
            if character == " ":
                self.list_form.append(" ")
            else:
                self.list_form.append("_")

    def solve(self, phrase):
        if self.phrase == phrase.upper():
            self.solved = True

class Player:
    def __init__(self, name, player_number):
        self.name = name
        self.money = 0
        self.player_number = player_number

if __name__ == "__main__":
    display_title()
    game = Game()
    game.start()