# 28 GHz two-way divider revision A

**0/3** user needs validated · **7/15** requirements verified (0 under-verified, 3 failed, 0 invalid, 3 incomplete, 2 unverified) · **0/0** risks mitigated · 27 test cases (27 owned, 0 unowned, 0 quarantined) · 8 gaps

_attribution: hybrid · lock: requirements/verification.rrlock_

## User needs — validation

| ID | Need | Requirements | Status |
|---|---|---|---|
| UN-1 | Comparable small-signal two-way 24-32 GHz combiner | REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-11, REQ-12, REQ-13 | ❌ FAILED |
| UN-2 | JLC-compatible test coupon using 0.51 mm core and 2.92 mm launches | REQ-8, REQ-9, REQ-10, REQ-11, REQ-13, REQ-14 | 🟡 PARTIAL |
| UN-3 | Traceable design with reproducible simulation evidence | REQ-7, REQ-15 | 🟡 PARTIAL |

## Requirements — verification

| ID | Requirement | Traces | Demands | Evidence | Status |
|---|---|---|---|---|---|
| REQ-1 | DUT-plane: Return loss >=15 dB at each port over 24-32 GHz | satisfies UN-1 | simulation | set 0/3 passed · 3 failed<br>✗ rf_validation::coarse_REQ-1 [simulation]<br>✗ rf_validation::fine_REQ-1 [simulation]<br>✗ rf_validation::finer_REQ-1 [simulation] | ❌ FAILED |
| REQ-2 | DUT-plane: Isolation >=14 dB over 24-32 GHz | satisfies UN-1 | simulation | set 3/3 passed<br>✓ rf_validation::coarse_REQ-2 [simulation]<br>✓ rf_validation::fine_REQ-2 [simulation]<br>✓ rf_validation::finer_REQ-2 [simulation] | ✅ VERIFIED |
| REQ-3 | DUT-plane: Excess insertion loss <=0.7 dB in both directions over 24-32 GHz | satisfies UN-1 | simulation | set 0/3 passed · 3 failed<br>✗ rf_validation::coarse_REQ-3 [simulation]<br>✗ rf_validation::fine_REQ-3 [simulation]<br>✗ rf_validation::finer_REQ-3 [simulation] | ❌ FAILED |
| REQ-4 | DUT-plane: Amplitude imbalance <=0.5 dB over 24-32 GHz | satisfies UN-1 | simulation | set 3/3 passed<br>✓ rf_validation::coarse_REQ-4 [simulation]<br>✓ rf_validation::fine_REQ-4 [simulation]<br>✓ rf_validation::finer_REQ-4 [simulation] | ✅ VERIFIED |
| REQ-5 | DUT-plane: Phase imbalance <=5 degrees over 24-32 GHz | satisfies UN-1 | simulation | set 3/3 passed<br>✓ rf_validation::coarse_REQ-5 [simulation]<br>✓ rf_validation::fine_REQ-5 [simulation]<br>✓ rf_validation::finer_REQ-5 [simulation] | ✅ VERIFIED |
| REQ-6 | DUT-plane: Equal-phase coherent combining loss <=0.7 dB | satisfies UN-1 | simulation | set 0/3 passed · 3 failed<br>✗ rf_validation::coarse_REQ-6 [simulation]<br>✗ rf_validation::fine_REQ-6 [simulation]<br>✗ rf_validation::finer_REQ-6 [simulation] | ❌ FAILED |
| REQ-7 | DUT-plane: Scattering matrix is passive within 0.001 numerical tolerance | satisfies UN-3 | simulation | set 3/3 passed<br>✓ rf_validation::coarse_REQ-7 [simulation]<br>✓ rf_validation::fine_REQ-7 [simulation]<br>✓ rf_validation::finer_REQ-7 [simulation] | ✅ VERIFIED |
| REQ-8 | 40 x 36 mm two-layer RO4350B coupon with 0.51 mm core | satisfies UN-2 | inspection | set 1/1 passed<br>✓ rf_validation::core_and_outline [inspection] | ✅ VERIFIED |
| REQ-9 | Three 1092-03A-6 2.92 mm edge-launch footprints and microstrip feeds | satisfies UN-2 | inspection | set 1/1 passed<br>✓ rf_validation::launch_footprints [inspection] | ✅ VERIFIED |
| REQ-10 | Zero native KiCad DRC violations and unconnected items | satisfies UN-2 | inspection | set 1/1 passed<br>✓ rf_validation::native_drc [inspection] | ✅ VERIFIED |
| REQ-11 | Complete fixture meets RF limits at calibrated connector reference planes | satisfies UN-1, UN-2 | hil | — | ⚪ UNVERIFIED |
| REQ-12 | Qualify 5 W coherent combining under specified thermal conditions | satisfies UN-1 | hil | — | ⚪ UNVERIFIED |
| REQ-13 | Whole populated assembly meets every RF acceptance limit at the three coaxial connector planes | satisfies UN-1, UN-2 | simulation | set 0/1 passed · 1 skipped<br>– assembly_validation::full_assembly_rf_acceptance [simulation] | 🟡 INCOMPLETE |
| REQ-14 | Assembly model covers actual geometry, materials, contacts and package parasitics with qualified provenance | satisfies UN-2 | inspection | set 0/1 passed · 1 skipped<br>– assembly_validation::assembly_model_scope [inspection] | 🟡 INCOMPLETE |
| REQ-15 | Whole-assembly RF results have mesh, time-domain and tolerance convergence evidence | satisfies UN-3 | simulation | set 0/1 passed · 1 skipped<br>– assembly_validation::mesh_and_tolerance_convergence [simulation] | 🟡 INCOMPLETE |

