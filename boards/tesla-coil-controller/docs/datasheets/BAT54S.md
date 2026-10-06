# BAT54S — datasheet extraction

Source: [BAT54S.pdf](BAT54S.pdf), supplied by user 2026-09-28. PDF is authoritative for drawings and tables.

## PDF page 1

```text
                           BAT54S
                           Schottky barrier diodes
                           1 July 2022                                                              Product data sheet




1. General description
                       Planar Schottky barrier diodes with an integrated guard ring for stress protection, encapsulated in a
                       small SOT23 (TO-236AB) Surface-Mounted Device (SMD) plastic package.


2. Features and benefits
                       •   Low forward voltage
                       •   Low capacitance


3. Applications
                       •   Ultra high-speed switching
                       •   Line termination
                       •   Voltage clamping
                       •   Reverse polarity protection


4. Quick reference data
Table 1. Quick reference data
Symbol          Parameter                 Conditions                                       Min      Typ          Max      Unit
VR             reverse voltage                                                             -        -            30       V
VF             forward voltage            IF = 100 mA; tp ≤ 300 µs; δ ≤ 0.02;              -        -            800      mV
                                          pulsed; Tamb = 25 °C
IR             reverse current            VR = 25 V; tp ≤ 300 µs; δ ≤ 0.02;                -        -            2        µA
                                          pulsed; Tamb = 25 °C


5. Pinning information
Table 2. Pinning information
Pin        Symbol      Description                  Simplified outline            Graphic symbol
1         A1          anode (diode 1)                                3

2         K2          cathode (diode 2)                                                                 K1; A2

3         K1; A2      cathode 1; anode 2
                                                                                               A1                    K2

                                                                                                           006aaa437
                                                          1               2
                                                               SOT23
```

## PDF page 2

```text
Nexperia                                                                                                                                                              BAT54S
                                                                                                                                                Schottky barrier diodes


6. Ordering information
Table 3. Ordering information
Type number                   Package
                                     Name                  Description                                                                                              Version
BAT54S                               SOT23                 plastic, surface-mounted package; 3 terminals; 1.9 mm                                                    SOT23
                                                           pitch; 2.9 mm x 1.3 mm x 1 mm body


7. Marking
Table 4. Marking codes
Type number                                                                            Marking code[1]
BAT54S                                                                                 %V4

[1]    % = placeholder for manufacturing site code



8. Limiting values
Table 5. Limiting values
In accordance with the Absolute Maximum Rating System (IEC 60134).
Symbol                Parameter                      Conditions                                                                                  Min              Max             Unit
VR                    reverse voltage                                                                                                            -                30              V
IF                    forward current                Tamb = 25 °C                                                                                -                200             mA
IFRM                  repetitive peak forward        tp ≤ 1 s; δ ≤ 0.5; Tamb = 25 °C                                                             -                300             mA
                      current
IFSM                  non-repetitive peak            tp < 10 ms; Tj(init) = 25 °C                                                                -                600             mA
                      forward current
Per device; one diode loaded
Ptot                  total power dissipation        Tamb ≤ 25 °C                                                                       [1]      -                250             mW
Tj                    junction temperature                                                                                                       -                150             °C
Tamb                  ambient temperature                                                                                                        -55              150             °C
Tstg                  storage temperature                                                                                                        -65              150             °C

[1]    Device mounted on an FR4 Printed-Circuit Board (PCB), single-sided copper, tin-plated and standard footprint.



9. Thermal characteristics
Table 6. Thermal characteristics
Symbol         Parameter                        Conditions                                                                                Min        Typ            Max            Unit
Rth(j-a)            thermal resistance from in free air                                                                       [1] [2]     -          -              500            K/W
                    junction to ambient

[1]    For Schottky barrier diodes thermal runaway has to be considered, as in some applications the reverse power losses PR are a
       significant part of the total power losses.
[2]    Device mounted on an FR4 Printed-Circuit Board (PCB), single-sided copper, tin-plated and standard footprint.




BAT54S                                           All information provided in this document is subject to legal disclaimers.                              © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                         1 July 2022                                                                                                    2/9
```

