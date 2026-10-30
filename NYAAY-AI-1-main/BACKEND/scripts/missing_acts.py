import os
import sys
import json

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.corpus.manifest import CorpusManifestManager

# Rough list of expected acts based on Phase B execution plan
EXPECTED_ACTS = {
    "Constitutional & Administrative": ["Constitution of India", "RTI 2005", "Prevention of Corruption 1988", "Lokpal 2013", "Administrative Tribunals 1985", "Citizenship 1955", "Passport Entry 1920"],
    "Criminal Law": ["BNS 2023", "IPC 1860", "BNSS 2023", "CrPC 1973", "BSA 2023", "Evidence Act 1872", "JJ Act 2015", "POCSO 2012", "SC/ST Act 1989", "NDPS 1985", "Arms Act 1959", "Explosives 1884", "PMLA 2002", "UAPA 1967", "Foreigners 1946"],
    "Property & Real Estate": ["Transfer of Property Act 1882", "Registration Act 1908", "Stamp Act 1899", "RERA 2016", "Land Acquisition 2013", "Benami 1988", "Easements Act 1882", "Government Grants Act 1895"],
    "Civil & Procedural": ["CPC 1908", "Limitation Act 1963", "Arbitration 1996", "Legal Services 1987", "Contempt of Courts 1971", "Court Fees 1870", "Oaths Act 1969"],
    "Contract & Commercial": ["Indian Contract Act 1872", "Sale of Goods 1930", "NI Act 1881", "Partnership 1932", "LLP 2008", "Companies Act 2013", "IBC 2016", "Competition Act 2002", "Specific Relief 1963"],
    "Family Law": ["Hindu Marriage 1955", "Hindu Succession 1956", "Hindu Minority & Guardianship 1956", "Hindu Adoption & Maintenance 1956", "Muslim Personal Law 1937", "Muslim Women (Divorce) 1986", "Muslim Women (Marriage) 2019", "Christian Marriage 1872", "Indian Divorce 1869", "Parsi Marriage 1936", "Special Marriage 1954", "Foreign Marriage 1969", "Guardians & Wards 1890", "DV Act 2005", "Dowry Prohibition 1961", "Senior Citizens 2007", "Child Marriage Prohibition 2006"],
    "Labour & Employment": ["Wages Code 2019", "Industrial Relations Code 2020", "Social Security Code 2020", "OSH Code 2020", "EPF 1952", "ESIC 1948", "POSH 2013", "Maternity Benefit 1961", "Payment of Gratuity 1972", "Contract Labour 1970", "Child Labour 1986", "Bonded Labour 1976"],
    "Consumer & Product": ["Consumer Protection 2019", "BIS 2016", "Legal Metrology 2009", "FSSAI 2006", "Drugs & Cosmetics 1940"],
    "Intellectual Property": ["Patents 1970", "Copyright 1957", "Trade Marks 1999", "Designs 2000", "GI Act 1999", "PPVFR 2001", "SICLD 2000"],
    "Cyber & Technology": ["IT Act 2000", "DPDP 2023", "IT Intermediary Rules 2021", "IT Security Rules 2011", "CERT-In 2022"],
    "Tax Law": ["Income Tax 1961", "CGST/SGST/IGST 2017", "Customs 1962", "Wealth Tax 1957", "Black Money 2015"],
    "Banking & Finance": ["RBI Act 1934", "Banking Regulation 1949", "SARFAESI 2002", "FEMA 1999", "SEBI 1992", "SCRA 1956", "Chit Funds 1982", "Payment Systems 2007"],
    "Environment & Land": ["EPA 1986", "Water Act 1974", "Air Act 1981", "Wildlife Protection 1972", "Forest Rights 2006", "Biological Diversity 2002", "Mines & Minerals 1957"],
    "Healthcare": ["Mental Healthcare 2017", "Clinical Establishments 2010", "Organ Transplant 1994", "PCPNDT 1994", "MTP 1971", "Epidemic Diseases 1897"],
    "Education": ["RTE 2009", "UGC 1956", "AICTE 1987"],
    "Tenant / Housing": ["Model Tenancy 2021", "Maharashtra Rent Control 1999", "Delhi Rent Control 1958", "Tamil Nadu City Tenancy 2017", "TPA Lease Chapters"],
    "Agriculture": ["Essential Commodities 1955", "APMC (state model)", "FPC (Companies Act provisions)"]
}


def print_missing_acts():
    manager = CorpusManifestManager()
    acts = manager.manifest.get("acts", {})
    
    # Extract names or short names of ingested acts to match against our expected list
    ingested_names = [a.get("act_name", "").lower() for a in acts.values()]
    ingested_short = [a.get("short_name", "").lower() for a in acts.values()]
    
    missing_count = 0
    print("Missing Acts:")
    for domain, act_list in EXPECTED_ACTS.items():
        domain_missing = []
        for expected_act in act_list:
            expected_lower = expected_act.lower()
            found = False
            for i_name, i_short in zip(ingested_names, ingested_short):
                if expected_lower in i_name or expected_lower in i_short or i_short in expected_lower:
                    found = True
                    break
            if not found:
                domain_missing.append(expected_act)
                missing_count += 1
                
        if domain_missing:
            print(f"  Domain: {domain}")
            for a in domain_missing:
                print(f"    - {a}")
                
    print(f"\nTotal Missing: {missing_count}")

if __name__ == "__main__":
    print_missing_acts()
