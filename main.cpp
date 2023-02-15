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



//Podesiti u labosu

const char *ssid = "S20";
const char *password = "Matislobode";

float bpm =14.7;
float vrijednost=120;







StaticJsonDocument <200> doc;



WiFiServer server(80);
WiFiClient client;



void setup()

{
  Serial.begin(9600);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(250);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("IP adresa: ");
  Serial.println(WiFi.localIP());

  server.begin();
}





void loop()
{
 


   doc["bpm"]=bpm;
   doc["temperatura"]=vrijednost;



   String json;
   String jsonPretty;

   serializeJson(doc,json);
    delay(1000);


    Serial.println(json);

   const char *serverName= "http://192.168.66.199/vitalne_funkcije";
    HTTPClient http;
    http.begin(serverName);


    http.addHeader("Content-Type","application/json");


    int httpResponseCode =http.POST(json);
    delay(2000);



    Serial.println(httpResponseCode);
    Serial.println(http.getString());
    http.end();



   
}