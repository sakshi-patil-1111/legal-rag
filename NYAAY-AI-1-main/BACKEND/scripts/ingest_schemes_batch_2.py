import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.knowledge.ingestion import ingestion_pipeline
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

schemes = [
    {
        "metadata": {
            "scheme_name": "Mahatma Gandhi National Rural Employment Guarantee Act",
            "scheme_id": "MGNREGA",
            "ministry": "Ministry of Rural Development",
            "department": "Department of Rural Development",
            "implementing_authority": "Gram Panchayats",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Rural Employment",
            "section_type": "Welfare",
            "source_url": "https://nrega.nic.in/",
            "source_domain": "nrega.nic.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2005-08-25",
            "update_date": "2024-01-01",
            "effective_date": "2006-02-02",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Rural Household",
            "residency": "Rural",
            "benefit_type": "Employment / Wages"
        },
        "text": """
# Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)

## Objective
To enhance livelihood security in rural areas by providing at least 100 days of guaranteed wage employment in a financial year to every rural household whose adult members volunteer to do unskilled manual work.

## Eligibility
- Must be a citizen of India residing in a rural area.
- Must be 18 years of age or older.
- Must be willing to do unskilled manual work.
- The applicant must be part of a local household in the Gram Panchayat.

## Exclusions
- Individuals residing in urban areas are not eligible.
- Individuals unwilling to do manual unskilled work.
- Employment is capped at 100 days per household per financial year (with exceptions for drought-notified areas or forest rights act beneficiaries which may get 150 days).

## Benefits
- Guaranteed 100 days of wage employment per financial year per household.
- Wages are paid according to the statutory minimum wages for agricultural labourers in the state.
- If employment is not provided within 15 days of application, a daily unemployment allowance must be paid.
- Worksite facilities such as drinking water, shade, and first aid are provided.
- Equal wages for men and women.

## Required Documents
- Aadhaar Card (mandatory for wage payment linking).
- Bank/Post Office Account Details.
- Ration Card / Voter ID / Proof of residence for household identification.

## Application Process
- Registration at the local Gram Panchayat.
- The Gram Panchayat issues a Job Card to the household.
- The job card holder submits a written request for work (for at least 14 days of continuous work) to the Gram Panchayat or Block Office.
"""
    },
    {
        "metadata": {
            "scheme_name": "National Food Security Act / Public Distribution System",
            "scheme_id": "NFSA-PDS",
            "ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
            "department": "Department of Food and Public Distribution",
            "implementing_authority": "State Governments",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Food Security",
            "section_type": "Welfare",
            "source_url": "https://nfsa.gov.in/",
            "source_domain": "nfsa.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2013-07-05",
            "update_date": "2024-01-01",
            "effective_date": "2013-07-05",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Poor Households",
            "benefit_type": "Subsidized Food Grains"
        },
        "text": """
# National Food Security Act (NFSA) / Public Distribution System (PDS)

## Objective
To provide for food and nutritional security in human life cycle approach, by ensuring access to adequate quantity of quality food at affordable prices.

## Eligibility
Coverage under NFSA is categorized into two groups:
1. **Antyodaya Anna Yojana (AAY) households**: The poorest of the poor households as identified by the State Government.
2. **Priority Households (PHH)**: Households identified by State Governments as per their specific socio-economic criteria.

General criteria utilized by states for PHH include:
- Landless agricultural laborers, marginal farmers, rural artisans, and informal sector workers in urban areas.
- Households with destitute, widows, terminally ill persons, or disabled persons.
- BPL (Below Poverty Line) families.

## Exclusions
- Families paying income tax.
- Families with regular government employees.
- Families owning a specified extent of irrigated land or motorized vehicles (criteria vary slightly by State).

## Benefits
- **Priority Households (PHH)**: 5 kg of foodgrains per person per month at subsidized prices (often free under PMGKAY currently).
- **AAY Households**: 35 kg of foodgrains per household per month at subsidized prices/free.
- Nutritional support for pregnant women and lactating mothers (Maternity Benefit).
- Nutritional support for children aged 6 months to 14 years through Anganwadis and Mid-Day Meals.

## Required Documents
- Aadhaar Card of family members.
- Income Certificate.
- Address Proof (Electricity bill, etc.).
- Caste/Category certificate (if applicable).

## Application Process
- Apply for a Ration Card at the local Food and Civil Supplies Office or online via the State's specific PDS portal.
- After field verification, an AAY or PHH Ration Card is issued.
- Beneficiaries collect rations using biometric authentication (ePoS) at Fair Price Shops.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Matru Vandana Yojana",
            "scheme_id": "PMMVY",
            "ministry": "Ministry of Women and Child Development",
            "department": "Department of Women and Child Development",
            "implementing_authority": "State Governments / UTs",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Maternity",
            "section_type": "Welfare",
            "source_url": "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana",
            "source_domain": "wcd.nic.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2017-01-01",
            "update_date": "2024-01-01",
            "effective_date": "2017-01-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 19,
            "age_max": None,
            "income_limit": 800000,
            "beneficiary_type": "Pregnant Women",
            "gender": "Female",
            "benefit_type": "Cash Assistance"
        },
        "text": """
# Pradhan Mantri Matru Vandana Yojana (PMMVY)

## Objective
A maternity benefit program to provide partial compensation for the wage loss in terms of cash incentives so that the woman can take adequate rest before and after delivery of the first child, and to improve health-seeking behaviour amongst Pregnant Women and Lactating Mothers (PW&LM).

## Eligibility
- Pregnant Women and Lactating Mothers (PW&LM) who are socially or economically disadvantaged.
- The applicant must be at least 19 years old.
- The benefit is available for the first living child in the family.
- Extended to the second child only if the second child is a girl.
- Beneficiary must belong to categories like SC/ST, BPL, E-Shram card holders, PMJAY beneficiaries, MGNREGA job card holders, Kisan Samman Nidhi beneficiaries, women with family income < 8 Lakhs, divyang women (40% disabled), or Anganwadi workers.

## Exclusions
- PW&LM who are in regular employment with the Central Government or State Governments or Public Sector Undertakings (PSUs) or those who are in receipt of similar benefits under any law for the time being in force.

## Benefits
- **First Child**: Total cash incentive of ₹5,000 paid in two installments:
  - 1st Installment (₹3,000): On registration of pregnancy and at least one Antenatal Check-up (ANC).
  - 2nd Installment (₹2,000): After childbirth registration and child receiving the first cycle of BCG, OPV, DPT, and Hepatitis-B, or equivalent substitute.
- **Second Child (if a girl)**: ₹6,000 paid in a single installment after birth and immunization.
- Payments are credited directly into the Aadhaar linked bank/post office account (DBT).

## Required Documents
- Aadhaar Card of the beneficiary.
- MCP (Mother and Child Protection) Card.
- Bank or Post Office Account details.
- Proof of belonging to eligible category (e.g., E-Shram card, BPL card, income certificate).

## Application Process
- Beneficiaries can apply online on the PMMVY portal (pmmvy.nic.in) or offline at an Anganwadi Centre (AWC) or approved Health facility.
"""
    },
    {
        "metadata": {
            "scheme_name": "National Social Assistance Programme",
            "scheme_id": "NSAP",
            "ministry": "Ministry of Rural Development",
            "department": "Department of Rural Development",
            "implementing_authority": "State Governments",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Social Security",
            "section_type": "Welfare",
            "source_url": "https://nsap.nic.in/",
            "source_domain": "nsap.nic.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "1995-08-15",
            "update_date": "2024-01-01",
            "effective_date": "1995-08-15",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "BPL, Elderly, Widows, Disabled",
            "benefit_type": "Pension"
        },
        "text": """
# National Social Assistance Programme (NSAP)

## Objective
To provide social assistance to the destitute, elderly, widows, and persons with disabilities from below poverty line (BPL) families. NSAP encompasses several sub-schemes including IGNOAPS, IGNWPS, IGNDPS, NFBS, and Annapurna.

## Eligibility (General for NSAP)
- The applicant must belong to a Below Poverty Line (BPL) household as per criteria prescribed by the Government of India.
- Must fall into a vulnerable category: elderly (60+), widow (40+), disabled (18+, 80% disability), or facing death of the primary breadwinner.
- For National Family Benefit Scheme (NFBS): Death of the primary breadwinner (aged 18-59) of a BPL family.
- For Annapurna Scheme: Destitute senior citizens (65+) who are eligible for IGNOAPS but are not receiving the pension.

## Exclusions
- Families above the poverty line (APL).
- Individuals receiving other state/central pensions for the same purpose.

## Benefits
- Differs by sub-scheme (e.g., Old Age Pension, Widow Pension).
- NFBS provides a lump sum assistance of ₹20,000 to the bereaved household on the death of the primary breadwinner.
- Annapurna Scheme provides 10 kg of food grains per month free of cost.
- States usually top-up the central assistance with their own contributions.

## Required Documents
- BPL Ration Card / SECC Data proof.
- Aadhaar Card.
- Bank/Post Office Account Details.
- Death certificate of husband (for IGNWPS).
- Disability certificate (for IGNDPS).
- Death certificate of primary breadwinner (for NFBS).

## Application Process
- Applications are submitted to the Gram Panchayat / Block Development Office / Municipal office.
- States also provide online application portals through e-District platforms.
"""
    },
    {
        "metadata": {
            "scheme_name": "Indira Gandhi National Old Age Pension Scheme",
            "scheme_id": "IGNOAPS",
            "ministry": "Ministry of Rural Development",
            "department": "Department of Rural Development",
            "implementing_authority": "State Governments",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Senior Citizens",
            "section_type": "Pension",
            "source_url": "https://nsap.nic.in/",
            "source_domain": "nsap.nic.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2007-11-19",
            "update_date": "2024-01-01",
            "effective_date": "2007-11-19",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 60,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "BPL Senior Citizens",
            "benefit_type": "Pension"
        },
        "text": """
# Indira Gandhi National Old Age Pension Scheme (IGNOAPS)

## Objective
To provide financial assistance and social security to elderly persons living below the poverty line.

## Eligibility
- The applicant must be 60 years of age or older.
- The applicant must belong to a Below Poverty Line (BPL) household according to the criteria prescribed by the Government of India.
- Destitute elders without regular means of subsistence from their own source of income or through financial support from family members.

## Exclusions
- Persons below 60 years of age.
- Individuals who do not belong to a BPL household.
- Persons receiving regular pensions from government employment or other sources.

## Benefits
- For persons between 60 and 79 years: Central assistance of ₹200 per month.
- For persons aged 80 years and above: Central assistance of ₹500 per month.
- State Governments typically add their own contribution to this amount, meaning beneficiaries receive a higher total amount (e.g., ₹1000 to ₹3000 depending on the state).

## Required Documents
- Proof of Age (Birth certificate, Aadhaar card, Voter ID, School leaving certificate).
- BPL Certificate or Ration Card.
- Passport size photographs.
- Bank or Post Office account passbook.

## Application Process
- The eligible person needs to apply using the prescribed form at the Block Development Office (BDO) in rural areas or Executive Officer of Municipality in urban areas.
- Online applications are available through various State Government portals or the UMANG app.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Awas Yojana - Urban",
            "scheme_id": "PMAY-U",
            "ministry": "Ministry of Housing and Urban Affairs",
            "department": "MoHUA",
            "implementing_authority": "MoHUA / State Nodal Agencies",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Urban Housing",
            "section_type": "Welfare",
            "source_url": "https://pmaymis.gov.in/",
            "source_domain": "pmaymis.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2015-06-25",
            "update_date": "2024-01-01",
            "effective_date": "2015-06-25",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": 1800000,
            "beneficiary_type": "Urban Poor / Middle Class",
            "residency": "Urban",
            "benefit_type": "Housing Subsidy"
        },
        "text": """
# Pradhan Mantri Awas Yojana - Urban (PMAY-U)

## Objective
To provide "Housing for All" in urban areas by providing central assistance to implementing agencies through States/Union Territories for providing houses to all eligible families/beneficiaries.

## Eligibility
- The beneficiary family should not own a pucca house in their name or in the name of any family member anywhere in India.
- The beneficiary family must reside in an urban area (statutory town).
- The scheme is available to EWS (Economically Weaker Section), LIG (Low Income Group), and MIG (Middle Income Group).
- **Income Criteria:**
  - EWS: Annual household income up to ₹3,00,000.
  - LIG: Annual household income from ₹3,00,001 to ₹6,00,000.
  - MIG I: Annual household income from ₹6,00,001 to ₹12,00,000.
  - MIG II: Annual household income from ₹12,00,001 to ₹18,00,000.
- For EWS and LIG categories, female ownership or co-ownership of the house is mandatory (except when there is no adult female in the family).

## Exclusions
- Families owning a pucca house anywhere in India.
- Families who have previously availed central assistance under any housing scheme from the Government of India.
- Families whose income exceeds ₹18,00,000 annually.

## Benefits
- **Credit Linked Subsidy Scheme (CLSS)**: Interest subsidy on home loans (up to 6.5% for EWS/LIG, 4% for MIG-I, 3% for MIG-II).
- **In-Situ Slum Redevelopment (ISSR)**: Central assistance of ₹1 lakh per house for eligible slum dwellers.
- **Affordable Housing in Partnership (AHP)**: Central assistance of ₹1.5 lakh per EWS house.
- **Beneficiary-led Construction/Enhancement (BLC)**: Central assistance of ₹1.5 lakh per EWS house for construction on their own land.

## Required Documents
- Aadhaar Card (mandatory).
- PAN Card / Voter ID.
- Income Proof (Form 16, ITR, Salary Slips, or Affidavit for EWS/LIG).
- Property documents (for BLC or CLSS).
- Bank account details.

## Application Process
- Applicants can apply online at the PMAY-U web portal (pmaymis.gov.in) or offline at Common Service Centers (CSCs) / Urban Local Bodies (ULBs).
- For CLSS, individuals apply directly to the banks or housing finance companies for the loan.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Kaushal Vikas Yojana",
            "scheme_id": "PMKVY",
            "ministry": "Ministry of Skill Development and Entrepreneurship",
            "department": "MSDE",
            "implementing_authority": "National Skill Development Corporation (NSDC)",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Skill Development",
            "section_type": "Employment",
            "source_url": "https://www.pmkvyofficial.org/",
            "source_domain": "pmkvyofficial.org",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2015-07-15",
            "update_date": "2024-01-01",
            "effective_date": "2015-07-15",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 15,
            "age_max": 45,
            "income_limit": None,
            "beneficiary_type": "Youth",
            "occupation": "Unemployed / School Dropout",
            "benefit_type": "Training / Certification"
        },
        "text": """
# Pradhan Mantri Kaushal Vikas Yojana (PMKVY)

## Objective
To enable Indian youth to take up industry-relevant skill training that will help them in securing a better livelihood. Individuals with prior learning experience or skills are also assessed and certified under Recognition of Prior Learning (RPL).

## Eligibility
- The candidate must be an Indian national.
- The scheme is applicable to any candidate of working age (generally between 15-45 years of age).
- Target audience: Unemployed youth, school/college dropouts.
- Applicant must possess an Aadhaar card and a bank account.
- For RPL (Recognition of Prior Learning): Individuals with prior experience in the relevant trade.

## Exclusions
- Individuals who are currently enrolled in formal schooling or regular college education (except where specified short-term training is allowed).
- Candidates who have already obtained a PMKVY certificate for the same job role.

## Benefits
- **Short Term Training (STT)**: Free of cost training at PMKVY Training Centres (TCs) covering soft skills, entrepreneurship, financial and digital literacy.
- **Recognition of Prior Learning (RPL)**: Assessment and certification of existing skills, giving them a formal qualification.
- Free training and assessment.
- Reward money (in previous versions, now replaced by direct placement assistance and free certification).
- Insurance coverage (Rozgar Mela participation and accident insurance for RPL candidates).
- Placement assistance upon successful completion of training.

## Required Documents
- Aadhaar Card.
- Two passport-size photographs.
- Bank Account Passbook.
- Proof of education (if applicable for specific job roles).

## Application Process
- Candidates can find a nearby Training Centre through the Skill India Digital portal or PMKVY website (pmkvyofficial.org).
- Enroll at the training centre by submitting required documents.
- Training is free, and after completion, an assessment is conducted to issue the certificate.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana",
            "scheme_id": "PMFBY",
            "ministry": "Ministry of Agriculture and Farmers Welfare",
            "department": "Department of Agriculture and Farmers Welfare",
            "implementing_authority": "Empaneled General Insurance Companies",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Agriculture",
            "section_type": "Insurance",
            "source_url": "https://pmfby.gov.in/",
            "source_domain": "pmfby.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2016-02-18",
            "update_date": "2024-01-01",
            "effective_date": "2016-04-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Farmers",
            "occupation": "Farmer",
            "benefit_type": "Crop Insurance"
        },
        "text": """
# Pradhan Mantri Fasal Bima Yojana (PMFBY)

## Objective
To provide comprehensive insurance cover against failure of the crop, thus helping in stabilizing the income of farmers. The scheme covers all food & oilseed crops and annual commercial/horticultural crops for which past yield data is available.

## Eligibility
- All farmers growing notified crops in a notified area during the season who have an insurable interest in the crop are eligible.
- Both loanee farmers (those who have taken agricultural loans/KCC) and non-loanee farmers (those growing crops without bank credit) can participate. Enrollment is voluntary for all farmers.
- Tenant farmers and sharecroppers are also eligible.

## Exclusions
- Damage to harvested crop kept in the field after a specified number of days (usually 14 days) post-harvest.
- Wilful damage, theft, or localized damage not covered under the specified localized calamities.
- Crops not notified by the State Government for that specific region.

## Benefits
- Comprehensive risk cover from pre-sowing to post-harvest losses.
- Farmers pay a highly subsidized, uniform premium:
  - Kharif crops: Maximum 2% of the sum insured.
  - Rabi crops: Maximum 1.5% of the sum insured.
  - Annual Commercial/Horticultural crops: Maximum 5% of the sum insured.
- The balance premium is paid by the Government (shared equally by Central and State Governments) to provide full insured amount to farmers against crop loss.
- Uses technology like drones and smartphones for faster assessment of crop loss and claim settlement.

## Required Documents
- Aadhaar Card.
- Land records (Pattadar passbook, Khasra/Khatauni).
- Sowing certificate or crop declaration.
- Bank account details.
- Tenancy agreement (for tenant farmers/sharecroppers).

## Application Process
- Farmers can apply online at the National Crop Insurance Portal (pmfby.gov.in).
- Offline applications can be submitted through bank branches, Common Service Centres (CSCs), Primary Agricultural Credit Societies (PACS), or insurance brokers.
- Loanee farmers can be automatically covered by their bank if they do not opt out.
"""
    }
]

