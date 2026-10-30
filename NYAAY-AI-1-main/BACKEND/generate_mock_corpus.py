import os

os.makedirs('data/corpus', exist_ok=True)

bns_content = """PART I
PRELIMINARY
CHAPTER I
INTRODUCTION
Section 1. Short title, extent and commencement.
(1) This Act may be called the Bharatiya Nyaya Sanhita, 2023.
(2) It extends to the whole of India.
(3) It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.

CHAPTER VI
OF OFFENCES AFFECTING THE HUMAN BODY
Of Offences Affecting Life
Section 101. Murder.
Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.

Section 102. Culpable homicide not amounting to murder.
Whoever commits culpable homicide not amounting to murder, shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine, if the act by which the death is caused is done with the intention of causing death, or of causing such bodily injury as is likely to cause death;

Section 103. Punishment for murder.
(1) Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.
(2) When a group of five or more persons acting in concert commits murder on the ground of race, caste or community, sex, place of birth, language, personal belief or any other similar ground each member of such group shall be punished with death or with imprisonment for life, and shall also be liable to fine.
"""

constitution_content = """PART III
FUNDAMENTAL RIGHTS
Right to Equality
Article 14. Equality before law.
The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.

Article 15. Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth.
(1) The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.
(2) No citizen shall, on grounds only of religion, race, caste, sex, place of birth or any of them, be subject to any disability, liability, restriction or condition with regard to—
(a) access to shops, public restaurants, hotels and places of public entertainment; or
(b) the use of wells, tanks, bathing ghats, roads and places of public resort maintained wholly or partly out of State funds or dedicated to the use of the general public.

Article 21. Protection of life and personal liberty.
No person shall be deprived of his life or personal liberty except according to procedure established by law.
"""

bnss_content = """PART I
CHAPTER I
Section 1. Short title, extent and commencement.
This Act may be called the Bharatiya Nagarik Suraksha Sanhita, 2023.

CHAPTER XII
INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE
Section 173. Information in cognizable cases.
(1) Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it, and the substance thereof shall be entered in a book to be kept by such officer in such form as the State Government may prescribe in this behalf:
Provided that if the information is given by the woman against whom an offence under section 64, section 65, section 66, section 67, section 68, section 69, section 70, section 71, section 74, section 75, section 76, section 77, section 78, section 79 or section 124 of the Bharatiya Nyaya Sanhita, 2023 is alleged to have been committed or attempted, then such information shall be recorded, by a woman police officer or any woman officer:
"""

bsa_content = """PART I
CHAPTER I
Section 1. Short title, extent and commencement.
This Act may be called the Bharatiya Sakshya Adhiniyam, 2023.

CHAPTER II
OF THE RELEVANCY OF FACTS
Section 5. Evidence may be given of facts in issue and relevant facts.
Evidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.
Explanation.—This section shall not enable any person to give evidence of a fact which he is disentitled to prove by any provision of the law for the time being in force relating to Civil Procedure.
"""

with open('data/corpus/bns.txt', 'w', encoding='utf-8') as f:
    f.write(bns_content)
with open('data/corpus/constitution.txt', 'w', encoding='utf-8') as f:
    f.write(constitution_content)
with open('data/corpus/bnss.txt', 'w', encoding='utf-8') as f:
    f.write(bnss_content)
with open('data/corpus/bsa.txt', 'w', encoding='utf-8') as f:
    f.write(bsa_content)

print("Mock Corpus generated successfully in data/corpus/")
