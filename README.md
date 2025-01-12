# Proiect-PR-IOT
Sistem de monitorizare pentru o seră inteligentă

1. Introducere
Descriere generală:
    Proiectul presupune dezvoltarea unui sistem de monitorizare și control bazat pe microcontroller-ul ESP32, 
care colectează date despre condițiile ambientale folosind senzori și trimite informații prin actuatori. Proiectul 
este reprezentat de creearea unui sistem pentru o seră inteligentă, care să măsoare temperatura, umiditatea, 
factorul de lumină și umiditatea solului.

Obiectivele proiectului:
    Monitorizarea temperaturii, umidității aerului, luminii ambientale și umidității solului.
    Controlul activităților printr-o aplicație de control bazată pe un server Flask.
    Afișarea alertelor folosind un buzzer, un led și, opțional, un display LCD pentru mesaje informative.

Tehnologii folosite:
    ESP32 pentru conectivitate WiFi și interfațarea cu senzori.
    Flask pentru backend și gestionarea comenzilor.
    HTTP Client pentru comunicarea între ESP32 și server.
    Arduino IDE pentru crearea codului de pe placuța ESP32.

2. Arhitectura Sistemului
Diagramă de topologie a rețelei:
    Include o diagramă logică ce arată conexiunile între componente:
        ESP32 -> Server Flask (rețea WiFi locală)
    Senzori conectați la ESP32:
        DHT22: Temperatură și umiditate aer 
        Senzor analogic pentru umiditatea solului
        Fotorezistor pentru măsurarea nivelului de lumină
    Actuatori conectați:
        Buzzer pentru alerte, un led ce se aprinde pentru a simula "aducerea de lumină" când este cazul.
        (Opțional) LCD I2C pentru afișarea informațiilor.

3. Protocoale de Comunicație
    WiFi (802.11): Utilizat pentru conectarea ESP32 la serverul Flask.
    I2C (eventual): Daca voi face și partea cu ecranul LCD.
    HTTP REST API:
        Metoda POST: Transmiterea datelor de la senzori către server.
        Endpoint: /api/data
        Metoda GET: Preluarea comenzilor de la server.
        Endpoint: /api/command
            Răspuns: {"command": "humidity"}

4. Descrierea Componentelor
Senzori:
    DHT22:
        Rol: Măsoară temperatura și umiditatea aerului.
        Conectare: Pin digital pe ESP32.
    
    Senzor de Umiditate Sol:
        Rol: Măsoară umiditatea solului în mod analogic.
        Conectare: Pin analogic (A0) pe ESP32.

    Fotorezistor:
        Rol: Măsoară intensitatea luminii.
        Conectare: Pin analogic.

Actuatori:
    Buzzer:
        Rol: Avertizează utilizatorul în funcție de comanda primită.
        Control: Pin digital.
    Led:
        Rol: Avertizează utilizatorul în funcție de comanda primită.
        Control: Pin digital.
   
    LCD I2C (opțional):
        Rol: Afișează mesaje precum „Umiditatea aerului scăzută”.
        Interfață: I2C (SDA, SCL).

Server Flask:
    Rol: Gestionarea datelor de la senzori și trimiterea comenzilor către ESP32.
    Endpoints:
        /api/data (POST): Primește date de la ESP32.
        /api/command (GET): Trimite comenzi către ESP32.

5. Funcționarea Sistemului
Inițializare ESP32:
    Se conectează la rețeaua WiFi.
    Inițializează senzorii și actuatorii.

Transmiterea datelor:
    ESP32 colectează datele senzorilor.
    Trimite datele către server printr-o cerere HTTP POST.

Primirea comenzilor:
    Serverul trimite comenzi (ex: humidity, temperature) în funcție de nevoile definite.
    ESP32 reacționează (ex: activează buzzerul sau afișează pe LCD).

Comunicarea bidirecțională:
    Sistemul oferă feedback în timp real între server și microcontroller.