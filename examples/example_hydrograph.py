import io

from swmm_api import read_inp_file
from swmm_api.input_file.sections import GroundwaterFlow

txt = """[HYDROGRAPHS]
; All three unit hydrographs in this group have the same shapes except those in July,
; which have only a short- and medium-term response and a different shape.
UH101 RG1
UH101 ALL SHORT 0.033 1.0 2.0
UH101 ALL MEDIUM 0.300 3.0 2.0
UH101 ALL LONG 0.033 10.0 2.0
UH101 JUL SHORT 0.033 0.5 2.0
UH101 JUL MEDIUM 0.011 2.0 2.0

[TREATMENT]
; 1-st order decay of BOD
Node23 BOD C = BOD * exp(-0.05*HRT)
; lead removal is 20% of TSS removal
Node23 Lead R = 0.2 * R_TSS

[GWF]
;Two-stage linear reservoir for lateral flow
Subcatch1 LATERAL 0.001*Hgw + 0.05*(Hgw–5)*STEP(Hgw–5)

;Constant seepage rate to deep aquifer
Subactch1 DEEP 0.002
"""

inp = read_inp_file(txt)
print(inp.HYDROGRAPHS.to_inp_lines())

inp.GWF.add_obj(GroundwaterFlow('Subc2', GroundwaterFlow.TYPES.LATERAL, '0.001*Hgw + 0.05*(Hgw–5)*STEP(Hgw–5)'))
