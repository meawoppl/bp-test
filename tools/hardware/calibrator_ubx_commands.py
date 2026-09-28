#!/usr/bin/env python3
"""Print offline M10 SPG 5.10 bring-up frames; never opens a serial port.
Run from any directory. Send one SET at a time, await ACK, then GET/readback.
Detect receiver version first; adapt unsupported keys rather than ignoring NAK.
"""
import json
import struct

# name, key, little-endian value format, initial integration value
SETTINGS = [
    ('CFG-UART1INPROT-UBX', 0x10730001, 'B', 1),
    ('CFG-UART1OUTPROT-UBX', 0x10740001, 'B', 1),
    ('CFG-UART1OUTPROT-NMEA', 0x10740002, 'B', 0),
    ('CFG-PM-OPERATEMODE', 0x20d00001, 'B', 0),
    ('CFG-PM-EXTINTWAKE', 0x10d0000c, 'B', 0),
    ('CFG-PM-EXTINTBACKUP', 0x10d0000d, 'B', 0),
    ('CFG-PM-EXTINTINACTIVE', 0x10d0000e, 'B', 0),
    ('CFG-RATE-MEAS', 0x30210001, 'H', 1000),
    ('CFG-RATE-NAV', 0x30210002, 'H', 1),
    ('CFG-RATE-TIMEREF', 0x20210003, 'B', 1),
    ('CFG-TP-PULSE_DEF', 0x20050023, 'B', 0),
    ('CFG-TP-PULSE_LENGTH_DEF', 0x20050030, 'B', 1),
    ('CFG-TP-PERIOD_TP1', 0x40050002, 'I', 1000000),
    ('CFG-TP-PERIOD_LOCK_TP1', 0x40050003, 'I', 1000000),
    ('CFG-TP-LEN_TP1', 0x40050004, 'I', 0),
    ('CFG-TP-LEN_LOCK_TP1', 0x40050005, 'I', 100000),
    ('CFG-TP-SYNC_GNSS_TP1', 0x10050008, 'B', 1),
    ('CFG-TP-USE_LOCKED_TP1', 0x10050009, 'B', 1),
    ('CFG-TP-ALIGN_TO_TOW_TP1', 0x1005000a, 'B', 1),
    ('CFG-TP-POL_TP1', 0x1005000b, 'B', 1),
    ('CFG-TP-TIMEGRID_TP1', 0x2005000c, 'B', 1),
    ('CFG-TP-TP1_ENA', 0x10050007, 'B', 1),
    ('CFG-MSGOUT-UBX_NAV_PVT_UART1', 0x20910007, 'B', 1),
    ('CFG-MSGOUT-UBX_NAV_TIMEGPS_UART1', 0x20910048, 'B', 1),
    ('CFG-MSGOUT-UBX_TIM_TP_UART1', 0x2091017e, 'B', 1),
    ('CFG-MSGOUT-UBX_TIM_TM2_UART1', 0x20910179, 'B', 1),
]


def frame(cls, msg, payload=b''):
    body = bytes([cls, msg]) + struct.pack('<H', len(payload)) + payload
    a = b = 0
    for byte in body:
        a = (a + byte) & 255
        b = (b + a) & 255
    return b'\xb5\x62' + body + bytes([a, b])


def setting(name, key, fmt, value):
    # VALSET version 0, RAM-only layer bit, two reserved bytes.
    put = frame(0x06, 0x8a, b'\x00\x01\x00\x00' +
                struct.pack('<I', key) + struct.pack('<' + fmt, value))
    # VALGET version 0, RAM layer enum, position 0.
    get = frame(0x06, 0x8b, b'\x00\x00\x00\x00' + struct.pack('<I', key))
    return dict(name=name, key=f'0x{key:08x}', value=value,
                set_hex=put.hex(' '), readback_hex=get.hex(' '))


def recipe():
    return dict(
        status='Offline reference only; receiver firmware support and ACK/readback required',
        initial_uart='38400 8N1, detect MON-VER before sending settings',
        mon_ver_poll_hex=frame(0x0a, 0x04).hex(' '),
        baud_change=setting('CFG-UART1-BAUDRATE', 0x40520001, 'I', 115200),
        baud_transition='Send at current baud, drain TX, switch host to 115200; '
                        'ACK may be at either rate; confirm MON-VER and VALGET at new rate',
        configuration=[setting(*row) for row in SETTINGS],
        calibration='Read and record CFG-TP-ANT_CABLEDELAY 0x30050001 and '
                    'CFG-TP-USER_DELAY_TP1 0x40050006; no guessed compensation is written',
    )


if __name__ == '__main__':
    print(json.dumps(recipe(), indent=2))
