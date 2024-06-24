#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <Wire.h>
#include <SPI.h>

#define TFT_CS 10
#define TFT_RST 9
#define TFT_DC 8
#define ST7735_BLACK 0x0000
#define ST7735_RED 0xF800
#define ST7735_BLUE 0x001F

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);

const int LED_PIN = 13;  // Internal LED pin on Arduino Uno
const int SPEAKER_PIN = A3; // Speaker pin
const int SPEAKER_PIN2 = A2; // Speaker pin
unsigned long previousMillis = 0; // Variable to store the previous time
const long interval = 15000; // Interval in milliseconds (15 seconds)
const int toneFrequency = 1000; // Frequency in Hertz (you can adjust this as needed)
const int beepDuration = 5000; // Duration in milliseconds (5 seconds)
const int beepInterval = 1000; // Interval in milliseconds (1 second)
byte count = 10;
bool t = 0;

void setup(void) 
{
  // LCD Initialization
  tft.initR(INITR_BLACKTAB);
  tft.fillScreen(ST7735_BLUE);
  tft.println("");
  // Pin setup
  pinMode(LED_PIN, OUTPUT); // Set LED pin as output
  pinMode(SPEAKER_PIN, OUTPUT); // Set speaker pin as output
  Serial.begin(9600); // Initialize serial communication
  Serial.println("Setup complete. Send 'TRIGGERED' to turn on the LED.");
}

void loop() 
{
  if (Serial.available() > 0) 
  {
    String input = Serial.readString(); // Read serial input as a string
    input.trim(); // Remove leading and trailing whitespaces

    Serial.print("Received input: ");
    Serial.println(input); // Debug print

    if (input.indexOf("TRIGGERED") != -1)
    {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned ON");
      previousMillis = millis(); // Save the current time

      // Speaker beeping logic
      for (int i = 0; i < 3; i++) 
      {
        tone(SPEAKER_PIN, toneFrequency, beepDuration);
        tone(SPEAKER_PIN2, toneFrequency, beepDuration);
        tft.fillScreen(ST7735_RED);
        delay(beepDuration); // Wait for the beep to finish
        if (i < 2) 
        {
          delay(beepInterval); // Wait for the interval between beeps
        }
      }
      noTone(SPEAKER_PIN); // Stop the tone after beeping sequence
      noTone(SPEAKER_PIN2);
      tft.fillScreen(ST7735_BLACK);
    }else 
    {
      Serial.println("Input not recognized");
    }
  }
}
