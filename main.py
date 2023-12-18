# Import necessary libraries
import pygame
import sys
import os
import random
import time
import mysql.connector
from mysql.connector import errorcode
from pygame.locals import *
from button import Button 
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Jiten123@',
    'database': 'space',
}

# Connect to the database
try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    # Handle connection errors
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Invalid credentials")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: Database does not exist")
    else:
        print("Error: {}".format(err))
    sys.exit()

# Initialize Pygame
pygame.font.init()
pygame.mixer.init()

# Constants and screen setup
WIDTH, HEIGHT = 1400, 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# ... (other color constants)

# Initialize Pygame window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Menu")
FONT = pygame.font.Font("Assets/font.ttf", 50)

# Load images and set up game elements
WIN = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
pygame.display.set_caption("Space_Shooter")

BORDER = pygame.Rect(WIDTH//2-8,0,16,HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/plasma.mp3')

HEALTH_FONT = pygame.font.Font("Assets/font.ttf", 30)
WIN_FONT = pygame.font.Font("Assets/font.ttf", 100)

BLUE_HIT = pygame.USEREVENT +1
RED_HIT = pygame.USEREVENT +2

MOVEMENT_DURATION = 1  # Duration for each movement in seconds

last_movement_time = time.time()
direction = None

FPS=60
VEL=8
BULLET_VEL = 15
MAX_BULLETS = 4
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 100,100
JOYSTICK_SPACE_WIDTH = 700
JOYSTICK_SPACE_HEIGHT = 700

BLUE_SPACESHIP = pygame.image.load(os.path.join('Assets','spaceship_blue.png'))
BLUE_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(BLUE_SPACESHIP, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

RED_SPACESHIP = pygame.image.load(os.path.join('Assets','spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets','space 4.png')),(WIDTH, HEIGHT))

is_bot=False


# Function to update player score in the database
def update_score(player, score):
    try:
        # Connect to the database
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Execute SQL update query
        update_query = "UPDATE player_scores SET score = %s WHERE player_name = %s"
        cursor.execute(update_query, (player_score, player_name))

        # Confirm if any rows were affected
        rows_affected = cursor.rowcount
        print(f"Rows affected: {rows_affected}")

        # Commit the changes and close the cursor and connection
        cnx.commit()
        cursor.close()
        cnx.close()

        if rows_affected == 0:
            print(f"Player '{player_name}' not found or score is unchanged.")
        else:
            print("Score updated successfully.")
    except mysql.connector.Error as err:
        # Handle errors
        print("Error updating score:", err)

# Function to draw game window
def draw_window(red, blue, red_bullets, blue_bullets, red_health, blue_health):
    WIN.blit(SPACE, (0,0))
    pygame.draw.rect(WIN, BLACK, BORDER )

    red_health_text = HEALTH_FONT.render("HP:"+str(red_health), 1, WHITE)
    blue_health_text = HEALTH_FONT.render("HP:"+str(blue_health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width()-10,10))
    WIN.blit(blue_health_text,(10,10))

    WIN.blit(BLUE_SPACESHIP, (blue.x, blue.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
         pygame.draw.rect(WIN,(255,0,0),bullet)
    for bullet in blue_bullets:
         pygame.draw.rect(WIN,(0,0,255),bullet)

    pygame.display.update()

def get_player_name(player_number):
    root = tk.Tk()
    root.withdraw()

    style = ttk.Style()
    style.theme_use('clam')

    players = []
    for player_number in range(1, 3):
        dialog = simpledialog.askstring(f"Enter Player {player_number} Name", f"Player {player_number} Name:")
        players.append(dialog)

    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Ensure the table exists before insertion
        create_table(cursor)

        insert_query = "INSERT INTO player_scores (player_name, score) VALUES (%s, %s)"
        for player in players:
            cursor.execute(insert_query, (player, 0))  # Assuming the initial score is 0 for each player

        cnx.commit()
        cursor.close()
        cnx.close()

        print("Players inserted into the database.")
    except mysql.connector.Error as err:
        print("Error inserting player names:", err)

    return players


# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Jiten123@',
    'database': 'Spaco',
}

# Function to create a database table
def create_table(cursor):
    try:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS player_scores (id INT AUTO_INCREMENT PRIMARY KEY, player_name VARCHAR(255), score INT)"
        )
    except mysql.connector.Error as err:
        print("Error creating table:", err)


# Function to create the database and table
def create_database():
    try:
        # Connect to MySQL without specifying a database
        cnx = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = cnx.cursor()

        # Create a new database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")

        # Switch to the specified database
        cursor.execute(f"USE {db_config['database']}")

        # Create a table to store player name and score if it doesn't exist
        create_table(cursor)

        # Commit the changes and close the cursor and connection
        cnx.commit()
        cursor.close()
        cnx.close()

        print(f"Database '{db_config['database']}' and table 'player_scores' created successfully.")
    except mysql.connector.Error as err:
        print("Error creating database and table:", err)

# Function for blue spaceship movement

def blue_movement(keys_pressed, blue):
    # Handle blue spaceship movement
        if keys_pressed[pygame.K_a] and blue.x - VEL>0: #left
            blue.x -= VEL
        if keys_pressed[pygame.K_d] and blue.x + VEL<592: #right
            blue.x += VEL
        if keys_pressed[pygame.K_w] and blue.y - VEL>0: #up
            blue.y -= VEL
        if keys_pressed[pygame.K_s] and blue.y +VEL<700: #down
            blue.y += VEL    

# Function for red spaceship movement
def red_movement(keys_pressed, red):
    # Handle red spaceship movement
        if keys_pressed[pygame.K_LEFT] and red.x -VEL>BORDER.x + BORDER.width: #left
            red.x -= VEL
        if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH: #right
            red.x += VEL
        if keys_pressed[pygame.K_UP] and red.y - VEL>0: #up
            red.y -= VEL
        if keys_pressed[pygame.K_DOWN] and red.y +VEL<700: #down
            red.y += VEL

# Function for bot movement
def bot_movement(red, blue,blue_bullets):
    # Bot movement logic
    global last_movement_time, direction_x, direction_y

    current_time = time.time()
    time_elapsed = current_time - last_movement_time

    # Determine X-direction based on the blue player's X-coordinate
    options = ["RIGHT", "LEFT"]
    options2 = ['UP', 'DOWN']
    direction_x = random.choice(options) if time_elapsed >= MOVEMENT_DURATION else direction_x  # Stop X-movement if already aligned

    # Determine Y-direction based on the blue player's Y-coordinate
    if red.y < blue.y:  # If red player is above the blue player
        direction_y = 'DOWN'
    elif red.y > blue.y:  # If red player is below the blue player
        direction_y = 'UP'
    else:
        direction_y = random.choice(options2) if time_elapsed >= MOVEMENT_DURATION else direction_y  # Stop Y-movement if already aligned

    # Evade bullets if they are detected in the vicinity
    for bullet in blue_bullets:
        # Check if bullet is coming towards the bot's position
        if bullet.x > red.x:
            direction_x = 'LEFT' if red.x + VEL > BORDER.x + BORDER.width else direction_x
        elif bullet.x < red.x:
            direction_x = 'RIGHT' if red.x - VEL + red.width < WIDTH else direction_x

        if bullet.y > red.y:
            direction_y = 'UP' if red.y + VEL > BORDER.y else direction_y
        elif bullet.y < red.y:
            direction_y = 'DOWN' if red.y - VEL + red.height < BORDER.y + JOYSTICK_SPACE_HEIGHT else direction_y

    # Movement logic when no specific player movement triggers bot movement
    if direction_x == 'LEFT' and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    elif direction_x == 'RIGHT' and red.x + VEL + red.width < WIDTH:
        red.x += VEL

    if direction_y == 'UP' and red.y - VEL > BORDER.y:
        red.y -= VEL
    elif direction_y == 'DOWN' and red.y + VEL < BORDER.y + JOYSTICK_SPACE_HEIGHT:
        red.y += VEL

    last_movement_time = current_time


# Function for bot shooting
def bot_shoot(red_bullets, red):
    # Bot shooting logic
    # Simulate bot shooting randomly
    shoot_probability = random.random()  # Generate a random number between 0 and 1
    
    if shoot_probability < 0.9 and len(red_bullets) < MAX_BULLETS:
        bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
        red_bullets.append(bullet)
        BULLET_HIT_SOUND.play()

# Function for joystick-controlled red spaceship movement
def joystick_red_movement(red):
    # Joystick movement logic
    # Get joystick axes
    left_right_axis = pygame.joystick.Joystick(0).get_axis(0)  # X-axis
    up_down_axis = pygame.joystick.Joystick(0).get_axis(1)  # Y-axis

    # Modify red spaceship's movement based on joystick inputs
    if abs(left_right_axis) > 0.1:
        if left_right_axis < -0.1 and red.x - VEL > BORDER.x + BORDER.width:  # left
            red.x -= VEL
        elif left_right_axis > 0.1 and red.x + VEL + red.width < BORDER.x + BORDER.width + JOYSTICK_SPACE_WIDTH:  # right
            red.x += VEL

    if abs(up_down_axis) > 0.1:
        if up_down_axis < -0.1 and red.y - VEL > BORDER.y:  # up
            red.y -= VEL
        elif up_down_axis > 0.1 and red.y + VEL < BORDER.y + JOYSTICK_SPACE_HEIGHT:  # down
            red.y += VEL

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
print(joysticks)

# Function to handle bullets and collisions
def handle_bullets(blue_bullets, red_bullets, blue, red):
    # Bullet handling logic
     for bullet in blue_bullets:
          bullet.x += BULLET_VEL
          if red.colliderect(bullet):
               pygame.event.post(pygame.event.Event(RED_HIT))
               blue_bullets.remove(bullet)
          elif bullet.x > WIDTH:
               blue_bullets.remove(bullet)

     for bullet in red_bullets:
          bullet.x -= BULLET_VEL
          if blue.colliderect(bullet):
               pygame.event.post(pygame.event.Event(BLUE_HIT))
               red_bullets.remove(bullet)
          elif bullet.x <0:
               red_bullets.remove(bullet)


# Function to draw the winner on the screen
def draw_winner(text):
    # Draw winner logic
     draw_text = WIN_FONT.render(text, 1, WHITE)
     WIN.blit(draw_text, (WIDTH/2- draw_text.get_width()/2,HEIGHT/2 - draw_text.get_height()/2))
     pygame.display.update()
     pygame.time.delay(5000)

# Main game function
def main():
    # Game setup and main loop
    red = pygame.Rect(1150, 350, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    blue = pygame.Rect(150, 350, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    blue_name = get_player_name(1)
    red_name = get_player_name(2)

    blue_bullets=[]
    red_bullets=[]

    red_health=10
    blue_health=10

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
          
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                
            #joystick_red_movement(red)

            
            if is_bot == True:
                bot_movement(red,blue,blue_bullets)
                bot_shoot(red_bullets, red)

            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_SPACE and len(blue_bullets) < MAX_BULLETS:
                      bullet = pygame.Rect(blue.x + blue.width, blue.y + blue.height//2 - 2,10,5)
                      blue_bullets.append(bullet)
                      BULLET_HIT_SOUND.play()
                      
                 if event.key == pygame.K_RCTRL and len(red_bullets)<MAX_BULLETS:
                      bullet = pygame.Rect(red.x, red.y + red.height//2 - 2,10,5)
                      red_bullets.append(bullet)
                      BULLET_HIT_SOUND.play()

            if event.type == pygame.JOYBUTTONDOWN:
                 if event.button == 0: 
                     if len(red_bullets) < MAX_BULLETS:
                         bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                         red_bullets.append(bullet)
                         BULLET_HIT_SOUND.play()

            if event.type == RED_HIT:
                 red_health -=1
            
            if event.type == BLUE_HIT:
                 blue_health -=1



        win_text=''
        if red_health<=0:
             win_text = "BLUE WINS!"
             
        if blue_health<=0:
             win_text = "RED WINS!"

        if win_text != '':
            draw_winner(win_text)
            update_score(blue_name, blue_health)
            update_score(red_name, red_health)
            main_menu()
            break
             
        
        if win_text != '':
             draw_winner(win_text)
             main_menu()
             break
             
        keys_pressed = pygame.key.get_pressed()
        blue_movement(keys_pressed, blue)
        red_movement(keys_pressed, red)

        handle_bullets(blue_bullets, red_bullets, blue, red)
        
        draw_window(red,blue, red_bullets, blue_bullets, red_health, blue_health)
       

 
SCREEN = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Menu")

BG = pygame.image.load("Assets/Background2.png").convert()  # Load the image
BG = pygame.transform.scale(BG, (1400, 800))


# Function to start the game
def play():
    # Play screen logic
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")
        main()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()

bot_selected = False
player_selected = False

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("Assets/font.ttf", size)

# Function to handle options menu
def options():
    # Options menu logic
    global is_bot, bot_selected, player_selected
    options_background = pygame.image.load("Assets/BAckground2.png")
    options_background = pygame.transform.scale(options_background, (1400, 800))

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(options_background, (0, 0))

        OPTIONS_TEXT = get_font(60).render("OPTIONS MENU", True, "#b68f40")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(700, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(700, 600), 
                            text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        BOT_BUTTON = Button(image=None, pos=(700, 360), 
                            text_input="BOT", font=get_font(75), base_color="White", hovering_color="Green")
        PLAYER_BUTTON = Button(image=None, pos=(700, 460), 
                            text_input="PLAYER", font=get_font(75), base_color="White", hovering_color="Green")

        # Check and change color based on selection state
        if bot_selected:
            BOT_BUTTON.changeColor("Green")
        else:
            BOT_BUTTON.changeColor(OPTIONS_MOUSE_POS)

        if player_selected:
            PLAYER_BUTTON.changeColor("Green")
        else:
            PLAYER_BUTTON.changeColor(OPTIONS_MOUSE_POS)

        BOT_BUTTON.update(SCREEN)
        PLAYER_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                elif BOT_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    is_bot = True
                    bot_selected = True
                    player_selected = False
                elif PLAYER_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    is_bot = False
                    bot_selected = False
                    player_selected = True

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

# Main menu function
def main_menu():
    # Main menu logic
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(700, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(700, 300), 
                    text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(700, 450), 
                    text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(700, 600), 
                    text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


# Start the main menu
if __name__ == "__main__":
    main_menu()
