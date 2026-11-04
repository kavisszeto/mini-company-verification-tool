import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")

# Test 1：Companies House（00445790 is Tesco PLC's company number）
r = requests.get(
    "https://api.company-information.service.gov.uk/company/00445790",
    auth=(API_KEY, ""),
)
print("Companies House:", r.status_code)
if r.ok:
    data = r.json()
    print(data["company_name"], "|", data["company_status"], "|", data["date_of_creation"])

# Test 2：postcodes.io（key is not required）
r2 = requests.get("https://api.postcodes.io/postcodes/SW1A1AA/validate")
print("Postcode valid:", r2.json()["result"])