## PDF page 3

```text
Nexperia                                                                                                                                                                BAT54S
                                                                                                                                                    Schottky barrier diodes


10. Characteristics
Table 7. Characteristics
Symbol          Parameter                                  Conditions                                                                         Min      Typ            Max            Unit
VF                              forward voltage            IF = 0.1 mA; tp ≤ 300 µs; δ ≤ 0.02;                                                -        -              240            mV
                                                           pulsed; Tamb = 25 °C
                                                           IF = 1 mA; tp ≤ 300 µs; δ ≤ 0.02;                                                  -        -              320            mV
                                                           pulsed; Tamb = 25 °C
                                                           IF = 10 mA; tp ≤ 300 µs; δ ≤ 0.02;                                                 -        -              400            mV
                                                           pulsed; Tamb = 25 °C
                                                           IF = 30 mA; tp ≤ 300 µs; δ ≤ 0.02;                                                 -        -              500            mV
                                                           pulsed; Tamb = 25 °C
                                                           IF = 100 mA; tp ≤ 300 µs; δ ≤ 0.02;                                                -        -              800            mV
                                                           pulsed; Tamb = 25 °C
IR                              reverse current            VR = 25 V; tp ≤ 300 µs; δ ≤ 0.02;                                                  -        -              2              µA
                                                           pulsed; Tamb = 25 °C
Cd                              diode capacitance          VR = 1 V; f = 1 MHz; Tamb = 25 °C                                                  -        -              10             pF
trr                             reverse recovery time      IF = 10 mA; IR = 10 mA; IR(meas) = 1 mA;                                           -        -              5              ns
                                                           RL = 100 Ω; Tamb = 25 °C

                                                             006aac829                                                                                           aaa-004515
           103                                                                                               103

          IF                                                    (3)                                       IR                            (1)
                                                     (1)
         (mA)                                                                                            (µA)
                                                                      (2)
           102                                                                                               102
                                                                                                                                        (2)



            10                                                                                                 10


                    (1)   (2)     (3)

                1                                                                                               1                       (3)




          10-1                                                                                              10-1
              0.0                       0.4         0.8                  1.2                                        0                   10            20                      30
                                                           VF (V)                                                                                              VR (V)

                (1) Tamb = 125 °C                                                                                 (1) Tamb = 125 °C
                (2) Tamb = 85 °C                                                                                  (2) Tamb = 85 °C
                (3) Tamb = 25 °C                                                                                  (3) Tamb = 25 °C
Fig. 1.         Forward current as a function of forward                                         Fig. 2.          Reverse current as a function of reverse
                voltage; typical values                                                                           voltage; typical values




BAT54S                                                     All information provided in this document is subject to legal disclaimers.                      © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                                   1 July 2022                                                                                            3/9
```

## PDF page 4

```text
Nexperia                                                                                                                                                  BAT54S
                                                                                                                                        Schottky barrier diodes

                                                                                                                 006aac891
                                              10
                                           Cd
                                          (pF)
                                                 8



                                                 6



                                                 4



                                                 2



                                                 0
                                                     0                     10                       20                       30
                                                                                                              VR (V)

             Tamb = 25 °C; f = 1 MHz
Fig. 3.      Diode capacitance as a function of reverse voltage; typical values


11. Test information

                                                                                               tr                 tp
                                                                                                                                  t
                                     D.U.T.
                                                                                               10 %
                                IF                                                                                                    + IF              trr
            RS = 50 Ω
                                                           SAMPLING                                                                                                      t
                                                         OSCILLOSCOPE
         V = VR + IF × RS                                  Ri = 50 Ω
                                                                                                      90 %                                                         (1)
                                                                                  VR
                                                          mga881
                                                                                                          input signal                       output signal

             (1) IR = 1 mA
Fig. 4.      Reverse recovery time test circuit and waveforms




BAT54S                                               All information provided in this document is subject to legal disclaimers.              © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                              1 July 2022                                                                                   4/9
```

## PDF page 5

