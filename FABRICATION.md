# Fabrication and assembly — experimental revision A

The Gerber/drill ZIP represents the committed 40 × 36 mm board. It has native KiCad DRC approval but **fails RF requirements**. Use it as a small-signal experimental coupon, not a production-equivalent combiner. Complete populated-assembly simulation at connector reference planes is mandatory under [spec.json](spec.json), and currently blocked; see [assembly status](reports/assembly-validation.json).

## JLC quote selections

| Item | Selection |
|---|---|
| Layers | 2 |
| Laminate | Rogers RO4350B |
| Core | 0.51 mm |
| Nominal finished thickness | JLC 0.65 mm option; confirm actual stackup |
| Copper | Nominal 1 oz, 35 µm |
| Finish | ENIG |
| Mask / legend | Green / white |
| Outline | 40 × 36 mm |
| Via | 0.30 mm plated drill / 0.80 mm copper diameter |
| Connector mounting holes | 2.06 mm NPTH, 9.53 mm spacing, 2.79 mm edge setback |

The explicit modeled copper/core thickness sum is 0.58 mm (35 + 510 + 35 µm). The nominal 0.65 mm finished-board selection is a vendor option, not a claim that 70 µm of finish has been modeled. Confirm the supplied dielectric core remains 0.51 mm and review JLC's finished stackup before ordering. Copper roughness and ENIG loss are not simulated.

Published fabrication sources: [JLC RF PCB service](https://jlcpcb.com/pcb-fabrication/high-frequency-pcb), [core options](https://jlcpcb.com/news/rogers-ptfe-high-frequency-pcb-available). Manufacturer mechanical drawing: [1092-03A-6](reference/1092-03A-6.pdf). RF microstrip and DUT copper are mask-open. The backside ground is continuous except for mechanical-hole clearances.

## Manual assembly and test

Install three Southwest Microwave 1092-03A-6 end launches. Their 2.92 mm interface is specified to 40 GHz; the planar launch transition on this coupon is not manufacturer RF-qualified. Check the connector block, pin contact and clamp seating against the board thickness before assembly.

Install Vishay CH02016-100RGFTF, 100 ohm, active face down across RF1 pads 4/5. The CAD pad geometry is inherited from the simulation's lumped resistor; verify the specific part termination overlap and solder process under magnification. The part has no packaged-resistor EM model in this run. See [CH datasheet](reference/ch.pdf). Do not substitute a generic 0201 resistor and assume identical RF behavior.

Begin with low-power VNA measurements (e.g. ≤0 dBm), measure all three ports, and account for the launch/feed sections when comparing DUT-plane results. There is no thermal or 5 W qualification, assembly service order or vendor upload in this repository. BOM lists manual components; no automated placement file is provided.
