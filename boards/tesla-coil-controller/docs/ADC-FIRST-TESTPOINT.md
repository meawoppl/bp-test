# ADC first-data probe

`ADC_FIRST` now connects U1 pin 15 (AD7606C-16 FRSTDATA) to **TP1**, a 1 mm exposed top-side probe pad at **(98.5, 103.5) mm**, beside the ADC's lower-right corner. The silkscreen identifies it as `ADC_FIRST`. It is outside the package and daughterboard envelope, with probe access visible in the native top-side render.

The former J7 pin 7 connection is removed and explicitly marked unused in the schematic. Replacing the service-header run reduced this net from 93.919 mm and two vias to **3.577 mm, no vias**, using a uniform 0.20 mm top-layer track with straight pad exits and a 45-degree miter. TP1 is bare copper, excluded from the BOM and component placement output; no purchased part is needed.

FRSTDATA indicates the first channel's serial readout. In the configured serial interface it returns low after the first 16 SCLK falling edges; `ADC_BUSY` remains the FPGA's conversion-complete indication. See the [saved ADC datasheet](datasheets/AD7606C-16.pdf).

The circuit contract, schematic generator, placement table and reviewed copper snapshot include this change. The FPGA routing audit checks that the net joins only U1.15 and TP1.1, reaches both pads and has no vias. [Measured geometry](adc-first-testpoint.json) records the final board hash.

Native ERC and schematic parity pass. Physical DRC has no new findings; the same four intentional CST handoff ends and 29 unrelated open connections remain. The schematic PDF and top-side 3D preview were refreshed and inspected. The whole-board layout-quality backlog remains open. The net-name silk is an intentional identification label requested for probing; the reused standard test-point footprint has a 0.12 mm silk ring, which the 0.15 mm profile flags and which remains a final DFM cleanup item. No DRC exclusions or relaxed rules were added, and no fabrication package was published for this unrouted draft.
