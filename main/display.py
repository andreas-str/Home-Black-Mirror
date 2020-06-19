import external
import constants
import time
import datetime
import pathlib
import pygame
import pygame.freetype
import pygame.gfxdraw
from astral.sun import sun
from astral.geocoder import database, lookup
import sq_database

main_path = pathlib.Path(__file__).parent.as_posix()
fonts_path = str(main_path) + "/fonts"
icons_path = str(main_path) + "/icons"


# Globals pls dont kill me I know ok
class GB():
    screen = None
    surface_day_main = None
    surface_weather = None
    surface_notifications = None
    surface_global_info = None
    surface_debug = None
    surface_graph = None
    running = True
    update_control = True
    intentional_shutdown = False
    init_control = True
    is_day_time = 0
    tick_timer = 0
    ir_timer = 0
    last_weather_update = 0
    mode = 0
    update_graph = False
    pygame.freetype.init()
    main_font = pygame.freetype.Font(fonts_path + "/AurulentSansMono_Regular.ttf", 150)
    main_font_medium = pygame.freetype.Font(fonts_path + "/Code_New_Roman.ttf", 70)
    main_font_small = pygame.freetype.Font(fonts_path + "/F25_Bank_Printer.ttf", 40)
    main_font_tiny = pygame.freetype.Font(fonts_path + "/Code_New_Roman.ttf", 30)
    temp_icon = pygame.image.load(icons_path+ "/temp_icon.png")
    hum_icon = pygame.image.load(icons_path+ "/hum_icon.png")
    sun_icon = pygame.image.load(icons_path+ "/sun.png")
    cloud_icon = pygame.image.load(icons_path+ "/cloud.png")
    moon_icon = pygame.image.load(icons_path+ "/moon.png")

# force stop the display loop
def stop_display_loop(cond):
    if cond:
        GB.intentional_shutdown = True
    GB.running = False

