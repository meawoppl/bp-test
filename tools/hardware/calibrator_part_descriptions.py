#!/usr/bin/env python3
"""Set each calibrator footprint's description to what the part does on this board.

The KiCad library text ("Resistor SMD 0805 ... generated with
kicad-footprint-generator") says nothing about a part's job. This writes a
functional one-liner into every footprint's `descr`, which is what the
kicadmium workbench shows as "Description". Run it again after adding parts;
it fails on any footprint that has no entry.

Usage: /usr/bin/python3 tools/hardware/calibrator_part_descriptions.py
"""
import re
import sys

import pcbnew

BOARD = "boards/gps-time-calibrator/calibrator.kicad_pcb"

FIXED = {
    # Connectors, module interface and mechanics
    "J1": "Board-to-board plug to the ESP32 side of the module: USB, 5 V input, GPS UART, PPS, reset and control GPIOs.",
    "J2": "Board-to-board receptacle to the FPGA side of the module: display column drives, LED_OE_N, PPS, trigger and the 10 MHz clock.",
    "J3": "USB-C input: 5 V power (PD-negotiated) and USB data for the module's ESP32.",
    "J5": "SMA input for the active GNSS antenna; also carries the antenna's DC bias.",
    "J6": "SMA trigger input; 5 V tolerant, detected at a 2.5 V threshold.",
    "J7": "SMA trigger output, driven at 5 V from the FPGA through U10.",
    "J8": "OLED header: GND, 3.3 V, I2C SCL (ESP GPIO2), SDA (ESP GPIO1).",
    "DS1": "0.96 inch I2C OLED showing date/time; mounted on spacers and wired through J8.",
    "H1": "M3 clamp screw midway between J1 and J2; tensions the module onto both connectors.",
    "H2": "M3 corner mounting hole.",
    "H3": "M3 corner mounting hole.",
    "H4": "M3 corner mounting hole.",
    "H5": "M3 corner mounting hole.",
    # ICs and oscillator
    "U1": "ESD protection for the USB-C data pair (D+/D-) and VBUS.",
    "U2": "Always-on 3.3 V LDO from USB VBUS; powers the logic rail for the display buffers, OLED and pull-ups.",
    "U3": "Octal buffer driving display column gates for bits 8-15 from the FPGA; LED_OE_N blanks its outputs.",
    "U4": "Octal buffer driving display column gates for bits 0-7 from the FPGA; LED_OE_N blanks its outputs.",
    "U5": "Switchable 3.3 V LDO for the GPS receiver, enabled by ESP GPIO6 (GPS_EN).",
    "U6": "u-blox MAX-M10S GNSS receiver: UART time/position and the PPS timing reference.",
    "U7": "Schmitt buffer translating the comparator's 5 V trigger to 3.3 V for the GPS EXTINT, FPGA and ESP32.",
    "U9": "Fast comparator that detects the external trigger input against the 2.5 V threshold.",
    "U10": "5 V line driver for the FPGA's trigger output to J7.",
    "U11": "USB-C PD sink controller; requests 5 V / 3 A from the source, status over I2C.",
    "U12": "Always-on 3.3 V LDO (+3V3_CC) for the PD controller's I2C pull-ups.",
    "U14": "eFuse load switch creating the switched 5 V rail, enabled by ESP GPIO4; sets the current limit and reports load current.",
    "U15": "Low-noise 3.3 V LDO for the OCXO, enabled by ESP GPIO5.",
    "Y1": "10 MHz OCXO frequency reference; clocks the FPGA through R173.",
    "L1": "27 nH bias choke: feeds antenna DC onto the RF line while blocking RF from the supply.",
    # Indicators
    "D1": "Power LED: lit while the switched 5 V rail is on.",
    "D74": "PPS indicator LED: blinks with the GPS timepulse.",
    # Resistors outside the display
    "R3": "2.2 kOhm current limit for the 5 V power LED D1.",
    "R4": "100 kOhm pull-up holding ESP32 GPIO0 (boot strap) high for normal run.",
    "R5": "10 Ohm feed from the receiver's VCC_RF to the antenna bias network.",
    "R6": "33 Ohm source damping on the PPS branch to the FPGA (IOT_46B_G0).",
    "R7": "33 Ohm source damping on the PPS branch to ESP32 GPIO38.",
    "R8": "1 kOhm series input resistor on the trigger input; forms the input filter with C75.",
    "R9": "100 kOhm pulldown holding the trigger input low when J6 is open.",
    "R80": "100 Ohm series resistor carrying the 3.3 V trigger to the FPGA (IOT_50B).",
    "R81": "100 Ohm series resistor carrying the 3.3 V trigger to ESP32 GPIO21.",
    "R140": "10 kOhm pull-up holding LED_OE_N high, so the display stays blank until the FPGA enables it.",
    "R160": "Upper 10 kOhm of the divider setting the 2.5 V trigger threshold from 5 V.",
    "R161": "Lower 10 kOhm of the divider setting the 2.5 V trigger threshold.",
    "R162": "33 Ohm series termination for the 5 V trigger output on J7.",
    "R163": "100 kOhm pulldown keeping the trigger output low while the FPGA is unconfigured.",
    "R164": "Sets the PD controller's 3 A current request.",
    "R167": "10 kOhm I2C pull-up on the PD controller's SDA.",
    "R168": "10 kOhm I2C pull-up on the PD controller's SCL.",
    "R169": "100 kOhm pulldown keeping the 5 V load switch U14 off until ESP GPIO4 enables it.",
    "R170": "Sets the eFuse current limit (about 2.5 A) and scales its current-monitor output.",
    "R173": "33 Ohm series termination on the 10 MHz OCXO clock to the FPGA.",
    "R174": "4.7 kOhm I2C pull-up on the OLED's SCL (ESP GPIO2).",
    "R175": "4.7 kOhm I2C pull-up on the OLED's SDA (ESP GPIO1).",
    "R176": "100 kOhm isolation resistor; with C78 filters the load-current monitor into ESP32 ADC GPIO3.",
    "R177": "100 kOhm pulldown keeping the GPS LDO U5 off until ESP GPIO6 enables it.",
    "R178": "100 kOhm pulldown keeping the OCXO LDO U15 off until ESP GPIO5 enables it.",
    "R179": "1 kOhm current limit for the PPS indicator LED D74.",
    "R180": "33 Ohm series resistor from ESP32 GPIO40 to the GPS receiver's RESET_N.",
    # Capacitors outside the display
    "C1": "100 nF bypass on USB VBUS at the ESD array U1.",
    "C2": "4.7 uF input capacitor for the always-on logic LDO U2.",
    "C3": "4.7 uF output capacitor for U2 (3.3 V logic rail).",
    "C4": "100 nF bypass for display buffer U3.",
    "C5": "100 nF bypass for display buffer U4.",
    "C6": "4.7 uF input capacitor for the GPS LDO U5.",
    "C7": "4.7 uF output capacitor for the GPS LDO U5.",
    "C8": "100 nF bypass on the GPS receiver's VCC pin (U6 pin 8).",
    "C9": "4.7 uF bulk bypass on the GPS receiver supply at V_BCKP/V_IO (U6 pins 6-7).",
    "C10": "10 nF RF bypass on the antenna bias node; keeps RF out of the DC feed.",
    "C11": "100 nF bypass for the trigger translator U7.",
    "C13": "100 nF filter on the 2.5 V trigger threshold.",
    "C14": "100 nF bypass for the trigger comparator U9.",
    "C15": "100 nF bypass for the trigger output driver U10.",
    "C64": "1 uF VBUS bypass at the PD controller U11.",
    "C65": "4.7 uF input capacitor for the 3.3 V LDO U12.",
    "C66": "4.7 uF output capacitor for U12 (+3V3_CC).",
    "C68": "Sets the eFuse U14's output slew rate (inrush limit).",
    "C69": "100 nF VBUS bypass at the eFuse U14 input.",
    "C70": "10 uF input capacitor for the OCXO LDO U15.",
    "C71": "22 uF output capacitor for the OCXO LDO U15; it needs at least 10 uF effective for stability.",
    "C73": "100 nF bypass at the OCXO Y1 supply pin.",
    "C74": "10 uF local reservoir at the OCXO Y1.",
    "C75": "1 nF trigger input filter capacitor (with R8).",
    "C76": "100 nF bypass at the OLED header J8.",
    "C77": "10 uF reservoir at the OLED header J8.",
    "C78": "100 nF filter capacitor on the load-current monitor into the ESP32 ADC (with R176).",
    # Test pads
    "TP1": "Test pad: USB VBUS input.",
    "TP2": "Test pad: switched 5 V load rail.",
    "TP3": "Test pad: 3.3 V logic rail.",
    "TP4": "Test pad: 3.3 V rail for the PD I2C pull-ups.",
    "TP5": "Test pad: 3.3 V GPS rail.",
    "TP6": "Test pad: 3.3 V OCXO rail.",
    "TP7": "Test pad: 5 V load-switch enable (ESP GPIO4).",
    "TP8": "Test pad: OCXO LDO enable (ESP GPIO5).",
    "TP9": "Test pad: GPS LDO enable (ESP GPIO6).",
    "TP10": "Test pad: PD controller I2C SDA.",
    "TP11": "Test pad: PD controller I2C SCL.",
    "TP12": "Test pad: filtered load-current monitor at ESP32 ADC GPIO3.",
    "TP13": "Test pad: PPS at the GPS receiver.",
    "TP14": "Test pad: PPS at the FPGA.",
    "TP15": "Test pad: PPS at ESP32 GPIO38.",
    "TP16": "Test pad: 10 MHz clock at the FPGA.",
    "TP17": "Test pad: filtered trigger input.",
    "TP18": "Test pad: 2.5 V trigger threshold.",
    "TP19": "Test pad: comparator output (5 V trigger).",
    "TP20": "Test pad: translated 3.3 V trigger.",
    "TP23": "Test pad: FPGA trigger output, before the 5 V driver.",
    "TP24": "Test pad: 5 V driver output, before R162.",
    "TP25": "Test pad: GPS UART TX (to ESP32 GPIO44).",
    "TP26": "Test pad: GPS UART RX (from ESP32 GPIO43).",
    "TP27": "Test pad: GPS receiver RESET_N.",
    "TP28": "Test pad: receiver VCC_RF antenna supply.",
    "TP29": "Test pad: antenna DC bias after R5.",
    "TP30": "Test pad: display output enable LED_OE_N.",
    "TP63": "Test pad: OLED I2C SCL (ESP GPIO2).",
    "TP64": "Test pad: OLED I2C SDA (ESP GPIO1).",
    "TP65": "Test pad: ESP32 GPIO0 boot strap.",
}