# Add more schemes
schemes.extend([
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Jan Dhan Yojana",
            "scheme_id": "PMJDY",
            "ministry": "Ministry of Finance",
            "department": "Department of Financial Services",
            "implementing_authority": "Public and Private Sector Banks",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Financial Inclusion",
            "section_type": "Banking",
            "source_url": "https://pmjdy.gov.in/",
            "source_domain": "pmjdy.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2014-08-28",
            "update_date": "2024-01-01",
            "effective_date": "2014-08-28",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 10,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Unbanked Citizens",
            "benefit_type": "Bank Account"
        },
        "text": """
# Pradhan Mantri Jan Dhan Yojana (PMJDY)

## Objective
To ensure comprehensive financial inclusion of all the households in the country by providing universal access to banking facilities with at least one basic banking account for every unbanked adult.

## Eligibility
- Any Indian citizen can open a PMJDY account.
- Minors above the age of 10 years can also open a PMJDY account.
- Must not already have any other Savings Bank account (or must close it within 30 days of opening PMJDY).
- There is no minimum income requirement.

## Exclusions
- Individuals holding an active regular savings bank account in any bank.

## Benefits
- Zero balance basic savings bank deposit (BSBD) account.
- No minimum balance maintenance required.
- Free RuPay debit card provided.
- In-built accident insurance cover of ₹2 lakh (₹1 lakh for accounts opened before 28.08.2018) with the RuPay card (requires at least one successful financial or non-financial transaction within 90 days prior to the accident).
- Overdraft facility up to ₹10,000 available to one account per household (preferably the female member) after 6 months of satisfactory operation.
- Access to Direct Benefit Transfers (DBT) from government schemes.

## Required Documents
- Aadhaar Card (If Aadhaar is present, no other document is required).
- If Aadhaar is not available, any officially valid document (OVD) like Voter ID, Driving License, PAN card, Passport, or NREGA card.
- Two passport-sized photographs.

## Application Process
- Application forms are available at all bank branches and Bank Mitras (Business Correspondents).
- The account can be opened on the spot using e-KYC.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
            "scheme_id": "PMJJBY",
            "ministry": "Ministry of Finance",
            "department": "Department of Financial Services",
            "implementing_authority": "LIC and other Life Insurance Companies",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Insurance",
            "section_type": "Life Insurance",
            "source_url": "https://jansuraksha.gov.in/",
            "source_domain": "jansuraksha.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2015-05-09",
            "update_date": "2024-01-01",
            "effective_date": "2015-05-09",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": 50,
            "income_limit": None,
            "beneficiary_type": "Citizens",
            "benefit_type": "Life Insurance"
        },
        "text": """
# Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)

## Objective
To provide life insurance cover to all sections of society, especially the poor and underprivileged, at a highly affordable premium.

## Eligibility
- Any individual possessing a savings bank account or a post office savings bank account.
- Age between 18 to 50 years.
- The applicant must give consent to join and enable auto-debit of the premium from their account.
- The life cover continues up to the age of 55 years provided the individual continues to pay the premium.
- An individual can enroll through only one bank account, even if they have multiple accounts.

## Exclusions
- Individuals below 18 or above 50 years for new enrollment.
- If a person has enrolled through multiple bank accounts, the claim will only be paid once, and the extra premium is forfeited.
- Suicide is not covered during the first 30 days of enrollment (lien period). Death due to any reason within 30 days of enrollment is not covered (except accident).

## Benefits
- Life cover of ₹2,00,000 (Two Lakh Rupees) payable to the nominee upon the death of the insured due to any cause.
- Annual premium is ₹436 (auto-debited from the bank account).
- Coverage period is from 1st June to 31st May of the subsequent year.

## Required Documents
- Savings Bank Account details.
- Aadhaar Card (primary KYC).
- Consent-cum-declaration form for auto-debit.

## Application Process
- Visit the bank branch or post office where the savings account is held.
- Fill the PMJJBY enrollment form and submit it.
- Can also be enrolled online via net banking or mobile banking apps of participating banks.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Suraksha Bima Yojana",
            "scheme_id": "PMSBY",
            "ministry": "Ministry of Finance",
            "department": "Department of Financial Services",
            "implementing_authority": "General Insurance Companies",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Insurance",
            "section_type": "Accident Insurance",
            "source_url": "https://jansuraksha.gov.in/",
            "source_domain": "jansuraksha.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2015-05-09",
            "update_date": "2024-01-01",
            "effective_date": "2015-05-09",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": 70,
            "income_limit": None,
            "beneficiary_type": "Citizens",
            "benefit_type": "Accident Insurance"
        },
        "text": """
# Pradhan Mantri Suraksha Bima Yojana (PMSBY)

## Objective
To provide accidental death and disability insurance cover to the people of India at a highly affordable premium.

## Eligibility
- Any individual with a savings bank account or a post office savings bank account.
- Age between 18 to 70 years.
- Consent for auto-debit of the premium must be provided.
- An individual can join the scheme through only one bank account.

## Exclusions
- Individuals below 18 or above 70 years.
- Death or disability due to natural causes, disease, or suicide is NOT covered. Only accidental death or disability is covered.
- Multiple enrollments across different banks will result in a single claim payout and forfeiture of excess premiums.

## Benefits
- Accidental Death: ₹2,00,000 to the nominee.
- Total and irrecoverable loss of both eyes or loss of use of both hands or feet or loss of sight of one eye and loss of use of hand or foot: ₹2,00,000.
- Total and irrecoverable loss of sight of one eye or loss of use of one hand or foot: ₹1,00,000.
- Annual premium is just ₹20 per annum, auto-debited.
- Coverage is from 1st June to 31st May.

## Required Documents
- Savings Bank Account.
- Aadhaar Card.
- Auto-debit consent form.

## Application Process
- Apply at the bank branch / post office where the account is maintained.
- Submit the consent form.
- Enrollment can also be done via internet banking or SMS.
"""
    },
    {
        "metadata": {
            "scheme_name": "Prime Minister's Employment Generation Programme",
            "scheme_id": "PMEGP",
            "ministry": "Ministry of Micro, Small and Medium Enterprises",
            "department": "MSME",
            "implementing_authority": "KVIC / KVIB / DIC",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Entrepreneurship",
            "section_type": "Loan",
            "source_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
            "source_domain": "kviconline.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2008-08-15",
            "update_date": "2024-01-01",
            "effective_date": "2008-08-15",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Entrepreneurs",
            "benefit_type": "Loan and Subsidy"
        },
        "text": """
# Prime Minister's Employment Generation Programme (PMEGP)

## Objective
To generate employment opportunities in rural as well as urban areas of the country through setting up of new self-employment ventures/projects/micro enterprises.

## Eligibility
- Any individual above 18 years of age.
- At least VIII standard pass for projects costing above ₹10 lakh in the manufacturing sector and above ₹5 lakh in the business/service sector.
- Only new projects are considered for sanction under PMEGP.
- Self Help Groups (including those belonging to BPL provided that they have not availed benefits under any other Scheme).
- Institutions registered under Societies Registration Act, Production Co-operative Societies, and Charitable Trusts.

## Exclusions
- Existing Units (under PMRY, REGP or any other scheme of Government of India or State Government) are not eligible.
- Units that have already availed Government Subsidy under any other scheme are not eligible.

## Benefits
- Bank loan for setting up micro-enterprises.
- Maximum project cost: ₹50 lakh in the manufacturing sector and ₹20 lakh in the business/service sector.
- **Margin Money Subsidy**:
  - General Category: 15% (Urban) or 25% (Rural) of project cost. Beneficiary contribution is 10%.
  - Special Category (SC/ST/OBC/Minorities/Women, Ex-servicemen, Physically handicapped, NER, Hill and Border areas): 25% (Urban) or 35% (Rural) of project cost. Beneficiary contribution is 5%.
- EDP (Entrepreneurship Development Programme) training is provided.

## Required Documents
- Aadhaar Card / PAN Card.
- Project Report (Business Plan).
- Passport Size Photos.
- Special Category Certificate (Caste certificate, Disability certificate, Ex-servicemen certificate).
- Rural Area certificate (if applicable).
- Education/Skill Development training certificate (if applicable).

## Application Process
- Apply online at the PMEGP e-Portal (kviconline.gov.in).
- The application is scrutinized by the District Level Task Force Committee (DLTFC) and forwarded to banks.
- Bank appraises the project and sanctions the loan. After EDP training, the first installment is released and the margin money subsidy is claimed from KVIC.
"""
    },
    {
        "metadata": {
            "scheme_name": "Jal Jeevan Mission",
            "scheme_id": "JJM",
            "ministry": "Ministry of Jal Shakti",
            "department": "Department of Drinking Water and Sanitation",
            "implementing_authority": "Village Water and Sanitation Committee",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Rural Development",
            "section_type": "Infrastructure",
            "source_url": "https://jaljeevanmission.gov.in/",
            "source_domain": "jaljeevanmission.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2019-08-15",
            "update_date": "2024-01-01",
            "effective_date": "2019-08-15",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Rural Household",
            "residency": "Rural",
            "benefit_type": "Water Connection"
        },
        "text": """
# Jal Jeevan Mission (JJM)

## Objective
To provide safe and adequate drinking water through individual household tap connections (Functional Household Tap Connection - FHTC) by 2024 to all households in rural India.

## Eligibility
- Any rural household in India that currently lacks a functional household tap connection.
- Schools, Anganwadi centres, Gram Panchayat buildings, health centres, wellness centres, and community buildings in rural areas.

## Exclusions
- Urban households (which are covered under AMRUT/JJM-Urban).
- Households that already have a functional, adequate, and safe tap connection.

## Benefits
- Provision of a Functional Household Tap Connection (FHTC) providing 55 litres per capita per day (lpcd) of prescribed quality drinking water on a regular and long-term basis.
- Involves greywater management and water conservation at the village level.
- 100% funding by government (Central and State share) for laying the infrastructure, though community contribution (in cash/kind/labour, usually 5-10%) may be required for in-village infrastructure ownership.

## Required Documents
- Generally, no individual documents are required to apply, as it is a saturation scheme driven at the village level.
- Village Action Plan (VAP) is required from the Gram Panchayat.

## Application Process
- The scheme is implemented by the Village Water and Sanitation Committee (VWSC) or Pani Samiti at the village level.
- An individual rural household without a tap can demand connection through their Gram Panchayat or Pani Samiti.
- There is no direct online application for individual households; implementation is community-based.
"""
    },
    {
        "metadata": {
            "scheme_name": "Swachh Bharat Mission",
            "scheme_id": "SBM",
            "ministry": "Ministry of Drinking Water and Sanitation / MoHUA",
            "department": "Department of Drinking Water and Sanitation",
            "implementing_authority": "Gram Panchayats / Urban Local Bodies",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Sanitation",
            "section_type": "Welfare",
            "source_url": "https://swachhbharatmission.gov.in/",
            "source_domain": "swachhbharatmission.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2014-10-02",
            "update_date": "2024-01-01",
            "effective_date": "2014-10-02",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "BPL and eligible APL Households",
            "benefit_type": "Sanitation Subsidy"
        },
        "text": """
# Swachh Bharat Mission (Gramin and Urban)

## Objective
To accelerate the efforts to achieve universal sanitation coverage, eradicate open defecation, and implement solid and liquid waste management.

## Eligibility
- **Gramin (Rural)**: BPL households, and identified APL households restricted to SC/STs, small and marginal farmers, landless labourers with homestead, physically handicapped, and women-headed households.
- **Urban**: Urban households lacking individual household toilets, and communities lacking public toilets. EWS/LIG populations are prioritized.
- The household must not have availed benefits for toilet construction under any other government scheme.

## Exclusions
- APL (Above Poverty Line) households in rural areas that do not fall into the specified vulnerable categories (they are motivated to build toilets with their own funds).
- Households that already possess a functional toilet.

## Benefits
- Financial incentive of ₹12,000 for the construction of an Individual Household Latrine (IHHL) for eligible rural households (includes water storage facility).
- In Urban areas, central incentive of ₹4,000 for IHHL (State adds varying amounts, typically making it ₹12,000 to ₹20,000).
- Construction of Community Sanitary Complexes (CSCs).

## Required Documents
- Aadhaar Card.
- Bank Account Details.
- BPL Card or Proof of belonging to eligible APL categories (SC/ST certificate, Disability certificate).
- Photograph of the beneficiary.

## Application Process
- **Rural**: Apply through the Gram Panchayat or online at the SBM-G portal. Upon verification, the incentive is released in two installments directly to the bank account upon uploading geo-tagged photos of the construction stages.
- **Urban**: Apply online at the SBM-Urban portal or via the Urban Local Body (ULB)/Municipality.
"""
    },
    {
        "metadata": {
            "scheme_name": "Unique Disability ID",
            "scheme_id": "UDID",
            "ministry": "Ministry of Social Justice and Empowerment",
            "department": "Department of Empowerment of Persons with Disabilities",
            "implementing_authority": "Government of India",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Disability Welfare",
            "section_type": "Welfare",
            "source_url": "https://www.swavlambancard.gov.in/",
            "source_domain": "swavlambancard.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2016-01-01",
            "update_date": "2024-01-01",
            "effective_date": "2016-01-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Persons with Disabilities",
            "benefit_type": "Identity and Benefits"
        },
        "text": """
# Unique Disability ID (UDID)

## Objective
To create a National Database for Persons with Disabilities (PwDs), and to issue a Unique Disability Identity Card to each person with disabilities. The project will not only encourage transparency, efficiency, and ease of delivering the government benefits to the person with disabilities, but also ensure uniformity.

## Eligibility
- Any Indian citizen suffering from a disability as recognized under the Rights of Persons with Disabilities Act, 2016.
- The 21 recognized disabilities include Blindness, Low-vision, Leprosy Cured persons, Hearing Impairment (deaf and hard of hearing), Locomotor Disability, Dwarfism, Intellectual Disability, Mental Illness, Autism Spectrum Disorder, Cerebral Palsy, Muscular Dystrophy, Chronic Neurological conditions, Specific Learning Disabilities, Multiple Sclerosis, Speech and Language disability, Thalassemia, Hemophilia, Sickle Cell disease, Multiple Disabilities including deaf-blindness, Acid Attack victim, and Parkinson's disease.

## Exclusions
- Persons who do not have a formally diagnosed disability as per the RPwD Act 2016 parameters.

## Benefits
- Single document of identification and verification of disability for availing various government benefits.
- It negates the need for making multiple copies of documents, as the card captures all necessary details decoded by a reader.
- It helps PwDs in availing reservations in education and government jobs.
- Availing free/concessional travel on state buses and railways.
- Availing scholarships, aids and appliances under ADIP scheme, and disability pensions.

## Required Documents
- Recent Color Photograph.
- Signature / Thumb Impression.
- Address Proof (Aadhaar, Voter ID, Domicile certificate).
- Identity Proof (Aadhaar, PAN).
- Disability Certificate issued by a competent medical authority (if already available; if not, the applicant is assessed by the medical board after applying).

## Application Process
- Register online at the Swavlamban Card portal (swavlambancard.gov.in).
- Fill in personal, disability, employment, and identity details.
- Upload required documents.
- An application number is generated. The applicant has to visit the Chief Medical Officer (CMO) / Medical Board of the district for an assessment of the disability percentage.
- Once assessed and approved, the UDID card is generated and mailed to the address.
"""
    }
])

def main():
    logger.info(f"Starting batch 2 ingestion of {len(schemes)} government schemes...")
    
    success_count = 0
    fail_count = 0
    
    for scheme in schemes:
        try:
            logger.info(f"Ingesting scheme: {scheme['metadata']['scheme_name']}")
            ingestion_pipeline.process_document(
                text=scheme["text"],
                base_metadata=scheme["metadata"]
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to ingest {scheme['metadata']['scheme_name']}: {e}")
            fail_count += 1
            
    logger.info("=================================")
    logger.info("BATCH 2 INGESTION COMPLETE")
    logger.info(f"Total schemes attempted: {len(schemes)}")
    logger.info(f"Successfully ingested: {success_count}")
    logger.info(f"Failed to ingest: {fail_count}")
    logger.info("=================================")

if __name__ == "__main__":
    main()
