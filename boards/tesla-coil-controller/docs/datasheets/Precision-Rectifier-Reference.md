# Precision-Rectifier-Reference — datasheet text extraction

Source PDF: [Precision-Rectifier-Reference.pdf](Precision-Rectifier-Reference.pdf)

Manufacturer/reference source: https://www.ti.com/lit/ug/tidu030/tidu030.pdf

Extracted 2026-09-28 using `pdftotext -layout`. The PDF is authoritative for pin diagrams, plots, equations and table alignment.

## PDF page 1

```text
Ting Ye
TI Precision Designs: Verified Design
Precision Full-Wave Rectifier, Dual-Supply



TI Precision Designs                                                     Circuit Description
TI Precision Designs are analog solutions created by                     This dual-supply precision full-wave rectifier can turn
TI’s analog experts. Verified Designs offer the theory,                  alternating current (ac) signals to single polarity
component selection, simulation, complete PCB                            signals. The op amps, U1A and U1B, buffer the input
schematic & layout, bill of materials, and measured                      signal and compensate for the voltage drops across
performance of useful circuits. Circuit modifications                    D1 and D2 allowing for small signal inputs. This
that help to meet alternate design goals are also                        implementation functions with limited distortion for 20
discussed.                                                               Vpp input signals at frequencies up to 50 kHz and for
                                                                         signals as small as 50 mVpp at frequencies up to 1
                                                                         kHz. The circuit can be used in applications that need
                                                                         to quantify the absolute value of input signals which
                                                                         have both positive and negative polarities.

Design Resources
                                                                                                       Ask The Analog Experts
Design Archive             All Design files                                                            WEBENCH® Design Center
TINA-TI™                   SPICE Simulator                                                             TI Precision Designs Library
OPA2211                    Product Folder




        An IMPORTANT NOTICE at the end of this TI reference design addresses authorized use, intellectual property matters and
        other important disclaimers and information.
TINA-TI is a trademark of Texas Instruments
WEBENCH is a registered trademark of Texas Instruments

TIDU030-December 2013-Revised December 2013                                     Precision Full-Wave Rectifier, Dual-Supply                  1
                                              Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 2

```text
www.ti.com

1     Design Summary
        The design requirements are as follows:

            Supply Voltage: +/-15 V

            Input: +/- 50 mV to +/- 10 V

            Output: 50 mV to 10 V Full-Wave Rectified Output

        The main goal of this design was to optimize the transient performance of the circuit with a 20 Vpp input
        signal such that the output distortion near the transition regions was minimal. The results in Figure 1 show
        minimal distortion on the output (CH3) with a 10 kHz full-scale 20 Vpp input signal. Maintaining low
        distortion for large input signals is possible up to frequencies near 50 kHz. Rectification is possible for
        input amplitudes down to 50 mVpp but is only possible at input frequencies less than 1 kHz.




    Figure 1: Measured input (CH1) and output (CH3) transient waveform at input 1 kHz with 20 Vpp Sine-
                                                  wave




2               Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                             Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 3

```text
www.ti.com

2     Theory of Operation
       The schematic for the dual-supply rectifier is shown in Figure 1. This topology was chosen over other full-
       wave rectifier topologies for its simplicity while achieving the desired performance. U1A and U1B control the
       biasing of D1 and D2 to change the signal path based on the polarity of the input signal achieving the full-
       wave rectification. The input impedance of the circuit is set by the termination resistor R 4 and can be set to
       match the source impedance or as high as the input impedance of the U1A amplifier.




                                              Figure 2: Circuit schematic

2.1    Simplified Circuit for Positive Input Signals
       The circuit schematic and transfer function for positive input signals are shown in Figure 3 and Equation
       (1. Positive input signals reverse-bias D1 and forward-bias D2 making the components act like an open
       circuit and short circuit respectively. In this configuration, the U1A amplifier drives the non-inverting input of
       U1B such the voltage at the inverting input of U1A that is equal to VIN. Because current doesn’t flow into the
       high-impedance inverting input of U1A, there is no current through R1 or R2 and U1B acts as a buffer. U1A
       must therefore also act as a buffer and VOUT is simply equal to VIN.




                              Figure 3: Simplified circuit for positive input signals

                                                           VOUT  VIN
                                                                                                                        (1)




TIDU030-December 2013-Revised December 2013                                Precision Full-Wave Rectifier, Dual-Supply         3
                                         Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 4

```text
www.ti.com

