"""
Secure FAQ Parser

Secure parser for FAQ files with comprehensive validation and sanitization.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import html
import bleach

from services.file_upload_service import file_upload_service
# Local exception classes
class ValidationError(Exception):
    """Validation-related error."""
    pass

class SecurityError(Exception):
    """Security-related error."""
    pass

logger = logging.getLogger(__name__)


class SecureFAQParser:
    """Secure parser for FAQ files with validation and sanitization."""
    
    def __init__(self):
        """Initialize secure FAQ parser."""
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.max_questions = 1000
        self.max_question_length = 500
        self.max_answer_length = 5000
        self.allowed_html_tags = {
            'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
        }
        self.allowed_html_attributes = {
            'class', 'id', 'title', 'lang', 'dir'
        }
    
    def parse_faq_file(self, file_content: str, filename: str) -> Dict[str, Any]:
        """
        Parse FAQ file content securely.
        
        Args:
            file_content: File content as string
            filename: Original filename
            
        Returns:
            Parsed FAQ data
        """
        try:
            # Validate file content
            self._validate_file_content(file_content, filename)
            
            # Detect file format
            file_format = self._detect_file_format(filename, file_content)
            
            # Parse based on format
            if file_format == "markdown":
                return self._parse_markdown_faq(file_content)
            elif file_format == "text":
                return self._parse_text_faq(file_content)
            else:
                raise ValidationError(f"Unsupported file format: {file_format}")
                
        except Exception as e:
            logger.error(f"Error parsing FAQ file {filename}: {e}")
            raise ValidationError(f"Failed to parse FAQ file: {str(e)}")
    
    def _validate_file_content(self, content: str, filename: str) -> None:
        """Validate file content for security and format."""
        # Check file size
        if len(content) > self.max_file_size:
            raise ValidationError(f"File size exceeds maximum allowed size")
        
        # Check for suspicious content
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'eval\s*\(',
            r'document\.cookie',
            r'document\.write',
            r'window\.location',
            r'\.innerHTML\s*=',
            r'\.outerHTML\s*='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise SecurityError(f"Suspicious content detected in file {filename}")
        
        # Check for excessive binary content
        binary_chars = sum(1 for c in content if ord(c) < 32 and c not in '\t\n\r')
        binary_ratio = binary_chars / len(content) if content else 0
        
        if binary_ratio > 0.1:  # More than 10% binary content
            raise ValidationError("File contains excessive binary content")
    
    def _detect_file_format(self, filename: str, content: str) -> str:
        """Detect file format from filename and content."""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.md') or filename_lower.endswith('.markdown'):
            return "markdown"
        elif filename_lower.endswith('.txt'):
            return "text"
        else:
            # Try to detect from content
            if content.strip().startswith('#') or '##' in content:
                return "markdown"
            else:
                return "text"
    
    def _parse_markdown_faq(self, content: str) -> Dict[str, Any]:
        """Parse Markdown FAQ format."""
        questions = []
        current_question = None
        current_answer = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a question (starts with # or ##)
            if line.startswith('#') and not line.startswith('###'):
                # Save previous question if exists
                if current_question:
                    answer = self._sanitize_answer('\n'.join(current_answer))
                    if answer:
                        questions.append({
                            "question": current_question,
                            "answer": answer
                        })
                
                # Start new question
                current_question = self._sanitize_question(line.lstrip('#').strip())
                current_answer = []
            
            elif current_question and line:
                # Add to current answer
                current_answer.append(line)
        
        # Save last question
        if current_question:
            answer = self._sanitize_answer('\n'.join(current_answer))
            if answer:
                questions.append({
                    "question": current_question,
                    "answer": answer
                })
        
        return self._validate_and_format_faq(questions)
    
    def _parse_text_faq(self, content: str) -> Dict[str, Any]:
        """Parse text FAQ format."""
        questions = []
        current_question = None
        current_answer = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a question (starts with Q:, Question:, or similar)
            if re.match(r'^(Q|Question|Q\d+)[:\.]\s*', line, re.IGNORECASE):
                # Save previous question if exists
                if current_question:
                    answer = self._sanitize_answer('\n'.join(current_answer))
                    if answer:
                        questions.append({
                            "question": current_question,
                            "answer": answer
                        })
                
                # Start new question
                question_text = re.sub(r'^(Q|Question|Q\d+)[:\.]\s*', '', line, flags=re.IGNORECASE)
                current_question = self._sanitize_question(question_text)
                current_answer = []
            
            elif current_question and line:
                # Add to current answer
                current_answer.append(line)
        
        # Save last question
        if current_question:
            answer = self._sanitize_answer('\n'.join(current_answer))
            if answer:
                questions.append({
                    "question": current_question,
                    "answer": answer
                })
        
        return self._validate_and_format_faq(questions)
    
    def _sanitize_question(self, question: str) -> str:
        """Sanitize question text."""
        if not question:
            return ""
        
        # Remove HTML tags and decode entities
        question = html.unescape(question)
        question = re.sub(r'<[^>]+>', '', question)
        
        # Limit length
        if len(question) > self.max_question_length:
            question = question[:self.max_question_length] + "..."
        
        # Remove excessive whitespace
        question = re.sub(r'\s+', ' ', question).strip()
        
        return question
    
    def _sanitize_answer(self, answer: str) -> str:
        """Sanitize answer text."""
        if not answer:
            return ""
        
        # Remove HTML tags and decode entities
        answer = html.unescape(answer)
        
        # Allow only safe HTML tags
        answer = bleach.clean(
            answer,
            tags=self.allowed_html_tags,
            attributes=self.allowed_html_attributes,
            strip=True
        )
        
        # Limit length
        if len(answer) > self.max_answer_length:
            answer = answer[:self.max_answer_length] + "..."
        
        # Remove excessive whitespace
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        answer = re.sub(r'[ \t]+', ' ', answer)
        
        return answer.strip()
    
    def _validate_and_format_faq(self, questions: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate and format FAQ data."""
        if not questions:
            raise ValidationError("No valid questions found in FAQ file")
        
        if len(questions) > self.max_questions:
            raise ValidationError(f"Too many questions: {len(questions)} > {self.max_questions}")
        
        # Validate each question
        validated_questions = []
        for i, qa in enumerate(questions):
            if not qa.get("question") or not qa.get("answer"):
                logger.warning(f"Skipping invalid question at index {i}")
                continue
            
            if len(qa["question"]) < 10:
                logger.warning(f"Question too short at index {i}")
                continue
            
            if len(qa["answer"]) < 10:
                logger.warning(f"Answer too short at index {i}")
                continue
            
            validated_questions.append({
                "id": i + 1,
                "question": qa["question"],
                "answer": qa["answer"],
                "category": self._categorize_question(qa["question"]),
                "keywords": self._extract_keywords(qa["question"])
            })
        
        if not validated_questions:
            raise ValidationError("No valid questions found after validation")
        
        return {
            "total_questions": len(validated_questions),
            "questions": validated_questions,
            "categories": list(set(q["category"] for q in validated_questions)),
            "parsed_at": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
    
    def _categorize_question(self, question: str) -> str:
        """Categorize question based on content."""
        question_lower = question.lower()
        
        # Define categories and keywords
        categories = {
            "appointments": ["appointment", "schedule", "booking", "time", "date", "available"],
            "services": ["service", "treatment", "procedure", "cleaning", "checkup", "exam"],
            "insurance": ["insurance", "coverage", "payment", "cost", "price", "bill"],
            "location": ["location", "address", "directions", "parking", "find"],
            "contact": ["contact", "phone", "email", "call", "reach", "speak"],
            "hours": ["hours", "open", "closed", "time", "schedule", "available"],
            "emergency": ["emergency", "urgent", "pain", "hurt", "immediate"],
            "general": ["general", "info", "information", "about", "what", "how"]
        }
        
        # Find best matching category
        best_category = "general"
        max_matches = 0
        
        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in question_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from question."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "can", "what", "when", "where", "why", "how"
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', question.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords, limited to 10
        return list(set(keywords))[:10]


# Global secure FAQ parser instance
secure_faq_parser = SecureFAQParser()


def parse_faq_file_securely(file_content: str, filename: str) -> Dict[str, Any]:
    """Parse FAQ file securely."""
    return secure_faq_parser.parse_faq_file(file_content, filename)
