#!/usr/bin/env python3
"""
Flash Test JSON Processor
=========================
Reads flash test measurement JSON files (zstandard + delta-encoded arrays),
extracts IV curve data, computes Single Diode Model (SDM) fit curves,
and outputs structured results as JSON for downstream plotting.

Dependencies:
    pip install zstandard

Usage:
    python flash_test_processor.py input.json                     # outputs to stdout
    python flash_test_processor.py input.json -o output.json      # outputs to file
    python flash_test_processor.py input.json -o output.json -n 300  # 300-pt SDM curve

Output JSON structure:
    {
        "module": { serial, technology, nameplate_pmax, isc, voc, imp, vmp, num_cells },
        "params_measured": { Pmp, Voc, Isc, Vmp, Imp, FF, irradiance, temperature },
        "params_corrected": { Pmp, Voc, Isc, Vmp, Imp, FF, temperature_ref },
        "sdm_params_measured": { I_L, I_o, R_s, R_sh, nNsVth },
        "sdm_params_corrected": { I_L, I_o, R_s, R_sh, nNsVth },
        "coefficients": { alpha, beta, kappa },
        "checks": { normalized_rms_error, enough_mpp_datapoints, voc_points, range_isc_points },
        "iv_curve_measured": {
            "scatter": [ { V, I }, ... ],           # raw measured points (all flashes)
            "sdm_fit": [ { V, I, P }, ... ],         # smooth SDM model curve
            "mpp_polyfit": [ { V, P }, ... ]          # polynomial fit near MPP
        },
        "iv_curve_corrected": {
            "scatter": [ { V, I }, ... ],
            "sdm_fit": [ { V, I, P }, ... ],
            "mpp_polyfit": [ { V, P }, ... ]
        }
    }
"""

import argparse
import base64
import json
import math
import struct
import sys
from pathlib import Path

try:
    import zstandard
