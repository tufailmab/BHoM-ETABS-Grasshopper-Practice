#!/usr/bin/env python3
"""
Rebar Calculator (Pakistan standard sizes)
-------------------------------------------
Interactive, always-on loop.

For each run it asks you for:
  1) The bar diameter you want to use (pick from the standard list, or
     type a custom diameter)
  2) The required steel area for that frame member (As_required)

...and prints:
  - Area provided by ONE bar
  - Number of bars needed (rounded UP, since you can never use a
    fraction of a bar) via ceil()
  - Total area actually provided by that many bars
  - Excess area / % over-provided
  - Optional: total steel weight, if you give a member length

Type 'q', 'quit' or 'exit' at any prompt to stop the program.
Type 'list' at the diameter prompt to see the size table again.
"""

import math
import sys

# ---------------------------------------------------------------------
# Standard deformed (ribbed) metric rebar sizes commonly available in
# Pakistan (mm). Add/remove sizes here if your supplier stocks different
# ones -- everything else in the script recalculates automatically.
# ---------------------------------------------------------------------
STANDARD_SIZES_MM = [6, 8, 10, 12, 16, 20, 22, 25, 28, 32, 36, 40]

QUIT_WORDS = {"q", "quit", "exit"}


def bar_area_mm2(dia_mm: float) -> float:
    """Cross-sectional area of a single round bar, in mm^2."""
    return math.pi * dia_mm ** 2 / 4.0


def bar_weight_kg_per_m(dia_mm: float) -> float:
    """Standard steel-rebar approximation: d^2 / 162 (d in mm) -> kg/m."""
    return dia_mm ** 2 / 162.0


def mm2_to(value_mm2: float, unit: str) -> float:
    """Convert an area in mm^2 to the requested unit."""
    unit = unit.lower()
    if unit in ("mm2", "mm^2", "mm"):
        return value_mm2
    if unit in ("cm2", "cm^2", "cm"):
        return value_mm2 / 100.0
    if unit in ("m2", "m^2", "m"):
        return value_mm2 / 1_000_000.0
    if unit in ("in2", "in^2", "in"):
        return value_mm2 / 645.16
    if unit in ("ft2", "ft^2", "ft"):
        return value_mm2 / 92_903.04
    raise ValueError(f"Unknown unit: {unit}")


def to_mm2(value: float, unit: str) -> float:
    """Convert an area given in `unit` back to mm^2."""
    unit = unit.lower()
    if unit in ("mm2", "mm^2", "mm"):
        return value
    if unit in ("cm2", "cm^2", "cm"):
        return value * 100.0
    if unit in ("m2", "m^2", "m"):
        return value * 1_000_000.0
    if unit in ("in2", "in^2", "in"):
        return value * 645.16
    if unit in ("ft2", "ft^2", "ft"):
        return value * 92_903.04
    raise ValueError(f"Unknown unit: {unit}")


def print_size_table():
    print("\nAvailable standard bar sizes:")
    print(f"{'#':<4}{'Dia (mm)':<12}{'Area (mm2)':<14}{'Area (in2)':<14}{'Weight (kg/m)':<15}")
    for i, d in enumerate(STANDARD_SIZES_MM, start=1):
        a = bar_area_mm2(d)
        print(f"{i:<4}{d:<12}{a:<14.2f}{mm2_to(a, 'in2'):<14.5f}{bar_weight_kg_per_m(d):<15.4f}")
    print("(Type the number, the mm value, or a custom diameter e.g. '18' or '0.75in')\n")


def parse_diameter(raw: str):
    """
    Accepts:
      - a menu index, e.g. '5'  -> maps to STANDARD_SIZES_MM[4]
      - a plain mm value, e.g. '18' or '18mm'
      - an inch value, e.g. '0.75in' or '3/4in'
    Returns diameter in mm, or None if it can't be parsed.
    """
    raw = raw.strip().lower()

    # menu index (only if it's a small int within the list length and not
    # also a plausible bar size typed directly, e.g. '10' should mean 10mm,
    # not option #10 -- so indices are only accepted with an explicit '#')
    if raw.startswith("#"):
        try:
            idx = int(raw[1:])
            if 1 <= idx <= len(STANDARD_SIZES_MM):
                return float(STANDARD_SIZES_MM[idx - 1])
        except ValueError:
            pass
        return None

    # inches, supports simple fractions like 3/4in
    if raw.endswith("in"):
        num = raw[:-2].strip()
        try:
            if "/" in num:
                n, d = num.split("/")
                inches = float(n) / float(d)
            else:
                inches = float(num)
            return inches * 25.4
        except (ValueError, ZeroDivisionError):
            return None

    # plain mm, with or without unit suffix
    if raw.endswith("mm"):
        raw = raw[:-2].strip()
    try:
        return float(raw)
    except ValueError:
        return None


