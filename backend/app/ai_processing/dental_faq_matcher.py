"""
Production Dental FAQ Matcher and Intent Recognition

Advanced semantic matching system for dental practice voice assistants
with optimized FAQ processing and intelligent intent recognition.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Dental practice intent types."""
    APPOINTMENT_BOOKING = "appointment_booking"
    APPOINTMENT_CANCEL = "appointment_cancel"
    APPOINTMENT_RESCHEDULE = "appointment_reschedule"
    HOURS_INQUIRY = "hours_inquiry"
    INSURANCE_INQUIRY = "insurance_inquiry"
    SERVICES_INQUIRY = "services_inquiry"
    LOCATION_INQUIRY = "location_inquiry"
    EMERGENCY = "emergency"
    PAYMENT_INQUIRY = "payment_inquiry"
    FAQ_SPECIFIC = "faq_specific"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent recognition analysis."""
    intent: IntentType
    confidence: float
    matched_keywords: List[str]
    extracted_entities: Dict[str, Any]
    suggested_response: str
    tenant_specific: bool = False
    faq_matched: Optional[str] = None


@dataclass
class PracticeConfig:
    """Configuration data for a dental practice."""
    practice_id: str
    name: str
    phone_number: Optional[str] = None
    hours_json: Optional[Dict] = None
    insurances_json: Optional[List[str]] = None
    faq_json: Optional[Dict[str, str]] = None
    services_json: Optional[List[str]] = None
    location_json: Optional[Dict] = None


class DentalFAQMatcher:
    """
    Production dental FAQ matching and intent recognition system.
    
    Features:
    - Semantic FAQ matching with configurable thresholds
    - Multi-stage intent recognition (exact, substring, keyword, semantic)
    - Entity extraction for dates, times, services, and insurance
    - Practice-specific response generation
    - Optimized for VAPI webhook integration
    """
    
    def __init__(self):
        """Initialize the FAQ matcher with intent patterns."""
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[IntentType, Dict]:
        """Load intent recognition patterns and responses."""
        return {
            IntentType.APPOINTMENT_BOOKING: {
            "keywords": [
                "schedule", "book", "appointment", "visit", "see doctor",
                "make appointment", "need appointment", "available times",
                "next available", "when can i come", "need to see dentist",
                "checkup", "cleaning", "consultation", "emergency visit"
            ],
            "patterns": [
                r"(?:schedule|book|make)\s+(?:an?\s+)?appointment",
                r"(?:need|want)\s+(?:to\s+)?(?:schedule|book)",
                r"available\s+(?:times?|slots?|appointments?)",
                r"next\s+(?:available|open)\s+(?:slot|time|appointment)",
                r"(?:when|what\s+time)\s+can\s+i\s+(?:come|visit|see)"
            ],
            "response": "I'd be happy to help you schedule an appointment. Let me gather some information to find the best time for you."
        },
            
            IntentType.APPOINTMENT_CANCEL: {
                "keywords": ["cancel", "cancellation", "can't make it", "need to cancel"],
                "patterns": [
                    r"(?:need\s+to\s+|want\s+to\s+)?cancel",
                    r"can'?t\s+make\s+(?:it|my\s+appointment)"
                ],
                "response": "I can help you cancel your appointment. May I have your name and appointment date to locate your booking?"
            },
            
            IntentType.APPOINTMENT_RESCHEDULE: {
                "keywords": ["reschedule", "change appointment", "move appointment", "different time"],
                "patterns": [
                    r"(?:reschedule|change|move)\s+(?:my\s+)?appointment",
                    r"different\s+(?:time|day|date)"
                ],
                "response": "I can help you reschedule your appointment. What would be a better time for you?"
            },
            
            IntentType.HOURS_INQUIRY: {
                "keywords": ["hours", "open", "close", "operating hours", "office hours", "what time"],
                "patterns": [
                    r"(?:office|operating|business)\s+hours",
                    r"what\s+time\s+(?:do\s+you\s+)?(?:open|close)",
                    r"are\s+you\s+open"
                ],
                "response": "Our office hours vary by day. Let me provide you with our current schedule. Is there a specific day you'd like to visit?"
            },
            
            IntentType.INSURANCE_INQUIRY: {
                "keywords": ["insurance", "coverage", "accept", "covered", "plan", "benefits"],
                "patterns": [
                    r"(?:do\s+you\s+)?(?:accept|take)\s+(?:my\s+)?insurance",
                    r"insurance\s+(?:coverage|plans?|benefits)",
                    r"(?:is|am)\s+(?:this|i)\s+covered"
                ],
                "response": "We work with most major insurance plans. What insurance provider do you have? I can verify your coverage."
            },
            
            IntentType.SERVICES_INQUIRY: {
                "keywords": ["services", "treatment", "procedure", "cleaning", "filling", "crown"],
                "patterns": [
                    r"what\s+(?:services|treatments?|procedures?)",
                    r"do\s+you\s+(?:do|offer|provide)",
                    r"(?:cleaning|filling|crown|root\s+canal|whitening)"
                ],
                "response": "We offer comprehensive dental services including cleanings, fillings, crowns, and more. What specific treatment are you interested in?"
            },
            
            IntentType.LOCATION_INQUIRY: {
                "keywords": ["location", "address", "where", "directions", "parking"],
                "patterns": [
                    r"where\s+(?:are\s+you\s+)?(?:located|at)",
                    r"(?:your\s+)?(?:address|location)",
                    r"directions\s+to"
                ],
                "response": "We're conveniently located with easy access and parking. Would you like our address and directions?"
            },
            
            IntentType.EMERGENCY: {
                "keywords": ["emergency", "pain", "urgent", "broke", "lost filling", "swollen"],
                "patterns": [
                    r"(?:dental\s+)?emergency",
                    r"(?:severe|bad|terrible)\s+(?:pain|toothache)",
                    r"(?:broke|lost|fell\s+out)\s+(?:tooth|filling|crown)"
                ],
                "response": "I understand this is urgent. For dental emergencies, please call our emergency line or visit the nearest hospital if severe. Can you describe what happened?"
            },
            
            IntentType.PAYMENT_INQUIRY: {
                "keywords": ["payment", "cost", "price", "how much", "financing", "payment plan"],
                "patterns": [
                    r"(?:how\s+much|what\s+(?:does|is)\s+the\s+cost)",
                    r"payment\s+(?:plans?|options?)",
                    r"(?:financing|credit|payment)\s+available"
                ],
                "response": "We offer flexible payment options and financing plans. Costs vary by treatment. Would you like information about a specific procedure?"
            }
        }
    
    def _normalize_text(self, text: str) -> str:
        """Enhanced text normalization for better FAQ matching."""
        if not text:
            return ""
        
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        
        # Normalize common variations
        normalizations = {
            r'\bu\b': 'you',
            r'\bur\b': 'your', 
            r'\bhrs?\b': 'hours',
            r'\bappt\b': 'appointment',
            r'\bdentist\b': 'dental',
            r'\bdoc\b': 'doctor'
        }
        
        for pattern, replacement in normalizations.items():
            text = re.sub(pattern, replacement, text)
        
        return re.sub(r'\s+', ' ', text).strip()
    
    async def analyze_transcript(
        self, 
        transcript: str, 
        practice_config: Optional[PracticeConfig] = None,
        vapi_call_data: Optional[Dict] = None
    ) -> IntentResult:
        """
        Analyze transcript and return intent with confidence and response.
        
        Args:
            transcript: The conversation transcript to analyze
            practice_config: Practice-specific configuration and FAQs
            vapi_call_data: Additional context from VAPI
            
        Returns:
            IntentResult with analysis and suggested response
        """
        if not transcript or not transcript.strip():
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                extracted_entities={},
                suggested_response="I didn't catch that. Could you please repeat your question?"
            )
        
        normalized_transcript = self._normalize_text(transcript)
        
        # Check practice-specific FAQs first
        if practice_config and practice_config.faq_json:
            faq_result = self._match_practice_faq(normalized_transcript, practice_config)
            if faq_result.confidence >= 0.7:  # High confidence threshold for FAQ match
                return faq_result
        
        # General intent recognition
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        matched_keywords = []
        
        for intent_type, intent_data in self.intent_patterns.items():
            confidence, keywords = self._calculate_intent_confidence(
                normalized_transcript, intent_data
            )
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
                matched_keywords = keywords
        
        # Extract entities
        entities = self._extract_entities(normalized_transcript, best_intent)
        
        # Generate response
        response = self._generate_response(best_intent, entities, practice_config)
        
        return IntentResult(
            intent=best_intent,
            confidence=best_confidence,
            matched_keywords=matched_keywords,
            extracted_entities=entities,
            suggested_response=response,
            tenant_specific=bool(practice_config)
        )
    
    def _match_practice_faq(self, transcript: str, practice_config: PracticeConfig) -> IntentResult:
        """Match transcript against practice-specific FAQs."""
        best_match = ""
        best_similarity = 0.0
        best_answer = ""
        
        for faq_question, faq_answer in practice_config.faq_json.items():
            normalized_question = self._normalize_text(faq_question)
            
            # Calculate similarity using multiple methods
            similarity = max(
                SequenceMatcher(None, transcript, normalized_question).ratio(),
                self._keyword_similarity(transcript, normalized_question),
                self._substring_similarity(transcript, normalized_question)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = faq_question
                best_answer = faq_answer
        
        if best_similarity >= 0.7:  # FAQ match threshold
            return IntentResult(
                intent=IntentType.FAQ_SPECIFIC,
                confidence=best_similarity,
                matched_keywords=[],
                extracted_entities={"response": best_answer},
                suggested_response=best_answer,
                tenant_specific=True,
                faq_matched=best_match
            )
        
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            matched_keywords=[],
            extracted_entities={},
            suggested_response=""
        )
    
    def _calculate_intent_confidence(self, transcript: str, intent_data: Dict) -> Tuple[float, List[str]]:
        """Calculate confidence score for an intent."""
        matched_keywords = []
        keyword_matches = 0
        total_keywords = len(intent_data["keywords"])
        
        # Keyword matching
        for keyword in intent_data["keywords"]:
            if keyword.lower() in transcript:
                matched_keywords.append(keyword)
                keyword_matches += 1
        
        keyword_score = keyword_matches / total_keywords if total_keywords > 0 else 0
        
        # Pattern matching
        pattern_score = 0
        for pattern in intent_data.get("patterns", []):
            if re.search(pattern, transcript, re.IGNORECASE):
                pattern_score = max(pattern_score, 0.8)
        
        # Combined score
        confidence = max(keyword_score * 0.6 + pattern_score * 0.4, pattern_score)
        
        return confidence, matched_keywords
    
    def _keyword_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on common keywords."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        return len(common_words) / max(len(words1), len(words2))
    
    def _substring_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on common substrings."""
        if not text1 or not text2:
            return 0.0
        
        # Find longest common substring
        longer = text1 if len(text1) > len(text2) else text2
        shorter = text2 if len(text1) > len(text2) else text1
        
        max_length = 0
        for i in range(len(shorter)):
            for j in range(i + 3, len(shorter) + 1):  # Minimum 3 chars
                substring = shorter[i:j]
                if substring in longer:
                    max_length = max(max_length, len(substring))
        
        return max_length / max(len(text1), len(text2))
    
    def _extract_entities(self, transcript: str, intent: IntentType) -> Dict[str, Any]:
        """Extract relevant entities from transcript."""
        entities = {}
        
        # Time-related entities
        time_patterns = {
            "time": r"(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))",
            "day": r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow)",
            "date": r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december))"
        }
        
        for entity_type, pattern in time_patterns.items():
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                entities[entity_type] = match.group(1)
        
        # Intent-specific entities
        if intent == IntentType.INSURANCE_INQUIRY:
            insurance_pattern = r"(delta|aetna|cigna|blue\s+cross|humana|metlife|united|anthem)"
            match = re.search(insurance_pattern, transcript, re.IGNORECASE)
            if match:
                entities["insurance_provider"] = match.group(1)
        
        elif intent == IntentType.SERVICES_INQUIRY:
            service_pattern = r"(cleaning|whitening|filling|crown|root\s+canal|extraction|braces|implants)"
            match = re.search(service_pattern, transcript, re.IGNORECASE)
            if match:
                entities["service_type"] = match.group(1)
        
        elif intent == IntentType.EMERGENCY:
            pain_pattern = r"(severe|terrible|unbearable|mild|moderate|intense)"
            match = re.search(pain_pattern, transcript, re.IGNORECASE)
            if match:
                entities["pain_level"] = match.group(1)
        
        return entities
    
    def _generate_response(
        self, 
        intent: IntentType, 
        entities: Dict[str, Any], 
        practice_config: Optional[PracticeConfig] = None
    ) -> str:
        """Generate appropriate response based on intent and practice data."""
        if intent == IntentType.UNKNOWN:
            return self._generate_unknown_response(practice_config)
        
        if intent == IntentType.FAQ_SPECIFIC:
            return entities.get("response", "I can help you with that.")
        
        # Get base response
        base_response = self.intent_patterns[intent]["response"]
        
        # Personalize with practice data
        if practice_config:
            base_response = self._personalize_response(base_response, intent, practice_config)
        
        # Add entity-specific information
        if entities:
            base_response = self._enhance_response_with_entities(base_response, entities, intent)
        
        return base_response
    
    def _generate_unknown_response(self, practice_config: Optional[PracticeConfig] = None) -> str:
        """Generate response for unknown intents."""
        base = "I'm not sure I understand. Could you please tell me how I can help you today?"
        
        if practice_config:
            services = "appointments, insurance questions, office hours, and other inquiries"
            if practice_config.services_json:
                top_services = practice_config.services_json[:3]
                services = f"appointments, {', '.join(top_services)}, and other inquiries"
            return f"{base} I can assist with {services}."
        
        return f"{base} I can assist with appointments, insurance questions, office hours, or other inquiries."
    
    def _personalize_response(
        self, 
        response: str, 
        intent: IntentType, 
        practice_config: PracticeConfig
    ) -> str:
        """Personalize response with practice-specific information."""
        if intent == IntentType.HOURS_INQUIRY and practice_config.hours_json:
            hours_text = self._format_hours(practice_config.hours_json)
            return f"Our office hours are {hours_text}. Is there a specific day you'd like to visit?"
        
        elif intent == IntentType.INSURANCE_INQUIRY and practice_config.insurances_json:
            insurances = practice_config.insurances_json
            if len(insurances) <= 2:
                insurance_text = " and ".join(insurances)
            else:
                insurance_text = ", ".join(insurances[:-1]) + f", and {insurances[-1]}"
            return f"We accept {insurance_text} insurance plans. What insurance do you have?"
        
        elif intent == IntentType.SERVICES_INQUIRY and practice_config.services_json:
            services = practice_config.services_json
            if len(services) <= 2:
                services_text = " and ".join(services)
            else:
                services_text = ", ".join(services[:-1]) + f", and {services[-1]}"
            return f"We offer {services_text}. What specific treatment are you interested in?"
        
        elif intent == IntentType.LOCATION_INQUIRY and practice_config.location_json:
            address = practice_config.location_json.get("address", "our convenient location")
            return f"We're located at {address}. Would you like detailed directions?"
        
        return response
    
    def _format_hours(self, hours_json: Dict) -> str:
        """Format hours JSON into readable text."""
        day_mapping = {
            "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", 
            "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday"
        }
        
        formatted_hours = []
        for day_abbr, times in hours_json.items():
            if times and day_abbr in day_mapping:
                day_name = day_mapping[day_abbr]
                time_range = times[0] if isinstance(times, list) and times else str(times)
                formatted_hours.append(f"{day_name} {time_range}")
        
        return ", ".join(formatted_hours) if formatted_hours else "available upon request"
    
    def _enhance_response_with_entities(
        self, 
        response: str, 
        entities: Dict[str, Any], 
        intent: IntentType
    ) -> str:
        """Enhance response with extracted entity information."""
        if "day" in entities:
            day = entities['day'].lower()
            if day in ['today', 'tomorrow']:
                response += f" For {day}, let me check our availability."
            else:
                response += f" For {entities['day'].title()}, let me check our availability."
        
        if "insurance_provider" in entities:
            provider = entities['insurance_provider'].title()
            response += f" I see you have {provider} insurance."
        
        if "service_type" in entities:
            service = entities['service_type'].replace('_', ' ')
            response += f" You're asking about {service} services."
        
        if "pain_level" in entities:
            response += f" I understand you're experiencing {entities['pain_level']} pain."
        
        return response


