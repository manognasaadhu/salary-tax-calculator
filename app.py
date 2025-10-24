from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_tax(salary):
    # Example Indian tax slabs for FY 2025-26 (simplified)
    tax = 0
    if salary <= 250000:
        tax = 0
    elif salary <= 500000:
        tax = (salary - 250000) * 0.05
    elif salary <= 1000000:
        tax = 12500 + (salary - 500000) * 0.20
    else:
        tax = 112500 + (salary - 1000000) * 0.30
    return round(tax, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    tax = None
    salary = None
    if request.method == "POST":
        salary = float(request.form.get("salary", 0))
        tax = calculate_tax(salary)
    return render_template("index.html", tax=tax, salary=salary)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
