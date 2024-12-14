from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Variabilă globală pentru ultima comandă
last_command = ""

# Variabile globale pentru datele senzorilor
sensor_data = {
    "temperature": "N/A",
    "humidity": "N/A",
    "light": "N/A",
    "soil_moisture": "N/A"
}

# Istoricul valorilor pentru fiecare parametru
sensor_history = {
    "temperature": [],
    "humidity": [],
    "light_level": [],
    "soil_moisture": []
}

@app.route('/')
def index():
    # Trimite variabila 'sensor_data' către șablonul HTML ca 'data'
    return render_template('index.html', data=sensor_data, history=sensor_history)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
