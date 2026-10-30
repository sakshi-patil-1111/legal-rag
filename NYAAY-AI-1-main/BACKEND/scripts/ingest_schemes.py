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
            "scheme_name": "Pradhan Mantri Awas Yojana - Gramin",
            "scheme_id": "PMAY-G",
            "ministry": "Ministry of Rural Development",
            "department": "Department of Rural Development",
            "implementing_authority": "Ministry of Rural Development",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Housing",
            "section_type": "Welfare",
            "source_url": "https://pmayg.nic.in/netiay/about-us.aspx",
            "source_domain": "pmayg.nic.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2016-11-20",
            "update_date": "2024-01-01",
            "effective_date": "2016-11-20",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Rural Poor",
            "residency": "Rural",
            "benefit_type": "Housing Subsidy"
        },
        "text": """
# Pradhan Mantri Awas Yojana - Gramin (PMAY-G)

## Objective
To provide a pucca house with basic amenities to all rural families who are houseless or living in kutcha or dilapidated houses.

## Eligibility
- Applicants must belong to the rural areas of India.
- The applicant must be living in a kutcha house (0, 1 or 2 room houses with kutcha wall and kutcha roof).
- Houseless families are eligible.
- Households without a literate adult above 25 years of age.
- Households without an adult male member between 16 and 59 years of age.
- Female-headed households with no adult male member between 16 and 59 years of age.
- Households with a disabled member and no able-bodied adult member.
- Landless households deriving the major part of their income from manual casual labour.
- Automatically included categories: Households without shelter, destitute/living on alms, manual scavengers, primitive tribal groups, legally released bonded labourers.

## Exclusions
- Families with motorized 2/3/4 wheelers or fishing boats.
- Families with mechanized 3/4 wheeler agricultural equipment.
- Families with a Kisan Credit Card (KCC) limit of ₹50,000 or more.
- Households where any member is a government employee.
- Households where any member is earning more than ₹10,000 per month.
- Households paying income tax or professional tax.
- Families owning a refrigerator or a landline phone.
- Families owning 2.5 acres or more of irrigated land, or 5 acres or more of un-irrigated land.

## Benefits
- Unit assistance of ₹1,20,000 in plains and ₹1,30,000 in hilly states, difficult areas, and IAP districts.
- Beneficiaries receive ₹90.95 per day for unskilled labour for 90/95 days under MGNREGA.
- Assistance of ₹12,000 for the construction of a toilet under Swachh Bharat Mission (Gramin).

## Required Documents
- Aadhaar Card
- Job Card under MGNREGA
- Bank Account Details
- Swachh Bharat Mission Number

## Application Process
- The selection is based on the SECC-2011 data, subject to verification by the Gram Sabha.
- Eligible families not in the SECC list are added through the Awaas+ survey.
- Applicants do not apply directly online; they must contact their Gram Panchayat for inclusion and verification.
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi",
            "scheme_id": "PM-KISAN",
            "ministry": "Ministry of Agriculture and Farmers Welfare",
            "department": "Department of Agriculture, Cooperation & Farmers Welfare",
            "implementing_authority": "Government of India",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Agriculture",
            "section_type": "Financial Assistance",
            "source_url": "https://pmkisan.gov.in/",
            "source_domain": "pmkisan.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2019-02-24",
            "update_date": "2024-01-01",
            "effective_date": "2018-12-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Farmers",
            "occupation": "Farmer",
            "benefit_type": "Cash Assistance"
        },
        "text": """
# Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)

## Objective
To supplement the financial needs of landholding farmers to procure various inputs to ensure proper crop health and appropriate yields, commensurate with the anticipated farm income.

## Eligibility
- The scheme is applicable to all landholding farmers' families in the country.
- The farmer's family is defined as husband, wife, and minor children who own cultivable land as per the land records of the respective State/UT.
- Land ownership must be in the name of the farmer.

## Exclusions
- Institutional landholders.
- Farmer families in which one or more of its members belong to the following categories:
  - Former and present holders of constitutional posts.
  - Former and present Ministers, State Ministers, MPs, MLAs, MLCs, Mayors, or Chairpersons of District Panchayats.
  - All serving or retired officers and employees of Central/State Government Ministries, Offices, Departments, and field organizations (excluding Multi Tasking Staff / Class IV/Group D employees).
  - All superannuated/retired pensioners whose monthly pension is ₹10,000 or more.
  - All persons who paid Income Tax in the last assessment year.
  - Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies and carrying out profession by undertaking practices.

