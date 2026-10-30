import os

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")

def ensure_dir():
    os.makedirs(CORPUS_DIR, exist_ok=True)

def write_file(filename, content):
    with open(os.path.join(CORPUS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

CONSTITUTION_MD = """
# The Constitution of India

## PART III
### FUNDAMENTAL RIGHTS

#### Right to Equality
**Article 14. Equality before law.**
The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.

**Article 15. Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth.**
(1) The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.

#### Right to Freedom
**Article 19. Protection of certain rights regarding freedom of speech, etc.**
(1) All citizens shall have the right—
(a) to freedom of speech and expression;
(b) to assemble peaceably and without arms;
(c) to form associations or unions;
(d) to move freely throughout the territory of India;
(e) to reside and settle in any part of the territory of India; and
(g) to practise any profession, or to carry on any occupation, trade or business.

**Article 21. Protection of life and personal liberty.**
No person shall be deprived of his life or personal liberty except according to procedure established by law.

## PART IV
### DIRECTIVE PRINCIPLES OF STATE POLICY
**Article 39A. Equal justice and free legal aid.**
The State shall secure that the operation of the legal system promotes justice, on a basis of equal opportunity, and shall, in particular, provide free legal aid, by suitable legislation or schemes or in any other way, to ensure that opportunities for securing justice are not denied to any citizen by reason of economic or other disabilities.
"""

BNSS_MD = """
# Bharatiya Nagarik Suraksha Sanhita, 2023

## CHAPTER XII
### INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE

**Section 173. Information in cognizable cases.**
(1) Every information relating to the commission of a cognizable offence, irrespective of the area where the offence is committed, may be given orally or by electronic communication to an officer in charge of a police station, and if given orally, it shall be reduced to writing by him or under his direction, and be read over to the informant.
(2) A copy of the information as recorded under sub-section (1) shall be given forthwith, free of cost, to the informant.
(3) Any person aggrieved by a refusal on the part of an officer in charge of a police station to record the information referred to in sub-section (1) may send the substance of such information, in writing and by post, to the Superintendent of Police concerned who, if satisfied that such information discloses the commission of a cognizable offence, shall either investigate the case himself or direct an investigation to be made by any police officer subordinate to him.
(4) A person can also approach the Magistrate under Section 175(3) of this Sanhita.

**Section 175. Magistrate's power to direct investigation.**
(3) Any Magistrate empowered under section 210 may order such an investigation as above-mentioned.

## CHAPTER XXXV
### BAIL AND BONDS

**Section 479. Maximum period for which an undertrial prisoner can be detained.**
(1) Where a person has, during the period of investigation, inquiry or trial under this Sanhita of an offence under any law (not being an offence for which the punishment of death or life imprisonment has been specified as one of the punishments under that law) undergone detention for a period extending up to one-half of the maximum period of imprisonment specified for that offence under that law, he shall be released by the Court on bail.

**Section 482. Direction for grant of bail to person apprehending arrest (Anticipatory Bail).**
(1) Where any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction under this section that in the event of such arrest he shall be released on bail.
"""

BNS_MD = """
# Bharatiya Nyaya Sanhita, 2023

## CHAPTER VI
### OF OFFENCES AFFECTING THE HUMAN BODY

**Section 103. Punishment for murder.**
(1) Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.

**Section 105. Culpable homicide not amounting to murder.**
Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment of either description for a term which may extend to five years, and shall also be liable to fine.

## CHAPTER XVII
### OF OFFENCES AGAINST PROPERTY

**Section 303. Theft.**
(1) Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.
(2) Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.

**Section 309. Robbery.**
In all robbery there is either theft or extortion. Theft is "robbery" if, in order to the committing of the theft, or in committing the theft, or in carrying away or attempting to carry away property obtained by the theft, the offender, for that end, voluntarily causes or attempts to cause to any person death or hurt or wrongful restraint, or fear of instant death or of instant hurt, or of instant wrongful restraint.
"""

CONTRACT_ACT_MD = """
# Indian Contract Act, 1872

## CHAPTER I
### OF THE COMMUNICATION, ACCEPTANCE AND REVOCATION OF PROPOSALS

**Section 2. Interpretation-clause.**
In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context:
(a) When one person signifies to another his willingness to do or to abstain from doing anything, with a view to obtaining the assent of that other to such act or abstinence, he is said to make a proposal;
(b) When the person to whom the proposal is made signifies his assent thereto, the proposal is said to be accepted. A proposal, when accepted, becomes a promise;
(h) An agreement enforceable by law is a contract.

## CHAPTER VI
### OF THE CONSEQUENCES OF BREACH OF CONTRACT

**Section 73. Compensation for loss or damage caused by breach of contract.**
When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach, or which the parties knew, when they made the contract, to be likely to result from the breach of it.
"""

IT_ACT_MD = """
# Information Technology Act, 2000

## CHAPTER XI
### OFFENCES

**Section 43. Penalty and compensation for damage to computer, computer system, etc.**
If any person without permission of the owner or any other person who is incharge of a computer, computer system or computer network, accesses or secures access to such computer, downloads, copies or extracts any data, or introduces any computer contaminant or computer virus into any computer, he shall be liable to pay damages by way of compensation to the person so affected.

**Section 66. Computer related offences.**
If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.

**Section 66D. Punishment for cheating by personation by using computer resource.**
Whoever, by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.
"""

CONSUMER_MD = """
# Consumer Protection Act, 2019

## CHAPTER I
### PRELIMINARY

**Section 2. Definitions.**
(7) "consumer" means any person who buys any goods for a consideration which has been paid or promised or partly paid and partly promised, or under any system of deferred payment.
(9) "consumer rights" includes the right to be protected against the marketing of goods, products or services which are hazardous to life and property.
(10) "defect" means any fault, imperfection or shortcoming in the quality, quantity, potency, purity or standard which is required to be maintained by or under any law for the time being in force.

## CHAPTER IV
### CONSUMER DISPUTES REDRESSAL COMMISSION

**Section 34. Jurisdiction of District Commission.**
(1) Subject to the other provisions of this Act, the District Commission shall have jurisdiction to entertain complaints where the value of the goods or services paid as consideration does not exceed one crore rupees.
"""

JUDGMENT_KESAVANANDA = """
# Kesavananda Bharati Sripadagalvaru & Ors vs State of Kerala & Anr
**Citation:** (1973) 4 SCC 225
**Court:** Supreme Court of India
**Bench:** S.M. Sikri (CJ), J.M. Shelat, K.S. Hegde, A.N. Grover, A.N. Ray, P. Jaganmohan Reddy, D.G. Palekar, H.R. Khanna, K.K. Mathew, M.H. Beg, S.N. Dwivedi, A.K. Mukherjea, Y.V. Chandrachud
**Date:** 24 April 1973

## Facts
The petitioner, Kesavananda Bharati, head of a Hindu math in Kerala, challenged the Kerala Land Reforms Act, 1963, which sought to impose restrictions on the management of the math's property. He argued that his fundamental rights under Articles 25, 26, and 31 of the Constitution were violated. During the pendency of the petition, the 24th, 25th, and 29th Amendments to the Constitution were passed, which the petitioner also challenged.

## Issues
1. What is the extent of the amending power of Parliament under Article 368 of the Constitution?
2. Does the power to amend include the power to destroy or alter the "basic structure" of the Constitution?

## Arguments
The petitioners argued that the power of Parliament to amend the Constitution under Article 368 is not absolute and cannot be used to alter the fundamental features or the "basic structure" of the Constitution. The respondents (State and Union) argued that the amending power is limitless and encompasses all provisions of the Constitution.

## Reasoning
The majority held that while Parliament has wide powers to amend the Constitution, this power is not absolute. Article 368 does not enable Parliament to alter the basic structure or framework of the Constitution. The Court reasoned that an amendment must leave the fundamental identity of the Constitution intact.

## Ratio Decidendi
Parliament cannot alter the basic structure or framework of the Constitution of India.

## Held
The 24th Amendment is valid, but the power to amend the Constitution under Article 368 is subject to the implied limitation that the basic structure cannot be altered.

## Acts Referenced
- Constitution of India

## Sections Referenced
- Article 368
- Article 13
- Article 25
- Article 26
- Article 31

## Keywords
Basic Structure Doctrine, Amending Power, Fundamental Rights, Constitutional Amendment, Land Reforms.
"""

JUDGMENT_LALITA_KUMARI = """
# Lalita Kumari vs Govt. of U.P. & Ors
**Citation:** (2014) 2 SCC 1
**Court:** Supreme Court of India
**Bench:** P. Sathasivam (CJ), B.S. Chauhan, Ranjana Prakash Desai, Ranjan Gogoi, S.A. Bobde
**Date:** 12 November 2013

## Facts
The petitioner filed a writ petition under Article 32 of the Constitution, stating that the police had refused to register an FIR regarding the kidnapping of his minor daughter. He approached the Superintendent of Police but no action was taken.

## Issues
Whether a police officer is bound to register a First Information Report (FIR) upon receiving any information relating to commission of a cognizable offence under Section 154 of the Code of Criminal Procedure, 1973 (now Section 173 of BNSS, 2023), or whether the police officer has the power to conduct a preliminary inquiry in order to test the veracity of such information before registering the FIR.

## Arguments
The petitioners argued that Section 154 uses the word "shall", making the registration of an FIR mandatory if the information discloses a cognizable offence. The respondents argued that a preliminary inquiry is necessary to prevent frivolous or malicious complaints.

## Reasoning
The Court emphasized the mandatory nature of Section 154 (now 173 BNSS). The legislative intent behind the use of the word "shall" leaves no discretion to the police officer if the information discloses a cognizable offence. The Court reasoned that mandatory registration of FIRs guarantees transparency, upholds the rule of law, and ensures the victim's right to justice. Preliminary inquiries are only permitted in specific categories of cases (e.g., matrimonial disputes, commercial offences, medical negligence, corruption cases) or when there is a delay in reporting.

## Ratio Decidendi
Registration of FIR is mandatory under Section 154 of the CrPC (Section 173 BNSS) if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation.

## Held
The Court issued mandatory guidelines stating that FIR registration is obligatory if a cognizable offence is disclosed. If the information does not disclose a cognizable offence but indicates the necessity for an inquiry, a preliminary inquiry may be conducted only to ascertain whether a cognizable offence is disclosed or not.

## Acts Referenced
- Code of Criminal Procedure, 1973
- Bharatiya Nagarik Suraksha Sanhita, 2023
- Constitution of India

## Sections Referenced
- Section 154 CrPC
- Section 173 BNSS
- Article 32

## Keywords
Mandatory FIR, Cognizable Offence, Preliminary Inquiry, Police Officer Duty.
"""

if __name__ == "__main__":
    ensure_dir()
    write_file("Constitution_of_India.md", CONSTITUTION_MD)
    write_file("Bharatiya_Nagarik_Suraksha_Sanhita.md", BNSS_MD)
    write_file("Bharatiya_Nyaya_Sanhita.md", BNS_MD)
    write_file("Indian_Contract_Act.md", CONTRACT_ACT_MD)
    write_file("Information_Technology_Act.md", IT_ACT_MD)
    write_file("Consumer_Protection_Act.md", CONSUMER_MD)
    
    write_file("judgment_kesavananda_bharati.md", JUDGMENT_KESAVANANDA)
    write_file("judgment_lalita_kumari.md", JUDGMENT_LALITA_KUMARI)
    print("Authentic Knowledge Base files generated.")
