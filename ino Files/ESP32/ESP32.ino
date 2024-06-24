#include <Wire.h>
#include "SparkFun_LPS28DFW_Arduino_Library.h"
#include <SPI.h>

LPS28DFW pressureSensor;

uint8_t i2cAddress = LPS28DFW_I2C_ADDRESS_DEFAULT;

void setup()
{
    // Start serial
    Serial.begin(115200);
    // Initialize the I2C library
    Wire.begin();
    while(pressureSensor.begin(i2cAddress) != LPS28DFW_OK)
    {
        // Not connected, inform user
        Serial.println("Error: LPS28DFW not connected, check wiring and I2C address!");
        delay(1000);
    }

    Serial.println("LPS28DFW connected!");
}

void loop()
{
    pressureSensor.getSensorData();

    // Print temperature and pressure
    Serial.print("t: ");
    Serial.print(pressureSensor.data.heat.deg_c);
    Serial.print("\t\t");
    Serial.print("p: ");
    Serial.println(pressureSensor.data.pressure.hpa);

    // Delay
    delay(100);
}
