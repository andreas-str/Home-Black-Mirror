import Adafruit_DHT

def get_home_temp_hum():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    except:
        print("get_home_hum_temp error")
    
    temp_hum = [humidity, temperature]
    return temp_hum

def get_outside_temp_hum():
    #do smth here