## Test methods

| ID | Method | Level | Used by |
|---|---|---|---|
| TM-1 | Exported-footprint native FDTD on three grids | simulation | REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7 |
| TM-2 | KiCad native DRC and geometry inspection | inspection | REQ-8, REQ-9, REQ-10 |
| TM-3 | Calibrated three-port VNA measurement | hil | REQ-11 |
| TM-4 | Controlled-power thermal qualification | hil | REQ-12 |
| TM-5 | Complete assembly EM/co-simulation at coaxial connector planes | simulation | REQ-13, REQ-15 |
| TM-6 | Assembly model coverage and provenance inspection | inspection | REQ-14 |

## Verification sets

Each entity's set: the cases it owns, the cases it expects (literal selectors, the lock) and every quarantined case that names it. It is verified only when the whole set passed together.

### REQ-1 — ❌ FAILED

set 0/3 passed · 3 failed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-1 | failed | simulation | model | rf_validation::coarse_REQ-1 |  |
| //:validation#rf_validation::fine_REQ-1 | failed | simulation | model | rf_validation::fine_REQ-1 |  |
| //:validation#rf_validation::finer_REQ-1 | failed | simulation | model | rf_validation::finer_REQ-1 |  |

### REQ-2 — ✅ VERIFIED

set 3/3 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-2 | passed | simulation | model | rf_validation::coarse_REQ-2 |  |
| //:validation#rf_validation::fine_REQ-2 | passed | simulation | model | rf_validation::fine_REQ-2 |  |
| //:validation#rf_validation::finer_REQ-2 | passed | simulation | model | rf_validation::finer_REQ-2 |  |

### REQ-3 — ❌ FAILED

set 0/3 passed · 3 failed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-3 | failed | simulation | model | rf_validation::coarse_REQ-3 |  |
| //:validation#rf_validation::fine_REQ-3 | failed | simulation | model | rf_validation::fine_REQ-3 |  |
| //:validation#rf_validation::finer_REQ-3 | failed | simulation | model | rf_validation::finer_REQ-3 |  |

### REQ-4 — ✅ VERIFIED

