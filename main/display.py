import external
import constants
import time
import datetime
import pygame
import pygame.freetype
import pygame.gfxdraw
from astral.sun import sun
from astral.geocoder import database, lookup

# Globals
class GB():
    screen = None
    surface_day_main = None
    running = True
    init_control = True
    pygame.freetype.init()
    main_font = pygame.freetype.Font("fonts/AurulentSansMono-Regular.otf", 130)
    main_font_small = pygame.freetype.Font("fonts/F25_Bank_Printer.ttf", 40)

# stop or stop the loop to update the screen
def start_stop_display_loop(cond):
    GB.running = cond

# main display loop :P
def main_display_loop():
    pygame.init()
    # set pygame settings
    pygame.display.set_caption('Black mirror')
    GB.screen = pygame.display.set_mode((1280,960), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # start loop
    while GB.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GB.running = False
            elif event.type == pygame.KEYDOWN:
                if event.unicode == 's':
                    GB.running = False

        # update display
        update_display()
        pygame.display.update()
        # set fps
        clock.tick(5)

    pygame.quit()

def update_display():

    GB.screen.fill(constants.black) 

    time_now, pm_am_now = get_time()
    GB.main_font.render_to(GB.screen, (45, 30), time_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (450, 100), pm_am_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (130, 160), get_date(), constants.gray1)

    # Things to do only once
    if GB.init_control:
        create_day_curve()
        GB.init_control = False
    
    update_day_curve()
    GB.screen.blit(GB.surface_day_main, [800,30])

def get_time():
    # convert time to 12 hour format
    hour_now = datetime.datetime.now().time().hour
    minute_now = datetime.datetime.now().time().minute
    tfhour = time.strptime(str(hour_now) + ":" + str(minute_now), "%H:%M")
    twhour_now = time.strftime( "%I:%M", tfhour)
    pm_am_now = time.strftime( "%p", tfhour)

    return twhour_now, pm_am_now

def get_date():
    # convert date to proper date
    date_now = str(datetime.datetime.now().date().day) + "-" + str(datetime.datetime.now().date().month)+ "-" + str(datetime.datetime.now().date().year)
    return date_now

def create_day_curve():

    GB.surface_day_main = pygame.Surface((450, 250))

def update_day_curve():

    city = lookup(constants.location, database())
    sun_info = sun(city.observer, date=datetime.datetime.now())

    time_left = (sun_info['sunrise'].hour * 60) + sun_info['sunrise'].minute
    time_middle = ((sun_info['sunset'].hour * 60) + sun_info['sunset'].minute) - ((sun_info['sunrise'].hour * 60) + sun_info['sunrise'].minute) + time_left

    time_now = (datetime.datetime.now().time().hour * 60) + datetime.datetime.now().time().minute
    data_points = []

    # clear screen
    GB.surface_day_main.fill(constants.black) 
    
    # draw lines
    # main seperation line
    pygame.draw.lines(GB.surface_day_main, constants.gray1, False, [(25,125), (425,125)], 3)
    # left bottom line
    pygame.draw.lines(GB.surface_day_main, constants.gray2, False, constants.day_points_btm_left, 3)
    # main top line
    pygame.draw.lines(GB.surface_day_main, constants.white, False, constants.day_points_top, 3)
    # right bottom line
    pygame.draw.lines(GB.surface_day_main, constants.gray2, False, constants.day_points_btm_right, 3)

    if time_now <= time_left:
        # its night now, left
        # calculate index
        index = constants.map_num(time_now, 0, time_left, 0, 10)
        index = int(index) + 2

        for i in range(0, index):
            data_points.append(constants.day_points_btm_left[i])
        data_points.append((((index - 2) * 10) + 25, 125 ))
        # fill graph
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, data_points, constants.gray2)
        # draw circle
        pygame.draw.circle(GB.surface_day_main, constants.moon_blue, data_points[(index-1)], 15, 0)

    elif time_now > time_left and time_now <= time_middle:
        # its day now
        # calculate index
        index = constants.map_num(time_now, time_left, time_middle, 0, 20)
        index = int(index) + 2

        for i in range(0, index):
            data_points.append(constants.day_points_top[i])
        data_points.append((((index - 2) * 10) + 125, 125 ))

        # fill graphs
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, constants.day_points_btm_left, constants.gray2)
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, data_points, constants.white)
        # draw circle
        pygame.draw.circle(GB.surface_day_main, constants.yellow, data_points[(index-1)], 15, 0)

    elif time_now > time_middle:
        # its night now, right
        # calculate index
        index = constants.map_num(time_now, time_middle, 1440, 0, 10)
        index = int(index) + 2

        for i in range(0, index):
            data_points.append(constants.day_points_btm_right[i])
        data_points.append((((index - 2) * 10) + 325, 125 ))

        # fill graphs
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, constants.day_points_btm_left, constants.gray2)
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, constants.day_points_top, constants.white)
        pygame.gfxdraw.filled_polygon(GB.surface_day_main, data_points, constants.gray2)
        # draw circle
        pygame.draw.circle(GB.surface_day_main, constants.moon_blue, data_points[(index-1)], 15, 0)