## Benefits
- Direct income support of ₹6,000 per year.
- The amount is transferred directly into the bank accounts of eligible farmers in three equal installments of ₹2,000 each, every four months.

## Required Documents
- Aadhaar Card (mandatory for all states except Assam, Meghalaya, and J&K).
- Citizenship proof.
- Land ownership documents.
- Bank account details.

## Application Process
- Eligible farmers can apply online directly through the Farmers Corner on the PM-KISAN portal (pmkisan.gov.in).
- Farmers can also apply offline by contacting local patwaris, revenue officials, or Nodal Officers nominated by the State Government.
- Common Service Centres (CSCs) are authorized to do the registration for a fee.
"""
    },
    {
        "metadata": {
            "scheme_name": "Post Matric Scholarship for SC Students",
            "scheme_id": "PMS-SC",
            "ministry": "Ministry of Social Justice and Empowerment",
            "department": "Department of Social Justice and Empowerment",
            "implementing_authority": "State Governments",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Scholarships",
            "section_type": "Education",
            "source_url": "https://socialjustice.gov.in/schemes/26",
            "source_domain": "socialjustice.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2020-12-01",
            "update_date": "2024-01-01",
            "effective_date": "2021-04-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": 250000,
            "beneficiary_type": "SC Students",
            "category": "SC",
            "occupation": "Student",
            "benefit_type": "Scholarship"
        },
        "text": """
# Post Matric Scholarship for SC Students

## Objective
To provide financial assistance to Scheduled Caste (SC) students studying at post-matriculation or post-secondary stages to enable them to complete their education.

## Eligibility
- The student must belong to a Scheduled Caste (SC).
- The student must be studying in India.
- The student must be studying at the post-matriculation (Class 11 and above) or post-secondary stage in recognized institutions.
- The student must have passed the previous final examination.
- The annual family income from all sources must not exceed ₹2,50,000 (Two Lakh Fifty Thousand Rupees).
- Students who pursue their studies through correspondence courses are also eligible.

## Exclusions
- Students receiving any other scholarship or stipend for the same course.
- Students enrolled in training courses like Aircraft Maintenance Engineer's Courses and Private Pilot license Courses.
- Students studying abroad.

## Benefits
- Academic allowance varying by course type (Group 1 to Group 4).
  - Group 1 (Degree and Post Graduate level courses in Medicine, Engineering, etc.): ₹13,500/year for hostellers, ₹7,000/year for day scholars.
  - Group 2 (Other Professional Courses leading to Degree, Diploma, Certificate): ₹9,500/year for hostellers, ₹6,500/year for day scholars.
  - Group 3 (Graduate and Post Graduate courses not covered under Group 1 & 2): ₹6,000/year for hostellers, ₹3,000/year for day scholars.
  - Group 4 (All post-matriculation level non-degree courses): ₹4,000/year for hostellers, ₹2,500/year for day scholars.
- Reimbursement of compulsory non-refundable fees.
- Extra allowances for students with disabilities (e.g., Reader Allowance, Transport Allowance, Escort Allowance).

## Required Documents
- Caste Certificate issued by competent authority.
- Income Certificate of parents/guardians.
- Mark sheet of the last qualifying examination.
- Aadhaar Card.
- Fee receipt of the institution.
- Bank Account Details linked with Aadhaar.

## Application Process
- Students must apply online through the National Scholarship Portal (NSP) or respective State Government Scholarship Portals.
- Applications must be verified by the educational institution and then by the State Government nodal officer.
- The scholarship amount is transferred directly into the student's Aadhaar seeded bank account via Direct Benefit Transfer (DBT).
"""
    },
    {
        "metadata": {
            "scheme_name": "Pradhan Mantri Ujjwala Yojana",
            "scheme_id": "PMUY",
            "ministry": "Ministry of Petroleum and Natural Gas",
            "department": "Ministry of Petroleum and Natural Gas",
            "implementing_authority": "Oil Marketing Companies (OMCs)",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Energy",
            "section_type": "Welfare",
            "source_url": "https://www.pmuy.gov.in/",
            "source_domain": "pmuy.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2016-05-01",
            "update_date": "2024-01-01",
            "effective_date": "2016-05-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Women",
            "gender": "Female",
            "benefit_type": "Subsidy"
        },
        "text": """
# Pradhan Mantri Ujjwala Yojana (PMUY)

## Objective
To safeguard the health of women and children by providing them with a clean cooking fuel (LPG), so that they don't have to compromise their health in smoky kitchens or wander in unsafe areas collecting firewood.

