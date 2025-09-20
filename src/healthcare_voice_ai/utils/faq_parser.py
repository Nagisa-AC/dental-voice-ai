"""
FAQ parsing utilities for processing text files into structured FAQ data.
"""

import re
import logging
from typing import List, Tuple, Optional
from healthcare_voice_ai.core.models.faq import FAQ, FAQCategory

logger = logging.getLogger(__name__)


class FAQParser:
    """Parser for converting text FAQ files into structured FAQ objects."""
    
    def __init__(self):
        """Initialize the FAQ parser."""
        self.question_patterns = [
            r'^Q:\s*(.+)$',
            r'^Question:\s*(.+)$',
            r'^Q\s*\d*[\.\)]\s*(.+)$',
            r'^\d+[\.\)]\s*(.+)\?$',
            r'^(.+)\?$'
        ]
        self.answer_patterns = [
            r'^A:\s*(.+)$',
            r'^Answer:\s*(.+)$',
            r'^A\s*\d*[\.\)]\s*(.+)$'
        ]
    
    def parse_text_content(self, content: str) -> List[FAQ]:
        """
        Parse text content into a list of FAQ objects.
        
        Args:
            content: Raw text content from FAQ file
            
        Returns:
            List of FAQ objects
        """
        try:
            # Clean and normalize the content
            content = self._clean_content(content)
            
            # Split into lines and process
            lines = content.split('\n')
            faqs = []
            current_question = None
            current_answer = None
            current_category = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a question
                question_match = self._match_question(line)
                if question_match:
                    # Save previous FAQ if we have one
                    if current_question and current_answer:
                        faq = self._create_faq(current_question, current_answer, current_category)
                        faqs.append(faq)
                    
                    # Start new FAQ
                    current_question = question_match
                    current_answer = None
                    current_category = self._detect_category(current_question)
                    continue
                
                # Check if this is an answer
                answer_match = self._match_answer(line)
                if answer_match:
                    current_answer = answer_match
                    continue
                
                # If we have a question but no answer yet, this might be part of the question
                if current_question and not current_answer:
                    current_question += " " + line
                    continue
                
                # If we have an answer, this might be part of the answer
                if current_answer:
                    current_answer += " " + line
                    continue
            
            # Don't forget the last FAQ
            if current_question and current_answer:
                faq = self._create_faq(current_question, current_answer, current_category)
                faqs.append(faq)
            
            logger.info(f"Successfully parsed {len(faqs)} FAQs from text content")
            return faqs
            
        except Exception as e:
            logger.error(f"Error parsing FAQ content: {e}")
            return []
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize the content."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common headers/footers
        content = re.sub(r'FREQUENTLY ASKED QUESTIONS.*?\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'FAQ.*?\n', '', content, flags=re.IGNORECASE)
        
        # Normalize line breaks
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content.strip()
    
    def _match_question(self, line: str) -> Optional[str]:
        """Check if a line matches a question pattern."""
        for pattern in self.question_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                question = match.group(1).strip()
                # Ensure it ends with a question mark
                if not question.endswith('?'):
                    question += '?'
                return question
        return None
    
    def _match_answer(self, line: str) -> Optional[str]:
        """Check if a line matches an answer pattern."""
        for pattern in self.answer_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit answer pattern, but we're in answer mode, treat as answer
        return line if line else None
    
    def _detect_category(self, question: str) -> Optional[FAQCategory]:
        """Detect FAQ category based on question content."""
        question_lower = question.lower()
        
        # Pricing keywords
        if any(keyword in question_lower for keyword in ['cost', 'price', 'fee', 'charge', 'expensive', 'cheap', 'payment']):
            return FAQCategory.PRICING
        
        # Hours keywords
        if any(keyword in question_lower for keyword in ['hour', 'open', 'close', 'time', 'when', 'available']):
            return FAQCategory.HOURS
        
        # Services keywords
        if any(keyword in question_lower for keyword in ['service', 'treatment', 'procedure', 'offer', 'do you']):
            return FAQCategory.SERVICES
        
        # Insurance keywords
        if any(keyword in question_lower for keyword in ['insurance', 'coverage', 'plan', 'accept']):
            return FAQCategory.INSURANCE
        
        # Policies keywords
        if any(keyword in question_lower for keyword in ['policy', 'cancel', 'reschedule', 'appointment', 'book']):
            return FAQCategory.POLICIES
        
        # Emergency keywords
        if any(keyword in question_lower for keyword in ['emergency', 'urgent', 'pain', 'hurt', 'broken']):
            return FAQCategory.EMERGENCY
        
        return FAQCategory.GENERAL
    
    def _create_faq(self, question: str, answer: str, category: Optional[FAQCategory]) -> FAQ:
        """Create an FAQ object with extracted keywords."""
        keywords = self._extract_keywords(question)
        
        return FAQ(
            question=question,
            answer=answer,
            category=category,
            keywords=keywords,
            priority=self._calculate_priority(question, category)
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove common words
        stop_words = {
            'what', 'how', 'do', 'does', 'is', 'are', 'can', 'could', 'would', 'should',
            'will', 'when', 'where', 'why', 'who', 'which', 'the', 'a', 'an', 'and',
            'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
            'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'among', 'your', 'you', 'we', 'our', 'us', 'i', 'me',
            'my', 'mine', 'this', 'that', 'these', 'those', 'there', 'here', 'now',
            'then', 'so', 'if', 'because', 'as', 'like', 'very', 'just', 'only',
            'also', 'too', 'either', 'neither', 'both', 'all', 'some', 'any', 'no',
            'not', 'yes', 'no', 'maybe', 'perhaps', 'probably', 'definitely'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Remove duplicates and limit to top 10
        return list(dict.fromkeys(keywords))[:10]
    
    def _calculate_priority(self, question: str, category: Optional[FAQCategory]) -> int:
        """Calculate priority for FAQ matching."""
        priority = 0
        
        # Category-based priority
        if category == FAQCategory.EMERGENCY:
            priority += 100
        elif category == FAQCategory.HOURS:
            priority += 80
        elif category == FAQCategory.PRICING:
            priority += 60
        elif category == FAQCategory.SERVICES:
            priority += 40
        elif category == FAQCategory.POLICIES:
            priority += 30
        
        # Question length priority (shorter questions are often more important)
        if len(question) < 50:
            priority += 20
        elif len(question) < 100:
            priority += 10
        
        # Common question patterns
        if any(pattern in question.lower() for pattern in ['what are', 'how much', 'when are', 'do you']):
            priority += 15
        
        return priority


def parse_faq_file(content: str) -> List[FAQ]:
    """
    Convenience function to parse FAQ content.
    
    Args:
        content: Raw text content from FAQ file
        
    Returns:
        List of FAQ objects
    """
    parser = FAQParser()
    return parser.parse_text_content(content)
