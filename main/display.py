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
    surface_weather = None
    running = True
    update_control = True
    init_control = True
    tick_timer = 0
    pygame.freetype.init()
    main_font = pygame.freetype.Font("fonts/AurulentSansMono-Regular.otf", 130)
    main_font_small = pygame.freetype.Font("fonts/F25_Bank_Printer.ttf", 40)

# force stop the display loop
def stop_display_loop():
    GB.running = False

# pause screen updates (sleep mode)
def spause_screen_updates(cond):
    GB.update_control = cond

# main display loop
def main_display_loop():
    pygame.init()
    # set pygame settings
    pygame.display.set_caption('Black mirror')
    #GB.screen = pygame.display.set_mode((1280,960), pygame.RESIZABLE)
    GB.screen = pygame.display.set_mode((640,480), pygame.RESIZABLE)
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
        if GB.update_control:
            update_display()
            pygame.display.update()
        # set fps
        clock.tick(10)

    pygame.quit()

def update_display():

    GB.screen.fill(constants.black) 

    time_now, pm_am_now = get_time()
    GB.main_font.render_to(GB.screen, (50, 60), time_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (440, 130), pm_am_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (120, 195), get_date(), constants.gray1)

    # Things to do only once
    if GB.init_control:
        create_surfaces()
        update_day_curve()
        update_weather()
        GB.init_control = False

    # Things to do once every 1 minute
    if GB.tick_timer > 600:
        update_day_curve()
        GB.tick_timer = 0

    update_weather()

    GB.tick_timer += 1
    GB.screen.blit(GB.surface_day_main, [800,30])
    GB.screen.blit(GB.surface_weather, [0,0])

def get_time():
    # convert time to 12 hour format
    tfhour = time.strptime(str(datetime.datetime.now().time().hour) + ":" + str(datetime.datetime.now().time().minute), "%H:%M")
    twhour_now = time.strftime( "%I:%M", tfhour)
    pm_am_now = time.strftime( "%p", tfhour)

    return twhour_now, pm_am_now

def get_date():
    # convert date to proper date
    date_now = str(datetime.datetime.now().date().day) + "-" + str(datetime.datetime.now().date().month)+ "-" + str(datetime.datetime.now().date().year)
    return date_now

def create_surfaces():
    GB.surface_day_main = pygame.Surface((450, 250))
    GB.surface_weather = pygame.Surface((100, 100))

def update_day_curve():

    city = lookup(constants.location, database())
    sun_info = sun(city.observer, date=datetime.datetime.now())

    time_left = (sun_info['sunrise'].hour * 60) + sun_info['sunrise'].minute + 35
    time_middle = ((sun_info['sunset'].hour * 60) + sun_info['sunset'].minute + 35) - ((sun_info['sunrise'].hour * 60) + sun_info['sunrise'].minute + 35) + time_left

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

def update_weather():
    Data = external.get_rf_data()

    GB.surface_weather.fill(constants.black) 