set 3/3 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-4 | passed | simulation | model | rf_validation::coarse_REQ-4 |  |
| //:validation#rf_validation::fine_REQ-4 | passed | simulation | model | rf_validation::fine_REQ-4 |  |
| //:validation#rf_validation::finer_REQ-4 | passed | simulation | model | rf_validation::finer_REQ-4 |  |

### REQ-5 — ✅ VERIFIED

set 3/3 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-5 | passed | simulation | model | rf_validation::coarse_REQ-5 |  |
| //:validation#rf_validation::fine_REQ-5 | passed | simulation | model | rf_validation::fine_REQ-5 |  |
| //:validation#rf_validation::finer_REQ-5 | passed | simulation | model | rf_validation::finer_REQ-5 |  |

### REQ-6 — ❌ FAILED

set 0/3 passed · 3 failed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-6 | failed | simulation | model | rf_validation::coarse_REQ-6 |  |
| //:validation#rf_validation::fine_REQ-6 | failed | simulation | model | rf_validation::fine_REQ-6 |  |
| //:validation#rf_validation::finer_REQ-6 | failed | simulation | model | rf_validation::finer_REQ-6 |  |

### REQ-7 — ✅ VERIFIED

set 3/3 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::coarse_REQ-7 | passed | simulation | model | rf_validation::coarse_REQ-7 |  |
| //:validation#rf_validation::fine_REQ-7 | passed | simulation | model | rf_validation::fine_REQ-7 |  |
| //:validation#rf_validation::finer_REQ-7 | passed | simulation | model | rf_validation::finer_REQ-7 |  |

### REQ-8 — ✅ VERIFIED

set 1/1 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::core_and_outline | passed | inspection | model | rf_validation::core_and_outline |  |

### REQ-9 — ✅ VERIFIED

set 1/1 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::launch_footprints | passed | inspection | model | rf_validation::launch_footprints |  |

### REQ-10 — ✅ VERIFIED

set 1/1 passed

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#rf_validation::native_drc | passed | inspection | model | rf_validation::native_drc |  |

### REQ-13 — 🟡 INCOMPLETE

set 0/1 passed · 1 skipped

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#assembly_validation::full_assembly_rf_acceptance | skipped | simulation | model | assembly_validation::full_assembly_rf_acceptance |  |

### REQ-14 — 🟡 INCOMPLETE

set 0/1 passed · 1 skipped

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#assembly_validation::assembly_model_scope | skipped | inspection | model | assembly_validation::assembly_model_scope |  |

### REQ-15 — 🟡 INCOMPLETE

set 0/1 passed · 1 skipped

| Case | State | Level | Via | Selector | Note |
|---|---|---|---|---|---|
| //:validation#assembly_validation::mesh_and_tolerance_convergence | skipped | simulation | model | assembly_validation::mesh_and_tolerance_convergence |  |

## Case attribution

| Target | Cases | Owned | Quarantined | Unowned | Owners |
|---|---|---|---|---|---|
| //:validation | 27 | 27 | 0 | 0 | REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-9, REQ-10, REQ-13, REQ-14, REQ-15 |

## Gaps

| Kind | Entity | Route | Detail |
|---|---|---|---|
| failed | REQ-1 | autonomous | failing evidence: rf_validation::coarse_REQ-1, rf_validation::fine_REQ-1, rf_validation::finer_REQ-1 |
| failed | REQ-3 | autonomous | failing evidence: rf_validation::coarse_REQ-3, rf_validation::fine_REQ-3, rf_validation::finer_REQ-3 |
| failed | REQ-6 | autonomous | failing evidence: rf_validation::coarse_REQ-6, rf_validation::fine_REQ-6, rf_validation::finer_REQ-6 |
| unverified | REQ-11 | human-gate | no test evidence |
| unverified | REQ-12 | human-gate | no test evidence |
| incomplete | REQ-13 | autonomous | 0/1 passed; 1 skipped (//:validation) |
| incomplete | REQ-14 | human-gate | 0/1 passed; 1 skipped (//:validation) |
| incomplete | REQ-15 | autonomous | 0/1 passed; 1 skipped (//:validation) |