# main display loop
def main_display_loop():
    pygame.init()
    #kill mixer, reduce cpu usage workaround
    pygame.mixer.quit()
    # set pygame settings
    pygame.display.set_caption('Black mirror')
    if external.using_pi:
        GB.screen = pygame.display.set_mode((915,531), pygame.FULLSCREEN)
    else:
        GB.screen = pygame.display.set_mode((915,531), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    #hide mouse
    pygame.mouse.set_visible(False)

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
                    GB.update_graph = False
                    if GB.mode > 3:
                        GB.mode = 0
                elif event.unicode == 'f':
                    if GB.screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((915,531))
                    else:
                        pygame.display.set_mode((915,531), pygame.FULLSCREEN)
                    
        # update display
        if GB.update_control:
            update_display(GB.mode)
            pygame.display.update()
        
        #screen_update_control()
        # set fps
        clock.tick(1)
    pygame.quit()
    return GB.intentional_shutdown

def update_display(mode):

    GB.screen.fill(constants.black) 

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
        #after midnight, move todays data to yesterdays data on the database
        if(datetime.datetime.now().time().hour == 0 and datetime.datetime.now().time().minute <= 1):
            data = sq_database.get_data_today()
            sq_database.add_yesterday_database_data(data)
            sq_database.empty_today_database_data()

    # check ir sensor and count apropriately 
    if external.check_ir_sensor():
        GB.ir_timer += 1
        #reset main timer
        if GB.tick_timer > 0:
            GB.tick_timer = 0
    else:
        # normal transition, change modes
        if (GB.ir_timer >= 1 and GB.ir_timer < 5):
            GB.mode += 1
            GB.update_graph = False
            if GB.mode > 3:
                GB.mode = 0
        elif GB.ir_timer >= 5 and GB.ir_timer < 10:
            stop_display_loop(False)
        elif GB.ir_timer >= 10 and GB.ir_timer < 20:
            stop_display_loop(True)

        # update timers
        GB.ir_timer = 0
        GB.tick_timer += 1
    
    # update surfaces
    if mode == 0:  #main mode
        time_now, pm_am_now = get_time()
        update_notifications()
        GB.main_font.render_to(GB.screen, (10, 50), time_now, constants.white)
        GB.main_font_small.render_to(GB.screen, (125, 200), get_date(), constants.gray1)
        GB.screen.blit(GB.surface_day_main, [475,10])
        GB.screen.blit(GB.surface_weather, [475,270])
        GB.screen.blit(GB.surface_notifications, [20,270])
    elif mode == 1: #today graph
        if GB.update_graph == False:
            GB.surface_graph = draw_graph(1)
            GB.update_graph = True
        GB.screen.blit(GB.surface_graph, [0,0])
    elif mode == 2: #yesterday graph
        if GB.update_graph == False:
            GB.surface_graph = draw_graph(2)
            GB.update_graph = True
        GB.screen.blit(GB.surface_graph, [0,0])
    if mode == 3:  #debug mode
        debug_info()
        draw_graph(0)
        GB.screen.blit(GB.surface_debug, [80,110])
    
    #check ir again lastly, so info surface is on top
    if external.check_ir_sensor():
        # update info surface
        global_info(GB.ir_timer)
        GB.screen.blit(GB.surface_global_info, [0,0])


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
    GB.surface_notifications = pygame.Surface((450, 350))
    GB.surface_global_info = pygame.Surface((915,531), pygame.SRCALPHA)
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
            #get hour and save current data to todays database
            current_hour = datetime.datetime.now().time().hour
            weather_data = (int(Data[0]), int(Data[1]), int(Data[2]), current_hour, get_date(), current_hour)
            sq_database.update_database(weather_data)

def update_notifications():
    GB.surface_notifications.fill(constants.black)
    GB.main_font_tiny.render_to(GB.surface_notifications, (0, 150), "This is a notification area", constants.white) 


def debug_info():

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

def global_info(timer):

    GB.surface_global_info.fill(constants.dim) 
    color = constants.white
    size = 15

    if timer >= 5 and timer < 10:
        color = constants.red
    elif timer >= 10 and timer < 20:
        color = constants.red
        size = 50
        GB.main_font_medium.render_to(GB.surface_global_info, (200, 55), "Shutting down", constants.red)

    pygame.draw.lines(GB.surface_global_info, color, True, [(0,0), (915,0), (915,531), (0,531)], size)

def draw_graph(type):
    data = None
    temp_points = [(0,0)]*24
    hum_points = [(0,0)]*24
    panel_points = [(0,0)]*24
    surface_main = pygame.Surface((915,531))
    surface_temp = pygame.Surface((852, 130))
    surface_hum = pygame.Surface((852, 130))
    surface_sun = pygame.Surface((852, 130))
    #fill em black
    surface_temp.fill(constants.black) 
    surface_hum.fill(constants.black) 
    surface_sun.fill(constants.black)
    #draw boxes
    pygame.draw.lines(surface_temp, constants.white, False, [(0,0), (0,128), (850,128)], 2)
    pygame.draw.lines(surface_hum, constants.white, False, [(0,0), (0,128), (850,128)], 2)
    pygame.draw.lines(surface_sun, constants.white, False, [(0,0), (0,128), (850,128)], 2)
    #draw texts
    GB.main_font_small.render_to(surface_temp, (265, 15), "Temperature", constants.gray4)
    GB.main_font_small.render_to(surface_hum, (305, 15), "Humidity", constants.gray4)
    GB.main_font_small.render_to(surface_sun, (305, 15), "Sunlight", constants.gray4)

    if type == 1:
        data = sq_database.get_data_today()
        GB.main_font_small.render_to(surface_main, (380, 0), "Today", constants.white)
    elif type == 2:
        data = sq_database.get_data_yesterday()
        GB.main_font_small.render_to(surface_main, (340, 5), "Yesterday", constants.white)

    if data == None:
        GB.main_font_small.render_to(surface_main, (340, 100), "No Data!", constants.white)
        return surface_main
    #init values, reversed for sorting
    min_max_temp = [99, 0]
    min_max_hum = [99, 0]
    min_max_panel = [999, 0]
    for i in range(24):
        #find mins
        if data[i][1] > 0 and data[i][1] < min_max_temp[0]:
            min_max_temp[0] = data[i][1]
        if data[i][2] > 0 and data[i][2] < min_max_hum[0]:
            min_max_hum[0] = data[i][2]
        if data[i][3] > 0 and data[i][3] < min_max_panel[0]:
            min_max_panel[0] = data[i][3]
        #find maxs
        if data[i][1] > 0 and data[i][1] > min_max_temp[1]:
            min_max_temp[1] = data[i][1]
        if data[i][2] > 0 and data[i][2] > min_max_hum[1]:
            min_max_hum[1] = data[i][2]
        if data[i][3] > 0 and data[i][3] > min_max_panel[1]:
            min_max_panel[1] = data[i][3]

    #draw min max
    GB.main_font_tiny.render_to(surface_main, (15, 45), str(min_max_temp[1]), constants.white)
    GB.main_font_tiny.render_to(surface_main, (15, 155), str(min_max_temp[0]), constants.white)
    GB.main_font_tiny.render_to(surface_main, (15, 210), str(min_max_hum[1]), constants.white)
    GB.main_font_tiny.render_to(surface_main, (15, 320), str(min_max_hum[0]), constants.white)
    GB.main_font_tiny.render_to(surface_main, (0, 375), str(min_max_panel[1]), constants.white)
    GB.main_font_tiny.render_to(surface_main, (0, 485), str(min_max_panel[0]), constants.white)

    for i in range(0,7):
        GB.main_font_tiny.render_to(surface_main, (50+(i*137), 180), str(i*4), constants.white)
        GB.main_font_tiny.render_to(surface_main, (50+(i*137), 345), str(i*4), constants.white)
        GB.main_font_tiny.render_to(surface_main, (50+(i*137), 510), str(i*4), constants.white)

    for graph_data in data:
        if graph_data[1] > 0 and min_max_temp[1] != min_max_temp[0]:
            point = int(constants.map_num(graph_data[1], min_max_temp[0], min_max_temp[1], 0, 130))
            temp_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130-point))
        else:
            temp_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130))
        if graph_data[2] > 0 and min_max_hum[1] != min_max_hum[0]:
            point = int(constants.map_num(graph_data[2], min_max_hum[0], min_max_hum[1], 0, 130))
            hum_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130-point))
        else:
            hum_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130))
        if graph_data[3] > 0 and min_max_panel[1] != min_max_panel[0]:
            point = int(constants.map_num(graph_data[3], min_max_panel[0], min_max_panel[1], 0, 130))
            panel_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130-point))
        else:
            panel_points[graph_data[0]-1] = ((((graph_data[0]-1) * 37), 130))

    panel_points.append((0,130))
    hum_points.append((0,130))
    temp_points.append((0,130))

    pygame.gfxdraw.filled_polygon(surface_temp, temp_points, constants.white)
    pygame.gfxdraw.filled_polygon(surface_hum, hum_points, constants.white)
    pygame.gfxdraw.filled_polygon(surface_sun, panel_points, constants.white)

    #add surfaces to main surface and return
    surface_main.blit(surface_temp, [53,45])
    surface_main.blit(surface_hum, [53,210])
    surface_main.blit(surface_sun, [53,375])
    return surface_main

