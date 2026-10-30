import { BareAct } from '../types';

export const BARE_ACTS_CATALOG: BareAct[] = [
  {
    id: 'rti-2005',
    actCode: 'ACT-22-2005',
    title: 'Right to Information Act, 2005',
    year: 2005,
    actNumber: 'No. 22 of 2005',
    category: 'CIVIC_RIGHTS',
    sectionCount: 31,
    summary: 'Empowers citizens to secure access to information under the control of public authorities, promoting transparency and accountability.',
    keySections: ['Sec 6 (Application)', 'Sec 7 (Disposal of Request - 30 days)', 'Sec 18 (Powers of Commission)', 'Sec 19 (Appeals)', 'Sec 20 (Penalties up to ₹25,000)']
  },
  {
    id: 'cpa-2019',
    actCode: 'ACT-35-2019',
    title: 'Consumer Protection Act, 2019',
    year: 2019,
    actNumber: 'No. 35 of 2019',
    category: 'CONSUMER_COMMERCIAL',
    sectionCount: 107,
    summary: 'Provides protection of consumer interests, establishment of consumer disputes redressal commissions, mediation, and product liability.',
    keySections: ['Sec 2(7) (Consumer Definition)', 'Sec 2(47) (Unfair Trade Practice)', 'Sec 35 (District Commission Complaints)', 'Sec 84 (Product Liability)', 'Sec 88 (Penalties)']
  },
  {
    id: 'tpa-1882',
    actCode: 'ACT-04-1882',
    title: 'Transfer of Property Act, 1882',
    year: 1882,
    actNumber: 'No. 4 of 1882',
    category: 'PROPERTY_HOUSING',
    sectionCount: 137,
    summary: 'Regulates the transfer of property by act of parties, including leases of immovable property, rights and liabilities of lessor and lessee.',
    keySections: ['Sec 105 (Lease Defined)', 'Sec 106 (Duration & Notice Period)', 'Sec 108 (Rights & Liabilities)', 'Sec 111 (Determination of Lease)']
  },
  {
    id: 'rera-2016',
    actCode: 'ACT-16-2016',
    title: 'Real Estate (Regulation and Development) Act, 2016',
    year: 2016,
    actNumber: 'No. 16 of 2016',
    category: 'PROPERTY_HOUSING',
    sectionCount: 92,
    summary: 'Protects buyers of real estate projects, enforces transparency in project execution, mandatory registration, and strict timeline adherence.',
    keySections: ['Sec 18 (Return of Amount and Interest on Delay)', 'Sec 14 (Adherence to Sanctioned Plans)', 'Sec 31 (Filing Complaints)', 'Sec 59 (Penalties)']
  },
  {
    id: 'cpc-1908',
    actCode: 'ACT-05-1908',
    title: 'Code of Civil Procedure, 1908',
    year: 1908,
    actNumber: 'No. 5 of 1908',
    category: 'PENAL_PROCEDURAL',
    sectionCount: 158,
    summary: 'Consolidates and amends laws relating to the procedure of the Courts of Civil Judicature in India.',
    keySections: ['Sec 80 (Notice against Govt Authority)', 'Sec 9 (Courts to try civil suits)', 'Order 39 (Temporary Injunctions)', 'Sec 151 (Inherent Powers)']
  },
  {
    id: 'const-1950',
    actCode: 'CONST-INDIA',
    title: 'Constitution of India, 1950',
    year: 1950,
    actNumber: 'Constitutional Charter',
    category: 'CONSTITUTIONAL',
    sectionCount: 395,
    summary: 'Supreme legal framework laying down fundamental political code, structure, procedures, powers, and fundamental rights of citizens.',
    keySections: ['Art 14 (Equality Before Law)', 'Art 19 (Right to Speech & Expression)', 'Art 21 (Right to Life & Personal Liberty)', 'Art 32 & 226 (Constitutional Remedies)']
  },
  {
    id: 'bns-2023',
    actCode: 'ACT-45-2023',
    title: 'Bharatiya Nyaya Sanhita, 2023',
    year: 2023,
    actNumber: 'No. 45 of 2023',
    category: 'PENAL_PROCEDURAL',
    sectionCount: 358,
    summary: 'Official criminal code of India replacing the Indian Penal Code of 1860, consolidating modern definitions of offenses.',
    keySections: ['Sec 316 (Criminal Breach of Trust)', 'Sec 318 (Cheating)', 'Sec 351 (Criminal Intimidation)', 'Sec 329 (Criminal Trespass)']
  },
  {
    id: 'bnss-2023',
    actCode: 'ACT-46-2023',
    title: 'Bharatiya Nagarik Suraksha Sanhita, 2023',
    year: 2023,
    actNumber: 'No. 46 of 2023',
    category: 'PENAL_PROCEDURAL',
    sectionCount: 531,
    summary: 'Replaces CrPC 1973 for criminal procedural law, arrest, investigation, bail, trial, and digital evidence collection protocols.',
    keySections: ['Sec 173 (Information in Cognizable Cases / Zero FIR)', 'Sec 175 (Investigation Powers)', 'Sec 479 (Bail Procedures)']
  },
  {
    id: 'bsa-2023',
    actCode: 'ACT-47-2023',
    title: 'Bharatiya Sakshya Adhiniyam, 2023',
    year: 2023,
    actNumber: 'No. 47 of 2023',
    category: 'PENAL_PROCEDURAL',
    sectionCount: 170,
    summary: 'Consolidates rules of evidence, admissibility of electronic records, burden of proof, and digital documentation standards.',
    keySections: ['Sec 57 (Primary Evidence)', 'Sec 61 (Electronic Records Admissibility)', 'Sec 63 (Electronic Evidence Certificate)']
  },
  {
    id: 'sra-1963',
    actCode: 'ACT-47-1963',
    title: 'Specific Relief Act, 1963',
    year: 1963,
    actNumber: 'No. 47 of 1963',
    category: 'CIVIC_RIGHTS',
    sectionCount: 44,
    summary: 'Defines and amends the law relating to certain kinds of specific civil reliefs, contract enforcement, and injunctions.',
    keySections: ['Sec 6 (Suit by person dispossessed of immovable property)', 'Sec 10 (Specific Performance of Contract)', 'Sec 38 (Perpetual Injunction)']
  },
  {
    id: 'contract-1872',
    actCode: 'ACT-09-1872',
    title: 'Indian Contract Act, 1872',
    year: 1872,
    actNumber: 'No. 9 of 1872',
    category: 'CONSUMER_COMMERCIAL',
    sectionCount: 238,
    summary: 'Governs law relating to contracts, validity, consideration, breach of contract, indemnity, and damages in India.',
    keySections: ['Sec 10 (What agreements are contracts)', 'Sec 73 (Compensation for loss caused by breach)', 'Sec 74 (Liquidated damages)']
  },
  {
    id: 'it-act-2000',
    actCode: 'ACT-21-2000',
    title: 'Information Technology Act, 2000',
    year: 2000,
    actNumber: 'No. 21 of 2000',
    category: 'CIVIC_RIGHTS',
    sectionCount: 94,
    summary: 'Legal framework for electronic governance, e-commerce, digital signatures, cyber offenses, and privacy protections.',
    keySections: ['Sec 43A (Compensation for failure to protect data)', 'Sec 66C (Identity Theft)', 'Sec 66D (Cheating by personation through computer)']
  },
  {
    id: 'epa-1986',
    actCode: 'ACT-29-1986',
    title: 'Environment (Protection) Act, 1986',
    year: 1986,
    actNumber: 'No. 29 of 1986',
    category: 'ENVIRONMENTAL_LABOR',
    sectionCount: 26,
    summary: 'Provides for the protection and improvement of environment and prevention of hazards to human beings, plants, and property.',
    keySections: ['Sec 7 (Discharge of environmental pollutants)', 'Sec 15 (Penalty for contravention)', 'Sec 19 (Cognizance of offenses by citizens)']
  },
  {
    id: 'ngt-2010',
    actCode: 'ACT-19-2010',
    title: 'National Green Tribunal Act, 2010',
    year: 2010,
    actNumber: 'No. 19 of 2010',
    category: 'ENVIRONMENTAL_LABOR',
    sectionCount: 38,
    summary: 'Establishes a specialized judicial body for environmental disputes, civil damages, and rapid adjudication of ecological violations.',
    keySections: ['Sec 14 (Tribunal Jurisdiction)', 'Sec 15 (Relief, compensation and restitution)', 'Sec 18 (Application to Tribunal)']
  },
  {
    id: 'motor-vehicles-1988',
    actCode: 'ACT-59-1988',
    title: 'Motor Vehicles Act, 1988 (Amended 2019)',
    year: 1988,
    actNumber: 'No. 59 of 1988',
    category: 'CIVIC_RIGHTS',
    sectionCount: 217,
    summary: 'Regulates road transport vehicles, driving licenses, mandatory third-party insurance, and civic road safety standards.',
    keySections: ['Sec 166 (Application for compensation)', 'Sec 198A (Road design authority liability)', 'Sec 134 (Duty of driver in accident)']
  },
  {
    id: 'limitation-1963',
    actCode: 'ACT-36-1963',
    title: 'Limitation Act, 1963',
    year: 1963,
    actNumber: 'No. 36 of 1963',
    category: 'PENAL_PROCEDURAL',
    sectionCount: 32,
    summary: 'Prescribes periods of limitation for suits, appeals, and applications to courts to prevent stale claims.',
    keySections: ['Sec 3 (Bar of limitation)', 'Sec 5 (Condonation of delay)', 'Sec 14 (Exclusion of time of proceeding bona fide in court)']
  }
];

export const CATEGORY_LABELS: Record<BareAct['category'], string> = {
  CIVIC_RIGHTS: 'Civic & Information Rights',
  CONSUMER_COMMERCIAL: 'Consumer & Commercial Law',
  PROPERTY_HOUSING: 'Property & Tenancy Law',
  CONSTITUTIONAL: 'Constitutional Charter',
  PENAL_PROCEDURAL: 'Procedural & Judicial Codes',
  ENVIRONMENTAL_LABOR: 'Environmental & Labor Standards'
};
