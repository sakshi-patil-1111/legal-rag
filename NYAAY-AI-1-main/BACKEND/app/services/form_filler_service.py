import json
import logging
from typing import Dict, Any, List
from app.ai.llm_client import FallbackGenAIClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# Single Source of Truth for Forms
FORM_TEMPLATES = {
    "RTI_FORM_A": {
        "name": "RTI Application Form A (Section 6(1))",
        "actReference": "Right to Information Act, 2005 (Act No. 22 of 2005)",
        "fields": [
            {
                "id": "APPLICANT_NAME",
                "question": "What is your full legal name as it appears on your government ID?",
                "explanation": "Under Section 6(1) of the RTI Act, any citizen of India is entitled to file an application."
            },
            {
                "id": "APPLICANT_ADDRESS",
                "question": "What postal address should the Public Information Officer mail the certified records to?",
                "explanation": "India Post will deliver the official reply packet to this residential or office address."
            },
            {
                "id": "PUBLIC_AUTHORITY",
                "question": "Which government department, ministry, or civic body holds the records you need?",
                "explanation": "Specifying the exact PIO or department prevents inter-departmental transfer delays under Section 6(3)."
            },
            {
                "id": "SPECIFIC_QUESTIONS",
                "question": "What specific public information or certified documents are you requesting? (Number them clearly)",
                "explanation": "Keep questions objective and focused on certified records, tender files, inspection memos, or ledger entries."
            },
            {
                "id": "FEE_PAYMENT_MODE",
                "question": "How are you submitting the mandatory ₹10 application fee?",
                "explanation": "Central and State rules require a nominal ₹10 fee (exempted for BPL ration card holders)."
            }
        ]
    },
    "CONSUMER_COMPLAINT_EDAIL": {
        "name": "Consumer Commission Grievance Petition (CPA 2019 / e-Daakhil)",
        "actReference": "Consumer Protection Act, 2019 (Act No. 35 of 2019)",
        "fields": [
            {
                "id": "APPLICANT_NAME",
                "question": "Who is the consumer who purchased the defective product or service?",
                "explanation": "The complainant must be the person who paid consideration or the beneficiary under Section 2(7)."
            },
            {
                "id": "OPPOSITE_PARTY",
                "question": "Who is the seller, e-commerce platform, or manufacturer you are claiming against?",
                "explanation": "Both the retailer and manufacturer share product liability under Section 84 of CPA 2019."
            },
            {
                "id": "PRODUCT_DETAILS",
                "question": "What product or service did you purchase, including invoice date and amount paid?",
                "explanation": "State invoice number, price paid, and warranty coverage period."
            },
            {
                "id": "DEFECT_DESCRIPTION",
                "question": "What defect occurred, and what unfair refusal did you receive from the opposite party?",
                "explanation": "Explain the malfunction and how the seller/service center failed to honor warranty."
            },
            {
                "id": "RELIEF_PRAYER",
                "question": "What monetary refund, replacement, or compensation amount are you demanding?",
                "explanation": "You can demand full purchase refund + interest + compensation for mental agony under Section 39."
            }
        ]
    },
    "GRATUITY_FORM_I": {
        "name": "Statutory Gratuity Claim (Form I under Rule 7(1))",
        "actReference": "Payment of Gratuity Act, 1972 & Central Rules, 1972",
        "fields": [
            {
                "id": "APPLICANT_NAME",
                "question": "What is the full name of the employee claiming statutory gratuity?",
                "explanation": "Form I is the statutory application for gratuity submitted to the employer under Rule 7."
            },
            {
                "id": "EMPLOYER_NAME",
                "question": "What is the registered company name and office address of your former employer?",
                "explanation": "Include company headquarters or local branch where you were stationed."
            },
            {
                "id": "TENURE_DATES",
                "question": "What was your date of joining and your official last working day?",
                "explanation": "Continuous service of 5+ years (rendered as 4 yrs 240 days) entitles full gratuity."
            },
            {
                "id": "GRATUITY_CALCULATED_AMOUNT",
                "question": "What is your last drawn Basic+DA salary and calculated gratuity amount?",
                "explanation": "Formula under Section 4(2): (Last Basic + DA / 26) * 15 * Completed Years."
            },
            {
                "id": "BANK_ACCOUNT_DETAILS",
                "question": "What bank account number and IFSC code should gratuity be wired to?",
                "explanation": "Employer is mandated under Section 7(3) to wire funds within 30 days of application."
            }
        ]
    }
}


