#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include "HX711.h"

#include "Wire.h"
#include <MAX3010x.h>
#include "filters.h"

#include <SPI.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_MLX90614.h>

// Definiranje senzora i display-a
LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// Podesiti u labosu
String server_ip = "192.168.1.198:5000";
const char *ssid = "S20";
const char *password = "Matislobode";
const int GUMB_mjerenje = 16;
const int LED_indikator = 17;

// Sensor (adjust to your sensor type)
MAX30102 sensor;
const auto kSamplingRate = sensor.SAMPLING_RATE_400SPS;
const float kSamplingFrequency = 400.0;

// Finger Detection Threshold and Cooldown
const unsigned long kFingerThreshold = 10000;
const unsigned int kFingerCooldownMs = 500;

// Edge Detection Threshold (decrease for MAX30100)
const float kEdgeThreshold = -2000.0;

// Filters
const float kLowPassCutoff = 5.0;
const float kHighPassCutoff = 0.5;

// Averaging
const bool kEnableAveraging = false;
const int kAveragingSamples = 5;
const int kSampleThreshold = 5;

// const char *ssid = "ljolja";
// const char *password = "purs2023";

const int DOUT = 22;
const int SCK_PIN = 18;
const int tipkalo = 13;

const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 5895655;

int tipkalo_pom, pomocna;
HX711 scale;

StaticJsonDocument<200> doc;

WiFiClient client;
long sila;
int id = 0;
float sila_raw = 0;
float prava_sila;

void setup()
{

  Serial.begin(9600);

  // Inicijalizacija gumba za mjerenje
  pinMode(GUMB_mjerenje, INPUT);
  pinMode(LED_indikator, OUTPUT);

  // Inicijalizacija infracrvenog senzora
  // Potrebno je pozvati prije uzimanja mjerenja sa senzora
  mlx.begin();
 
  // Inicijalizacija LCD-a
  lcd.init();
  // Paljenje pozadine LCD-a
  lcd.backlight();

  if (sensor.begin() && sensor.setSamplingRate(kSamplingRate))
  {
    Serial.println("Sensor initialized");
  }
  else
  {
    Serial.println("Sensor not found");
  
  }

  // Početak spajanja na WiFi
  WiFi.begin(ssid, password);


  //Sve dok nismo spojeni na WiFi, ispisuj točke u terminal svakih 250 milisekundi
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(250);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("IP adresa: ");
  Serial.println(WiFi.localIP());

  Serial.println("Uređaj je spreman za mjerenje i slanje podataka!");

}

// Filter Instances
LowPassFilter low_pass_filter_red(kLowPassCutoff, kSamplingFrequency);
LowPassFilter low_pass_filter_ir(kLowPassCutoff, kSamplingFrequency);
HighPassFilter high_pass_filter(kHighPassCutoff, kSamplingFrequency);
Differentiator differentiator(kSamplingFrequency);
MovingAverageFilter<kAveragingSamples> averager_bpm;
MovingAverageFilter<kAveragingSamples> averager_r;
MovingAverageFilter<kAveragingSamples> averager_spo2;

// Statistic for pulse oximetry
MinMaxAvgStatistic stat_red;
MinMaxAvgStatistic stat_ir;

// R value to SpO2 calibration factors
// See https://www.maximintegrated.com/en/design/technical-documents/app-notes/6/6845.html
float kSpO2_A = 1.5958422;
float kSpO2_B = -34.6596622;
float kSpO2_C = 112.6898759;

// Timestamp of the last heartbeat
long last_heartbeat = 0;

// Timestamp for finger detection
long finger_timestamp = 0;
bool finger_detected = false;

// Last diff to detect zero crossing
float last_diff = NAN;
bool crossed = false;
long crossed_time = 0;

void spremi_u_bazu(double vrijednost) 
{
  String vrijednost_string = String(vrijednost); // Pripremanje vrijednosti za slanje na server(konverzija  iz decimalnog broja u tekst)

  // Slanje podataka na server
  HTTPClient http;
  http.begin("http://" + server_ip + "/unos_temperature"); // Određivanje adrese na koju šaljemo podatke
  http.addHeader("Content-Type", "application/json"); // Tip podatka koji šaljemo na server da server zna kako tretirati taj podatak
  http.POST("{\"vrijednost\":" + vrijednost_string + "}"); // Samo slanje podataka na server
  http.end(); // Zatvaranje konekcije sa serverom i čiščenje radne memorije kontrolera
}

