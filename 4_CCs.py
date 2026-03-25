import time
import board
import busio
import usb_midi
import math
from adafruit_clue import clue
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
import adafruit_ble_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
import simpleio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

# --- 1. MIDI Configuration ---
midi_channel = 1
cc_x_num, cc_y_num, cc_prox_num, cc_accel_num = 1, 2, 3, 4
cc_nums = [cc_x_num, cc_y_num, cc_prox_num, cc_accel_num]

# --- 2. UI Setup ---
screen = displayio.Group()
clue.display.root_group = screen
ORANGE, BLUE, SILVER, BROWN, GRAY, GREEN = 0xCE6136, 0x668190, 0xAAAAAA, 0x805D40, 0x080808, 0x00FF00
rows = [75, 110, 145, 180]
colors = [ORANGE, BLUE, SILVER, GREEN]

bg_sprite = displayio.TileGrid(displayio.Bitmap(240, 240, 1), x=0, y=0, pixel_shader=displayio.Palette(1))
bg_sprite.pixel_shader[0] = GRAY
screen.append(bg_sprite)
screen.append(Rect(0, 0, 240, 8, fill=BROWN)) 
screen.append(Rect(0, 54, 240, 4, fill=BROWN))

def create_label(text, x, y, color, scale=2):
    lbl = label.Label(terminalio.FONT, text=text, color=color, scale=scale)
    lbl.x, lbl.y = x, y
    screen.append(lbl)
    return lbl

title_label = create_label("MIDI CLUE", 14, 27, SILVER, scale=3)
cc_labels = []
val_labels = []

for i in range(4):
    cc_labels.append(create_label(f"CC {cc_nums[i]}", 20, rows[i], colors[i]))
    val_labels.append(create_label("0", 168, rows[i], colors[i]))

picker_box = Rect(3, rows[0]-8, 8, 16, fill=ORANGE)
screen.append(picker_box)
footer_label = create_label("Initializing...", 10, 215, SILVER, scale=1)

# --- 1. The "Known Good" MIDI Setup ---
midi_usb = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_channel - 1)
midi_service = adafruit_ble_midi.MIDIService()
midi_ble = adafruit_midi.MIDI(midi_out=midi_service, out_channel=midi_channel - 1)

ble = adafruit_ble.BLERadio()
# We go back to the simplest advertisement that worked for you
advertisement = ProvideServicesAdvertisement(midi_service)
ble.name = "CLUE-MIDI" 

# --- 2. Logic Variables ---
cc_num_pick_toggle = 0
cc_send_toggle = True      
last_vals = [-1, -1, -1, -1]

ble.start_advertising(advertisement)

while True:
    # Handle Advertising (Simple & Reliable)
    if not ble.connected and not ble.advertising:
        ble.start_advertising(advertisement)

    # Sensor Readings
    accel_x, accel_y, accel_z = clue.acceleration
    prox = clue.proximity

    # Mapping (CC4 centered at ~64)
    current_vals = [
        int(simpleio.map_range(accel_x, -9, 9, 0, 127)),
        int(simpleio.map_range(accel_y, -9, 9, 0, 127)),
        int(simpleio.map_range(prox, 2, 120, 0, 127)),
        int(simpleio.map_range(accel_z, -10.5, 9.5, 0, 127)) 
    ]
    current_vals = [min(127, max(0, v)) for v in current_vals]

    # MIDI Sending (The New "Bundled" Method)
    if cc_send_toggle:
        messages_to_send = []
        for i in range(4):
            # Only update UI and prepare message if value changed
            if abs(current_vals[i] - last_vals[i]) > 1:
                val_labels[i].text = str(current_vals[i])
                last_vals[i] = current_vals[i]
                messages_to_send.append(ControlChange(cc_nums[i], current_vals[i]))

        if messages_to_send:
            # USB Send
            midi_usb.send(messages_to_send)
            
            # BLE Send (The key to iOS/OP-1 seeing the data)
            if ble.connected:
                try:
                    midi_ble.send(messages_to_send)
                except:
                    pass

    # --- 3. Interaction Logic (Keep this exactly as is) ---
    if clue.touch_1:
        cc_num_pick_toggle = (cc_num_pick_toggle + 1) % 4
        picker_box.y = rows[cc_num_pick_toggle] - 8
        picker_box.fill = colors[cc_num_pick_toggle]
        time.sleep(0.2)

    if clue.button_a:
        cc_nums[cc_num_pick_toggle] = max(0, cc_nums[cc_num_pick_toggle] - 1)
        cc_labels[cc_num_pick_toggle].text = f"CC {cc_nums[cc_num_pick_toggle]}"
        time.sleep(0.15)

    if clue.button_b:
        cc_nums[cc_num_pick_toggle] = min(127, cc_nums[cc_num_pick_toggle] + 1)
        cc_labels[cc_num_pick_toggle].text = f"CC {cc_nums[cc_num_pick_toggle]}"
        time.sleep(0.15)

    if clue.touch_2:
        cc_send_toggle = not cc_send_toggle
        footer_label.text = "SENDING" if cc_send_toggle else "PAUSED"
        time.sleep(0.3)

    time.sleep(0.01)
