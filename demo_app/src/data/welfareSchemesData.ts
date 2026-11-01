export interface WelfareScheme {
  id: string;
  code: string;
  name: string;
  ministry: string;
  category: 'HOUSING_RURAL' | 'AGRICULTURE_FOOD' | 'HEALTH_MATERNITY' | 'PENSION_SOCIAL' | 'FINANCIAL_INSURANCE' | 'SKILLS_EDUCATION';
  targetBeneficiaries: string;
  benefitBadge: string;
  maxBenefit: string;
  incomeLimit: string;
  eligibilityCriteria: string[];
  ineligibilityExclusions: string[];
  requiredDocuments: string[];
  applicationProcess: string[];
  officialPortalUrl: string;
  helplineNumber: string;
  plainLanguageSummary: string;
}

export const WELFARE_SCHEMES_CATALOG: WelfareScheme[] = [
  {
    "id": "pmay-g",
    "code": "PMAY-G",
    "name": "Pradhan Mantri Awas Yojana - Gramin",
    "ministry": "Ministry of Rural Development",
    "category": "HOUSING_RURAL",
    "targetBeneficiaries": "Rural Poor",
    "maxBenefit": "Direct cash assistance of \u20b91,20,000 in plains and \u20b91,30,000 in hilly/difficult areas for house construction.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Applicants must belong to the rural areas of India.",
      "The applicant must be living in a kutcha house (0, 1 or 2 room houses with kutcha wall and kutcha roof).",
      "Houseless families are eligible.",
      "Households without a literate adult above 25 years of age.",
      "Households without an adult male member between 16 and 59 years of age.",
      "Female-headed households with no adult male member between 16 and 59 years of age.",
      "Households with a disabled member and no able-bodied adult member.",
      "Landless households deriving the major part of their income from manual casual labour.",
      "Automatically included categories: Households without shelter, destitute/living on alms, manual scavengers, primitive tribal groups, legally released bonded labourers."
    ],
    "ineligibilityExclusions": [
      "Families with motorized 2/3/4 wheelers or fishing boats.",
      "Families with mechanized 3/4 wheeler agricultural equipment.",
      "Families with a Kisan Credit Card (KCC) limit of \u20b950,000 or more.",
      "Households where any member is a government employee.",
      "Households where any member is earning more than \u20b910,000 per month.",
      "Households paying income tax or professional tax.",
      "Families owning a refrigerator or a landline phone.",
      "Families owning 2.5 acres or more of irrigated land, or 5 acres or more of un-irrigated land."
    ],
    "requiredDocuments": [
      "Aadhaar Card",
      "Job Card under MGNREGA",
      "Bank Account Details",
      "Swachh Bharat Mission Number"
    ],
    "applicationProcess": [
      "The selection is based on the SECC-2011 data, subject to verification by the Gram Sabha.",
      "Eligible families not in the SECC list are added through the Awaas+ survey.",
      "Applicants do not apply directly online; they must contact their Gram Panchayat for inclusion and verification."
    ],
    "officialPortalUrl": "https://pmayg.nic.in/netiay/about-us.aspx",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a direct cash grant of up to \u20b91,30,000 for rural families to build a permanent, all-weather house with basic amenities.",
    "benefitBadge": "\u20b91.3L Grant"
  },
  {
    "id": "pm-kisan",
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi",
    "ministry": "Ministry of Agriculture and Farmers Welfare",
    "category": "AGRICULTURE_FOOD",
    "targetBeneficiaries": "Farmers",
    "maxBenefit": "\u20b96,000 per year delivered in 3 equal four-monthly installments of \u20b92,000 directly to the bank account.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The scheme is applicable to all landholding farmers' families in the country.",
      "The farmer's family is defined as husband, wife, and minor children who own cultivable land as per the land records of the respective State/UT.",
      "Land ownership must be in the name of the farmer."
    ],
    "ineligibilityExclusions": [
      "Institutional landholders.",
      "Farmer families in which one or more of its members belong to the following categories:",
      "Former and present holders of constitutional posts.",
      "Former and present Ministers, State Ministers, MPs, MLAs, MLCs, Mayors, or Chairpersons of District Panchayats.",
      "All serving or retired officers and employees of Central/State Government Ministries, Offices, Departments, and field organizations (excluding Multi Tasking Staff / Class IV/Group D employees).",
      "All superannuated/retired pensioners whose monthly pension is \u20b910,000 or more.",
      "All persons who paid Income Tax in the last assessment year.",
      "Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies and carrying out profession by undertaking practices."
    ],
    "requiredDocuments": [
      "Aadhaar Card (mandatory for all states except Assam, Meghalaya, and J&K).",
      "Citizenship proof.",
      "Land ownership documents.",
      "Bank account details."
    ],
    "applicationProcess": [
      "Eligible farmers can apply online directly through the Farmers Corner on the PM-KISAN portal (pmkisan.gov.in).",
      "Farmers can also apply offline by contacting local patwaris, revenue officials, or Nodal Officers nominated by the State Government.",
      "Common Service Centres (CSCs) are authorized to do the registration for a fee."
    ],
    "officialPortalUrl": "https://pmkisan.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides \u20b96,000 guaranteed cash every year directly to landholding farmers' bank accounts in three installments to cover farming expenses.",
    "benefitBadge": "\u20b96,000 / Year"
  },
  {
    "id": "pms-sc",
    "code": "PMS-SC",
    "name": "Post Matric Scholarship for SC Students",
    "ministry": "Ministry of Social Justice and Empowerment",
    "category": "SKILLS_EDUCATION",
    "targetBeneficiaries": "SC Students",
    "maxBenefit": "Covers compulsory non-refundable fees and provides a monthly maintenance allowance.",
    "incomeLimit": "250000",
    "eligibilityCriteria": [
      "The student must belong to a Scheduled Caste (SC).",
      "The student must be studying in India.",
      "The student must be studying at the post-matriculation (Class 11 and above) or post-secondary stage in recognized institutions.",
      "The student must have passed the previous final examination.",
      "The annual family income from all sources must not exceed \u20b92,50,000 (Two Lakh Fifty Thousand Rupees).",
      "Students who pursue their studies through correspondence courses are also eligible."
    ],
    "ineligibilityExclusions": [
      "Students receiving any other scholarship or stipend for the same course.",
      "Students enrolled in training courses like Aircraft Maintenance Engineer's Courses and Private Pilot license Courses.",
      "Students studying abroad."
    ],
    "requiredDocuments": [
      "Caste Certificate issued by competent authority.",
      "Income Certificate of parents/guardians.",
      "Mark sheet of the last qualifying examination.",
      "Aadhaar Card.",
      "Fee receipt of the institution.",
      "Bank Account Details linked with Aadhaar."
    ],
    "applicationProcess": [
      "Students must apply online through the National Scholarship Portal (NSP) or respective State Government Scholarship Portals.",
      "Applications must be verified by the educational institution and then by the State Government nodal officer.",
      "The scholarship amount is transferred directly into the student's Aadhaar seeded bank account via Direct Benefit Transfer (DBT)."
    ],
    "officialPortalUrl": "https://socialjustice.gov.in/schemes/26",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides financial assistance to Scheduled Caste students studying at post-matriculation or post-secondary stages to complete their education.",
    "benefitBadge": "Full Fee Cover"
  },
  {
    "id": "pmuy",
    "code": "PMUY",
    "name": "Pradhan Mantri Ujjwala Yojana",
    "ministry": "Ministry of Petroleum and Natural Gas",
    "category": "HEALTH_MATERNITY",
    "targetBeneficiaries": "Women",
    "maxBenefit": "Financial assistance of \u20b91,600 for a free LPG connection, plus first refill and stove free of cost.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The applicant must be a woman above 18 years of age.",
      "The applicant must belong to a Below Poverty Line (BPL) household.",
      "No other LPG connection should exist in the same household.",
      "The household must belong to any of the following categories:",
      "Eligible as per SECC 2011 list.",
      "SC/ST households.",
      "Beneficiaries of Pradhan Mantri Awas Yojana (PMAY) (Gramin).",
      "Antyodaya Anna Yojana (AAY) beneficiaries.",
      "Forest dwellers.",
      "Most Backward Classes (MBC).",
      "Tea and Ex-Tea Garden tribes.",
      "People residing in islands and river islands."
    ],
    "ineligibilityExclusions": [],
    "requiredDocuments": [
      "e-KYC (Aadhaar based).",
      "Ration Card issued by the State/UT Government or other state government document certifying family composition.",
      "Aadhaar of beneficiary and adult family members.",
      "Bank Account Number and IFSC.",
      "Proof of Address."
    ],
    "applicationProcess": [
      "Applicants can apply offline by filling up the application form and submitting it to the nearest LPG distributor.",
      "Online applications can be submitted through the official PMUY website (pmuy.gov.in).",
      "The documents are verified against the SECC database or other defined categories before issuing the connection."
    ],
    "officialPortalUrl": "https://www.pmuy.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides free LPG gas connections to women from below-poverty-line households, shifting them away from harmful firewood cooking.",
    "benefitBadge": "Free LPG"
  },
  {
    "id": "ab-pmjay",
    "code": "AB-PMJAY",
    "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana",
    "ministry": "Ministry of Health and Family Welfare",
    "category": "HEALTH_MATERNITY",
    "targetBeneficiaries": "Poor and Vulnerable",
    "maxBenefit": "\u20b95,00,000 health insurance cover per family per year for secondary and tertiary hospitalisation.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "PMJAY is an entitlement-based scheme based on deprivation and occupational criteria as per the Socio-Economic Caste Census (SECC) 2011 data.",
      "**Rural Area Categories**:",
      "D1: Households with only one room with kucha walls and kucha roof.",
      "D2: No adult member between age 16 to 59.",
      "D3: Female-headed households with no adult male member between 16 to 59.",
      "D4: Disabled member and no able-bodied adult member.",
      "D5: SC/ST households.",
      "D7: Landless households deriving major part of their income from manual casual labour.",
      "**Urban Area Categories**: Include rag pickers, beggars, domestic workers, street vendors/cobblers/hawkers, construction workers, plumbers, masons, sweepers, sanitation workers, transport workers, and other defined occupational categories.",
      "Automatically included categories: Destitute, living on alms, manual scavenger families, primitive tribal groups, legally released bonded labour.",
      "There is no restriction on family size, age, or gender."
    ],
    "ineligibilityExclusions": [],
    "requiredDocuments": [
      "Aadhaar Card or any other valid government ID (Voter ID, PAN Card, etc.).",
      "Ration Card or family composition document.",
      "PMJAY E-card / Golden Card (generated after verification)."
    ],
    "applicationProcess": [
      "There is no formal application process as it is an entitlement-based scheme.",
      "Beneficiaries can check their eligibility on the PMJAY portal (mera.pmjay.gov.in), PMJAY app, or by calling the toll-free number 14555.",
      "Upon hospitalization or at a Common Service Centre (CSC) / empaneled hospital, a PMJAY Mitr verifies the beneficiary's identity and issues a Golden Card/E-card."
    ],
    "officialPortalUrl": "https://pmjay.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Gives your entire family free, 100% cashless hospital treatment up to \u20b95 Lakhs every year for major surgeries and ICU care.",
    "benefitBadge": "\u20b95L Health Cover"
  },
  {
    "id": "mksy",
    "code": "MKSY",
    "name": "Mukhyamantri Kanya Sumangala Yojana",
    "ministry": "Department of Women and Child Development",
    "category": "HEALTH_MATERNITY",
    "targetBeneficiaries": "Girl Child",
    "maxBenefit": "Lump sum financial assistance of \u20b915,000 paid to the family upon the birth of a girl child.",
    "incomeLimit": "300000",
    "eligibilityCriteria": [
      "The beneficiary's family must be a resident of Uttar Pradesh and possess a residence proof (Ration Card, Aadhaar Card, Voter ID, Electricity Bill).",
      "The annual income of the beneficiary's family should be \u20b93 Lakhs or less.",
      "Maximum two girl children from a family can benefit from the scheme.",
      "If a woman has twin girls during her second delivery, then the third girl child will also be eligible.",
      "If an orphan girl is adopted, a maximum of two girls (including biological and adopted) will benefit.",
      "The girl child should have been born on or after 01/04/2019 (for Stage 1 benefits)."
    ],
    "ineligibilityExclusions": [],
    "requiredDocuments": [
      "Aadhaar Card of parents/guardian.",
      "Birth certificate of the girl child.",
      "Immunization card (for Stage 2).",
      "Admission certificate from the school (for educational stages).",
      "Income Certificate.",
      "Residence Proof of Uttar Pradesh.",
      "Bank Account Details.",
      "Adoption certificate (if applicable)."
    ],
    "applicationProcess": [
      "Applications must be submitted online through the official portal (mksy.up.gov.in) or offline at the Block Development Officer (BDO), SDM, or District Probation Officer (DPO) office.",
      "Registration requires verifying mobile number and Aadhaar."
    ],
    "officialPortalUrl": "https://mksy.up.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a financial grant for the birth of a girl child to improve child sex ratio and promote girl child education.",
    "benefitBadge": "\u20b915,000 Grant"
  },
  {
    "id": "supi",
    "code": "SUPI",
    "name": "Stand-Up India Scheme",
    "ministry": "Ministry of Finance",
    "category": "SKILLS_EDUCATION",
    "targetBeneficiaries": "SC/ST/Women Entrepreneurs",
    "maxBenefit": "Bank loan between \u20b910 Lakh and \u20b91 Crore to cover 85% of project cost for greenfield enterprises.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The applicant must be an SC/ST and/or a woman entrepreneur.",
      "The applicant must be above 18 years of age.",
      "The loans under the scheme are available for only greenfield projects (first-time venture of the beneficiary in the manufacturing, services, agri-allied activities, or trading sector).",
      "In case of non-individual enterprises, at least 51% of the shareholding and controlling stake should be held by either an SC/ST or a Woman entrepreneur.",
      "The borrower should not be in default to any bank or financial institution."
    ],
    "ineligibilityExclusions": [
      "Existing businesses are not eligible; the enterprise must be a greenfield project.",
      "Applicants who have defaulted on previous bank loans."
    ],
    "requiredDocuments": [
      "Identity Proof (Aadhaar, Voter ID, PAN).",
      "Residence Proof.",
      "Caste Certificate for SC/ST applicants.",
      "Project Report / Business Plan.",
      "Quotations for machinery or other assets to be purchased.",
      "Rent agreement or lease deed if the business premises are rented."
    ],
    "applicationProcess": [
      "Applications can be accessed at a bank branch, online through the Stand-Up India portal (standupmitra.in), or through the Lead District Manager (LDM).",
      "Applicants register on the portal, provide business details, and are connected with relevant banks and handholding agencies for support."
    ],
    "officialPortalUrl": "https://www.standupmitra.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Facilitates bank loans between \u20b910 Lakhs and \u20b91 Crore to SC/ST or women entrepreneurs for setting up new manufacturing or service businesses.",
    "benefitBadge": "\u20b910L - \u20b91Cr Loan"
  },
  {
    "id": "pm-v",
    "code": "PM-V",
    "name": "PM Vishwakarma Scheme",
    "ministry": "Ministry of Micro, Small and Medium Enterprises",
    "category": "SKILLS_EDUCATION",
    "targetBeneficiaries": "Artisans and Craftspeople",
    "maxBenefit": "Collateral-free loans up to \u20b93 Lakhs at 5% interest, \u20b915,000 toolkit incentive, and a \u20b9500 daily training stipend.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "An artisan or craftsperson working with hands and tools and engaged in one of the 18 family-based traditional trades specified in the scheme.",
      "The minimum age of the beneficiary should be 18 years on the date of registration.",
      "The beneficiary should be engaged in the concerned trade on the date of registration.",
      "The beneficiary must not have availed loans under similar credit-based schemes of Central/State Government (like PMEGP, PM SVANidhi, MUDRA) in the past 5 years.",
      "Only one member of a family can register and avail the benefits. A 'family' for this purpose is defined as husband, wife, and unmarried children."
    ],
    "ineligibilityExclusions": [
      "Persons employed in government service and their family members are not eligible.",
      "Families who have already availed PM SVANidhi, PMEGP, or Mudra loans in the last 5 years."
    ],
    "requiredDocuments": [
      "Aadhaar Card.",
      "Mobile number linked with Aadhaar.",
      "Bank Account Details.",
      "Ration Card (for family details)."
    ],
    "applicationProcess": [
      "Beneficiaries must register online through Common Service Centres (CSCs) using the PM Vishwakarma portal (pmvishwakarma.gov.in).",
      "Verification is done in three steps:",
      "1. Gram Panchayat / Urban Local Body Level",
      "2. District Implementation Committee",
      "3. Screening Committee"
    ],
    "officialPortalUrl": "https://pmvishwakarma.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Supports traditional artisans and craftspeople with skill training, a \u20b915,000 toolkit grant, and collateral-free business loans.",
    "benefitBadge": "\u20b93L Loan + Toolkit"
  },
  {
    "id": "mgnrega",
    "code": "MGNREGA",
    "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
    "ministry": "Ministry of Rural Development",
    "category": "HOUSING_RURAL",
    "targetBeneficiaries": "Rural Household",
    "maxBenefit": "100 days of guaranteed wage employment per financial year at statutory state minimum wage rates.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Must be a citizen of India residing in a rural area.",
      "Must be 18 years of age or older.",
      "Must be willing to do unskilled manual work.",
      "The applicant must be part of a local household in the Gram Panchayat."
    ],
    "ineligibilityExclusions": [
      "Individuals residing in urban areas are not eligible.",
      "Individuals unwilling to do manual unskilled work.",
      "Employment is capped at 100 days per household per financial year (with exceptions for drought-notified areas or forest rights act beneficiaries which may get 150 days)."
    ],
    "requiredDocuments": [
      "Aadhaar Card (mandatory for wage payment linking).",
      "Bank/Post Office Account Details.",
      "Ration Card / Voter ID / Proof of residence for household identification."
    ],
    "applicationProcess": [
      "Registration at the local Gram Panchayat.",
      "The Gram Panchayat issues a Job Card to the household.",
      "The job card holder submits a written request for work (for at least 14 days of continuous work) to the Gram Panchayat or Block Office."
    ],
    "officialPortalUrl": "https://nrega.nic.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Guarantees 100 days of paid manual labor work per year for any rural household willing to do public works, providing a financial safety net.",
    "benefitBadge": "100 Days Wage"
  },
  {
    "id": "nfsa-pds",
    "code": "NFSA-PDS",
    "name": "National Food Security Act / Public Distribution System",
    "ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
    "category": "AGRICULTURE_FOOD",
    "targetBeneficiaries": "Poor Households",
    "maxBenefit": "5 kg foodgrains per person/month for Priority Households; 35 kg per household for Antyodaya Anna Yojana.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Coverage under NFSA is categorized into two groups:",
      "1. **Antyodaya Anna Yojana (AAY) households**: The poorest of the poor households as identified by the State Government.",
      "2. **Priority Households (PHH)**: Households identified by State Governments as per their specific socio-economic criteria.",
      "General criteria utilized by states for PHH include:",
      "Landless agricultural laborers, marginal farmers, rural artisans, and informal sector workers in urban areas.",
      "Households with destitute, widows, terminally ill persons, or disabled persons.",
      "BPL (Below Poverty Line) families."
    ],
    "ineligibilityExclusions": [
      "Families paying income tax.",
      "Families with regular government employees.",
      "Families owning a specified extent of irrigated land or motorized vehicles (criteria vary slightly by State)."
    ],
    "requiredDocuments": [
      "Aadhaar Card of family members.",
      "Income Certificate.",
      "Address Proof (Electricity bill, etc.).",
      "Caste/Category certificate (if applicable)."
    ],
    "applicationProcess": [
      "Apply for a Ration Card at the local Food and Civil Supplies Office or online via the State's specific PDS portal.",
      "After field verification, an AAY or PHH Ration Card is issued.",
      "Beneficiaries collect rations using biometric authentication (ePoS) at Fair Price Shops."
    ],
    "officialPortalUrl": "https://nfsa.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Ensures affordable food access by providing monthly subsidized foodgrains (rice at \u20b93/kg, wheat at \u20b92/kg) to poor and vulnerable households.",
    "benefitBadge": "Subsidized Food"
  },
  {
    "id": "pmmvy",
    "code": "PMMVY",
    "name": "Pradhan Mantri Matru Vandana Yojana",
    "ministry": "Ministry of Women and Child Development",
    "category": "HEALTH_MATERNITY",
    "targetBeneficiaries": "Pregnant Women",
    "maxBenefit": "\u20b95,000 cash incentive in three installments for the first child, and \u20b96,000 for a second girl child.",
    "incomeLimit": "800000",
    "eligibilityCriteria": [
      "Pregnant Women and Lactating Mothers (PW&LM) who are socially or economically disadvantaged.",
      "The applicant must be at least 19 years old.",
      "The benefit is available for the first living child in the family.",
      "Extended to the second child only if the second child is a girl.",
      "Beneficiary must belong to categories like SC/ST, BPL, E-Shram card holders, PMJAY beneficiaries, MGNREGA job card holders, Kisan Samman Nidhi beneficiaries, women with family income < 8 Lakhs, divyang women (40% disabled), or Anganwadi workers."
    ],
    "ineligibilityExclusions": [
      "PW&LM who are in regular employment with the Central Government or State Governments or Public Sector Undertakings (PSUs) or those who are in receipt of similar benefits under any law for the time being in force."
    ],
    "requiredDocuments": [
      "Aadhaar Card of the beneficiary.",
      "MCP (Mother and Child Protection) Card.",
      "Bank or Post Office Account details.",
      "Proof of belonging to eligible category (e.g., E-Shram card, BPL card, income certificate)."
    ],
    "applicationProcess": [
      "Beneficiaries can apply online on the PMMVY portal (pmmvy.nic.in) or offline at an Anganwadi Centre (AWC) or approved Health facility."
    ],
    "officialPortalUrl": "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides cash incentives to pregnant women and lactating mothers for their first living child to support nutrition and partial wage loss.",
    "benefitBadge": "\u20b95,000 Cash"
  },
  {
    "id": "nsap",
    "code": "NSAP",
    "name": "National Social Assistance Programme",
    "ministry": "Ministry of Rural Development",
    "category": "PENSION_SOCIAL",
    "targetBeneficiaries": "BPL, Elderly, Widows, Disabled",
    "maxBenefit": "Monthly financial assistance varying between \u20b9200 to \u20b9500 (plus state top-ups) based on the sub-scheme.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The applicant must belong to a Below Poverty Line (BPL) household as per criteria prescribed by the Government of India.",
      "Must fall into a vulnerable category: elderly (60+), widow (40+), disabled (18+, 80% disability), or facing death of the primary breadwinner.",
      "For National Family Benefit Scheme (NFBS): Death of the primary breadwinner (aged 18-59) of a BPL family.",
      "For Annapurna Scheme: Destitute senior citizens (65+) who are eligible for IGNOAPS but are not receiving the pension."
    ],
    "ineligibilityExclusions": [
      "Families above the poverty line (APL).",
      "Individuals receiving other state/central pensions for the same purpose."
    ],
    "requiredDocuments": [
      "BPL Ration Card / SECC Data proof.",
      "Aadhaar Card.",
      "Bank/Post Office Account Details.",
      "Death certificate of husband (for IGNWPS).",
      "Disability certificate (for IGNDPS).",
      "Death certificate of primary breadwinner (for NFBS)."
    ],
    "applicationProcess": [
      "Applications are submitted to the Gram Panchayat / Block Development Office / Municipal office.",
      "States also provide online application portals through e-District platforms."
    ],
    "officialPortalUrl": "https://nsap.nic.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a basic monthly pension to vulnerable individuals living below the poverty line, including the elderly, widows, and disabled.",
    "benefitBadge": "Monthly Pension"
  },
  {
    "id": "ignoaps",
    "code": "IGNOAPS",
    "name": "Indira Gandhi National Old Age Pension Scheme",
    "ministry": "Ministry of Rural Development",
    "category": "PENSION_SOCIAL",
    "targetBeneficiaries": "BPL Senior Citizens",
    "maxBenefit": "Monthly pension of \u20b9200 (ages 60-79) or \u20b9500 (age 80+), often supplemented by state contributions.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The applicant must be 60 years of age or older.",
      "The applicant must belong to a Below Poverty Line (BPL) household according to the criteria prescribed by the Government of India.",
      "Destitute elders without regular means of subsistence from their own source of income or through financial support from family members."
    ],
    "ineligibilityExclusions": [
      "Persons below 60 years of age.",
      "Individuals who do not belong to a BPL household.",
      "Persons receiving regular pensions from government employment or other sources."
    ],
    "requiredDocuments": [
      "Proof of Age (Birth certificate, Aadhaar card, Voter ID, School leaving certificate).",
      "BPL Certificate or Ration Card.",
      "Passport size photographs.",
      "Bank or Post Office account passbook."
    ],
    "applicationProcess": [
      "The eligible person needs to apply using the prescribed form at the Block Development Office (BDO) in rural areas or Executive Officer of Municipality in urban areas.",
      "Online applications are available through various State Government portals or the UMANG app."
    ],
    "officialPortalUrl": "https://nsap.nic.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a guaranteed monthly cash pension for BPL senior citizens aged 60 and above with no regular means of subsistence.",
    "benefitBadge": "Old Age Pension"
  },
  {
    "id": "pmay-u",
    "code": "PMAY-U",
    "name": "Pradhan Mantri Awas Yojana - Urban",
    "ministry": "Ministry of Housing and Urban Affairs",
    "category": "HOUSING_RURAL",
    "targetBeneficiaries": "Urban Poor / Middle Class",
    "maxBenefit": "Interest subsidy up to \u20b92.67 Lakhs on home loans, or a direct grant of \u20b91.5 Lakhs for construction.",
    "incomeLimit": "1800000",
    "eligibilityCriteria": [
      "The beneficiary family should not own a pucca house in their name or in the name of any family member anywhere in India.",
      "The beneficiary family must reside in an urban area (statutory town).",
      "The scheme is available to EWS (Economically Weaker Section), LIG (Low Income Group), and MIG (Middle Income Group).",
      "**Income Criteria:**",
      "EWS: Annual household income up to \u20b93,00,000.",
      "LIG: Annual household income from \u20b93,00,001 to \u20b96,00,000.",
      "MIG I: Annual household income from \u20b96,00,001 to \u20b912,00,000.",
      "MIG II: Annual household income from \u20b912,00,001 to \u20b918,00,000.",
      "For EWS and LIG categories, female ownership or co-ownership of the house is mandatory (except when there is no adult female in the family)."
    ],
    "ineligibilityExclusions": [
      "Families owning a pucca house anywhere in India.",
      "Families who have previously availed central assistance under any housing scheme from the Government of India.",
      "Families whose income exceeds \u20b918,00,000 annually."
    ],
    "requiredDocuments": [
      "Aadhaar Card (mandatory).",
      "PAN Card / Voter ID.",
      "Income Proof (Form 16, ITR, Salary Slips, or Affidavit for EWS/LIG).",
      "Property documents (for BLC or CLSS).",
      "Bank account details."
    ],
    "applicationProcess": [
      "Applicants can apply online at the PMAY-U web portal (pmaymis.gov.in) or offline at Common Service Centers (CSCs) / Urban Local Bodies (ULBs).",
      "For CLSS, individuals apply directly to the banks or housing finance companies for the loan."
    ],
    "officialPortalUrl": "https://pmaymis.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Helps urban families buy or build their first home by offering an upfront interest subsidy up to \u20b92.67 Lakhs on their home loan.",
    "benefitBadge": "\u20b92.67L Subsidy"
  },
  {
    "id": "pmkvy",
    "code": "PMKVY",
    "name": "Pradhan Mantri Kaushal Vikas Yojana",
    "ministry": "Ministry of Skill Development and Entrepreneurship",
    "category": "SKILLS_EDUCATION",
    "targetBeneficiaries": "Youth",
    "maxBenefit": "Free short-term skill training, RPL certification, and placement assistance with a \u20b9500 monetary reward.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "The candidate must be an Indian national.",
      "The scheme is applicable to any candidate of working age (generally between 15-45 years of age).",
      "Target audience: Unemployed youth, school/college dropouts.",
      "Applicant must possess an Aadhaar card and a bank account.",
      "For RPL (Recognition of Prior Learning): Individuals with prior experience in the relevant trade."
    ],
    "ineligibilityExclusions": [
      "Individuals who are currently enrolled in formal schooling or regular college education (except where specified short-term training is allowed).",
      "Candidates who have already obtained a PMKVY certificate for the same job role."
    ],
    "requiredDocuments": [
      "Aadhaar Card.",
      "Two passport-size photographs.",
      "Bank Account Passbook.",
      "Proof of education (if applicable for specific job roles)."
    ],
    "applicationProcess": [
      "Candidates can find a nearby Training Centre through the Skill India Digital portal or PMKVY website (pmkvyofficial.org).",
      "Enroll at the training centre by submitting required documents.",
      "Training is free, and after completion, an assessment is conducted to issue the certificate."
    ],
    "officialPortalUrl": "https://www.pmkvyofficial.org/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides free, industry-relevant skill training and certification to youth to help them secure better jobs and livelihoods.",
    "benefitBadge": "Free Skill Training"
  },
  {
    "id": "pmfby",
    "code": "PMFBY",
    "name": "Pradhan Mantri Fasal Bima Yojana",
    "ministry": "Ministry of Agriculture and Farmers Welfare",
    "category": "AGRICULTURE_FOOD",
    "targetBeneficiaries": "Farmers",
    "maxBenefit": "Comprehensive insurance coverage against crop failure with farmers paying only 1.5% to 2% maximum premium.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "All farmers growing notified crops in a notified area during the season who have an insurable interest in the crop are eligible.",
      "Both loanee farmers (those who have taken agricultural loans/KCC) and non-loanee farmers (those growing crops without bank credit) can participate. Enrollment is voluntary for all farmers.",
      "Tenant farmers and sharecroppers are also eligible."
    ],
    "ineligibilityExclusions": [
      "Damage to harvested crop kept in the field after a specified number of days (usually 14 days) post-harvest.",
      "Wilful damage, theft, or localized damage not covered under the specified localized calamities.",
      "Crops not notified by the State Government for that specific region."
    ],
    "requiredDocuments": [
      "Aadhaar Card.",
      "Land records (Pattadar passbook, Khasra/Khatauni).",
      "Sowing certificate or crop declaration.",
      "Bank account details.",
      "Tenancy agreement (for tenant farmers/sharecroppers)."
    ],
    "applicationProcess": [
      "Farmers can apply online at the National Crop Insurance Portal (pmfby.gov.in).",
      "Offline applications can be submitted through bank branches, Common Service Centres (CSCs), Primary Agricultural Credit Societies (PACS), or insurance brokers.",
      "Loanee farmers can be automatically covered by their bank if they do not opt out."
    ],
    "officialPortalUrl": "https://pmfby.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Protects farmers against crop loss due to natural calamities with highly subsidized insurance premiums (only 1.5% to 2% paid by farmers).",
    "benefitBadge": "Crop Insurance"
  },
  {
    "id": "pmjdy",
    "code": "PMJDY",
    "name": "Pradhan Mantri Jan Dhan Yojana",
    "ministry": "Ministry of Finance",
    "category": "FINANCIAL_INSURANCE",
    "targetBeneficiaries": "Unbanked Citizens",
    "maxBenefit": "Zero balance account, free RuPay debit card, \u20b910,000 overdraft facility, and \u20b92 Lakh accident insurance.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any Indian citizen can open a PMJDY account.",
      "Minors above the age of 10 years can also open a PMJDY account.",
      "Must not already have any other Savings Bank account (or must close it within 30 days of opening PMJDY).",
      "There is no minimum income requirement."
    ],
    "ineligibilityExclusions": [
      "Individuals holding an active regular savings bank account in any bank."
    ],
    "requiredDocuments": [
      "Aadhaar Card (If Aadhaar is present, no other document is required).",
      "If Aadhaar is not available, any officially valid document (OVD) like Voter ID, Driving License, PAN card, Passport, or NREGA card.",
      "Two passport-sized photographs."
    ],
    "applicationProcess": [
      "Application forms are available at all bank branches and Bank Mitras (Business Correspondents).",
      "The account can be opened on the spot using e-KYC."
    ],
    "officialPortalUrl": "https://pmjdy.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Allows any unbanked citizen to open a basic savings bank account with zero minimum balance, free debit card, and in-built insurance.",
    "benefitBadge": "Zero Balance A/C"
  },
  {
    "id": "pmjjby",
    "code": "PMJJBY",
    "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
    "ministry": "Ministry of Finance",
    "category": "FINANCIAL_INSURANCE",
    "targetBeneficiaries": "Citizens",
    "maxBenefit": "\u20b92,00,000 life insurance coverage for death due to any cause at a premium of \u20b9436/year.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any individual possessing a savings bank account or a post office savings bank account.",
      "Age between 18 to 50 years.",
      "The applicant must give consent to join and enable auto-debit of the premium from their account.",
      "The life cover continues up to the age of 55 years provided the individual continues to pay the premium.",
      "An individual can enroll through only one bank account, even if they have multiple accounts."
    ],
    "ineligibilityExclusions": [
      "Individuals below 18 or above 50 years for new enrollment.",
      "If a person has enrolled through multiple bank accounts, the claim will only be paid once, and the extra premium is forfeited.",
      "Suicide is not covered during the first 30 days of enrollment (lien period). Death due to any reason within 30 days of enrollment is not covered (except accident)."
    ],
    "requiredDocuments": [
      "Savings Bank Account details.",
      "Aadhaar Card (primary KYC).",
      "Consent-cum-declaration form for auto-debit."
    ],
    "applicationProcess": [
      "Visit the bank branch or post office where the savings account is held.",
      "Fill the PMJJBY enrollment form and submit it.",
      "Can also be enrolled online via net banking or mobile banking apps of participating banks."
    ],
    "officialPortalUrl": "https://jansuraksha.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "A highly affordable life insurance scheme offering \u20b92 Lakh cover for death due to any reason at just \u20b9436 per year.",
    "benefitBadge": "\u20b92L Life Cover"
  },
  {
    "id": "pmsby",
    "code": "PMSBY",
    "name": "Pradhan Mantri Suraksha Bima Yojana",
    "ministry": "Ministry of Finance",
    "category": "FINANCIAL_INSURANCE",
    "targetBeneficiaries": "Citizens",
    "maxBenefit": "\u20b92,00,000 accidental death/full disability cover, and \u20b91,00,000 for partial disability at \u20b920/year.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any individual with a savings bank account or a post office savings bank account.",
      "Age between 18 to 70 years.",
      "Consent for auto-debit of the premium must be provided.",
      "An individual can join the scheme through only one bank account."
    ],
    "ineligibilityExclusions": [
      "Individuals below 18 or above 70 years.",
      "Death or disability due to natural causes, disease, or suicide is NOT covered. Only accidental death or disability is covered.",
      "Multiple enrollments across different banks will result in a single claim payout and forfeiture of excess premiums."
    ],
    "requiredDocuments": [
      "Savings Bank Account.",
      "Aadhaar Card.",
      "Auto-debit consent form."
    ],
    "applicationProcess": [
      "Apply at the bank branch / post office where the account is maintained.",
      "Submit the consent form.",
      "Enrollment can also be done via internet banking or SMS."
    ],
    "officialPortalUrl": "https://jansuraksha.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "A highly affordable accidental insurance scheme offering \u20b92 Lakh cover for accidental death or full disability at just \u20b920 per year.",
    "benefitBadge": "\u20b92L Accident Cover"
  },
  {
    "id": "pmegp",
    "code": "PMEGP",
    "name": "Prime Minister's Employment Generation Programme",
    "ministry": "Ministry of Micro, Small and Medium Enterprises",
    "category": "SKILLS_EDUCATION",
    "targetBeneficiaries": "Entrepreneurs",
    "maxBenefit": "Margin money subsidy of 15% to 35% on project costs up to \u20b950 Lakhs (manufacturing) or \u20b920 Lakhs (service).",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any individual above 18 years of age.",
      "At least VIII standard pass for projects costing above \u20b910 lakh in the manufacturing sector and above \u20b95 lakh in the business/service sector.",
      "Only new projects are considered for sanction under PMEGP.",
      "Self Help Groups (including those belonging to BPL provided that they have not availed benefits under any other Scheme).",
      "Institutions registered under Societies Registration Act, Production Co-operative Societies, and Charitable Trusts."
    ],
    "ineligibilityExclusions": [
      "Existing Units (under PMRY, REGP or any other scheme of Government of India or State Government) are not eligible.",
      "Units that have already availed Government Subsidy under any other scheme are not eligible."
    ],
    "requiredDocuments": [
      "Aadhaar Card / PAN Card.",
      "Project Report (Business Plan).",
      "Passport Size Photos.",
      "Special Category Certificate (Caste certificate, Disability certificate, Ex-servicemen certificate).",
      "Rural Area certificate (if applicable).",
      "Education/Skill Development training certificate (if applicable)."
    ],
    "applicationProcess": [
      "Apply online at the PMEGP e-Portal (kviconline.gov.in).",
      "The application is scrutinized by the District Level Task Force Committee (DLTFC) and forwarded to banks.",
      "Bank appraises the project and sanctions the loan. After EDP training, the first installment is released and the margin money subsidy is claimed from KVIC."
    ],
    "officialPortalUrl": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a credit-linked subsidy to help unemployed youth and traditional artisans set up new micro-enterprises and generate employment.",
    "benefitBadge": "Up to 35% Subsidy"
  },
  {
    "id": "jjm",
    "code": "JJM",
    "name": "Jal Jeevan Mission",
    "ministry": "Ministry of Jal Shakti",
    "category": "HOUSING_RURAL",
    "targetBeneficiaries": "Rural Household",
    "maxBenefit": "Installation of a functional tap water connection providing 55 liters per capita per day of clean drinking water.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any rural household in India that currently lacks a functional household tap connection.",
      "Schools, Anganwadi centres, Gram Panchayat buildings, health centres, wellness centres, and community buildings in rural areas."
    ],
    "ineligibilityExclusions": [
      "Urban households (which are covered under AMRUT/JJM-Urban).",
      "Households that already have a functional, adequate, and safe tap connection."
    ],
    "requiredDocuments": [
      "Generally, no individual documents are required to apply, as it is a saturation scheme driven at the village level.",
      "Village Action Plan (VAP) is required from the Gram Panchayat."
    ],
    "applicationProcess": [
      "The scheme is implemented by the Village Water and Sanitation Committee (VWSC) or Pani Samiti at the village level.",
      "An individual rural household without a tap can demand connection through their Gram Panchayat or Pani Samiti.",
      "There is no direct online application for individual households; implementation is community-based."
    ],
    "officialPortalUrl": "https://jaljeevanmission.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Aims to provide every rural household with a functional household tap connection ensuring safe and adequate drinking water.",
    "benefitBadge": "Free Tap Water"
  },
  {
    "id": "sbm",
    "code": "SBM",
    "name": "Swachh Bharat Mission",
    "ministry": "Ministry of Drinking Water and Sanitation / MoHUA",
    "category": "HOUSING_RURAL",
    "targetBeneficiaries": "BPL and eligible APL Households",
    "maxBenefit": "Direct incentive of \u20b912,000 for the construction of an individual household latrine (IHHL).",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "**Gramin (Rural)**: BPL households, and identified APL households restricted to SC/STs, small and marginal farmers, landless labourers with homestead, physically handicapped, and women-headed households.",
      "**Urban**: Urban households lacking individual household toilets, and communities lacking public toilets. EWS/LIG populations are prioritized.",
      "The household must not have availed benefits for toilet construction under any other government scheme."
    ],
    "ineligibilityExclusions": [
      "APL (Above Poverty Line) households in rural areas that do not fall into the specified vulnerable categories (they are motivated to build toilets with their own funds).",
      "Households that already possess a functional toilet."
    ],
    "requiredDocuments": [
      "Aadhaar Card.",
      "Bank Account Details.",
      "BPL Card or Proof of belonging to eligible APL categories (SC/ST certificate, Disability certificate).",
      "Photograph of the beneficiary."
    ],
    "applicationProcess": [
      "**Rural**: Apply through the Gram Panchayat or online at the SBM-G portal. Upon verification, the incentive is released in two installments directly to the bank account upon uploading geo-tagged photos of the construction stages.",
      "**Urban**: Apply online at the SBM-Urban portal or via the Urban Local Body (ULB)/Municipality."
    ],
    "officialPortalUrl": "https://swachhbharatmission.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides financial assistance to rural households to construct their own toilets, promoting sanitation and ending open defecation.",
    "benefitBadge": "\u20b912,000 Grant"
  },
  {
    "id": "udid",
    "code": "UDID",
    "name": "Unique Disability ID",
    "ministry": "Ministry of Social Justice and Empowerment",
    "category": "HEALTH_MATERNITY",
    "targetBeneficiaries": "Persons with Disabilities",
    "maxBenefit": "Issuance of a Universal Disability Identity Card validating disability status nationwide.",
    "incomeLimit": "Not specified",
    "eligibilityCriteria": [
      "Any Indian citizen suffering from a disability as recognized under the Rights of Persons with Disabilities Act, 2016.",
      "The 21 recognized disabilities include Blindness, Low-vision, Leprosy Cured persons, Hearing Impairment (deaf and hard of hearing), Locomotor Disability, Dwarfism, Intellectual Disability, Mental Illness, Autism Spectrum Disorder, Cerebral Palsy, Muscular Dystrophy, Chronic Neurological conditions, Specific Learning Disabilities, Multiple Sclerosis, Speech and Language disability, Thalassemia, Hemophilia, Sickle Cell disease, Multiple Disabilities including deaf-blindness, Acid Attack victim, and Parkinson's disease."
    ],
    "ineligibilityExclusions": [
      "Persons who do not have a formally diagnosed disability as per the RPwD Act 2016 parameters."
    ],
    "requiredDocuments": [
      "Recent Color Photograph.",
      "Signature / Thumb Impression.",
      "Address Proof (Aadhaar, Voter ID, Domicile certificate).",
      "Identity Proof (Aadhaar, PAN).",
      "Disability Certificate issued by a competent medical authority (if already available; if not, the applicant is assessed by the medical board after applying)."
    ],
    "applicationProcess": [
      "Register online at the Swavlamban Card portal (swavlambancard.gov.in).",
      "Fill in personal, disability, employment, and identity details.",
      "Upload required documents.",
      "An application number is generated. The applicant has to visit the Chief Medical Officer (CMO) / Medical Board of the district for an assessment of the disability percentage.",
      "Once assessed and approved, the UDID card is generated and mailed to the address."
    ],
    "officialPortalUrl": "https://www.swavlambancard.gov.in/",
    "helplineNumber": "Refer to official portal",
    "plainLanguageSummary": "Provides a single national identity card for persons with disabilities, streamlining access to various government benefits and reservations.",
    "benefitBadge": "Universal ID"
  }
];