class FormFillerService:
    def __init__(self):
        self.llm = FallbackGenAIClient()

    def _get_form_template(self, form_id: str):
        if form_id not in FORM_TEMPLATES:
            raise ValueError(f"Unknown form ID: {form_id}")
        return FORM_TEMPLATES[form_id]

    def _determine_current_field(self, template, collected_fields: Dict[str, str]):
        for field in template["fields"]:
            if field["id"] not in collected_fields or not str(collected_fields[field["id"]]).strip():
                return field
        return None  # Complete

    def start_session(self, form_id: str) -> Dict[str, Any]:
        """Initializes a form session and generates a greeting."""
        template = self._get_form_template(form_id)
        first_field = template["fields"][0]
        
        prompt = f"""You are an AI Legal Intake Officer for NYAAY AI.
Your task is to help a citizen fill out the {template['name']} ({template['actReference']}).
Write a friendly, concise, and professional opening greeting (max 30 words) welcoming them, and then ask the very first required question: "{first_field['question']}"
"""
        try:
            response = self.llm.models.generate_content(
                model=settings.CIVIC_MODEL,
                contents=prompt
            )
            ai_text = response.text
        except Exception as e:
            logger.error(f"Failed to generate opening message: {e}")
            ai_text = f"Hello! I am your AI Intake Officer for {template['name']}. I will guide you through a step-by-step interview.\n\n{first_field['question']}"

        return {
            "form_id": form_id,
            "status": "IN_PROGRESS",
            "collected_fields": {},
            "current_field": first_field["id"],
            "ai_response": ai_text
        }

    def process_answer(self, form_id: str, collected_fields: Dict[str, str], user_answer: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Processes a user answer, validates it, and advances the form state."""
        template = self._get_form_template(form_id)
        
        current_field = self._determine_current_field(template, collected_fields)
        if not current_field:
            return {
                "status": "COMPLETE",
                "collected_fields": collected_fields,
                "current_field": None,
                "ai_response": "That's everything I need. Your form is now complete and ready for review."
            }

        # Find what the *next* field would be if this one succeeds
        next_field = None
        for i, field in enumerate(template["fields"]):
            if field["id"] == current_field["id"] and i + 1 < len(template["fields"]):
                next_field = template["fields"][i + 1]
                break

        # Validate with LLM
        prompt = f"""You are an AI Legal Intake Officer helping a user fill out the {template['name']}.
Current Field to fill: "{current_field['question']}"
Next Field to ask (if current is valid): "{next_field['question'] if next_field else 'None (Form Complete)'}"

User's response: "{user_answer}"

Analyze the user's response to see if it adequately answers the "Current Field".
If YES:
1. Extract the clean value for the form.
2. Write a natural conversational response acknowledging it briefly, and then asking the "Next Field" question (if there is one). If there is no next field, say the form is complete.

If NO or AMBIGUOUS:
1. Write a natural conversational response asking for clarification or correcting the user. Do not move on.

Respond ONLY with valid JSON using exactly this schema:
{{
    "is_valid": boolean,
    "extracted_value": "clean value to put in the form, or null if invalid",
    "ai_response": "Your conversational response to the user"
}}
"""
        try:
            response = self.llm.models.generate_content(
                model=settings.CIVIC_MODEL, # Use standard flash for better JSON reasoning
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            result = json.loads(response.text)
        except Exception as e:
            logger.error(f"Failed to process form answer: {e}")
            raise RuntimeError("Failed to process answer with AI. Please try again.")

        is_valid = result.get("is_valid", False)
        ai_response = result.get("ai_response", "I'm sorry, I didn't catch that. Could you please provide your answer again?")
        extracted_value = result.get("extracted_value")

        if is_valid and extracted_value:
            # Advance state
            collected_fields[current_field["id"]] = str(extracted_value)
            
            new_current_field = self._determine_current_field(template, collected_fields)
            status = "COMPLETE" if not new_current_field else "IN_PROGRESS"
            
            return {
                "status": status,
                "collected_fields": collected_fields,
                "current_field": new_current_field["id"] if new_current_field else None,
                "ai_response": ai_response
            }
        else:
            # Do not advance
            return {
                "status": "IN_PROGRESS",
                "collected_fields": collected_fields,
                "current_field": current_field["id"],
                "ai_response": ai_response
            }

    def get_template(self, form_id: str) -> Dict[str, Any]:
        """Returns the raw template data, useful for UI rendering."""
        return self._get_form_template(form_id)

form_filler_service = FormFillerService()
