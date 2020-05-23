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
    surface_notifications = None
    surface_debug = None
    running = True
    update_control = True
    init_control = True
    is_day_time = 0
    tick_timer = 0
    last_weather_update = 0
    mode = 0
    pygame.freetype.init()
    main_font = pygame.freetype.Font("fonts/AurulentSansMono-Regular.otf", 180)
    main_font_medium = pygame.freetype.Font("fonts/Code New Roman.otf", 70)
    main_font_small = pygame.freetype.Font("fonts/F25_Bank_Printer.ttf", 40)
    main_font_tiny = pygame.freetype.Font("fonts/Code New Roman.otf", 30)
    temp_icon = pygame.image.load("icons/temp_icon.png")
    hum_icon = pygame.image.load("icons/hum_icon.png")
    sun_icon = pygame.image.load("icons/sun.png")
    cloud_icon = pygame.image.load("icons/cloud.png")
    moon_icon = pygame.image.load("icons/moon.png")

# force stop the display loop
def stop_display_loop():
    GB.running = False

# allow screen sleep mode
def screen_update_control():
    GB.update_control = True

# main display loop
def main_display_loop():
    pygame.init()
    #kill mixer, reduce cpu usage workaround
    pygame.mixer.quit()
    # set pygame settings
    pygame.display.set_caption('Black mirror')
    GB.screen = pygame.display.set_mode((1280,960), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # start loop
    while GB.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GB.running = False
            elif event.type == pygame.KEYDOWN:
                if event.unicode == 'q':
                    GB.running = False
                elif event.unicode == 'm':
                    GB.mode += 1
                    if GB.mode > 1:
                        GB.mode = 0
                    
        # update display
        if GB.update_control:
            update_display(GB.mode)
            pygame.display.update()
        
        #screen_update_control()
        # set fps
        clock.tick(1)

    pygame.quit()

def update_display(mode):

    GB.screen.fill(constants.black) 

    time_now, pm_am_now = get_time()
    GB.main_font.render_to(GB.screen, (50, 50), time_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (595, 155), pm_am_now, constants.white)
    GB.main_font_small.render_to(GB.screen, (200, 230), get_date(), constants.gray1)

    # Things to do only once
    if GB.init_control:
        create_surfaces()
        update_day_curve()
        update_weather()
        update_notifications()
        GB.init_control = False

    # Things to do once every 1 minute
    if GB.tick_timer > 60:
        update_day_curve()
        update_weather()
        GB.tick_timer = 0

    # Things to do always
    update_notifications()
    if mode == 1:
        debug_info(True)
    else:
        debug_info(False)

    GB.tick_timer += 1
    GB.screen.blit(GB.surface_day_main, [800,30])
    GB.screen.blit(GB.surface_weather, [800,290])
    GB.screen.blit(GB.surface_notifications, [20,270])
    GB.screen.blit(GB.surface_debug, [20,635])

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
    GB.surface_weather = pygame.Surface((450, 200))
    GB.surface_notifications = pygame.Surface((750, 350))
    GB.surface_debug = pygame.Surface((750, 300))

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
        GB.is_day_time = 0
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
        # save index
        GB.is_day_time = index

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
        GB.is_day_time = -1
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

    if Data == None:
        GB.main_font_small.render_to(GB.surface_weather, (0, 0), "Weather Station", constants.white)
        GB.main_font_small.render_to(GB.surface_weather, (0, 36), "not connected!", constants.white)
    else:
        GB.main_font_medium.render_to(GB.surface_weather, (85, 10), str(Data[0]) + '\u00b0' + "C", constants.white)
        GB.surface_weather.blit(GB.temp_icon, (10,0))
        GB.main_font_medium.render_to(GB.surface_weather, (85, 90), str(Data[1]) + "%", constants.white)
        GB.surface_weather.blit(GB.hum_icon, (5,79))
        if GB.is_day_time == 0 or GB.is_day_time == -1:
            GB.surface_weather.blit(GB.moon_icon, (290,25))
        else:

            #GB.surface_weather.blit(GB.sun_icon, (290,25))
            GB.surface_weather.blit(GB.cloud_icon, (290,25))

        if external.Ext_ctrl.new_rx_data == False:
            GB.last_weather_update += 1
            if GB.last_weather_update > 1:
                GB.main_font_tiny.render_to(GB.surface_weather, (145, 170), str(GB.last_weather_update) + " mins ago", constants.white)
        else:
            GB.last_weather_update = 0
            external.Ext_ctrl.new_rx_data = False

def update_notifications():
    GB.surface_notifications.fill(constants.black)
    GB.main_font_tiny.render_to(GB.surface_notifications, (30, 200), "This is a notification area, maybe", constants.white) 


def debug_info(cond):
    if cond:

        GB.surface_debug.fill(constants.black) 

        #draw box
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(180,3), (747,3)], 2)
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(180,3), (180,35)], 2)
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(3,35), (180,35)], 2)
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(747,3), (747,297)], 2)
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(3,35), (3,747)], 2)
        pygame.draw.lines(GB.surface_debug, constants.gray2, False, [(3,297), (747,297)], 2)

        #draw text
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 7), "Debug info", constants.white)

        #col 1
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 50), "Pi Temp: " + str(external.get_pi_temp()), constants.white)
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 80), "Tick Timer: " + str(GB.tick_timer), constants.white)
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 110), "Is Daytime: " + str(GB.is_day_time), constants.white)
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 140), "Last RF Updt: " + str(GB.last_weather_update), constants.white)
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 170), "RF Active: " + str(external.Ext_ctrl.rx_thread_running), constants.white)
        GB.main_font_tiny.render_to(GB.surface_debug, (7, 200), "RF Raw: " + str(external.Ext_ctrl.rx_buffer), constants.white)
    else:
        GB.surface_debug.fill(constants.black) 