```text
Nexperia                                                                                                                                                                                   BAT54S
                                                                                                                                                                Schottky barrier diodes


12. Package outline
  Plastic surface-mounted package; 3 leads                                                                                                                                                         SOT23




                                                              D                                      B                                           E                    A            X




                                                                                                                                                 HE                                    v     A




                                                                       3




                                                                                                                                                                      Q


                                                                                                                                A

                                                                                                                                        A1

                                    1                                                      2                                                                                   c

                                                   e1                  bp                            w        B                                                   Lp

                                                              e
                                                                                                                                                     detail X




                                                                                0                    1                  2 mm

                                                                                                scale




     Dimensions (mm are the original dimensions)

          Unit          A     A1        bp     c        D          E        e       e1         HE        Lp       Q        v        w

                max     1.1   0.1       0.48 0.15       3.0       1.4                          2.5       0.45 0.55
         mm     nom                                                         1.9     0.95                                 0.2        0.1
                min     0.9             0.38 0.09       2.8       1.2                          2.1       0.15 0.45

                                                                                                                                                                                               sot023_po

              Outline                                                           References                                                               European
                                                                                                                                                                                       Issue date
              version                    IEC                       JEDEC                         JEITA                                                   projection
                                                                                                                                                                                       14-06-19
                SOT23                                             TO-236AB                                                                                                             14-09-22

Fig. 5.         Package outline SOT23




BAT54S                                                              All information provided in this document is subject to legal disclaimers.                            © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                                              1 July 2022                                                                                                5/9
```

## PDF page 6

```text
Nexperia                                                                                                                                              BAT54S
                                                                                                                                  Schottky barrier diodes


13. Soldering
                                             3.3

                                             2.9

                                             1.9




                                                                                                                                   solder lands


                                                                                                                                   solder resist
               3     1.7                                                                       2

                                                                                                                                   solder paste


                            0.7                                                       0.6                                          occupied area
                           (3×)                                                      (3×)
                                                                                                                        Dimensions in mm

                                              0.5
                                             (3×)
                                              0.6
                                             (3×)

                                               1                                                                                          sot023_fr

Fig. 6.   Reflow soldering footprint for SOT23
                                                      2.2
                                    1.2
                                   (2×)




                            1.4
                           (2×)


                                                                                                                                    solder lands


              4.6    2.6                                                                                                            solder resist


                                                                                                                                    occupied area


                                                                                                                         Dimensions in mm
                           1.4




                                                                                                   preferred transport direction during soldering

                                                      2.8

                                                      4.5                                                                                 sot023_fw

Fig. 7.   Wave soldering footprint for SOT23




BAT54S                                    All information provided in this document is subject to legal disclaimers.                     © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                  1 July 2022                                                                                           6/9
```

## PDF page 7

```text
Nexperia                                                                                                                                 BAT54S
                                                                                                                     Schottky barrier diodes


14. Revision history
Table 8. Revision history
Data sheet ID           Release date                  Data sheet status                              Change notice      Supersedes
BAT54S v.6             20220701                       Product data sheet                             -                  BAT54_SER v.5
Modifications:         •   Family data sheet reduced to single type data sheet.
                       •   Product changed to non-automotive qualification. Please refer to nexperia.com for automotive
                           (-Q) product alternative(s).
                       •   Packing information removed.
BAT54_SER v.5          20121005                       Product data sheet                             -                  BAT54_SERIES v.4
BAT54_SERIES v.4       20020304                       Product data sheet                             -                  BAT54_SERIES v.3
BAT54_SERIES v.3       20011012                       Product specification                          -                  BAT54 v.2
BAT54 v.2              19990506                       Product specification                          -                  BAT54 v.1
BAT54 v.1              19960319                       Product specification                          -                  -




BAT54S                                  All information provided in this document is subject to legal disclaimers.          © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                1 July 2022                                                                                7/9
```

## PDF page 8

