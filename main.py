import os
from datetime import date

import requests
from dotenv import load_dotenv

import re

load_dotenv()
API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")

COMPANY_URL = "https://api.company-information.service.gov.uk/company/{}"
POSTCODE_URL = "https://api.postcodes.io/postcodes/{}/validate"

# Statuses that mean the entity is valid
# ("open" = UK branch, "registered" = overseas entity)
VALID_STATUSES = ("active", "open", "registered")

# Entity types registered outside the UK (no UK postcode expected)
NON_UK_TYPES = ("oversea-company", "registered-overseas-entity")


def get_company(company_number):
    """Fetch company profile from Companies House. Returns None if not found."""
    r = requests.get(COMPANY_URL.format(company_number), auth=(API_KEY, ""), timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def is_valid_postcode(postcode):
    """Check whether a UK postcode is valid using postcodes.io."""
    r = requests.get(POSTCODE_URL.format(postcode), timeout=10)
    r.raise_for_status()
    return r.json()["result"]


def check_risks(company):
    """Apply risk rules to the company profile and return a list of flags."""
    risks = []

    # Rule 1: company is not active
    # ("open" is used for UK branches of overseas companies and also means trading)
    status = company.get("company_status", "unknown")
    if status not in VALID_STATUSES:
        risks.append(f"Company is not active (status: {status})")

    # Rule 2: incorporated less than 6 months ago
    created = company.get("date_of_creation")
    if created:
        age_days = (date.today() - date.fromisoformat(created)).days
        if age_days < 183:
            risks.append(f"Company incorporated less than 6 months ago ({age_days} days).")

    # Rule 3: missing or invalid registered office postcode
    # (skipped for non-UK entities, as their address is outside the UK)
    postcode = company.get("registered_office_address", {}).get("postal_code")
    is_overseas = company.get("type") in NON_UK_TYPES
    if not is_overseas:
        if not postcode:
            risks.append("No registered office postcode")
        elif not is_valid_postcode(postcode):
            risks.append(f"Invalid postcode: {postcode}")

    return risks


def main():
    number = normalise_company_number(input("Enter company number: "))
    if number is None:
        print("❌ Invalid company number format")
        return
    company = get_company(number)

    if company is None:
        print("❌ Company not found")
        return

    address = company.get("registered_office_address", {})
    print("\n===== Company Profile =====")
    print("Name:         ", company.get("company_name"))
    print("Number:       ", number)
    print("Status:       ", company.get("company_status", "-").replace("-", " ").capitalize())
    print("Incorporated: ", company.get("date_of_creation"))
    print("Postcode:     ", address.get("postal_code"))

    risks = check_risks(company)
    print("\n===== Risk Check =====")
    if risks:
        for risk in risks:
            print("⚠️ ", risk)
    else:
        print("✅ No risks found")


def normalise_company_number(raw):
    """Clean user input and return a valid company number, or None if invalid."""
    number = raw.replace(" ", "").upper()
    if number.isdigit():
        number = number.zfill(8)
    if not re.fullmatch(r"[A-Z0-9]{8}", number):
        return None
    return number


if __name__ == "__main__":
    main()