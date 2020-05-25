
#include <VirtualWire.h>
#include "DHT.h"
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/power.h>

#define LED_PIN 13
#define TX_PIN 6
#define DHT_PIN 3
#define PANEL_PIN A1
//power pins used to enable/disable external devices, so that they use no power during sleep
#define POWER_PIN1 4
#define POWER_PIN2 5
int counter = 10;

DHT dht(DHT_PIN, DHT11);

// watchdog interrupt
ISR (WDT_vect)
{
  // disable watchdog
  wdt_disable();
}

void setup()
{
  //Serial.begin(9600);
  pinMode(POWER_PIN1, OUTPUT);
  pinMode(POWER_PIN2, OUTPUT);
  //pinMode(LED_PIN, OUTPUT);
  vw_set_tx_pin(TX_PIN);
  vw_setup(1000);	 // Bits per sec
  dht.begin();
}

void loop()
{

  // we sleep for 8 seconds on every loop run, so increasing counter comparison.. 
  // lets us skip everything and sleep longer and use less power
  if (counter++ > 10) {
    // reset timer
    counter = 0;
    // enable power
    digitalWrite(POWER_PIN1, HIGH);
    // wait for sensor to warm up. dht11 needs at least 200ms to get a reading, use faster sensors pls
    delay(240);
    // read sensors
    int t = dht.readTemperature();
    int h = dht.readHumidity();
    //read panel
    int panel_voltage_value = analogRead(PANEL_PIN);

    //disable sensor power, enable transmitter power
    digitalWrite(POWER_PIN1, LOW);
    digitalWrite(POWER_PIN2, HIGH);

    // compose final message
    //limit panel value to 999 for easier decoding on receiver
    panel_voltage_value = map(panel_voltage_value, 0, 1023, 0, 999);
    char msg[10];
    sprintf(msg, "%d%d%d", t, h, panel_voltage_value);
    //Serial.print("Humidity: ");
    //Serial.println(h);
    //Serial.print("temp: ");
    //Serial.println(t);
    //Serial.print("panel: ");
    //Serial.println(panel_voltage_value);

    // send message
    vw_send((uint8_t *)msg, strlen(msg));
    vw_wait_tx();
    // disable transmitter power
    digitalWrite(POWER_PIN2, LOW);
  }

////////////////////////////////////////////////////////////////////
////////////////////Sleep stuff here////////////////////////////////

  // disable ADC clock
  ADCSRA &= ~ (1 << ADEN);
  // disable all peripherals
  power_all_disable ();
  // clear various "reset" flags
  MCUSR = 0;
  // allow changes, disable reset
  WDTCSR = bit (WDCE) | bit (WDE);
  // set interrupt mode and an interval
  // set WDIE, and 8 seconds delay
  WDTCSR = bit (WDIE) | bit (WDP3) | bit (WDP0);
  //kick timer
  wdt_reset();

  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  noInterrupts ();
  sleep_enable();
  interrupts ();
  //go to sleep finally
  sleep_cpu ();

  // we awake, cancel sleep just in case
  sleep_disable();

  // enable everything back
  power_all_enable ();
  // enable adc clock
  ADCSRA |= (1 << ADEN);

}
