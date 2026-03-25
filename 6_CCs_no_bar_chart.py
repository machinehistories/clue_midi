import time
import board
import usb_midi
import math
import adafruit_ble
from adafruit_clue import clue
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
import adafruit_ble_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.channel_pressure import ChannelPressure
import simpleio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

# --- 1. Global Setup ---
midi_chan = 1
mods = [
    ["CC-X", 1, True, False, 0, False], ["CC-Y", 2, True, False, 0, False],
    ["PROX", 3, True, False, 0, False], ["ACCL", 4, True, False, 0, False],
    ["AFTT", 0, True, False, 0, True],  ["BEND", 0, True, False, 0, True]
]

# --- 2. UI Setup ---
screen = displayio.Group()
clue.display.root_group = screen

chan_lbl = label.Label(terminalio.FONT, text="CH:1", scale=3, x=150, y=25, color=0x444444)
screen.append(chan_lbl)

rows_y = [70, 100, 130, 160, 190, 220]
name_lbls, cc_lbls, inv_lbls, val_lbls, status_boxes = [], [], [], [], []

for i in range(6):
    nl = label.Label(terminalio.FONT, text=mods[i][0], scale=2, x=10, y=rows_y[i], color=0x888888)
    name_lbls.append(nl); screen.append(nl)
    
    cc_text = str(mods[i][1]) if not mods[i][5] else "--"
    cl = label.Label(terminalio.FONT, text=cc_text, scale=2, x=80, y=rows_y[i], color=0x555555)
    cc_lbls.append(cl); screen.append(cl)
    
    il = label.Label(terminalio.FONT, text="+", scale=2, x=120, y=rows_y[i], color=0x666666)
    inv_lbls.append(il); screen.append(il)
    
    box = Rect(150, rows_y[i]-8, 14, 14, fill=0x444444, outline=0x666666)
    status_boxes.append(box); screen.append(box)
    
    vl = label.Label(terminalio.FONT, text="0", scale=2, x=195, y=rows_y[i], color=0xFFFFFF)
    val_lbls.append(vl); screen.append(vl)

# Selection Outlines (Pre-created to avoid AttributeError)
# 0: CC Column, 1: Invert Column, 2: Status Column, 3: Channel Header
selectors = [
    Rect(75, 0, 35, 24, outline=0xFFFFFF, stroke=2),
    Rect(115, 0, 25, 24, outline=0xFFFFFF, stroke=2),
    Rect(146, 0, 22, 24, outline=0xFFFFFF, stroke=2),
    Rect(145, 10, 90, 40, outline=0xFFFFFF, stroke=2)
]
for s in selectors:
    s.hidden = True
    screen.append(s)

def update_ui():
    chan_lbl.color = 0xFFFFFF if active_row == 6 else 0x444444
    chan_lbl.text = f"CH:{midi_chan}"
    
    # Hide all selectors first
    for s in selectors: s.hidden = True
    
    if active_row == 6:
        selectors[3].hidden = False
    else:
        for i in range(6):
            status_boxes[i].fill = 0x444444 if mods[i][2] else 0xFF0000
            inv_lbls[i].text = "-" if mods[i][3] else "+"
        
        # Show the correct column selector and move its Y position
        sel = selectors[active_col]
        sel.hidden = False
        sel.y = rows_y[active_row] - 12

# --- 3. MIDI & BLE ---
midi_usb = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_chan-1)
midi_service = adafruit_ble_midi.MIDIService()
midi_ble = adafruit_midi.MIDI(midi_out=midi_service, out_channel=midi_chan-1)
ble = adafruit_ble.BLERadio()
adv = ProvideServicesAdvertisement(midi_service)
ble.name = "CLUE-6"
ble.start_advertising(adv)

active_row, active_col = 0, 0
update_ui()

while True:
    if not ble.connected and not ble.advertising:
        ble.start_advertising(adv)

    ax, ay, az = clue.acceleration
    raw_in = [ax, ay, clue.proximity, max(0, math.sqrt(ax**2+ay**2+az**2)-9.8), clue.proximity, az]
    
    msgs = []
    for i in range(6):
        if i in [0, 1, 5]: v = int(simpleio.map_range(raw_in[i], -9, 9, 0, 127))
        elif i in [2, 4]:  v = int(simpleio.map_range(raw_in[i], 0, 150, 0, 127))
        else:              v = int(simpleio.map_range(raw_in[i], 0, 15, 0, 127))
        
        v = min(127, max(0, v))
        if mods[i][3]: v = 127 - v
        val_lbls[i].text = str(v)
        
        if mods[i][2] and abs(v - mods[i][4]) > 1:
            if i <= 3: msgs.append(ControlChange(mods[i][1], v))
            elif i == 4: msgs.append(ChannelPressure(v))
            elif i == 5: msgs.append(PitchBend(int(simpleio.map_range(v, 0, 127, 0, 16383))))
            mods[i][4] = v

    if msgs:
        midi_usb.send(msgs)
        if ble.connected: midi_ble.send(msgs)

    # Navigation
    if clue.touch_0: # Row Select
        active_row = (active_row + 1) % 7
        # Auto-jump column if fixed type
        if active_row < 6 and mods[active_row][5] and active_col == 0:
            active_col = 1
        update_ui(); time.sleep(0.2)
        
    if clue.touch_1 and active_row < 6: # Column Select
        active_col = (active_col + 1) % 3
        if mods[active_row][5] and active_col == 0:
            active_col = 1
        update_ui(); time.sleep(0.2)

    if clue.touch_2: # Toggle Action
        if active_row < 6:
            if active_col == 1: mods[active_row][3] = not mods[active_row][3]
            if active_col == 2: mods[active_row][2] = not mods[active_row][2]
        update_ui(); time.sleep(0.3)

    if clue.button_a or clue.button_b:
        btn = 1 if clue.button_b else -1
        if active_row == 6:
            midi_chan = min(16, max(1, midi_chan + btn))
            midi_usb.out_channel = midi_chan - 1
            midi_ble.out_channel = midi_chan - 1
        elif active_col == 0 and not mods[active_row][5]:
            mods[active_row][1] = min(127, max(0, mods[active_row][1] + btn))
            cc_lbls[active_row].text = str(mods[active_row][1])
        update_ui(); time.sleep(0.15)

    time.sleep(0.01)
