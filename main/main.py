# import stuff here
import display
import external

# main program code
def main():
    #start devices
    if external.init_devices() == -1:
        print("Device Init failed :(")
        #return None
    #start display
    display.main_display_loop()
    external.stop_rx_thread()

# run main
main()
