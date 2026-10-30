import os

RAW_DIR = "C:/Users/ANSH DARJI/Documents/NYAAY AI/BACKEND/data/raw/"
os.makedirs(RAW_DIR, exist_ok=True)

tier_1_acts = {
    "BSA_2023.txt": """PART I
PRELIMINARY

1. Short title, extent and commencement.
(1) This Act may be called the Bharatiya Sakshya Adhiniyam, 2023.
(2) It extends to the whole of India.
(3) It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.

PART II
RELEVANCY OF FACTS
CHAPTER I
GENERAL

2. Definitions.
In this Adhiniyam, unless the context otherwise requires,—
(a) "Court" includes all Judges and Magistrates, and all persons, except arbitrators, legally authorised to take evidence;
(b) "Document" means any matter expressed or described upon any substance by means of letters, figures or marks.

CHAPTER II
RELEVANCY OF FACTS

3. Evidence may be given of facts in issue and relevant facts.
Evidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.
""",
    "CPC_1908.txt": """PART I
SUITS IN GENERAL

1. Short title, commencement and extent.
(1) This Act may be cited as the Code of Civil Procedure, 1908.
(2) It shall come into force on the first day of January, 1909.

CHAPTER I
JURISDICTION OF THE COURTS AND RES JUDICATA

9. Courts to try all civil suits unless barred.
The Courts shall (subject to the provisions herein contained) have jurisdiction to try all suits of a civil nature excepting suits of which their cognizance is either expressly or impliedly barred.

10. Stay of suit.
No Court shall proceed with the trial of any suit in which the matter in issue is also directly and substantially in issue in a previously instituted suit between the same parties.

11. Res judicata.
No Court shall try any suit or issue in which the matter directly and substantially in issue has been directly and substantially in issue in a former suit between the same parties.
""",
    "Hindu_Marriage_Act_1955.txt": """PART I
PRELIMINARY

1. Short title and extent.
(1) This Act may be called the Hindu Marriage Act, 1955.
(2) It extends to the whole of India except the State of Jammu and Kashmir, and applies also to Hindus domiciled in the territories to which this Act extends who are outside the said territories.

CHAPTER II
HINDU MARRIAGES

5. Conditions for a Hindu marriage.
A marriage may be solemnized between any two Hindus, if the following conditions are fulfilled, namely:—
(i) neither party has a spouse living at the time of the marriage;
(ii) at the time of the marriage, neither party is incapable of giving a valid consent to it in consequence of unsoundness of mind.

13. Divorce.
(1) Any marriage solemnized, whether before or after the commencement of this Act, may, on a petition presented by either the husband or the wife, be dissolved by a decree of divorce on the ground that the other party—
(i) has, after the solemnization of the marriage, had voluntary sexual intercourse with any person other than his or her spouse.
"""
}

for filename, content in tier_1_acts.items():
    with open(os.path.join(RAW_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip())

print(f"Created {len(tier_1_acts)} raw Tier 1 Act text files.")
