from flask import Flask, request, jsonify
import os
import json
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)

# Helper: round to 2 decimal places as Decimal
def money(val):
    return float(Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

# Load slabs from environment variable TAX_SLABS (JSON) or use default example slabs
# Format: list of slabs with keys: "lower", "upper" (null for no limit), "rate"
# lower is inclusive, upper is exclusive for calculation ease
DEFAULT_SLABS = [
    {"lower": 0, "upper": 250000, "rate": 0.0},
    {"lower": 250000, "upper": 500000, "rate": 5.0},
    {"lower": 500000, "upper": 750000, "rate": 10.0},
    {"lower": 750000, "upper": 1000000, "rate": 15.0},
    {"lower": 1000000, "upper": None, "rate": 20.0}
]

def load_slabs():
    raw = os.environ.get("TAX_SLABS")
    if not raw:
        return DEFAULT_SLABS
    try:
        slabs = json.loads(raw)
        # ensure sorted by lower bound
        slabs_sorted = sorted(slabs, key=lambda s: s.get("lower", 0))
        return slabs_sorted
    except Exception:
        return DEFAULT_SLABS

SLABS = load_slabs()
CESS_PERCENT = float(os.environ.get("CESS_PERCENT", "0.0"))  # e.g., 4.0
FIXED_SURCHARGE = float(os.environ.get("FIXED_SURCHARGE", "0.0"))

def calculate_tax(gross_salary: float, deductions: float = 0.0):
    if gross_salary < 0:
        raise ValueError("Gross salary must be non-negative")
    taxable_income = max(0.0, gross_salary - deductions)
    remaining = taxable_income
    tax = 0.0
    breakdown = []

    for slab in SLABS:
        lower = float(slab.get("lower", 0))
        upper = slab.get("upper")
        rate = float(slab.get("rate", 0.0))

        # determine slab capacity
        if upper is None:
            slab_capacity = max(0.0, remaining)  # remaining all taxed at this rate
        else:
            slab_capacity = max(0.0, upper - lower)

        amount_in_slab = min(remaining, slab_capacity)
        if amount_in_slab <= 0:
            # nothing in this slab; continue to next
            breakdown.append({
                "range": f"{int(lower)} - {int(upper) if upper else '∞'}",
                "amount": 0.0,
                "rate": rate,
                "tax": 0.0
            })
            continue

        tax_in_slab = (amount_in_slab * rate) / 100.0
        tax += tax_in_slab
        breakdown.append({
            "range": f"{int(lower)} - {int(upper) if upper else '∞'}",
            "amount": money(amount_in_slab),
            "rate": rate,
            "tax": money(tax_in_slab)
        })
        remaining -= amount_in_slab
        if remaining <= 0:
            # append zeros for remaining slabs for clarity
            continue

    cess_amount = (tax * CESS_PERCENT) / 100.0
    total_tax = tax + cess_amount + FIXED_SURCHARGE

    return {
        "gross_salary": money(gross_salary),
        "deductions": money(deductions),
        "taxable_income": money(taxable_income),
        "slab_breakdown": breakdown,
        "tax_before_cess": money(tax),
        "cess_percent": CESS_PERCENT,
        "cess_amount": money(cess_amount),
        "fixed_surcharge": money(FIXED_SURCHARGE),
        "total_tax": money(total_tax)
    }

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json(force=True)
    if data is None:
        return jsonify({"error":"JSON payload required"}), 400

    try:
        gross_salary = float(data.get("gross_salary", 0.0))
        deductions = float(data.get("deductions", 0.0))
    except (TypeError, ValueError):
        return jsonify({"error":"gross_salary and deductions must be numbers"}), 400

    try:
        result = calculate_tax(gross_salary, deductions)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error":"internal error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
