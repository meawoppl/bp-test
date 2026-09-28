# Green display LEDs

D10-D73: YONGYUTAI YLED1206G / C30584801, green 1206, replacing YLED1206B. JLC lists Economic and Standard assembly. Supplier stock is dynamic; listings checked 2026-09-27 showed thousands available.

Datasheet Rev 2.0: 3.2 x 1.6 x 0.9 mm, Vf 2.4–3.1 V at 5 mA, 20 mA DC rating, 120 degree viewing angle. Existing individual 470 ohm 1% resistors retained: approximate 4.0–5.5 mA at 5 V, ignoring small MOSFET drop; about 7–15 mW per resistor. Nominal supply current for all 64 lit is approximately 0.26–0.35 A. Vf at the actual operating point and brightness must be measured.

Request all 64 LEDs per board from one common brightness and wavelength bin, preferably one reel across the order. The datasheet overall intensity range is 175–620 mcd at 5 mA, so a shared part number and individual resistors alone do not guarantee matched brightness. Capture optical calibration with the assembled board.

Polarity: manufacturer drawing calls physical anode 1 and cathode 2, whereas the EasyEDA green symbol uses logical 1=K, 2=A. The green footprint LED1206-RD has pad1 at local left and pad2 at local right, matching the KiCad logical mapping. Thus use 0 degree JLC correction for this green part. Blue C28310438 had the opposite logical mapping and required +180; that historical correction is retained only under the old part number. All display LEDs remain native 270 degrees, cathode up toward MOSFET, anode down toward resistor. Verify the green part preview polarity before ordering.

Sources:
- https://jlcpcb.com/partdetail/YONGYUTAI-YLED1206G/C30584801
- https://www.lcsc.com/product-detail/C30584801.html
- https://easyeda.com/api/products/C30584801/components
- libraries/datasheets/YLED1206G.pdf (repository-relative)
