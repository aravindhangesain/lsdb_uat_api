# Work Organization

## Project

Top-level work organizational unit; corresponds to a signed proposal or quote for work to be performed

Examples: 2019 PV Module PQP, Statistical Batch Testing

## Test Sequence Definition -> Work Order

Corresponds to a sequence of work performed on a set of Units

Example: Mechanical Stress Sequence, Thermal Cycling test leg

Test Sequence Definitions attach to a list of Procedure Definitions

Work Orders attach to exactly one Project

## Procedure Definition -> Procedure Result

Corresponds to a single test procedure performed on a single Unit

Examples: EL imaging, TC200 (thermal cycling, 200 cycles)

Procedure Definitions attach to no other organizational unit

Procedure Results attach to exactly one Work Order

## Step Definition -> Step Result

Corresponds to a discrete step in a test procedure

Examples: Capture background EL image, Measure open-circuit voltage

Step Definitions attach to no other organizational unit

Step Results attach to exactly one Procedure Result

### Step Type

Denotes a more general type of step for purposes of assembling a Procedure Definition

Examples: EL imaging, I-V curve tracing

## Measurement Definition -> Measurement Result

Corresponds to a single measured value captured at a step

Examples: EL image at 1x Isc, Open-circuit voltage

Measurement Definitions attach to exactly one Step Definition

Measurement Results attach to exactly one Step Result

### Measurement Type

Denotes a more general type of measurement for purposes of assembling a Step Definition

Examples: EL image, Voltage

### Measurement Result Type

Defines the data type stored in a Measurement Result

Examples: Boolean, Date Time, File, Guid, Image, Numeric, String