except ImportError:
    print("ERROR: zstandard package required. Install with: pip install zstandard", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────
# Array Decoding
# ─────────────────────────────────────────────
# JSON files store numeric arrays in a compressed binary format:
#   {
#     "__encoded_array__": true,
#     "data": "<base64-encoded zstandard-compressed bytes>",
#     ... plus either { dtype, shape } or { length, first }
#   }
#
# Two encoding variants exist:
#
# Variant A — "dtype/shape" format (direct values):
#   - "dtype": "float32" or "float64"
#   - "shape": [N] or N
#   - Decompressed bytes are N packed floats/doubles
#
# Variant B — "length/first" format (delta-encoded):
#   - "length": N (total number of values)
#   - "first": <float> (the first value)
#   - Decompressed bytes are (N-1) deltas (float32 or float64)
#   - Reconstruct: values[0] = first, values[i] = values[i-1] + delta[i-1]

def decode_array(obj):
    """Decode a compressed/encoded array from the JSON structure.
    
    Returns a list of floats, or None if the input is not an encoded array.
    """
    if not isinstance(obj, dict) or not obj.get("__encoded_array__"):
        return None

    raw = base64.b64decode(obj["data"])
    dctx = zstandard.ZstdDecompressor()

    # Variant A: dtype/shape — direct packed values
    if "dtype" in obj:
        shape = obj["shape"]
        length = shape[0] if isinstance(shape, list) else shape
        decompressed = dctx.decompress(raw, max_output_size=length * 8 + 4096)

        fmt_char = "f" if obj["dtype"] == "float32" else "d"
        elem_size = 4 if fmt_char == "f" else 8
        return list(struct.unpack(f"<{length}{fmt_char}", decompressed[: length * elem_size]))

    # Variant B: length/first — delta-encoded
    if "length" in obj:
        length = obj["length"]
        first = obj["first"]
        n_deltas = length - 1
        decompressed = dctx.decompress(raw, max_output_size=n_deltas * 8 + 4096)

        if len(decompressed) == n_deltas * 4:
            deltas = list(struct.unpack(f"<{n_deltas}f", decompressed))
        elif len(decompressed) == n_deltas * 8:
            deltas = list(struct.unpack(f"<{n_deltas}d", decompressed))
        else:
            raise ValueError(
                f"Delta bytes mismatch: got {len(decompressed)}, "
                f"expected {n_deltas * 4} (f32) or {n_deltas * 8} (f64)"
            )

        values = [first]
        for d in deltas:
            values.append(values[-1] + d)
        return values

    return None


# ─────────────────────────────────────────────
# SDM Curve Computation
# ─────────────────────────────────────────────
# The Single Diode Model defines an implicit I-V relationship:
#
#   I = I_L - I_o * (exp((V + I*R_s) / nNsVth) - 1) - (V + I*R_s) / R_sh
#
# where:
#   I_L     = photogenerated (light) current [A]
#   I_o     = diode reverse saturation current [A]
#   R_s     = series resistance [Ω]
#   R_sh    = shunt resistance [Ω]
#   nNsVth  = modified ideality factor × num_cells × thermal voltage [V]
#
# Since I appears on both sides, we solve iteratively using Newton's method
# for each voltage point.

def compute_sdm_curve(params, v_start=-1.5, v_end=47.0, n_points=500):
    """Evaluate the SDM I-V curve across a voltage range.
    
    Args:
        params: dict with keys I_L, I_o, R_s, R_sh, nNsVth
        v_start: starting voltage (negative to capture pre-Isc region)
        v_end: ending voltage (past Voc for extrapolation)
        n_points: number of evaluation points
    
    Returns:
        list of dicts: [ { V, I, P }, ... ]
    """
    I_L = params["I_L"]
    I_o = params["I_o"]
    R_s = params["R_s"]
    R_sh = params["R_sh"]
    nNsVth = params["nNsVth"]

    results = []
    for i in range(n_points):
        V = v_start + (v_end - v_start) * i / (n_points - 1)

        # Newton's method: solve f(I) = 0 where
        #   f(I) = I_L - I_o*(exp((V+I*Rs)/nNsVth) - 1) - (V+I*Rs)/Rsh - I
        #   f'(I) = -I_o*Rs/nNsVth * exp(...) - Rs/Rsh - 1
        I = I_L  # initial guess (short-circuit value)
        for _ in range(50):
            exp_arg = (V + I * R_s) / nNsVth
            exp_arg = min(exp_arg, 100.0)  # prevent overflow
            exp_val = math.exp(exp_arg)

            f = I_L - I_o * (exp_val - 1) - (V + I * R_s) / R_sh - I
            df = -I_o * R_s / nNsVth * exp_val - R_s / R_sh - 1

            delta = -f / df
            I += delta
            if abs(delta) < 1e-12:
                break

        P = V * I
        results.append({"V": round(V, 5), "I": round(I, 5), "P": round(P, 5)})

    return results


# ─────────────────────────────────────────────
# Main Processing
# ─────────────────────────────────────────────
# JSON file structure (key paths used):
#
# Root
# ├── ModuleSerialNumber          → string
# ├── ModuleProperty              → { nameplate_pmax, isc, voc, imp, vmp, number_of_cells, module_technology_name }
# ├── Flashes                     → list (2 or 4 flash objects, used for flash count only)
# ├── IVParams                    → main analysis results
# │   ├── v_oc, i_sc, v_mp, i_mp, p_mp, ff                    → measured (uncorrected) parameters
# │   ├── v_oc_corr, i_sc_corr, v_mp_corr, i_mp_corr, ...     → STC-corrected parameters
# │   ├── irradiance_meas, temperature_dut, temperature_ref    → conditions
# │   ├── alpha, beta, kappa                                   → temperature coefficients
# │   │
# │   ├── iv_raw                  → { v_meas, i_meas }         → encoded arrays, all measured points
# │   ├── iv_corr                 → { v_corr, i_corr }         → encoded arrays, STC-corrected points
# │   │
# │   ├── refined_fit_params      → { I_L, I_o, R_s, R_sh, nNsVth, fun }  → SDM params (measured)
# │   ├── refined_fit_corr_params → { I_L, I_o, R_s, R_sh, nNsVth, fun }  → SDM params (corrected)
# │   │
# │   ├── mpp_polyfit             → { v_smooth, p_smooth, v_mp, i_mp, p_mp, coeffs, degree, ... }
# │   ├── mpp_corr_polyfit        → { v_smooth, p_smooth, ... }
# │   │
# │   ├── Check Normalized RMS Error     → 0 or 1
# │   ├── Check Enough MPP Datapoints    → 0 or 1
# │   ├── Check Voc Points               → True/False
# │   └── Check Range Isc Points         → True/False
# │
# └── Array Encoding              → { dtype, encoding, codec }  → metadata about encoding scheme

def process_flash_test(data, sdm_points=500):
    """Process a flash test JSON file and return structured results.
    
    Args:
        filepath: path to the JSON file
        sdm_points: number of points for SDM curve evaluation
    
    Returns:
        dict with all extracted and computed data
    """

    iv = data["IVParams"]
    mod = data.get("ModuleProperty", {})
    flashes = data.get("Flashes", [])

    # ── Module info ──
    module = {
        "serial": data.get("ModuleSerialNumber", ""),
        "technology": mod.get("module_technology_name", ""),
        "nameplate_pmax": mod.get("nameplate_pmax"),
        "isc": mod.get("isc"),
        "voc": mod.get("voc"),
        "imp": mod.get("imp"),
        "vmp": mod.get("vmp"),
        "num_cells": mod.get("number_of_cells"),
        "num_flashes": len(flashes),
    }

    # ── Extracted parameters (measured / uncorrected) ──
    params_measured = {
        "Pmp": iv["p_mp"],
        "Voc": iv["v_oc"],
        "Isc": iv["i_sc"],
        "Vmp": iv["v_mp"],
        "Imp": iv["i_mp"],
        "FF": iv["ff"],
        "irradiance": iv.get("irradiance_meas"),
        "temperature": iv.get("temperature_dut"),
    }

    # ── STC-corrected parameters ──
    params_corrected = {
        "Pmp": iv["p_mp_corr"],
        "Voc": iv["v_oc_corr"],
        "Isc": iv["i_sc_corr"],
        "Vmp": iv["v_mp_corr"],
        "Imp": iv["i_mp_corr"],
        "FF": iv["ff_corr"],
        "temperature_ref": iv.get("temperature_ref"),
    }

    # ── SDM parameters ──
    sdm_measured = {k: v for k, v in iv["refined_fit_params"].items() if k != "fun"}
    sdm_corrected = {k: v for k, v in iv["refined_fit_corr_params"].items() if k != "fun"}

    # ── Temperature coefficients ──
    coefficients = {
        "alpha": iv.get("alpha"),
        "beta": iv.get("beta"),
        "kappa": iv.get("kappa"),
    }

    # ── Quality checks ──
    checks = {
        "normalized_rms_error": bool(iv.get("Check Normalized RMS Error")),
        "enough_mpp_datapoints": bool(iv.get("Check Enough MPP Datapoints")),
        "voc_points": bool(iv.get("Check Voc Points")),
        "range_isc_points": bool(iv.get("Check Range Isc Points")),
    }

    # ── Decode measured IV scatter points ──
    #    Source: IVParams.iv_raw.v_meas + IVParams.iv_raw.i_meas
    v_meas = decode_array(iv["iv_raw"]["v_meas"])
    i_meas = decode_array(iv["iv_raw"]["i_meas"])

    # ── Decode corrected IV scatter points ──
    #    Source: IVParams.iv_corr.v_corr + IVParams.iv_corr.i_corr
    v_corr = decode_array(iv["iv_corr"]["v_corr"])
    i_corr = decode_array(iv["iv_corr"]["i_corr"])

    scatter_measured = [
        {"V": round(v, 5), "I": round(i, 5)} for v, i in zip(v_meas, i_meas)
    ]
    scatter_corrected = [
        {"V": round(v, 5), "I": round(i, 5)} for v, i in zip(v_corr, i_corr)
    ]

    # ── Compute SDM fit curves ──
    #    Source: IVParams.refined_fit_params / refined_fit_corr_params
    #    Uses Newton's method to solve the implicit SDM equation at each V
    voc_meas = iv["v_oc"]
    voc_corr = iv["v_oc_corr"]
    sdm_curve_measured = compute_sdm_curve(
        sdm_measured, v_start=-1.5, v_end=voc_meas + 2.0, n_points=sdm_points
    )
    sdm_curve_corrected = compute_sdm_curve(
        sdm_corrected, v_start=-1.5, v_end=voc_corr + 2.0, n_points=sdm_points
    )

    # ── Decode MPP polyfit smooth curves ──
    #    Source: IVParams.mpp_polyfit.v_smooth + .p_smooth (200 pts typically)
    #    These are polynomial fits (degree 4) to the power curve near MPP
    mpp_polyfit_measured = []
    mpp_vs = decode_array(iv["mpp_polyfit"].get("v_smooth"))
    mpp_ps = decode_array(iv["mpp_polyfit"].get("p_smooth"))
    if mpp_vs and mpp_ps:
        mpp_polyfit_measured = [
            {"V": round(v, 5), "P": round(p, 5)} for v, p in zip(mpp_vs, mpp_ps)
        ]

    mpp_polyfit_corrected = []
    mpp_cvs = decode_array(iv["mpp_corr_polyfit"].get("v_smooth"))
    mpp_cps = decode_array(iv["mpp_corr_polyfit"].get("p_smooth"))
    if mpp_cvs and mpp_cps:
        mpp_polyfit_corrected = [
            {"V": round(v, 5), "P": round(p, 5)} for v, p in zip(mpp_cvs, mpp_cps)
        ]

    # ── Assemble output ──
    return {
        "module": module,
        "params_measured": params_measured,
        "params_corrected": params_corrected,
        "sdm_params_measured": sdm_measured,
        "sdm_params_corrected": sdm_corrected,
        "coefficients": coefficients,
        "checks": checks,
        "iv_curve_measured": {
            "scatter": scatter_measured,
            "sdm_fit": sdm_curve_measured,
            "mpp_polyfit": mpp_polyfit_measured,
        },
        "iv_curve_corrected": {
            "scatter": scatter_corrected,
            "sdm_fit": sdm_curve_corrected,
            "mpp_polyfit": mpp_polyfit_corrected,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Process flash test JSON files and extract IV curves + parameters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flash_test_processor.py measurement.json
  python flash_test_processor.py measurement.json -o result.json
  python flash_test_processor.py measurement.json -o result.json -n 300 --compact
        """,
    )
    parser.add_argument("input", help="Path to flash test JSON file")
    parser.add_argument("-o", "--output", help="Output JSON file (default: stdout)")
    parser.add_argument(
        "-n", "--sdm-points", type=int, default=500,
        help="Number of points for SDM curve (default: 500)"
    )
    parser.add_argument(
        "--compact", action="store_true",
        help="Compact JSON output (no indentation)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = process_flash_test(input_path, sdm_points=args.sdm_points)

    indent = None if args.compact else 2
    output_json = json.dumps(result, indent=indent)

    if args.output:
        Path(args.output).write_text(output_json)
        # Print summary to stderr so it doesn't pollute the JSON output
        m = result["module"]
        pm = result["params_measured"]
        pc = result["params_corrected"]
        n_scatter = len(result["iv_curve_measured"]["scatter"])
        n_sdm = len(result["iv_curve_measured"]["sdm_fit"])
        print(f"Processed: {m['serial']} ({m['technology']})", file=sys.stderr)
        print(f"  Nameplate: {m['nameplate_pmax']}W | Cells: {m['num_cells']} | Flashes: {m['num_flashes']}", file=sys.stderr)
        print(f"  Measured:  Pmp={pm['Pmp']:.2f}W  Voc={pm['Voc']:.3f}V  Isc={pm['Isc']:.3f}A  FF={pm['FF']:.4f}", file=sys.stderr)
        print(f"  Corrected: Pmp={pc['Pmp']:.2f}W  Voc={pc['Voc']:.3f}V  Isc={pc['Isc']:.3f}A  FF={pc['FF']:.4f}", file=sys.stderr)
        print(f"  IV scatter: {n_scatter} pts | SDM fit: {n_sdm} pts", file=sys.stderr)
        print(f"  Checks: RMS={'✓' if result['checks']['normalized_rms_error'] else '✗'}  "
              f"MPP={'✓' if result['checks']['enough_mpp_datapoints'] else '✗'}  "
              f"Voc={'✓' if result['checks']['voc_points'] else '✗'}  "
              f"Isc={'✓' if result['checks']['range_isc_points'] else '✗'}", file=sys.stderr)
        print(f"  Output: {args.output} ({len(output_json):,} bytes)", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
