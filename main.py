import pygame, sys
import os
import random
import time
from pygame.locals import *
from button import Button

pygame.font.init()
pygame.mixer.init()

# Constants for colors and screen size
WIDTH, HEIGHT = 1400, 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLACK=(0,0,0)


# Set up the Pygame window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Menu")

# Pygame font initialization
FONT = pygame.font.Font("Assets/font.ttf", 50)

WIN = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
pygame.display.set_caption("Space_Shooter")

BORDER = pygame.Rect(WIDTH//2-8,0,16,HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/plasma.mp3')

HEALTH_FONT = pygame.font.Font("Assets/font.ttf", 30)
WIN_FONT = pygame.font.Font("Assets/font.ttf", 100)

BLUE_HIT = pygame.USEREVENT +1
RED_HIT = pygame.USEREVENT +2

MOVEMENT_DURATION = 0.000001  # Duration for each movement in seconds
COOLDOWN_DURATION = 0.0000001
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


def draw_window(red, blue, red_bullets, blue_bullets,red_health, blue_health):

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

def blue_movement(keys_pressed, blue):
        if keys_pressed[pygame.K_a] and blue.x - VEL>0: #left
            blue.x -= VEL
        if keys_pressed[pygame.K_d] and blue.x + VEL<592: #right
            blue.x += VEL
        if keys_pressed[pygame.K_w] and blue.y - VEL>0: #up
            blue.y -= VEL
        if keys_pressed[pygame.K_s] and blue.y +VEL<700: #down
            blue.y += VEL

def red_movement(keys_pressed, red):
        if keys_pressed[pygame.K_LEFT] and red.x -VEL>BORDER.x + BORDER.width: #left
            red.x -= VEL
        if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH: #right
            red.x += VEL
        if keys_pressed[pygame.K_UP] and red.y - VEL>0: #up
            red.y -= VEL
        if keys_pressed[pygame.K_DOWN] and red.y +VEL<700: #down
            red.y += VEL
#def bot_movement(red):
#    global last_movement_time, direction

#    current_time = time.time()
#    time_elapsed = current_time - last_movement_time

#    if time_elapsed >= MOVEMENT_DURATION + COOLDOWN_DURATION:
#        direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
#        last_movement_time = current_time

#    if direction == 'UP' and red.y - VEL > BORDER.y:
#        red.y -= VEL
#    elif direction == 'DOWN' and red.y + VEL < BORDER.y + JOYSTICK_SPACE_HEIGHT:
#        red.y += VEL
#    elif direction == 'LEFT' and red.x - VEL > BORDER.x + BORDER.width:
#        red.x -= VEL
#    elif direction == 'RIGHT' and red.x + VEL + red.width < WIDTH:
#        red.x += VEL

def bot_movement(red, blue):
    global last_movement_time, direction_x, direction_y

    current_time = time.time()
    time_elapsed = current_time - last_movement_time

    if time_elapsed >= MOVEMENT_DURATION + COOLDOWN_DURATION:
        # Determine X-direction based on the blue player's X-coordinate
    options = ["RIGHT", "LEFT"]
    options2 = ['UP', 'DOWN']
    direction_x = random.choice(options)  # Stop X-movement if already aligned

        # Determine Y-direction based on the blue player's Y-coordinate
        if red.y < blue.y:  # If red player is above the blue player
            direction_y = 'DOWN'
        elif red.y > blue.y:  # If red player is below the blue player
            direction_y = 'UP'
            
        else:
            direction_y = random.choice(options2)  # Stop Y-movement if already aligned

        last_movement_time = current_time

    if direction_x == 'LEFT' and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    elif direction_x == 'RIGHT' and red.x + VEL + red.width < WIDTH:
        red.x += VEL

    if direction_y == 'UP' and red.y - VEL > BORDER.y:
        red.y -= VEL
    elif direction_y == 'DOWN' and red.y + VEL < BORDER.y + JOYSTICK_SPACE_HEIGHT:
        red.y += VEL


def bot_shoot(red_bullets, red):
    # Simulate bot shooting randomly
    shoot_probability = random.random()  # Generate a random number between 0 and 1
    
    if shoot_probability < 0.9 and len(red_bullets) < MAX_BULLETS:
        bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
        red_bullets.append(bullet)
        BULLET_HIT_SOUND.play()

def joystick_red_movement(red):
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

def handle_bullets(blue_bullets, red_bullets, blue, red):
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

def draw_winner(text):
     draw_text = WIN_FONT.render(text, 1, WHITE)
     WIN.blit(draw_text, (WIDTH/2- draw_text.get_width()/2,HEIGHT/2 - draw_text.get_height()/2))
     pygame.display.update()
     pygame.time.delay(5000)



def main():

    red = pygame.Rect(1150, 350, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    blue = pygame.Rect(150, 350, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

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
                bot_movement(red,blue)
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

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("Assets/font.ttf", size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")
        main()
        #PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        #PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        #SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        #PLAY_BACK = Button(image=None, pos=(640, 460), 
        #                   text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        #PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        #PLAY_BACK.update(SCREEN)

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

def options():
    
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
        #OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        #SCREEN.fill("white")

        #OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        #OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        #SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        #OPTIONS_BACK = Button(image=None, pos=(640, 460), 
          #                  text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        #OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        #OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
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

if __name__ == "__main__":
    main_menu()
