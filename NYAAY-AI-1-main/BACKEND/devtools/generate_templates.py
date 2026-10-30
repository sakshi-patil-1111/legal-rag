import os
import json

base_dir = r"C:\Users\ANSH DARJI\Documents\NYAAY AI\BACKEND\app\templates"

templates = {
    "POLICE_COMPLAINT": {
        "schema": {
            "mandatory_fields": ["complainant_name", "incident_date", "incident_location", "police_station", "accused_name_or_description", "brief_facts"],
            "optional_fields": ["witnesses", "evidence"]
        },
        "instructions": "Draft a formal criminal complaint to the Station House Officer (SHO). Begin with 'To, The Station House Officer, [Police Station], [District]'. Subject should clearly state the offenses. The body must chronologically narrate the incident."
    },
    "SP_COMPLAINT": {
        "schema": {
            "mandatory_fields": ["complainant_name", "sp_office_location", "previous_complaint_details", "brief_facts"],
            "optional_fields": []
        },
        "instructions": "Draft a complaint to the Superintendent of Police under Section 154(3) CrPC / corresponding BNSS section, when the local SHO refuses to register an FIR. State that a prior complaint was made but no action was taken."
    },
    "AFFIDAVIT": {
        "schema": {
            "mandatory_fields": ["deponent_name", "father_or_spouse_name", "age", "address", "purpose_of_affidavit", "facts"],
            "optional_fields": []
        },
        "instructions": "Draft a sworn affidavit. Begin with 'I, [Name], son/wife of [Name], aged [Age], residing at [Address], do hereby solemnly affirm and state as follows:'. Use numbered paragraphs starting with 'That...'. Conclude with a Verification clause: 'Verified at [Place] on this [Date] that the contents of paragraphs 1 to X are true and correct to my knowledge and belief.'"
    },
    "LEGAL_NOTICE": {
        "schema": {
            "mandatory_fields": ["sender_name", "recipient_name", "recipient_address", "cause_of_action", "demand", "deadline_in_days"],
            "optional_fields": []
        },
        "instructions": "Draft a formal legal notice sent by an advocate on behalf of a client. Use the header 'REGD. A.D. / SPEED POST'. Address the recipient formally. Narrate facts clearly, state the legal grievance, and explicitly state the demand and the deadline (e.g. 15 days) failing which legal action will be initiated."
    },
    "CONSUMER_COMPLAINT": {
        "schema": {
            "mandatory_fields": ["complainant_name", "opposite_party_name", "transaction_date", "amount_paid", "deficiency_in_service", "relief_sought"],
            "optional_fields": ["bill_no"]
        },
        "instructions": "Draft a complaint for the District Consumer Disputes Redressal Commission. Format as 'BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT [DISTRICT]'. Include Cause Title (Complainant vs Opposite Party). Detail the deficiency in service or unfair trade practice."
    },
    "RTI_APPLICATION": {
        "schema": {
            "mandatory_fields": ["applicant_name", "applicant_address", "public_information_officer_designation", "department", "information_sought"],
            "optional_fields": ["application_fee_details"]
        },
        "instructions": "Draft an application under the Right to Information Act, 2005. Address it to the Public Information Officer (PIO). Provide a clear, bulleted list of the exact information sought. Conclude with a statement that the fee has been paid."
    },
    "REPRESENTATION": {
        "schema": {
            "mandatory_fields": ["applicant_name", "authority_designation", "department", "grievance", "relief_sought"],
            "optional_fields": []
        },
        "instructions": "Draft a formal representation/petition to a government authority or department regarding a grievance. Maintain a respectful, formal tone (e.g. 'Respected Sir/Madam,')."
    },
    "DECLARATION": {
        "schema": {
            "mandatory_fields": ["declarant_name", "father_name", "address", "declaration_subject"],
            "optional_fields": []
        },
        "instructions": "Draft a general declaration (uncorroborated by oath, unlike an affidavit). State the facts clearly. End with a signature block and date/place."
    },
    "INDEMNITY_BOND": {
        "schema": {
            "mandatory_fields": ["executant_name", "beneficiary_name", "reason_for_indemnity", "maximum_liability_amount"],
            "optional_fields": []
        },
        "instructions": "Draft an Indemnity Bond. Begin with 'THIS DEED OF INDEMNITY is made at [Place] on [Date] by...'. Clearly state that the executant agrees to indemnify and hold harmless the beneficiary from all losses, damages, or claims arising out of the specified reason."
    },
    "POWER_OF_ATTORNEY": {
        "schema": {
            "mandatory_fields": ["principal_name", "agent_name", "specific_powers_granted", "duration_if_any"],
            "optional_fields": []
        },
        "instructions": "Draft a Special Power of Attorney (SPA) or General Power of Attorney (GPA). Begin 'KNOW ALL MEN BY THESE PRESENTS that I, [Principal]... do hereby appoint [Agent] as my true and lawful attorney...'. Enumerate the powers clearly in numbered bullet points."
    }
}

os.makedirs(base_dir, exist_ok=True)

for tmpl, data in templates.items():
    folder = os.path.join(base_dir, tmpl.lower())
    os.makedirs(folder, exist_ok=True)
    
    with open(os.path.join(folder, "schema.json"), "w") as f:
        json.dump(data["schema"], f, indent=2)
        
    with open(os.path.join(folder, "instructions.md"), "w") as f:
        f.write(data["instructions"])

print("Successfully generated all 10 templates.")
