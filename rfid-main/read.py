from flask import Flask, jsonify
from flask_cors import CORS
from evdev import InputDevice, categorize, ecodes
import select

DEVICE_PATH = '/dev/input/event0'  

app = Flask(__name__)
CORS(app)

device = InputDevice(DEVICE_PATH)
print(f"Lector conectado: {device.name}")

KEYMAP = {
    2: '1', 3: '2', 4: '3', 5: '4', 6: '5',
    7: '6', 8: '7', 9: '8', 10: '9', 11: '0'
}

@app.route('/rfid_uid', methods=['GET'])
def get_rfid_uid():
    print("Acerca la tarjeta:")
    uid = ""
    while True:
        r, _, _ = select.select([device], [], [], 6)
        if device in r:
            for event in device.read():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        code = key_event.scancode
                        if code == 28: 
                            print(f"UID leído: {uid}")
                            return jsonify({"uid": uid})
                        elif code in KEYMAP:
                            uid += KEYMAP[code]
        else:
            print("Tiempo de espera agotado.")
            return jsonify({"error": "No se ha leído ninguna tarjeta"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)