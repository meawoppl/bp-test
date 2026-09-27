# USB and OCXO model update, 2026-09-26

- J3 TYPE-C-31-M-12: downloaded detailed STEP from https://github.com/ai03-2725/Type-C.pretty/blob/master/HRO%20%20TYPE-C-31-M-12.step . Original retained under vendor/. Normalized with +90 degree X rotation and (-4.47,-3.65,0) mm translation for the KiCad footprint origin. Mounting pegs align at footprint (+/-2.89,-2.6); the mating face points out of the right edge. Community model, not manufacturer CAD. No explicit license file was found in the source repository; preserve attribution and review redistribution terms before distributing the model separately.
- Y1 AOC97FAJC-10.0000: drawing-derived detailed envelope from https://abracon.com/datasheets/AOC97.pdf page 4 (10 MHz package). Correct 9.7 x 7.5 x 3.9 mm body, 6 x 4 mm terminal grid and pin-1 marker. Cosmetic rounding, seams and lettering are illustrative. Abracon links https://abracon.com/Support/STEP/AOC97.STEP.zip but download returned HTTP 403, so this is explicitly not vendor STEP. Do not use the 20/48 MHz package drawing for this part.

Reproducible generator: tools/hardware/calibrator_connector_ocxo_models.py (CadQuery).
Board and library model paths updated; tools/hardware/calibrator_models.py preserves the selections.
Native KiCad angled render inspected at tmp/calibrator-model-upgrade/assembled.png. No pad, net or copper changes in this model update.
