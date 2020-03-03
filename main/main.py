# import stuff here
import display
import services
#import external
import time
import sys
import pygame
import pygame.freetype

# main program code
def main():

    running = True
    pygame.init()
    screen = pygame.display.set_mode((400,400), pygame.RESIZABLE)

    # main fonts
    main_font = pygame.freetype.Font("fonts/ARCADECLASSIC.TTF", 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.unicode == 's':
                    running = False

        screen.fill(display.black)

        main_font.render_to(screen, (0, 0), "Hello World!", display.white)

        pygame.display.flip()

    print ("axnenenenene")
    
# run main
main()