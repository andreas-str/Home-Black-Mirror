# import stuff here
import display
import external
import sq_database
try:
    from subprocess import call
except:
    print("no auto-shutdown supported!")


# main program code
def main():
    #start devices
    if external.init_devices() == -1:
        print("Device Init failed :(")
    #start display
    status = display.main_display_loop()
    external.stop_rx_thread()
    sq_database.close_database_connection()
    if status == True:
        call("sudo shutdown now", shell=True)

# run main
main()
