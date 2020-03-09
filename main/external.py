using_pi = True
try:
    from gpiozero import CPUTemperature
    import Adafruit_DHT
except:
    using_pi = False


def get_home_temp_hum():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    except:
        print("get_home_hum_temp error")
        return None

    return temperature, humidity

def get_pi_temp():
    if using_pi:
        cpu = CPUTemperature()
        pi_temp = cpu.temperature
        return pi_temp
    return None

def get_outside_temp_hum():
    #do smth here
    return 1
