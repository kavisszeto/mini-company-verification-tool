from flask import Flask, render_template, request

from main import get_company, check_risks

from main import get_company, check_risks, normalise_company_number

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    number = company = risks = error = postcode = None

    if request.method == "POST":
        number = normalise_company_number(request.form["number"])
        if number is None:
            error = "❌ Invalid company number format. Please enter 8 letters or digits, e.g. 00445790 or SC123456."
        else:
            try:
                company = get_company(number)
                if company is None:
                    error = "❌ Company not found"
                else:
                    risks = check_risks(company)
                    postcode = company.get("registered_office_address", {}).get("postal_code")
            except Exception as e:
                error = f"API error: {e}"

    return render_template(
        "index.html", number=number, company=company, risks=risks, error=error, postcode=postcode
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)