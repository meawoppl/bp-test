# Buffered auxiliary inputs

J3, J8, J9 and J10 serve AUX1–AUX4 respectively. Each is a left-facing, 2-pin JST-PH S2B-PH-K-S(LF)(SN), 2.0 mm pitch: pin 1 signal, pin 2 controller GND. Mating housing: PHR-2, with contacts selected for the wire gauge. These are four independent, shared-ground 0–5 V channels, not isolated or differential inputs. Use a twisted signal/return pair per channel. Exact LCSC sourcing remains to be qualified. [JST PH drawing](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf).

Each signal feeds a 1 MΩ input pull-down and 150 pF C0G RF shunt at cable entry, then 1 kΩ into 2.2 nF C0G. A BAV199,215 low-leakage dual diode clamps the filtered node toward GND and +5V_ADC. The 1 kΩ resistor limits clamp current. U70–U73 (OPA197IDBVR) are wired as direct-feedback voltage followers. Their outputs drive the existing R1–R4 100Ω / C11–C14 1nF ADC isolation networks, mapping AUX1/AUX2/AUX3/AUX4 to CH1/CH2/CH3/CH4 without rectification or scaling. DC input impedance is approximately 1 MΩ; the buffer is nominal unity gain. External source impedance and the ADC loading introduce small additional gain errors.

Each buffer runs from +12V_AUX and −5V_CT so neither end of 0–5 V is at its output rail. R740 (10Ω) / C740 (10µF) filter the 12 V feed; each amplifier has 100nF on each rail and C741 provides negative-rail bulk bypass. Eight total OPA197s (four CST, four AUX) require approximately 8mA typical / 10.4mA maximum room-temperature quiescent current from the negative rail before signal-dependent loading. Reserve at least 20mA provisionally; the shared 10Ω negative filter drops 0.2V at that load. Pump ripple, thermal/temperature corners and dynamic output current still need verification. Keep AUX return currents out of the GDT switching loops when routing.

## ADC channel assignment

The ADC assignments follow the connector-aligned buffer rows to eliminate analog-route crossovers; connector labels remain unchanged. Use [adc-channel-map.json](adc-channel-map.json) as the firmware mapping.

| Connector | Input | Buffer | ADC channel | ADC filter |
|---|---|---|---|---|
| J3 | AUX1 | U70 | 2 | R2 / C12 |
| J8 | AUX2 | U71 | 1 | R1 / C11 |
| J9 | AUX3 | U72 | 4 | R4 / C14 |
| J10 | AUX4 | U73 | 3 | R3 / C13 |

All four remain 0–5 V. CST1 raw/envelope remains CH5/CH6; CST2 remains CH7/CH8. The reordered routes use centered resistor-pad entries, uniform 0.25 mm traces and 45-degree mitres. The channel reorder removed two crossover vias. A subsequent local feedback reroute removed five more vias: U70–U73 pin 1 now connects directly to pin 4 on F.Cu. U71 has no output-net vias; the other channels retain the layer transitions needed for their ADC routes. No vias are inside these package bodies. See [aux-channel-reorder.json](aux-channel-reorder.json) for the geometry and connectivity audit.

## Filter estimate

The nominal input RC pole is 72.3kHz; the ADC-side pole is 1.59MHz. [Response plot](aux/filter-response.png) and [numeric results](aux/filter-response.json) come from `tools/hardware/simulate_tesla_aux.py`: a linear RC calculation with 50Ω source, 1MΩ ADC load and a single 10MHz closed-loop amplifier pole. It does not simulate nonlinear clamps, parasitics, power sequencing or field coupling.

Predicted gain: −0.092dB at 10kHz, −0.757dB at 30kHz, −4.94dB at 100kHz and −24.76dB at 1MHz. Phase at 30kHz is approximately −24.9°. Calibration must include this response if comparing phase/amplitude against the CST path. This is modest signal/EMI filtering, not a complete 200kSPS anti-alias specification. Source impedance materially changes the response; use low-impedance sensor outputs.

## Protection and remaining validation

The low-leakage clamp is signal conditioning, not a certified surge/ESD barrier. Operate within 0–5V with the controller powered. Positive faults can inject into +5V_ADC; neither continuous overvoltage nor driving an unpowered controller is qualified. No field/surge immunity or precision guarantee is claimed. The AUX signal paths and local supply returns are routed; the complete controller remains a routing draft.

OPA197 uses the existing local [TI datasheet](datasheets/OPA197.pdf). The BAV199 pin mapping (1=A1, 2=K2, 3=K1/A2) is verified against [Nexperia's datasheet](https://assets.nexperia.com/documents/data-sheet/BAV199.pdf). Nexperia returned HTTP 403 to direct PDF downloads; source notes are retained, but the local PDF/full extraction is pending. Exact LCSC order codes and stock remain to be qualified.

Local feedback geometry and connectivity are recorded in [aux-feedback-cleanup.json](aux-feedback-cleanup.json).
