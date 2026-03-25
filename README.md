# clue_midi
expansion of adafruit midi glove with additional features
I have a few versions. The most recent version is code.py and it exposes 6 midi messages, I also have a version with 4, and a version without the bar chart.:
# 🎛️ CLUE MIDI Motion Controller

A real-time **MIDI controller** built on the Adafruit CLUE using CircuitPython.
This project converts motion, proximity, and sensor data into expressive MIDI signals with a responsive on-device UI and live bar visualization.

---

## 🚀 Features

* 🎚️ **6 Modulation Sources**

  * Accelerometer (X, Y, Z)
  * Proximity sensor
  * Calculated acceleration magnitude
  * Aftertouch & pitch bend outputs

* 🎹 **MIDI Output**

  * USB MIDI
  * BLE MIDI (wireless)

* 🎛️ **Flexible Mapping**

  * Assignable CC values
  * Enable/disable per channel
  * Invert modulation per source

* 📊 **Real-Time Visualization**

  * Low-memory animated bar graph
  * Live value display per modulation source

* 🧭 **On-Device UI**

  * Touch navigation
  * Button-based editing
  * Channel selection (1–16)

---

## 🧰 Hardware

* Adafruit CLUE (nRF52840)
* Built-in sensors:

  * Accelerometer
  * Proximity sensor
  * Touch pads
  * Buttons

---

## 🧪 Software Requirements

* CircuitPython 10.x
* Required libraries:

  * `adafruit_clue`
  * `adafruit_ble`
  * `adafruit_ble_midi`
  * `adafruit_midi`
  * `adafruit_display_text`
  * `adafruit_display_shapes`

Copy all required libraries into the `/lib` folder on your CLUE.

---

## 📦 Installation

1. Install CircuitPython on your CLUE.
2. Copy required libraries to `/lib`.
3. Save the provided code as:

```
code.py
```

4. Reboot the device.

---

## 🎮 Controls

### Touch Inputs

* **Touch 0** → Cycle rows (mod sources / channel)
* **Touch 1** → Cycle columns (CC / invert / enable)
* **Touch 2** → Toggle value (invert / enable)

### Buttons

* **Button A / B**

  * Adjust CC values
  * Change MIDI channel

---

## 🎛️ Modulation Sources

| Source | Description            |
| ------ | ---------------------- |
| CC-X   | Accelerometer X-axis   |
| CC-Y   | Accelerometer Y-axis   |
| PROX   | Proximity sensor       |
| ACCL   | Acceleration magnitude |
| AFTT   | Channel pressure       |
| BEND   | Pitch bend             |

---

## 📡 MIDI Output

* Sends MIDI messages when values change
* Supports:

  * Control Change (CC)
  * Channel Pressure
  * Pitch Bend
* BLE MIDI automatically advertises as:

```
CLUE-6
```

---

## ⚡ Performance Notes

This project is optimized for **low memory usage** on the CLUE:

* Uses a **single bitmap** for bar visualization
* Avoids dynamic object allocation
* Incremental rendering prevents memory fragmentation

If you experience instability:

* Disable BLE for more headroom
* Reduce bar size or UI elements

---

## 🔧 Customization Ideas

* Add color gradients to bars
* Implement peak-hold meters
* Add preset storage in flash
* Map to musical scales or quantized values
* Integrate with Eurorack or synth rigs

---

## 🎯 Use Cases

* Motion-controlled MIDI modulation
* Live performance controller
* Experimental sound design
* MIDI LFO generator
* Wireless expressive controller

---

## 📜 License

MIT License (or your preferred license)

---

## 🙌 Acknowledgments

Built using the Adafruit CircuitPython ecosystem.

---

## 💡 Future Ideas

* Oscilloscope-style waveform display
* Multi-page UI
* MIDI clock sync
* Gesture recognition

---

Enjoy building and performing with it 🎶