void loop()
{
// Provjera da li je gumb pritisnut
  if (digitalRead(GUMB_mjerenje) == HIGH)
  {
    digitalWrite(LED_indikator, HIGH); // LED indikator svijetli dok traje mjerenje temperature

    Serial.println("Mjerenje temperature...");

    lcd.setCursor(2, 0);       // Postavljanje teksta na 2. stupac i 0. redak
    lcd.print("Temperatura:"); // Ispisivanje teksta na LCD-u

// Uzimanje mjerenja senzorom
    double vrijednost = mlx.readObjectTempC();

    lcd.setCursor(4, 1);   // Postavljanje teksta na 4. stupac i 1. redak
    lcd.print(vrijednost); // Ispisivanje temperature na LCD-u
    lcd.print(" C");       // Ispisivanje temperature na LCD-u

    // Slanje podataka na server samo ako su validni
    if (vrijednost != 0)
      spremi_u_bazu(vrijednost);

    digitalWrite(LED_indikator, LOW); // Gasimo LED indikator nakon završetka mjerenja
  }
  
    auto sample = sensor.readSample(1000);
    float current_value_red = sample.red;
    float current_value_ir = sample.ir;

    // Detect Finger using raw sensor value
    if (sample.red > kFingerThreshold)
    {
      if (millis() - finger_timestamp > kFingerCooldownMs)
      {
        finger_detected = true;
      }
    }
    else
    {
      // Reset values if the finger is removed
      differentiator.reset();
      averager_bpm.reset();
      averager_r.reset();
      averager_spo2.reset();
      low_pass_filter_red.reset();
      low_pass_filter_ir.reset();
      high_pass_filter.reset();
      stat_red.reset();
      stat_ir.reset();

      finger_detected = false;
      finger_timestamp = millis();
    }

    if (finger_detected)
    {
      current_value_red = low_pass_filter_red.process(current_value_red);
      current_value_ir = low_pass_filter_ir.process(current_value_ir);

      // Statistics for pulse oximetry
      stat_red.process(current_value_red);
      stat_ir.process(current_value_ir);

      // Heart beat detection using value for red LED
      float current_value = high_pass_filter.process(current_value_red);
      float current_diff = differentiator.process(current_value);

      // Valid values?
      if (!isnan(current_diff) && !isnan(last_diff))
      {

        // Detect Heartbeat - Zero-Crossing
        if (last_diff > 0 && current_diff < 0)
        {
          crossed = true;
          crossed_time = millis();
        }

        if (current_diff > 0)
        {
          crossed = false;
        }

        // Detect Heartbeat - Falling Edge Threshold
        if (crossed && current_diff < kEdgeThreshold)
        {
          if (last_heartbeat != 0 && crossed_time - last_heartbeat > 300)
          {
            // Show Results
            int bpm = 60000 / (crossed_time - last_heartbeat);
            float rred = (stat_red.maximum() - stat_red.minimum()) / stat_red.average();
            float rir = (stat_ir.maximum() - stat_ir.minimum()) / stat_ir.average();
            float r = rred / rir;
            float spo2 = kSpO2_A * r * r + kSpO2_B * r + kSpO2_C;

            if (bpm > 50 && bpm < 250)
            {
              // Average?
              if (kEnableAveraging)
              {
                int average_bpm = averager_bpm.process(bpm);
                int average_r = averager_r.process(r);
                int average_spo2 = averager_spo2.process(spo2);

                // Show if enough samples have been collected
                if (averager_bpm.count() >= kSampleThreshold)
                {
                  Serial.print("Time (ms): ");
                  Serial.println(millis());
                  Serial.print("Heart Rate (avg, bpm): ");
                  Serial.println(average_bpm);
                  Serial.print("R-Value (avg): ");
                  Serial.println(average_r);
                  Serial.print("SpO2 (avg, %): ");
                  Serial.println(average_spo2);
                }
              }
              else
              {
                Serial.print("Time (ms): ");
                Serial.println(millis());
                Serial.print("Heart Rate (current, bpm): ");
                Serial.println(bpm);
                Serial.print("R-Value (current): ");
                Serial.println(r);
                Serial.print("SpO2 (current, %): ");
                Serial.println(spo2);
              }
            }

            // Reset statistic
            stat_red.reset();
            stat_ir.reset();
          }

          crossed = false;
          last_heartbeat = crossed_time;
        }
      }

      last_diff = current_diff;
    }

    doc["bpm"] = last_heartbeat;

    String json;
    String jsonPretty;

    serializeJson(doc, json);

    Serial.println(json);

    HTTPClient http;
    http.begin("http://"  + server_ip +  "/vitalne_funkcije");

    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(json);
    delay(1000);

    Serial.println(httpResponseCode);
    Serial.println(http.getString());
    http.end(); 
}
