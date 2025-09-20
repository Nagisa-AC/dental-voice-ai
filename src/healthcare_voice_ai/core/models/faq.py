"""
FAQ models for clinic knowledge base management.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class FAQCategory(str, Enum):
    """FAQ category enumeration."""
    GENERAL = "general"
    PRICING = "pricing"
    HOURS = "hours"
    SERVICES = "services"
    INSURANCE = "insurance"
    POLICIES = "policies"
    EMERGENCY = "emergency"
    APPOINTMENTS = "appointments"


class FAQ(BaseModel):
    """Individual FAQ item."""
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer")
    category: Optional[FAQCategory] = Field(None, description="FAQ category")
    keywords: List[str] = Field(default_factory=list, description="Keywords for matching")
    priority: int = Field(default=0, description="Priority for matching (higher = more important)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class OfficeKnowledgeBase(BaseModel):
    """Office knowledge base containing FAQs and custom information."""
    tenant_id: str = Field(..., description="Office tenant ID")
    faqs: List[FAQ] = Field(default_factory=list, description="List of FAQs")
    custom_instructions: List[str] = Field(default_factory=list, description="Custom instructions for assistant")
    office_info: Dict[str, Any] = Field(default_factory=dict, description="Additional office information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def get_faqs_by_category(self, category: FAQCategory) -> List[FAQ]:
        """Get FAQs filtered by category."""
        return [faq for faq in self.faqs if faq.category == category]
    
    def search_faqs(self, query: str) -> List[FAQ]:
        """Search FAQs by question, answer, or keywords."""
        query_lower = query.lower()
        results = []
        
        for faq in self.faqs:
            # Check question
            if query_lower in faq.question.lower():
                results.append(faq)
                continue
            
            # Check answer
            if query_lower in faq.answer.lower():
                results.append(faq)
                continue
            
            # Check keywords
            if any(keyword.lower() in query_lower for keyword in faq.keywords):
                results.append(faq)
                continue
        
        # Sort by priority (higher priority first)
        return sorted(results, key=lambda x: x.priority, reverse=True)


class FAQSubmission(BaseModel):
    """FAQ submission from office owner."""
    tenant_id: str = Field(..., description="Office tenant ID")
    faq_content: str = Field(..., description="Raw FAQ text content")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")
    processed: bool = Field(default=False, description="Whether FAQs have been processed")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors if any")


class FAQProcessingResult(BaseModel):
    """Result of FAQ processing."""
    tenant_id: str = Field(..., description="Office tenant ID")
    total_faqs: int = Field(..., description="Total number of FAQs processed")
    successful_faqs: int = Field(..., description="Number of successfully processed FAQs")
    failed_faqs: int = Field(..., description="Number of failed FAQs")
    errors: List[str] = Field(default_factory=list, description="Processing errors")
    categories_found: List[FAQCategory] = Field(default_factory=list, description="Categories found in FAQs")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")


class FAQResponse(BaseModel):
    """FAQ response model for API endpoints."""
    tenant_id: str
    total_faqs: int
    categories: List[FAQCategory]
    sample_faqs: List[FAQ] = Field(..., description="Sample FAQs (first 5)")
    last_updated: datetime
    processing_status: str = Field(..., description="Processing status")
