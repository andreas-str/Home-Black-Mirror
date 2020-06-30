# Home-Black-Mirror

Small project using a small screen and a Raspberry Pi to display some constant information related to time, weather and notifications


# Raspberry Pi

This project was made to run on the original Raspberry Pi Model B, so because of the limited cpu power, a few compremises had to be made

To run, you need Python 3, and for dependancies you need astral, pygame, gpiozero, piVirtualWire and lastly pigpio. pigpio needs to be started prior to starting the the program. 

The system uses a 433Mhz receiver to get weather information from the weather station
User input is done using an ir range sensor

The resolution set is custom to fit on a composite 4.3" lcd. The main surfaces can be rearanged to fit a bigger screen if needed.

To run, execute the main with "python3 main.py" Pressing Q will quit the program. M will switch through the different modes

This program will run on a device other than a Raspberry pi for testing purposes 

Dependances: (can be instelled using PIP)
pathlib, pygame, astral, sqlite3, pigpio, gpiozero, imaplib

# Arduino

The arudino is used as the brains of the weather station. Its an Arduino pro mini, running at 8Mhz and 3v3. Attached to it are a DHT11 temperature and humidity sensor, a 433Mhz transmitter and a 2.5v solar panel. 

Code dependancies are DHT library as well as VirtualWire

The arduino is powered by a 9v battery

The arduino goes to power down sleep mode for 8 seconds using the watchdog timer, wakes up, increments a timer and goes back to sleep. After about 10 itteration, the sensors are powered up, a reading is taken and transmitted, and then it goes back to sleep. This cycle is continued forever