```text
Nexperia                                                                                                                                                            BAT54S
                                                                                                                                                Schottky barrier diodes
                                                                                                    injury, death or severe property or environmental damage. Nexperia and its

15. Legal information                                                                               suppliers accept no liability for inclusion and/or use of Nexperia products in
                                                                                                    such equipment or applications and therefore such inclusion and/or use is at
                                                                                                    the customer’s own risk.
                                                                                                    Quick reference data — The Quick reference data is an extract of the
Data sheet status                                                                                   product data given in the Limiting values and Characteristics sections of this
                                                                                                    document, and as such is not complete, exhaustive or legally binding.
 Document status         Product            Definition                                              Applications — Applications that are described herein for any of these
 [1][2]                  status [3]                                                                 products are for illustrative purposes only. Nexperia makes no representation
 Objective [short]       Development        This document contains data from                        or warranty that such applications will be suitable for the specified use
 data sheet                                 the objective specification for                         without further testing or modification.
                                            product development.                                    Customers are responsible for the design and operation of their applications
                                                                                                    and products using Nexperia products, and Nexperia accepts no liability for
 Preliminary [short]     Qualification      This document contains data from
                                                                                                    any assistance with applications or customer product design. It is customer’s
 data sheet                                 the preliminary specification.
                                                                                                    sole responsibility to determine whether the Nexperia product is suitable
 Product [short]         Production         This document contains the product                      and fit for the customer’s applications and products planned, as well as
 data sheet                                 specification.                                          for the planned application and use of customer’s third party customer(s).
                                                                                                    Customers should provide appropriate design and operating safeguards to
                                                                                                    minimize the risks associated with their applications and products.
[1]   Please consult the most recently issued document before initiating or
      completing a design.                                                                          Nexperia does not accept any liability related to any default, damage, costs
[2]   The term 'short data sheet' is explained in section "Definitions".                            or problem which is based on any weakness or default in the customer’s
[3]   The product status of device(s) described in this document may have                           applications or products, or the application or use by customer’s third party
      changed since this document was published and may differ in case of                           customer(s). Customer is responsible for doing all necessary testing for the
      multiple devices. The latest product status information is available on                       customer’s applications and products using Nexperia products in order to
      the internet at https://www.nexperia.com.                                                     avoid a default of the applications and the products or of the application or
                                                                                                    use by customer’s third party customer(s). Nexperia does not accept any
                                                                                                    liability in this respect.
Definitions                                                                                         Limiting values — Stress above one or more limiting values (as defined in
Draft — The document is a draft version only. The content is still under                            the Absolute Maximum Ratings System of IEC 60134) will cause permanent
internal review and subject to formal approval, which may result in                                 damage to the device. Limiting values are stress ratings only and (proper)
modifications or additions. Nexperia does not give any representations or                           operation of the device at these or any other conditions above those
warranties as to the accuracy or completeness of information included herein                        given in the Recommended operating conditions section (if present) or the
and shall have no liability for the consequences of use of such information.                        Characteristics sections of this document is not warranted. Constant or
                                                                                                    repeated exposure to limiting values will permanently and irreversibly affect
Short data sheet — A short data sheet is an extract from a full data sheet
                                                                                                    the quality and reliability of the device.
with the same product type number(s) and title. A short data sheet is
intended for quick reference only and should not be relied upon to contain                          Terms and conditions of commercial sale — Nexperia products are
detailed and full information. For detailed and full information see the relevant                   sold subject to the general terms and conditions of commercial sale, as
full data sheet, which is available on request via the local Nexperia sales                         published at http://www.nexperia.com/profile/terms, unless otherwise agreed
office. In case of any inconsistency or conflict with the short data sheet, the                     in a valid written individual agreement. In case an individual agreement is
full data sheet shall prevail.                                                                      concluded only the terms and conditions of the respective agreement shall
                                                                                                    apply. Nexperia hereby expressly objects to applying the customer’s general
Product specification — The information and data provided in a Product
                                                                                                    terms and conditions with regard to the purchase of Nexperia products by
data sheet shall define the specification of the product as agreed between
                                                                                                    customer.
Nexperia and its customer, unless Nexperia and customer have explicitly
agreed otherwise in writing. In no event however, shall an agreement be                             No offer to sell or license — Nothing in this document may be interpreted
valid in which the Nexperia product is deemed to offer functions and qualities                      or construed as an offer to sell products that is open for acceptance or the
beyond those described in the Product data sheet.                                                   grant, conveyance or implication of any license under any copyrights, patents
                                                                                                    or other industrial or intellectual property rights.
                                                                                                    Export control — This document as well as the item(s) described herein
Disclaimers                                                                                         may be subject to export control regulations. Export might require a prior
Limited warranty and liability — Information in this document is believed                           authorization from competent authorities.
to be accurate and reliable. However, Nexperia does not give any
                                                                                                    Non-automotive qualified products — Unless this data sheet expressly
representations or warranties, expressed or implied, as to the accuracy
                                                                                                    states that this specific Nexperia product is automotive qualified, the
or completeness of such information and shall have no liability for the
                                                                                                    product is not suitable for automotive use. It is neither qualified nor tested in
consequences of use of such information. Nexperia takes no responsibility
                                                                                                    accordance with automotive testing or application requirements. Nexperia
for the content in this document if provided by an information source outside
                                                                                                    accepts no liability for inclusion and/or use of non-automotive qualified
of Nexperia.
                                                                                                    products in automotive equipment or applications.
In no event shall Nexperia be liable for any indirect, incidental, punitive,
                                                                                                    In the event that customer uses the product for design-in and use in
special or consequential damages (including - without limitation - lost
                                                                                                    automotive applications to automotive specifications and standards,
profits, lost savings, business interruption, costs related to the removal
                                                                                                    customer (a) shall use the product without Nexperia’s warranty of the
or replacement of any products or rework charges) whether or not such
                                                                                                    product for such automotive applications, use and specifications, and (b)
damages are based on tort (including negligence), warranty, breach of
                                                                                                    whenever customer uses the product for automotive applications beyond
contract or any other legal theory.
                                                                                                    Nexperia’s specifications such use shall be solely at customer’s own risk,
Notwithstanding any damages that customer might incur for any reason                                and (c) customer fully indemnifies Nexperia for any liability, damages or failed
whatsoever, Nexperia’s aggregate and cumulative liability towards customer                          product claims resulting from customer design and use of the product for
for the products described herein shall be limited in accordance with the                           automotive applications beyond Nexperia’s standard warranty and Nexperia’s
Terms and conditions of commercial sale of Nexperia.                                                product specifications.
Right to make changes — Nexperia reserves the right to make changes                                 Translations — A non-English (translated) version of a document is for
to information published in this document, including without limitation                             reference only. The English version shall prevail in case of any discrepancy
specifications and product descriptions, at any time and without notice. This                       between the translated and English versions.
document supersedes and replaces all information supplied prior to the
publication hereof.
                                                                                                    Trademarks
Suitability for use — Nexperia products are not designed, authorized or
warranted to be suitable for use in life support, life-critical or safety-critical                  Notice: All referenced brands, product names, service names and
systems or equipment, nor in applications where failure or malfunction                              trademarks are the property of their respective owners.
of an Nexperia product can reasonably be expected to result in personal




BAT54S                                                      All information provided in this document is subject to legal disclaimers.                 © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                                    1 July 2022                                                                                       8/9
```

## PDF page 9

```text
Nexperia                                                                                                                                                  BAT54S
                                                                                                                                         Schottky barrier diodes


Contents
1. General description...................................................... 1
2. Features and benefits.................................................. 1
3. Applications.................................................................. 1
4. Quick reference data....................................................1
5. Pinning information......................................................1
6. Ordering information....................................................2
7. Marking.......................................................................... 2
8. Limiting values............................................................. 2
9. Thermal characteristics............................................... 2
10. Characteristics............................................................ 3
11. Test information.......................................................... 4
12. Package outline.......................................................... 5
13. Soldering..................................................................... 6
14. Revision history..........................................................7
15. Legal information........................................................8

© Nexperia B.V. 2022. All rights reserved

For more information, please visit: http://www.nexperia.com
For sales office addresses, please send an email to: salesaddresses@nexperia.com
Date of release: 1 July 2022




BAT54S                                                      All information provided in this document is subject to legal disclaimers.       © Nexperia B.V. 2022. All rights reserved


Product data sheet                                                                    1 July 2022                                                                             9/9
```