## Eligibility
- The applicant must be a woman above 18 years of age.
- The applicant must belong to a Below Poverty Line (BPL) household.
- No other LPG connection should exist in the same household.
- The household must belong to any of the following categories:
  - Eligible as per SECC 2011 list.
  - SC/ST households.
  - Beneficiaries of Pradhan Mantri Awas Yojana (PMAY) (Gramin).
  - Antyodaya Anna Yojana (AAY) beneficiaries.
  - Forest dwellers.
  - Most Backward Classes (MBC).
  - Tea and Ex-Tea Garden tribes.
  - People residing in islands and river islands.

## Benefits
- A financial support of ₹1600 for each LPG connection provided to BPL households.
- The connection includes a cylinder, pressure regulator, booklet, safety hose, and installation charges.
- Beneficiaries are eligible for an EMI facility to cover the cost of the first refill and the stove.
- Ongoing targeted subsidy of ₹300 per 14.2 kg cylinder for up to 12 refills per year.

## Required Documents
- e-KYC (Aadhaar based).
- Ration Card issued by the State/UT Government or other state government document certifying family composition.
- Aadhaar of beneficiary and adult family members.
- Bank Account Number and IFSC.
- Proof of Address.

## Application Process
- Applicants can apply offline by filling up the application form and submitting it to the nearest LPG distributor.
- Online applications can be submitted through the official PMUY website (pmuy.gov.in).
- The documents are verified against the SECC database or other defined categories before issuing the connection.
"""
    },
    {
        "metadata": {
            "scheme_name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana",
            "scheme_id": "AB-PMJAY",
            "ministry": "Ministry of Health and Family Welfare",
            "department": "National Health Authority",
            "implementing_authority": "National Health Authority",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Healthcare",
            "section_type": "Insurance",
            "source_url": "https://pmjay.gov.in/",
            "source_domain": "pmjay.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2018-09-23",
            "update_date": "2024-01-01",
            "effective_date": "2018-09-23",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": None,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Poor and Vulnerable",
            "benefit_type": "Health Insurance"
        },
        "text": """
# Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)

## Objective
To provide health protection cover to poor and vulnerable families against catastrophic health expenditure on secondary and tertiary care hospitalization.

## Eligibility
- PMJAY is an entitlement-based scheme based on deprivation and occupational criteria as per the Socio-Economic Caste Census (SECC) 2011 data.
- **Rural Area Categories**:
  - D1: Households with only one room with kucha walls and kucha roof.
  - D2: No adult member between age 16 to 59.
  - D3: Female-headed households with no adult male member between 16 to 59.
  - D4: Disabled member and no able-bodied adult member.
  - D5: SC/ST households.
  - D7: Landless households deriving major part of their income from manual casual labour.
- **Urban Area Categories**: Include rag pickers, beggars, domestic workers, street vendors/cobblers/hawkers, construction workers, plumbers, masons, sweepers, sanitation workers, transport workers, and other defined occupational categories.
- Automatically included categories: Destitute, living on alms, manual scavenger families, primitive tribal groups, legally released bonded labour.
- There is no restriction on family size, age, or gender.

## Benefits
- Health insurance cover of ₹5,00,000 (Five Lakh Rupees) per family per year.
- Covers secondary and tertiary care hospitalization across public and empaneled private hospitals.
- Cashless and paperless access to healthcare services at the point of service.
- Covers pre-hospitalization expenses for 3 days and post-hospitalization for 15 days.
- Covers room charges, medical consumables, nursing care, doctor's fees, OT charges, ICU charges, implants, etc.

## Required Documents
- Aadhaar Card or any other valid government ID (Voter ID, PAN Card, etc.).
- Ration Card or family composition document.
- PMJAY E-card / Golden Card (generated after verification).

## Application Process
- There is no formal application process as it is an entitlement-based scheme.
- Beneficiaries can check their eligibility on the PMJAY portal (mera.pmjay.gov.in), PMJAY app, or by calling the toll-free number 14555.
- Upon hospitalization or at a Common Service Centre (CSC) / empaneled hospital, a PMJAY Mitr verifies the beneficiary's identity and issues a Golden Card/E-card.
"""
    }
]

# Adding some state level and other varied schemes
schemes.extend([
    {
        "metadata": {
            "scheme_name": "Mukhyamantri Kanya Sumangala Yojana",
            "scheme_id": "MKSY",
            "ministry": "Department of Women and Child Development",
            "department": "Uttar Pradesh Government",
            "implementing_authority": "Uttar Pradesh Government",
            "government_level": "State",
            "state": "Uttar Pradesh",
            "scheme_category": "Women",
            "section_type": "Welfare",
            "source_url": "https://mksy.up.gov.in/",
            "source_domain": "mksy.up.gov.in",
            "source_authority": "Government of Uttar Pradesh",
            "source_type": "government_scheme",
            "publication_date": "2019-04-01",
            "update_date": "2024-01-01",
            "effective_date": "2019-04-01",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 0,
            "age_max": None,
            "income_limit": 300000,
            "beneficiary_type": "Girl Child",
            "gender": "Female",
            "residency": "Uttar Pradesh",
            "benefit_type": "Financial Assistance"
        },
        "text": """