2.2   Simplified Circuit for Negative Input Signals
      The circuit and transfer function for negative inputs are shown in Figure 4 and Equation (2. Negative input
      signals forward bias D1 and reverse bias D2. Therefore, U1A drives U1B like a standard inverting amplifier
      while R3 biases the non-inverting node of U1B to GND. In this configuration, the output will now be positive
      for negative input signals achieving the full-wave rectification.




                              Figure 4: Simplified circuit for negative input signals

                                                           VOUT     R
                                                                 ( 2 )
                                                            vIN     R1
                                                                                                                            (2)
                                                           VOUT
                                                                 1 V/V
                                                            vIN


2.3   Frequency Compensation
      Compensation capacitor, C7, is added to provide a local high-frequency feedback path for U1A which will
      help stabilize the output. The compensation capacitor should have a value that results in an equivalent
      impedance less than 100 Ω within the gain-bandwidth of the amplifier. Selecting too large of a capacitor
      will cause large distortion on the transition edges when the input signal changes polarity. C7 was
      experimentally selected to be 47pF based on the desired transient performance.




4             Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                           Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 5

```text
www.ti.com

3     Component Selection

3.1    Operational Amplifier
       Since integrity of transient waveforms is the primary concern in this circuit, parameters such as low noise,
       low total-harmonic-distortion (THD), wide bandwidths, high slew rate, high open-loop gain (AOL) are
       key specifications for choosing operational amplifiers (op amp). Rail-to-rail inputs (RRI) and rail-to-rail
       outputs (RRO) are advantageous by increasing the dynamic range.

       The OPA2211 is a low-noise precision bipolar input op amp making it an excellent choice for a high
       performance version of this circuit. The OPA2211 features 1.1 nV/ √Hz broadband noise and 0.00015%
       THD at 1 kHz, output slew rate of 27 V/μs, 45 MHz unity-gain bandwidth, and 130 dB of open-loop gain.
       Other amplifier options for this application include the OPA1611, OPA1612, or OPA827 as further
       discussed in Section 7.

3.2    Diode
       Careful diode selection for D1 and D2 is required to meet the frequency and linearity design goals.
       Important specifications of the diodes are low forward voltage (VF), fast switching speed (TT), low diode
       capacitance (CD), and low leakage current (IR). Schottky diodes usually have faster transition times and
       lower forward voltages but larger reverse leakage currents. In general, standard diodes have lower reverse
       current but slower speed. The diode used in this design is a fast switching diode, 1N4148, based on its
       performance and cost. Table 1 compares several diode candidates.
                                       Table 1: Diode Selection Parameters

                                1N4148                                BAT42W                              BAS70
             VF             720mV at IF=5mA                      400mV at IF=10mA                    410mV at IF=1mA
             TT                 4ns(max)                              5ns(max)                           5ns(max)
             CD         4pF(max) at 1MHz, VR=0V              7pF(typ) at 1MHz, VR=1V             2pF(max) at 1MHz, VR=0V
               IR            25nA at VR=20V                      500nA at VR=25V                     100nA at VR=50V



3.3    Passive Component
       The most crucial passive components to keep output voltage being precisely equal to V IN are the resistors,
       R1 and R2, which set the gain. The resistors were selected to be 0.1% tolerance to achieve good gain
       accuracy. R1 and R2 were selected to be 1 kΩ to reduce thermal noise and prevent the leakage current of
       the diodes from causing noticeable voltage drops across the resistors.

       The compensation capacitor, C7, was selected for proper voltage rating, C0G/NP0 dielectric, and tolerance
       of 5%. When C0G/NP0 capacitors are not available for the need of higher capacitance or voltage ratings,
       X7R dielectrics can be selected.

       The tolerance of the other passive components in this circuit can be selected for 1% or above since the
       components will not directly affect the accuracy of this circuit.




TIDU030-December 2013-Revised December 2013                                  Precision Full-Wave Rectifier, Dual-Supply    5
                                           Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 6

```text
www.ti.com

4     Simulation
                                     TM
       The TINA-TI schematic shown in Figure 5 includes the circuit values obtained in the design process. A
       dc offset voltage of 124.36 μV and dc quiescent current of 3.797 mA per channel were reported by the
       simulation.


                                                                                                  R1 1k                        R2 1k
                V+
                                               C2 100n                                                                                       V-
                                      C1 10u




                                                                                                                                             C9 100n
                                                                                                                                   C8 100p
                                                                                                  D1 1N4148
                                                                                   C7 47p
       V+ 15


                                                                            V-
                                                                                                                      -         U1B OPAy211
                                                                        -                                                                                    Vout
                                                                                                                          +
                                                                                                                      +                                      124.3602uV
                                                C4 100n
                                      C3 10u




                                                                            +                                                                           V+
        V- 15                                                           +
                                                                                 U1A OPAy211    D2 1N4148                                          Iq
                                                                +




                                                    VIN                     V+                                R3 1k




                                                                                                                                             C6 100n
                                                                                                                                                        3.7972mA




                                                                                                                                   C5 100p
                                                                       R4 49.9
                V-




                                                          TM
                Figure 5: TINA-TI                              simulation schematic showing dc offset and quiescent current

4.1    Transient Response
       The transient response of the design with a 20 Vpp, 50 kHz sine-wave input signal is shown in Figure 76.
       While there is some distortion when the input transitions from negative to positive polarities, it is limited
       and the output is accurately rectified. With the input at frequencies less than roughly 50 kHz, the output
       remains very accurately full-wave rectified as displayed with a 1kHz input signal in Figure 7.

                        T            20.00



                                     10.00
                       Voltage (V)




                                      0.00



                                     -10.00

                                                                     VIN
                                                                     Vout
                                     -20.00
                                               1.00m                     1.01m                 1.02m                          1.03m                     1.04m
                                                                                               Time (s)

                                                               TM
                     Figure 6: TINA-TI                              simulated transient waveform at +/- 10V and 50 kHz input


6                    Precision Full-Wave Rectifier, Dual-Supply                                                           TIDU030-December 2013-Revised December 2013
                                                                     Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 7

```text
www.ti.com


                                  T            20.00




                                 Voltage (V)   10.00



                                                0.00



                                               -10.00

                                                                         VIN
                                                                         Vout
                                               -20.00
                                                        1.00m              1.50m                      2.00m                          2.50m               3.00m
                                                                                                      Time (s)

                                                                 TM
                                Figure 7: TINA-TI                     simulated transient waveform at +/- 10V and 1 kHz input

                    The test results with a 20 Vpp input at frequencies of 100 kHz and 200 kHz are shown in Figure 8. The
                    output distortion when the input signal transitions from negative to positive is now very noticeable. The
                    distortion occurs during the time when the circuit transitions from forward biasing D1 to D2. The transition
                    time is caused by the forward voltage (VF), junction capacitance (CJ), and transition time (TT) of the
                    diodes along with the slew rate and output current limitations of U1A. Additional waveforms at other
                    frequencies can be seen in Appendix A.3.
  T            20.00                                                                              T            20.00



               10.00                                                                                           10.00
 Voltage (V)




                                                                                                 Voltage (V)




                0.00                                                                                            0.00



               -10.00                                                                                          -10.00

                                VIN                                                                                               VG1
                                Vout                                                                                              Vout
               -20.00                                                                                          -20.00
                        1.00m             1.00m            1.01m          1.01m          1.02m                          100.00u      0.10m        0.10m        107.50u   110.00u
                                                           Time (s)                                                                                Time (s)

                                               TM
  Figure 8: TINA-TI                                 Transient simulation for +/- 10V and 100 kHz (left) and 200 kHz (right) sinusoid wave
                                                                                  inputs




TIDU030-December 2013-Revised December 2013                                                                             Precision Full-Wave Rectifier, Dual-Supply                 7
                                                                       Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 8

```text
www.ti.com

    Figure 9 and Figure 10 show the circuit performance with a 50 mVpp low-level signal at 100 Hz and 1 kHz
    respectively. Distortion is noticeable for smaller level signals even at 1 kHz.
                     T
                                 30m




                                 15m
                   Voltage (V)




                                    0




                                 -15m
                                                       Vout
                                                       VIN
                                 -30m
                                        0.00               5.00m                10.00m                15.00m          20.00m
                                                                                Time (s)

                                               TM
            Figure 9: TINA-TI                       simulated output at 100 Hz with 50 mVpp sine-wave input


              T                  40.00m



                                 20.00m
             Voltage (V)




                                   0.00



                           -20.00m

                                                          VIN
                                                          Vout
                           -40.00m
                                          1.00m               1.50m                2.00m                   2.50m        3.00m
                                                                                   Time (s)

                                                  TM
            Figure 10: TINA-TI                         simulated output at 1 kHz with 50 mVpp sine-wave input




8          Precision Full-Wave Rectifier, Dual-Supply                                                TIDU030-December 2013-Revised December 2013
                                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 9

```text
www.ti.com

4.2    Transition Time Simulations
       As shown in the previous section, lower level input signals have a lower usable frequency range compared
       to larger signals. This is because the time it takes to change the biasing of the diodes to switch the polarity
       of the output increases as the amplitude of the input signal decreases. Figure 11 shows the output
       transition time for square wave inputs of different amplitudes.

         T                                1.00

        VIN = 1 Vpp

                                     -598.78m
                                      100.00m

        VIN = 100 mVpp

                                     -144.75m
                                       10.00m

        VIN = 10 mVpp

                                      -15.50m
                                        1.10m

        VIN = 1 mVpp

                                       -1.53m
                                                 90.00u                        110.00u                     130.00u                     150.00u
                                                                                              Time (s)

                                Figure 11: Transition time with different input signal amplitudes

       Applying a small square-wave step to the input can also be used to test the small-signal stability of the
       circuit. The results shown in Figure 12 display little overshoot or ringing, indicating that the system is
       stable.
                       T            40.00m



                                    20.00m
                      Voltage (V)




                                       0.00



                                    -20.00m

                                                           VIN
                                                           Vout
                                    -40.00m
                                              2.9990m          2.9995m            3.0000m           3.0005m         3.0010m
                                                                                   Time (s)

                                                    TM
                  Figure 12: TINA-TI                     simulated output step response with 50 mVpp input



TIDU030-December 2013-Revised December 2013                                               Precision Full-Wave Rectifier, Dual-Supply             9
                                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 10

```text
www.ti.com

5     PCB Design
       The PCB schematic and bill of materials can be found in the Appendix A.1 and A.2.

5.1    PCB Layout
       For optimal performance in this design follow standard precision PCB layout guidelines including: using
       ground planes, proper power supply decoupling, keeping the summing (inverting) node as small as
       possible, and using short thick traces for sensitive nodes. The layout for the design is shown in Figure 13.




                                              Figure 13: Altium PCB Layout




10             Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                            Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 11

```text
www.ti.com

6     Verification & Measured Performance

6.1    DC Measurements
       DC measurements were made for the offset voltage and the quiescent current for five units. The average
       values are reported in Table 2.
                                      Table 2: Measured dc result summary

                                                                         Measured Value
                                Output Offset Voltage (mV)                     0.354
                                 Quiescent Current (mA)                        6.8863


6.2    Transient Measurements
       The transient response of the design with a 20 Vpp, 1 kHz sine-wave input signal is shown in Figure 14.
       The design creates a very accurately full-wave rectified output with no obvious distortion.




                        Figure 14: Measured output with 1 kHz, 20 Vpp sine-wave input




TIDU030-December 2013-Revised December 2013                                Precision Full-Wave Rectifier, Dual-Supply   11
                                         Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 12

```text
www.ti.com

     The measured results with a 20 Vpp input at the maximum frequency of 100 kHz are shown in Figure 15.
     The distortion seen in the simulation results can also be seen in the measured results. Additional
     measured waveforms at other frequencies can be seen in Appendix Error! Reference source not found. .




                     Figure 15: Measured output at 100 kHz, 20 Vpp sine-wave input

     Figure 16 and Figure 17 shows low-level signals generation with 50 mVpp at 1 kHz and 5 kHz input
     respectively. The distortion becomes severe as input frequency increases. The output waveforms match
     simulation results shown in Figure 10 and Figure 24.




                     Figure 16: Measured output at 1 kHz, 50 mVpp sine-wave input




12          Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                         Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 13

```text
www.ti.com




                        Figure 17: Measured output at 5 kHz, 50 mVpp sine-wave input

6.3    Small-Signal Stability
       The small-signal stability of the circuit was tested by applying a step response to the input that caused the
       output changed by approximately 50 mV. The results are shown in Figure 18. The overshoot and ringing
       can be further reduced by increasing the value of C7 or adding capacitors across R2 at the expense of
       bandwidth and distortion. Smaller values for R1 and R2 will also help improve the small-signal response but
       the required output current will begin to cause the output voltage to decrease creating an offset between
       the output and the desired rectified output.




                            Figure 18: Measured output to 50 mVpp step response




TIDU030-December 2013-Revised December 2013                               Precision Full-Wave Rectifier, Dual-Supply   13
                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 14

```text
www.ti.com

6.4    Measured Result Summary
       The measured results show maximum speed at approximately 100 kHz with a 20 Vpp sine-wave input
       while achieving a low distortion full-wave rectified output. Low-level signals at frequencies less than or
       equal to 1 kHz can also achieve with good linearity.

7     Modifications
       This absolute circuit can be implemented by any op amp with sufficient bandwidth for the input signals.
       This circuit can process faster signals and be more accurate by applying low noise, low THD, wide
       bandwidths, high slew rate, and high AOL op amps. Other +/-15 V supply amplifiers suitable for this design
       are OPA1611, OPA827, OPA1602, OPA1662, and OPA627. The performance of these op amps is
       summarized in Table 3.
                                      Table 3. Alternate +36V Supply Amplifiers

                                                                       Noise at                              Iq per
                        # of   GBW    SR    Aol                                        THD+N at      IB, max
            Amplifier                                                   1 kHz                               channel,
                      Channel (MHz) (V/us) (dB)                                        1 kHz (%)       (pA)
                                                                      (nV/rtHz)                             max(mA)
            OPA1662           2          22        17        114         3.3           0.00006      1200000    1.8
            OPA1602           2          35        20        120         2.5           0.00003      200000     2.6
            OPA1611           1          40        27        130         1.1           0.000015     250000     3.6
            OPA827            1          22        28        126          4            0.00004        10       5.2
            OPA627            1          80        135       120         5.2           0.00003        10       7.5

       To achieve better performance for low-level signals consider a different full-wave rectifier topology.

8     About the Author
       Ting Ye is a field application engineer based in Taipei who supports industrial and precision customers.
       She performed a six month rotation working with the Precision Linear group where she supported op amp
       and current loop products for industrial applications.

9     Acknowledgements & References
       1.   R. Elliott. (2010 Feb. 27) Precision Rectifiers. Available:
            http://sound.westhost.com/appnotes/an001.htm

       2.   D. Jones and M. Stitt. (1997, Dec.). Precision Absolute Value Circuits. Available:
            http://www.ti.com/lit/an/sboa068/sboa068.pdf




14             Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                            Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 15

```text
www.ti.com

                                                    Appendix A.

A.1 Electrical Schematic
       The Altium electrical schematic for this design can be seen in Figure 19.




                                         Figure 19: Electrical Schematic




TIDU030-December 2013-Revised December 2013                               Precision Full-Wave Rectifier, Dual-Supply   15
                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 16

```text
www.ti.com

A.2 Bill of Materials
      The bill of materials for this circuit can be seen in Figure 20.




                                                Figure 20: Bill of Materials




16            Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                           Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 17

```text
www.ti.com

A.3 Additional Simulated Data
                   T            20.00



                                10.00
                  Voltage (V)




                                 0.00



                                -10.00

                                                      VIN
                                                      Vout
                                -20.00
                                         1.00m               1.05m              1.10m                    1.15m           1.20m
                                                                                Time (s)

                                   A. Transient simulation for +/- 10V and 10 kHz sinusoid wave input


                   T            20.00



                                10.00
                  Voltage (V)




                                 0.00



                                -10.00



                                -20.00
                                         1.00m               1.05m              1.10m                    1.15m           1.20m
                                                                                Time (s)

                                   B. Simulated output at +/- 10V and 10 kHz sinusoid wave input
                Figure 21: TINA-TI simulated transient waveform at +/- 10V and 10 kHz input
                                                 TM




TIDU030-December 2013-Revised December 2013                                             Precision Full-Wave Rectifier, Dual-Supply   17
                                                      Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 18

```text
www.ti.com


        T            20.00



                     10.00
       Voltage (V)



                      0.00



                     -10.00

                                           VIN
                                           Vout
                     -20.00
                              1.00m            1.01m                 1.02m                    1.03m        1.04m
                                                                     Time (s)

                        A. Transient simulation for +/- 10V and 50 kHz sinusoid wave input


        T            20.00



                     10.00
       Voltage (V)




                      0.00



                     -10.00



                     -20.00
                              1.00m            1.01m                 1.02m                    1.03m        1.04m
                                                                     Time (s)

                        B. Simulated output at +/- 10V and 50 kHz sinusoid wave input
     Figure 22: TINA-TI simulated transient waveform at +/- 10V and 50 kHz input
                                      TM




18   Precision Full-Wave Rectifier, Dual-Supply                                         TIDU030-December 2013-Revised December 2013
                                           Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 19

```text
www.ti.com


                   T            20.00



                                10.00
                  Voltage (V)



                                 0.00



                                -10.00

                                                        VG1
                                                        Vout
                                -20.00
                                         100.00u            0.10m                0.10m                107.50u           110.00u
                                                                                  Time (s)

                                  A. Transient simulation for +/- 10V and 200 kHz sinusoid wave input

                   T            20.00



                                10.00
                  Voltage (V)




                                 0.00



                                -10.00



                                -20.00
                                         100.00u            0.10m                0.10m                107.50u           110.00u
                                                                                  Time (s)

                                   B. Simulated output at +/- 10V and 200 kHz sinusoid wave input
               Figure 23: TINA-TI simulated transient waveform at +/- 10V and 200 kHz input
                                                   TM




TIDU030-December 2013-Revised December 2013                                               Precision Full-Wave Rectifier, Dual-Supply   19
                                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 20

```text
www.ti.com


        T            40.00m




       Voltage (V)   20.00m



                        0.00



                     -20.00m

                                              VIN
                                              Vout
                     -40.00m
                               1.00m                 1.10m              1.20m                   1.30m        1.40m
                                                                        Time (s)

                                       TM
     Figure 24: TINA-TI                     simulated output at 5 kHz with 50 mVpp sine-wave input




                      Figure 25: Measured output at 10 kHz with 20 Vpp sine-wave input




20   Precision Full-Wave Rectifier, Dual-Supply                                           TIDU030-December 2013-Revised December 2013
                                             Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 21

```text
www.ti.com




                      Figure 26: Measured output at 50 kHz with 20 Vpp sine-wave input




                     Figure 27: Measured output at 200 kHz with 20 Vpp sine-wave input




TIDU030-December 2013-Revised December 2013                               Precision Full-Wave Rectifier, Dual-Supply   21
                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 22

```text
www.ti.com

A.4 Output Fast Fourier Transform (FFT)
     The output FFT shown in Figure 28 was taken from 20 Hz to 10 kHz to view the output spectrum of the
     circuit with a 1 Vpp, 1 kHz input signal. Since harmonics of a full wave rectifier are double the base
     frequency, the harmonic tones are even harmonics at 2, 4, 6, 8, 10 kHz.




                         Figure 28: Output FFT with 1 kHz, 20 Vpp sine-wave input




                        Figure 29: FFT of output at 1 kHz with 100 mVpp sine-wave




22          Precision Full-Wave Rectifier, Dual-Supply                                TIDU030-December 2013-Revised December 2013
                                         Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 23

```text
www.ti.com




                        Figure 30: FFT of output at input 50 kHz with 20 Vpp sine-wave




TIDU030-December 2013-Revised December 2013                               Precision Full-Wave Rectifier, Dual-Supply   23
                                        Copyright © 2013, Texas Instruments Incorporated
```

## PDF page 24

```text
IMPORTANT NOTICE FOR TI REFERENCE DESIGNS
Texas Instruments Incorporated ("TI") reference designs are solely intended to assist designers (“Buyers”) who are developing systems that
incorporate TI semiconductor products (also referred to herein as “components”). Buyer understands and agrees that Buyer remains
responsible for using its independent analysis, evaluation and judgment in designing Buyer’s systems and products.
TI reference designs have been created using standard laboratory conditions and engineering practices. TI has not conducted any
testing other than that specifically described in the published documentation for a particular reference design. TI may make
corrections, enhancements, improvements and other changes to its reference designs.
Buyers are authorized to use TI reference designs with the TI component(s) identified in each particular reference design and to modify the
reference design in the development of their end products. HOWEVER, NO OTHER LICENSE, EXPRESS OR IMPLIED, BY ESTOPPEL
OR OTHERWISE TO ANY OTHER TI INTELLECTUAL PROPERTY RIGHT, AND NO LICENSE TO ANY THIRD PARTY TECHNOLOGY
OR INTELLECTUAL PROPERTY RIGHT, IS GRANTED HEREIN, including but not limited to any patent right, copyright, mask work right,
or other intellectual property right relating to any combination, machine, or process in which TI components or services are used.
Information published by TI regarding third-party products or services does not constitute a license to use such products or services, or a
warranty or endorsement thereof. Use of such information may require a license from a third party under the patents or other intellectual
property of the third party, or a license from TI under the patents or other intellectual property of TI.
TI REFERENCE DESIGNS ARE PROVIDED "AS IS". TI MAKES NO WARRANTIES OR REPRESENTATIONS WITH REGARD TO THE
REFERENCE DESIGNS OR USE OF THE REFERENCE DESIGNS, EXPRESS, IMPLIED OR STATUTORY, INCLUDING ACCURACY OR
COMPLETENESS. TI DISCLAIMS ANY WARRANTY OF TITLE AND ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT, QUIET POSSESSION, AND NON-INFRINGEMENT OF ANY THIRD PARTY
INTELLECTUAL PROPERTY RIGHTS WITH REGARD TO TI REFERENCE DESIGNS OR USE THEREOF. TI SHALL NOT BE LIABLE
FOR AND SHALL NOT DEFEND OR INDEMNIFY BUYERS AGAINST ANY THIRD PARTY INFRINGEMENT CLAIM THAT RELATES TO
OR IS BASED ON A COMBINATION OF COMPONENTS PROVIDED IN A TI REFERENCE DESIGN. IN NO EVENT SHALL TI BE
LIABLE FOR ANY ACTUAL, SPECIAL, INCIDENTAL, CONSEQUENTIAL OR INDIRECT DAMAGES, HOWEVER CAUSED, ON ANY
THEORY OF LIABILITY AND WHETHER OR NOT TI HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, ARISING IN
ANY WAY OUT OF TI REFERENCE DESIGNS OR BUYER’S USE OF TI REFERENCE DESIGNS.
TI reserves the right to make corrections, enhancements, improvements and other changes to its semiconductor products and services per
JESD46, latest issue, and to discontinue any product or service per JESD48, latest issue. Buyers should obtain the latest relevant
information before placing orders and should verify that such information is current and complete. All semiconductor products are sold
subject to TI’s terms and conditions of sale supplied at the time of order acknowledgment.
TI warrants performance of its components to the specifications applicable at the time of sale, in accordance with the warranty in TI’s terms
and conditions of sale of semiconductor products. Testing and other quality control techniques for TI components are used to the extent TI
deems necessary to support this warranty. Except where mandated by applicable law, testing of all parameters of each component is not
necessarily performed.
TI assumes no liability for applications assistance or the design of Buyers’ products. Buyers are responsible for their products and
applications using TI components. To minimize the risks associated with Buyers’ products and applications, Buyers should provide
adequate design and operating safeguards.
Reproduction of significant portions of TI information in TI data books, data sheets or reference designs is permissible only if reproduction is
without alteration and is accompanied by all associated warranties, conditions, limitations, and notices. TI is not responsible or liable for
such altered documentation. Information of third parties may be subject to additional restrictions.
Buyer acknowledges and agrees that it is solely responsible for compliance with all legal, regulatory and safety-related requirements
concerning its products, and any use of TI components in its applications, notwithstanding any applications-related information or support
that may be provided by TI. Buyer represents and agrees that it has all the necessary expertise to create and implement safeguards that
anticipate dangerous failures, monitor failures and their consequences, lessen the likelihood of dangerous failures and take appropriate
remedial actions. Buyer will fully indemnify TI and its representatives against any damages arising out of the use of any TI components in
Buyer’s safety-critical applications.
In some cases, TI components may be promoted specifically to facilitate safety-related applications. With such components, TI’s goal is to
help enable customers to design and create their own end-product solutions that meet applicable functional safety standards and
requirements. Nonetheless, such components are subject to these terms.
No TI components are authorized for use in FDA Class III (or similar life-critical medical equipment) unless authorized officers of the parties
have executed an agreement specifically governing such use.
Only those TI components that TI has specifically designated as military grade or “enhanced plastic” are designed and intended for use in
military/aerospace applications or environments. Buyer acknowledges and agrees that any military or aerospace use of TI components that
have not been so designated is solely at Buyer's risk, and Buyer is solely responsible for compliance with all legal and regulatory
requirements in connection with such use.
TI has specifically designated certain components as meeting ISO/TS16949 requirements, mainly for automotive use. In any case of use of
non-designated products, TI will not be responsible for any failure to meet ISO/TS16949.


                             Mailing Address: Texas Instruments, Post Office Box 655303, Dallas, Texas 75265
                                            Copyright © 2013, Texas Instruments Incorporated
```

