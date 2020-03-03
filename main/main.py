# import stuff here
import display
import services
#import external
import time
import datetime
import sys
import pygame
import pygame.freetype
using_pi = True
try:
    from gpiozero import CPUTemperature
except:
    using_pi = False


# main program code
def main():

    running = True
    pygame.init()
    pygame.display.set_caption('Black mirror')
    screen = pygame.display.set_mode((400,400), pygame.RESIZABLE)
    clockobject = pygame.time.Clock()

    # main fonts
    main_font = pygame.freetype.Font("fonts/Gameplay.ttf", 40)
    main_font_small = pygame.freetype.Font("fonts/Gameplay.ttf", 23)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.unicode == 's':
                    running = False

        #slow down loop to 1fps
        clockobject.tick(1)

        #convert time to 12 hour format
        hour_now = datetime.datetime.now().time().hour
        minute_now = datetime.datetime.now().time().minute
        tfhour = time.strptime(str(hour_now) + " : " + str(minute_now), "%H : %M")
        twhour_now = time.strftime( "%I : %M", tfhour)
        pm_am_now = time.strftime( "%p", tfhour)

        #convert date to proper date
        date_now = str(datetime.datetime.now().date().day) + " - " + str(datetime.datetime.now().date().month)+ " - " + str(datetime.datetime.now().date().year)

        #display stuff
        screen.fill(display.black) 
        main_font.render_to(screen, (10, 10), twhour_now, display.white)
        main_font_small.render_to(screen, (180, 25), pm_am_now, display.white)
        main_font_small.render_to(screen, (10, 70), date_now, display.white)

        if using_pi:
            cpu = CPUTemperature()
            pi_temp = cpu.temperature
            main_font_small.render_to(screen, (10, 100), str(pi_temp), display.white)

        #update display
        pygame.display.flip() 
    
# run main
main()