# Mukhyamantri Kanya Sumangala Yojana (Uttar Pradesh)

## Objective
To eliminate female foeticide, establish equal sex ratio, prevent child marriage, and promote the health and education of the girl child in Uttar Pradesh.

## Eligibility
- The beneficiary's family must be a resident of Uttar Pradesh and possess a residence proof (Ration Card, Aadhaar Card, Voter ID, Electricity Bill).
- The annual income of the beneficiary's family should be ₹3 Lakhs or less.
- Maximum two girl children from a family can benefit from the scheme.
- If a woman has twin girls during her second delivery, then the third girl child will also be eligible.
- If an orphan girl is adopted, a maximum of two girls (including biological and adopted) will benefit.
- The girl child should have been born on or after 01/04/2019 (for Stage 1 benefits).

## Benefits
Financial assistance of ₹15,000 (total) provided in 6 distinct stages:
1. **Stage 1**: ₹2,000 on the birth of a girl child (born on/after 01-04-2019).
2. **Stage 2**: ₹1,000 after complete immunization of the girl child within one year of birth.
3. **Stage 3**: ₹2,000 when the girl child is admitted to Class-I.
4. **Stage 4**: ₹2,000 when the girl child is admitted to Class-VI.
5. **Stage 5**: ₹3,000 when the girl child is admitted to Class-IX.
6. **Stage 6**: ₹5,000 when the girl child passes Class X/XII and enrolls in a 2-year or more degree/diploma course.

## Required Documents
- Aadhaar Card of parents/guardian.
- Birth certificate of the girl child.
- Immunization card (for Stage 2).
- Admission certificate from the school (for educational stages).
- Income Certificate.
- Residence Proof of Uttar Pradesh.
- Bank Account Details.
- Adoption certificate (if applicable).

## Application Process
- Applications must be submitted online through the official portal (mksy.up.gov.in) or offline at the Block Development Officer (BDO), SDM, or District Probation Officer (DPO) office.
- Registration requires verifying mobile number and Aadhaar.
"""
    },
    {
        "metadata": {
            "scheme_name": "Stand-Up India Scheme",
            "scheme_id": "SUPI",
            "ministry": "Ministry of Finance",
            "department": "Department of Financial Services",
            "implementing_authority": "SIDBI",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Entrepreneurship",
            "section_type": "Loan",
            "source_url": "https://www.standupmitra.in/",
            "source_domain": "standupmitra.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2016-04-05",
            "update_date": "2024-01-01",
            "effective_date": "2016-04-05",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "SC/ST/Women Entrepreneurs",
            "category": "SC/ST",
            "benefit_type": "Loan"
        },
        "text": """
# Stand-Up India Scheme

## Objective
To facilitate bank loans between ₹10 lakh and ₹1 Crore to at least one Scheduled Caste (SC) or Scheduled Tribe (ST) borrower and at least one woman borrower per bank branch for setting up a greenfield enterprise.

## Eligibility
- The applicant must be an SC/ST and/or a woman entrepreneur.
- The applicant must be above 18 years of age.
- The loans under the scheme are available for only greenfield projects (first-time venture of the beneficiary in the manufacturing, services, agri-allied activities, or trading sector).
- In case of non-individual enterprises, at least 51% of the shareholding and controlling stake should be held by either an SC/ST or a Woman entrepreneur.
- The borrower should not be in default to any bank or financial institution.

## Exclusions
- Existing businesses are not eligible; the enterprise must be a greenfield project.
- Applicants who have defaulted on previous bank loans.

## Benefits
- Composite loan (inclusive of term loan and working capital) between ₹10 lakh and up to ₹100 lakh (₹1 Crore).
- The loan is expected to cover 85% of the project cost (margin money is 15%).
- The rate of interest is the lowest applicable rate of the bank for that category (rating) not to exceed (base rate (MCLR) + 3% + tenor premium).
- The loan is repayable in 7 years with a maximum moratorium period of 18 months.
- Credit guarantee cover available through CGSSI.

