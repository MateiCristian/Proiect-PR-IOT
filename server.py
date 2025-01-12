from flask import Flask, request, jsonify, render_template
from flask import abort
from firebase import firebase
import requests
import threading
import time

app = Flask(__name__)

# Variabilă globală pentru ultima comandă
last_command = ""

API_TOKEN = "xrZQcxrzjAup!5I&"

firebase = firebase.FirebaseApplication('https://proiect-pr-default-rtdb.firebaseio.com/', None)

# Variabile globale pentru datele senzorilor
sensor_data = {
    "temperature": "N/A",
    "humidity": "N/A",
    "light_level": "N/A",
    "soil_moisture": "N/A"
}

# Istoricul valorilor pentru fiecare parametru
sensor_history = {
    "temperature": [],
    "humidity": [],
    "light_level": [],
    "soil_moisture": []
}

BOT_TOKEN = '7578328473:AAHfkWPB5qGv7qGmsa9QySXqxTBSYej0nuM'
CHAT_ID = '7632190114'

@app.route('/')
def index():
    # Trimite variabila 'sensor_data' către șablonul HTML ca 'data'
    result = firebase.get('/Content-Type', None)
    print(result)
    return render_template('index.html', data=sensor_data, history=sensor_history)

@app.before_request
def validate_token():
    # Obține token-ul din antetul cererii HTTP
    # Listează rutele care nu necesită token
    exempt_routes = ['/', '/static/', '/command/temperature', '/command/humidity', '/command/light_level', '/command/soil_moisture']
    
    # Dacă ruta cerută este în lista de excepții, continuă fără verificare
    if request.path in exempt_routes or request.path.startswith('/static/'):
        return
    
    token = request.headers.get("Authorization")
    if token != API_TOKEN:
        abort(403, description="Unauthorized: Invalid token")  # Refuză cererea dacă token-ul nu este corect

@app.route('/api/data', methods=['POST'])
def receive_data():
    global sensor_data, sensor_history
    data = request.json
    print(f"Date primite: {data}")
    # Actualizează datele senzorilor
    sensor_data.update(data)

     # Stochează datele în istoricul valorilor (limitat la ultimele 20 de intrări)
    for key in sensor_history:
        if key in data:
            sensor_history[key].append(data[key])
            if len(sensor_history[key]) > 20:
                sensor_history[key].pop(0)
                
     # Trimite datele în Firebase
    try:
        timestamp = str(int(time.time()))
        firebase.put('/Content-Type', name=timestamp, data=sensor_data)  # Înlocuiește valorile existente
        print("Datele au fost trimise cu succes în Firebase.")
    except Exception as e:
        print(f"Eroare la trimiterea datelor în Firebase: {e}")

    return jsonify({"status": "success"})

@app.route('/api/command', methods=['GET'])
def send_command():
    global last_command

    # Returnează comanda și apoi o resetează
    if last_command:
        command_to_send = last_command
        last_command = ""  # Resetează comanda
        return command_to_send
    else:
        return "", 204  # Nicio comandă disponibilă

@app.route('/command/<action>', methods=['POST'])
def set_command(action):
    global last_command
    allowed_commands = ["humidity", "temperature", "light_level", "soil_moisture"]
    if action in allowed_commands:
        last_command = action
        print(f"Comandă setată: {last_command}")
        return jsonify({"status": "command_set", "command": last_command})
    else:
        return jsonify({"status": "error", "message": "Invalid command"}), 400

@app.route('/api/notify', methods=['POST'])
def manual_notify():
    send_telegram_message(f"Actualizare date: {sensor_data}")
    return jsonify({"status": "Notification sent"})

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Mesaj trimis cu succes pe Telegram!")
    except Exception as e:
        print(f"Eroare la trimiterea mesajului: {e}")

def send_command_to_esp(action):
    allowed_commands = ["humidity", "temperature", "light_level", "soil_moisture"]
    if action in allowed_commands:
        try:
            response = requests.post(f"http://127.0.0.1:5000/command/{action}")
            if response.status_code == 200:
                print(f"Comandă trimisă către ESP32: {action}")
            else:
                print(f"Eroare la trimiterea comenzii: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Eroare la trimiterea comenzii către ESP32: {e}")
    else:
        print(f"Comandă invalidă: {action}")

def check_sensor_values():
    global sensor_data
    while True:
        try:
            # Praguri pentru notificări
            if sensor_data['temperature'] != "N/A" and float(sensor_data['temperature']) > 10:
                send_telegram_message(f"Temperatura este ridicată: {sensor_data['temperature']} °C")
                send_command_to_esp("temperature")  # Trimite comanda către ESP32
            
            if sensor_data['humidity'] != "N/A" and float(sensor_data['humidity']) < 30:
                send_telegram_message(f"Umiditatea este scăzută: {sensor_data['humidity']} %")
                send_command_to_esp("humidity")  # Trimite comanda către ESP32
            
            if sensor_data['soil_moisture'] != "N/A" and float(sensor_data['soil_moisture']) < 20:
                send_telegram_message(f"Umiditatea solului este scăzută: {sensor_data['soil_moisture']}")
                send_command_to_esp("soil_moisture")  # Trimite comanda către ESP32
            
            if sensor_data['light_level'] != "N/A" and float(sensor_data['light_level']) > 1000:
                send_telegram_message(f"Nivelul de lumină este ridicat: {sensor_data['light_level']} lx")
                send_command_to_esp("light_level")  # Trimite comanda către ESP32
        except Exception as e:
            print(f"Eroare în verificarea valorilor: {e}")
        
        # Interval de verificare (în secunde)
        time.sleep(60)



if __name__ == '__main__':
    # Pornește verificarea valorilor într-un thread separat
    threading.Thread(target=check_sensor_values, daemon=True).start()

    app.run(host='0.0.0.0', port=5000)
