using_pi = True
try:
    import time
    from gpiozero import CPUTemperature
    import piVirtualWire.piVirtualWire as piVirtualWire
    import pigpio
    import threading
except:
    using_pi = False

class Ext_devices():
    dhtDevice = None
    pigpioDevice = None
    RF_RX_Device = None

class Ext_ctrl():
    rx_thread = None
    rx_thread_running = False
    new_rx_data = False
    rx_buffer= None
    tx_buffer = None

def init_devices():
    if using_pi:
        print("init started, running on pi")
        #Init PIGIO 
        try:
            Ext_devices.pigpioDevice = pigpio.pi()
            print("pigpio started")
            #init virtual wire RX 
            Ext_devices.RF_RX_Device = piVirtualWire.rx(Ext_devices.pigpioDevice, 4, 1000)
            #enable screen
            Ext_devices.pigpioDevice.set_mode(17, pigpio.OUTPUT)
            Ext_devices.pigpioDevice.write(17,1)
            print("rx device started")
            #start thread 
            start_rx_thread()
            print("rx thread started")
            return 0
        except:
            return -1
    return -1

def get_pi_temp():
    if using_pi:
        cpu = CPUTemperature()
        return cpu.temperature
    return None

def start_rx_thread():
    if Ext_ctrl.rx_thread == None or Ext_ctrl.rx_thread.is_alive() == False:
        Ext_ctrl.rx_thread = threading.Thread(target=rf_data_routine)
        Ext_ctrl.rx_thread.start()
        Ext_ctrl.rx_thread_running = True

def stop_rx_thread():
    if Ext_ctrl.rx_thread_running:
        Ext_ctrl.rx_thread_running = False
        Ext_ctrl.rx_thread.join()
        Ext_devices.RF_RX_Device.cancel()
        Ext_devices.pigpioDevice.stop()

def rf_data_routine():
    print("rx routine started")
    while Ext_ctrl.rx_thread_running:
        while Ext_devices.RF_RX_Device.ready():
            buffer = Ext_devices.RF_RX_Device.get()
            Ext_ctrl.rx_buffer = buffer
            Ext_ctrl.new_rx_data = True
        time.sleep(0.5)

def get_rf_data():
    try:
        if len(Ext_ctrl.rx_buffer) > 4:
            temp = (int(chr(Ext_ctrl.rx_buffer[0])) * 10) + int(chr(Ext_ctrl.rx_buffer[1]))
            hum = (int(chr(Ext_ctrl.rx_buffer[2])) * 10) + int(chr(Ext_ctrl.rx_buffer[3]))
            panel_value = 0
            if len(Ext_ctrl.rx_buffer) == 5:
                panel_value = int(chr(Ext_ctrl.rx_buffer[4]))
            elif len(Ext_ctrl.rx_buffer) == 6:
                panel_value = (int(chr(Ext_ctrl.rx_buffer[4])) * 10) + int(chr(Ext_ctrl.rx_buffer[5]))
            elif len(Ext_ctrl.rx_buffer) == 7:
                panel_value = (int(chr(Ext_ctrl.rx_buffer[4])) * 100) + (int(chr(Ext_ctrl.rx_buffer[5])) * 10) + int(chr(Ext_ctrl.rx_buffer[6]))
            final_list = []
            final_list.append(temp)
            final_list.append(hum)
            final_list.append(panel_value)
            return final_list
    except:
        return None
    return None

def calculate_sun_brightness(current_time, panel_value):
    return 0

    