# Utility Functions
def create_practice_config_from_db_record(practice_record: Dict) -> PracticeConfig:
    """Create PracticeConfig from database record."""
    return PracticeConfig(
        practice_id=practice_record.get("id", ""),
        name=practice_record.get("name", ""),
        phone_number=practice_record.get("phone_number"),
        hours_json=practice_record.get("hours_json"),
        insurances_json=practice_record.get("insurances_json"),
        faq_json=practice_record.get("faq_json"),
        services_json=practice_record.get("services_json"),
        location_json=practice_record.get("location_json")
    )


def identify_practice_from_vapi_data(vapi_call_data: Dict) -> Optional[str]:
    """
    Identify dental practice from VAPI webhook data.
    
    Supports multiple identification methods:
    - Phone number matching (primary)
    - Assistant ID mapping 
    - Custom metadata
    """
    if not vapi_call_data:
        return None
    
    # Extract nested call data
    message_data = vapi_call_data.get("message", {})
    call_data = message_data.get("call", {}) if isinstance(message_data, dict) else {}
    
    # Method 1: Called phone number (primary for multi-practice)
    called_number = (
        call_data.get("phoneNumber") or 
        call_data.get("phoneNumberId") or
        vapi_call_data.get("phoneNumber")
    )
    if called_number:
        return called_number
    
    # Method 2: Assistant ID
    assistant_id = (
        call_data.get("assistantId") or
        vapi_call_data.get("assistantId")
    )
    if assistant_id:
        return assistant_id
    
    # Method 3: Custom metadata
    metadata_sources = [
        call_data.get("metadata", {}),
        message_data.get("metadata", {}),
        vapi_call_data.get("metadata", {})
    ]
    
    for metadata in metadata_sources:
        if isinstance(metadata, dict):
            practice_id = (
                metadata.get("practice_id") or 
                metadata.get("tenant_id") or
                metadata.get("practiceId")
            )
            if practice_id:
                return practice_id
    
    return None


# Global FAQ matcher instance
faq_matcher = DentalFAQMatcher()