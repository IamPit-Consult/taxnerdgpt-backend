def get_tax_analysis():
    """Collects detailed tax-related information from the user."""
    print("Welcome to the TaxNerdGPT Tax Analysis Questionnaire!")

    # Personal Information
    print("\nPersonal Information:")
    full_name = input("First & Last Name: ")
    cell = input("Cell Phone: ")
    email = input("Email Address: ")

    # Occupation
    print("\nOccupation:")
    occupation = input("What is your occupation, and how many years have you been employed there? ")

    # Income and Exemptions
    print("\nIncome and Exemptions:")
    annual_income = input("What is your annual income, and how many exemptions do you file on your W-4? ")

    # Dependents
    print("\nDependents:")
    dependents = input("Do you have children dependents, and if so, what are their ages? ")

    # Home Ownership
    print("\nHome Ownership:")
    home_ownership = input("Do you currently own or rent a home? ")
    renter_goal = input("If you are a renter, would you like to buy a home in 1 to 3 years from now? ")

    # Tax Filing History
    print("\nTax Filing History:")
    tax_history = input("Over the last 4 years of filing taxes, did you owe federal & state taxes, break even, or receive consistent refunds? ")

    # Side Gig Earnings
    print("\nSide Gig Earnings:")
    side_gig_earnings = input("Since tax year 2020, have you made extra money outside of your W-2 job from a cash-based side gig? If so, how much do/did you make monthly? ")

    # Business Ownership
    print("\nBusiness Ownership:")
    business_ownership = input("Are you an independent contractor, sole proprietor, or a small business owner? ")
    business_details = input("If you are a small business owner, is your business an LLC, INC, S-Corp, C-Corp, or a Non-Profit 501(c)(3) Tax Exempt? (Include the business entity name and date of incorporation.) ")

    # Cryptocurrency and Stocks
    print("\nCryptocurrency and Stocks:")
    crypto_activity = input("At any time in the prior calendar years (2020, 2021, 2022, 2023, & 2024), have you bought, sold, or traded any cryptocurrency, Bitcoin, or stocks? ")

    # Debts and Obligations
    print("\nDebts and Obligations:")
    debts = input("Do you owe any student loan debt, child support, EDD, traffic tickets, overpayment, or restitution? If so, how much do you owe? ")

    # Tax Advisor and Referrals
    print("\nTax Advisor and Referral Information:")
    tax_advisor = input("Name of Tax Advisor for Servicing: ")
    client_status = input("Are you a new customer or returning client? ")
    referral_source = input("How were you referred to us (name of person, social media, Billboard, or TaxNerd-wrapped car)? ")

    # Return collected data
    return {
        "Personal Information": {
            "Full Name": full_name,
            "Cell Phone": cell,
            "Email Address": email
        },
        "Occupation": {
            "Occupation": occupation
        },
        "Income and Exemptions": {
            "Annual Income": annual_income
        },
        "Dependents": {
            "Dependents": dependents
        },
        "Home Ownership": {
            "Home Ownership": home_ownership,
            "Renter Goal": renter_goal
        },
        "Tax Filing History": {
            "Tax History": tax_history
        },
        "Side Gig Earnings": {
            "Side Gig Earnings": side_gig_earnings
        },
        "Business Ownership": {
            "Business Ownership": business_ownership,
            "Business Details": business_details
        },
        "Cryptocurrency and Stocks": {
            "Crypto Activity": crypto_activity
        },
        "Debts and Obligations": {
            "Debts": debts
        },
        "Tax Advisor and Referral Information": {
            "Tax Advisor": tax_advisor,
            "Client Status": client_status,
            "Referral Source": referral_source
        }
    }

def display_tax_analysis(data):
    """Displays the collected tax analysis data."""
    print("\nTax Analysis Results:")
    for category, details in data.items():
        print(f"\n{category}:")
        for key, value in details.items():
            print(f"  - {key}: {value}")