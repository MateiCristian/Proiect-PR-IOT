#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
// #include <LiquidCrystal_I2C.h>

// Configurare WiFi
const char* ssid = "iPhone - Matei";
const char* password = "matei2301";
const char* serverUrl = "http://172.20.10.8:5000/api/data";
const char* commandUrl = "http://172.20.10.8:5000/api/command";
const char* apiToken = "xrZQcxrzjAup!5I&";  

// Configurare senzori
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define SOIL_SENSOR_PIN 34
#define LIGHT_SENSOR_PIN 35

// LCD
// LiquidCrystal_I2C lcd(0x27, 16, 2);

// Buzzer
#define BUZZER_PIN 27

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.println("Încerc să mă conectez la WiFi...");

  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED && retryCount < 20) {
    delay(500);
    Serial.print(".");
    retryCount++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectat la WiFi!");
    Serial.print("Adresa IP: ");
    Serial.println(WiFi.localIP());
  } else {
    while(WiFi.status() != WL_CONNECTED)
      Serial.println("\nEroare: Nu m-am putut conecta la WiFi. Verifică SSID/parola sau semnalul rețelei.");
    // while (true);  // Blochează programul pentru debug
  }

  dht.begin();
  pinMode(SOIL_SENSOR_PIN, INPUT);
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}


void sendSensorData() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soilMoisture = analogRead(SOIL_SENSOR_PIN);
  int lightLevel = analogRead(LIGHT_SENSOR_PIN);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", apiToken);  // Adaugă antetul cu token-ul

    String payload = "{\"temperature\":" + String(temp) + 
                     ",\"humidity\":" + String(humidity) + 
                     ",\"soil_moisture\":" + String(soilMoisture) +
                     ",\"light_level\":" + String(lightLevel) + "}";
    int httpResponseCode = http.POST(payload);
    Serial.println("Trimis date: " + String(httpResponseCode));
    http.end();
  }
}

void receiveCommand() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(commandUrl);
    http.addHeader("Authorization", apiToken);  // Adaugă token-ul de autentificare
    int httpResponseCode = http.GET();

     if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("Comandă primită: " + response);

      if (response == "humidity") {
        tone(BUZZER_PIN, 500, 500);
      } else if (response == "temperature") {
        tone(BUZZER_PIN, 700, 500);
      } else if (response == "light_level") {
        tone(BUZZER_PIN, 900, 500);
      } else if (response == "soil_moisture") {
        tone(BUZZER_PIN, 1200, 500);
      }
    } else if (httpResponseCode == 204) {
      Serial.println("Nicio comandă disponibilă.");
    } else {
      Serial.println("Eroare la primirea comenzii: " + String(httpResponseCode));
    }
    http.end();
  }
}

void loop() {
  sendSensorData();
  receiveCommand();
  delay(60000);  // Ajustează intervalul de actualizare
}