def display(ref):
    """Descriptions for the 4 x 16 optical display and its column drivers.

    Bit 15 is the leftmost column. LED D(10+n) sits in row n//16 + 1 and
    column bit 15 - n%16; column bit b is switched by Q(16-b). Each LED has
    its own 100 nF: C20-C35 for row 1, C80-C127 for rows 2-4.
    """
    kind, num = re.match(r"([A-Z]+)(\d+)", ref).groups()
    num = int(num)
    if kind == "D" and 10 <= num <= 73:
        n = num - 10
        bit, row = 15 - n % 16, n // 16 + 1
        return f"Display LED, row {row} bit {bit}: lit while column MOSFET Q{16 - bit} is on."
    if kind == "R" and 10 <= num <= 73:
        n = num - 10
        bit, row = 15 - n % 16, n // 16 + 1
        return f"470 Ohm current limit for display LED D{num} (row {row} bit {bit}) from the switched 5 V rail."
    if kind == "Q" and 1 <= num <= 16:
        bit = 16 - num
        return f"Low-side switch for display column bit {bit}: sinks that column's four LED cathodes."
    if kind == "R" and 100 <= num <= 115:
        bit = 115 - num
        return f"100 Ohm gate resistor between the buffer and column bit {bit}'s MOSFET Q{16 - bit}."
    if kind == "R" and 120 <= num <= 135:
        bit = 135 - num
        return f"100 kOhm gate pulldown keeping column bit {bit}'s MOSFET Q{16 - bit} off while the buffer is disabled."
    if kind == "C" and (20 <= num <= 35 or 80 <= num <= 127):
        row, col = (0, num - 20) if num <= 35 else ((num - 80) // 16 + 1, (num - 80) % 16)
        return (f"100 nF local bypass at display LED D{10 + row * 16 + col} (row {row + 1} bit {15 - col}); "
                "identical on every LED so all 64 turn on alike.")
    if kind == "C" and 40 <= num <= 55:
        bit = 55 - num
        return f"10 uF reservoir on the 5 V LED supply for display column bit {bit}."
    if kind == "C" and 60 <= num <= 63:
        return "10 uF bulk capacitor on the switched 5 V rail at the eFuse U14 output."
    return None


def main():
    board = pcbnew.LoadBoard(BOARD)
    missing, changed = [], 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        text = FIXED.get(ref) or display(ref)
        if text is None:
            missing.append(ref)
            continue
        if fp.GetLibDescription() != text:
            fp.SetLibDescription(text)
            changed += 1
    if missing:
        sys.exit(f"no description for: {', '.join(sorted(missing))}")
    board.Save(BOARD)
    print(f"{changed} of {len(board.GetFootprints())} descriptions updated")


if __name__ == "__main__":
    main()
