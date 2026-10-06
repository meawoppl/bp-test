# Source documents

- `AD7606C-16.pdf` / `.txt`: Analog Devices AD7606C-16 Rev A, downloaded 2026-09-27 from
  https://datasheet.lcsc.com/datasheet/pdf/015743c49bb420a4997007d6e77cabc1.pdf .
  Official: https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606c-16.pdf .
- `UD27C-through-hole-reference.pdf`: Daniel E. Marks through-hole UD2.7C reference,
  https://github.com/profdc9/DRSSTC-PCB-Pack/blob/master/ud27c%20thru%20hole/ud27-schematic.pdf .
  Original UD2.7 explanation: https://www.loneoceans.com/labs/ud27/ .

Documents retain their original authorship. Included as unmodified engineering references;
not claimed as bp-test designs. Their driver topology is being reviewed, not yet integrated.

- `CM600HA-24H.pdf`: Mitsubishi/Powerex datasheet, mirror
  https://makerselectronics.com/wp-content/uploads/2022/12/Mitsubishi-CM600HA-24H-datasheet-1.pdf .
- `LM5116.pdf`: https://www.ti.com/lit/ds/symlink/lm5116.pdf — selected main controller.
- `LM5164.pdf`: https://www.ti.com/lit/ds/symlink/lm5164.pdf — selected auxiliary converters.
- `UCC27423.pdf`: https://www.ti.com/lit/ds/symlink/ucc27423.pdf — planned predriver reference.
- `LM5146.pdf`: https://www.ti.com/lit/ds/symlink/lm5146.pdf — researched alternative; LM5116 chosen for accessible HTSSOP leads.

## CST front-end references

All local PDFs have Markdown text extractions alongside them.

- [OPA197 PDF](OPA197.pdf) / [Markdown](OPA197.md)
- [TPS60403 PDF](TPS60403.pdf) / [Markdown](TPS60403.md)
- [TLV3501 PDF](TLV3501.pdf) / [Markdown](TLV3501.md)
- [SN74LVC1G02 PDF](SN74LVC1G02.pdf) / [Markdown](SN74LVC1G02.md)
- [CRCW PDF](CRCW.pdf) / [Markdown](CRCW.md)
- [Precision-Rectifier-Reference PDF](Precision-Rectifier-Reference.pdf) / [Markdown](Precision-Rectifier-Reference.md)
- [BAT54S PDF](BAT54S.pdf) / [Markdown](BAT54S.md)
- [SMBJ PDF](SMBJ.pdf) / [Markdown](SMBJ.md)
- [BAV16W_1N4148W-Diodes PDF](BAV16W_1N4148W-Diodes.pdf) / [Markdown](BAV16W_1N4148W-Diodes.md)

BAT54S, SMBJ (DS19002), and BAV16W/1N4148W (DS30086) were supplied by the user. The last is a **Diodes Incorporated** reference, not the exact Nexperia `1N4148W,115` currently specified at D41/D42. Do not treat it as exact manufacturer qualification; resolve the selected ordering code against its own datasheet before release.

## GDT output stage

UCC27282, SN74LVC08A, STD80N10F7 and Panasonic ECQE-F PDFs and text/Markdown extractions are local. ST manufacturer PDF was retrieved through the LCSC mirror after direct ST download failed. See sources.json and OUTPUT-STAGE.md for selection and validation limits.

## Original UD2.7 ceramic output network

The original Rev C BOM and KEMET 1 uF part PDF/Markdown are archived here. ECQE-F is historical only: those film parts were removed. The 2.2 uF TDK full-part characteristic PDF download failed; exact bias/current curves remain to be archived/qualified.
