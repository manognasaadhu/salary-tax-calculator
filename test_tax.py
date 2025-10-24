import pytest
from app import calculate_tax

def test_zero_salary():
    out = calculate_tax(0, 0)
    assert out["total_tax"] == 0.0
    assert out["taxable_income"] == 0.0

def test_simple_salary():
    # using default slabs, 300000 gross, no deductions
    out = calculate_tax(300000, 0)
    # 0-250k => 0, 250k-300k => 50k @5% = 2500
    assert out["tax_before_cess"] == 2500.0

def test_with_deduction():
    out = calculate_tax(600000, 100000)
    # taxable = 500k -> slab: 0-250k 0, 250-500k 250k @5% => 12500
    assert out["tax_before_cess"] == 12500.0