## Required Documents
- Identity Proof (Aadhaar, Voter ID, PAN).
- Residence Proof.
- Caste Certificate for SC/ST applicants.
- Project Report / Business Plan.
- Quotations for machinery or other assets to be purchased.
- Rent agreement or lease deed if the business premises are rented.

## Application Process
- Applications can be accessed at a bank branch, online through the Stand-Up India portal (standupmitra.in), or through the Lead District Manager (LDM).
- Applicants register on the portal, provide business details, and are connected with relevant banks and handholding agencies for support.
"""
    },
    {
        "metadata": {
            "scheme_name": "PM Vishwakarma Scheme",
            "scheme_id": "PM-V",
            "ministry": "Ministry of Micro, Small and Medium Enterprises",
            "department": "MSME",
            "implementing_authority": "Ministry of MSME",
            "government_level": "Central",
            "state": "All India",
            "scheme_category": "Skill Development",
            "section_type": "Welfare",
            "source_url": "https://pmvishwakarma.gov.in/",
            "source_domain": "pmvishwakarma.gov.in",
            "source_authority": "Government of India",
            "source_type": "government_scheme",
            "publication_date": "2023-09-17",
            "update_date": "2024-01-01",
            "effective_date": "2023-09-17",
            "retrieved_at": datetime.now().isoformat(),
            "age_min": 18,
            "age_max": None,
            "income_limit": None,
            "beneficiary_type": "Artisans and Craftspeople",
            "occupation": "Artisan",
            "benefit_type": "Loan and Training"
        },
        "text": """
# PM Vishwakarma Scheme

## Objective
To provide end-to-end support to artisans and craftspeople who work with their hands and tools. The scheme aims to improve the quality, scale, and reach of their products, integrating them with the domestic and global value chains.

## Eligibility
- An artisan or craftsperson working with hands and tools and engaged in one of the 18 family-based traditional trades specified in the scheme.
- The minimum age of the beneficiary should be 18 years on the date of registration.
- The beneficiary should be engaged in the concerned trade on the date of registration.
- The beneficiary must not have availed loans under similar credit-based schemes of Central/State Government (like PMEGP, PM SVANidhi, MUDRA) in the past 5 years.
- Only one member of a family can register and avail the benefits. A 'family' for this purpose is defined as husband, wife, and unmarried children.

## Covered Trades
Carpenter, Boat Maker, Armourer, Blacksmith, Hammer and Tool Kit Maker, Locksmith, Goldsmith, Potter, Sculptor/Stone carver, Cobbler/Shoesmith/Footwear artisan, Mason, Basket/Mat/Broom Maker/Coir Weaver, Doll & Toy Maker (Traditional), Barber, Garland maker, Washerman, Tailor, and Fishing Net Maker.

## Exclusions
- Persons employed in government service and their family members are not eligible.
- Families who have already availed PM SVANidhi, PMEGP, or Mudra loans in the last 5 years.

## Benefits
- **Recognition**: PM Vishwakarma Certificate and ID Card.
- **Skill Upgradation**: Basic Training (5-7 days) and Advanced Training (15 days or more) with a stipend of ₹500 per day.
- **Toolkit Incentive**: e-Voucher up to ₹15,000 at the beginning of basic training.
- **Credit Support**: Collateral-free enterprise development loans. 
  - First tranche up to ₹1 lakh (repayable in 18 months).
  - Second tranche up to ₹2 lakhs (repayable in 30 months).
  - Concessional interest rate of 5%.
- **Digital Transaction Incentive**: ₹1 per transaction for up to 100 transactions monthly.
- **Marketing Support**: Quality certification, branding, e-commerce onboarding, and advertising.

## Required Documents
- Aadhaar Card.
- Mobile number linked with Aadhaar.
- Bank Account Details.
- Ration Card (for family details).

## Application Process
- Beneficiaries must register online through Common Service Centres (CSCs) using the PM Vishwakarma portal (pmvishwakarma.gov.in).
- Verification is done in three steps:
  1. Gram Panchayat / Urban Local Body Level
  2. District Implementation Committee
  3. Screening Committee
"""
    }
])

def main():
    logger.info(f"Starting ingestion of {len(schemes)} government schemes...")
    
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
    logger.info("INGESTION COMPLETE")
    logger.info(f"Total schemes attempted: {len(schemes)}")
    logger.info(f"Successfully ingested: {success_count}")
    logger.info(f"Failed to ingest: {fail_count}")
    logger.info("=================================")

if __name__ == "__main__":
    main()