def parse_area(raw: str):
    """
    Accepts a number with an optional unit suffix: mm2 (default), cm2,
    m2, in2, ft2 -- e.g. '850', '850mm2', '1.3in2', '0.08m2'.
    Returns the area converted to mm^2, or None if it can't be parsed.
    """
    raw = raw.strip().lower().replace(" ", "")
    for unit in ("mm2", "cm2", "m2", "in2", "ft2"):
        if raw.endswith(unit):
            num = raw[: -len(unit)]
            try:
                return to_mm2(float(num), unit)
            except ValueError:
                return None
    try:
        return float(raw)  # bare number -> assume mm^2
    except ValueError:
        return None


def main():
    print("=" * 70)
    print(" REBAR CALCULATOR -- number of bars needed for a required area")
    print(" (Standard Pakistani metric deformed bar sizes)")
    print("=" * 70)
    print_size_table()

    while True:
        dia_raw = input("Bar diameter (mm / e.g. '0.75in' / '#3' for menu item / 'list' / 'q'): ").strip()
        if dia_raw.lower() in QUIT_WORDS:
            print("Exiting. Stay safe on site!")
            sys.exit(0)
        if dia_raw.lower() == "list":
            print_size_table()
            continue

        dia_mm = parse_diameter(dia_raw)
        if dia_mm is None or dia_mm <= 0:
            print("  -> Couldn't understand that diameter, try again (e.g. '16', '16mm', '0.63in', '#5').\n")
            continue

        area_raw = input("Required steel area (mm2 default; or e.g. '1.2in2', '0.0008m2', 'q'): ").strip()
        if area_raw.lower() in QUIT_WORDS:
            print("Exiting. Stay safe on site!")
            sys.exit(0)

        area_required_mm2 = parse_area(area_raw)
        if area_required_mm2 is None or area_required_mm2 <= 0:
            print("  -> Couldn't understand that area, try again (e.g. '850', '850mm2', '1.3in2').\n")
            continue

        single_bar_area = bar_area_mm2(dia_mm)
        num_bars = math.ceil(area_required_mm2 / single_bar_area)
        area_provided_mm2 = num_bars * single_bar_area
        excess_mm2 = area_provided_mm2 - area_required_mm2
        excess_pct = (excess_mm2 / area_required_mm2) * 100.0

        print("\n" + "-" * 70)
        print(f" Bar diameter used         : {dia_mm:.2f} mm  ({dia_mm/25.4:.3f} in)")
        print(f" Area of ONE bar           : {single_bar_area:.2f} mm2  "
              f"({mm2_to(single_bar_area,'in2'):.5f} in2)")
        print(f" Required steel area (As)  : {area_required_mm2:.2f} mm2  "
              f"({mm2_to(area_required_mm2,'in2'):.5f} in2 / "
              f"{mm2_to(area_required_mm2,'cm2'):.3f} cm2)")
        print(f" >>> Number of bars needed : {num_bars}")
        print(f" Area actually provided    : {area_provided_mm2:.2f} mm2  "
              f"({mm2_to(area_provided_mm2,'in2'):.5f} in2)")
        print(f" Excess over required      : {excess_mm2:.2f} mm2  ({excess_pct:.1f}% over)")
        print("-" * 70)

        len_raw = input("Member length in m, for total steel weight (Enter to skip): ").strip()
        if len_raw and len_raw.lower() not in QUIT_WORDS:
            try:
                length_m = float(len_raw)
                total_weight = bar_weight_kg_per_m(dia_mm) * length_m * num_bars
                print(f" Total weight ({num_bars} bars x {length_m} m) : {total_weight:.2f} kg\n")
            except ValueError:
                print(" (Couldn't read that length, skipping weight calc.)\n")
        else:
            print()

        again = input("Run another calculation? (Enter = yes, 'q' = quit): ").strip().lower()
        if again in QUIT_WORDS:
            print("Exiting. Stay safe on site!")
            break
        print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Stay safe on site!")
