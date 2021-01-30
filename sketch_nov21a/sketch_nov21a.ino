#include <Wire.h>
#include "AirQuality.h"
#include "Arduino.h"
#include "DHT.h"

#include <SPI.h>
#include <SD.h>
const byte SDCARD_CS_PIN = 10;
/* 1: Salle de bain
 2: Commodités
 3: Salon
 4: Chambre 1
 5: Chambre 2
 6: Cuisine
 7: Couloir*/
char* filename= "05-14_7.csv"; //si trop long => crash
String context= "14;5;23;30;0;7;1"; //day;month;our;minute;second;salle;couloir(bool)
const unsigned long DELAY_BETWEEN_MEASURES = 0000;
String dataString =""; // holds the data to be written to the SD card
File file;


#define DHTPIN 2     // what pin the DHT is connected to
// Uncomment whatever type you're using!
#define DHTTYPE DHT11   // DHT 11
//#define DHTTYPE DHT22   // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE);

AirQuality airqualitysensor;
int current_quality =-1;
#define BUZZER 10

int dust_pin = 4;
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;//sampe 30s ;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;

void saveData(){
  if(SD.exists(filename)){ // check the card is still there
    // now append new data file
    file = SD.open(filename, FILE_WRITE);
    if (file){
      Serial.println("new line");
      file.println(dataString);
      file.close(); // close the file
    }else{
      Serial.println("Error writing to file !");
    }
  }
}
void setup()
{
  Wire.begin();    // initialize i2c

  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
  pinMode(dust_pin,INPUT);
  
  airqualitysensor.init(14);
  dht.begin();
  Serial.begin(9600);
  
  /* Initialisation de la carte SD */
  Serial.println(F("Initialisation de la carte SD ... "));
  if (!SD.begin(SDCARD_CS_PIN)) {
    Serial.println(F("Erreur : Impossible d'initialiser la carte SD"));
    Serial.println(F("Verifiez la carte SD et appuyez sur le bouton RESET"));
    for (;;); // Attend appui sur bouton RESET
  }

  /* Ouvre le fichier de sortie en écriture */
  Serial.println(F("Ouverture du fichier de sortie ... "));
  file = SD.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println(F("Erreur : Impossible d'ouvrir le fichier de sortie"));
    Serial.println(F("Verifiez la carte SD et appuyez sur le bouton RESET"));
    for (;;); // Attend appui sur bouton RESET
  }
  file.println("Jour;Mois;Heure;Minutes;Secondes;Lieu;Couloir;Temperature;Humidite;Particules;Qualite;Son");
  file.close();
}

void loop()
{
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  long sound = analogRead(A0);

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Checking Air Quality
  current_quality=airqualitysensor.slope();
 
  // Checking Dust Sensor
  duration = pulseIn(dust_pin, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;

  if ((millis()-starttime) > sampletime_ms) //if the sample time == 30s
  {
    ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
    lowpulseoccupancy = 0;
    starttime = millis();
  }

  Serial.print(t);
  Serial.print(";");
  Serial.print(h);
  Serial.print(";");
  Serial.print(concentration);
  Serial.print(";");
  Serial.print(airqualitysensor.first_vol);
  Serial.print(";");
  //Serial.println(current_quality);
  float volt = sound * (5.0 / 1023.0);
  sound = 94 + ( 20.0  * log10 (volt/3.16));
  Serial.println(sound);
  
  dataString = context+";"+String(t)+";"+String(h)+";"+String(concentration)+";"
                      +String(airqualitysensor.first_vol)+";"+String(sound);
  saveData();
  delay(DELAY_BETWEEN_MEASURES);
}

ISR(TIMER2_OVF_vect)
{
  if(airqualitysensor.counter==122)//set 2 seconds as a detected duty
  {

    airqualitysensor.last_vol=airqualitysensor.first_vol;
    airqualitysensor.first_vol=analogRead(A3);
    airqualitysensor.counter=0;
    airqualitysensor.timer_index=1;
    //PORTB=PORTB^0x20;
  }
  else
  {
    airqualitysensor.counter++;
  }
}
