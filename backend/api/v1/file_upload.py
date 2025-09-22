"""
File Upload API Endpoints

API endpoints for secure file upload and validation.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from services.file_upload_service import (
    file_upload_service, validate_file_upload, save_uploaded_file
)
from services.security_service import security_service
from core.auth import get_current_user, AuthUser
from services.file_upload_service import FileUploadConfig, FileType
from utils.secure_faq_parser import parse_faq_file_securely

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload/faq")
async def upload_faq_file(
    request: Request,
    faq_file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Upload and validate FAQ file securely.
    
    This endpoint allows users to upload FAQ files with comprehensive
    security validation and parsing.
    """
    try:
        # CSRF validation is handled by middleware
        
        # Validate file upload
        validation_result = validate_file_upload(faq_file, current_user.id)
        
        if not validation_result["valid"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "File validation failed",
                    "details": validation_result["errors"],
                    "warnings": validation_result.get("warnings", [])
                }
            )
        
        # Check if file type is supported for FAQ parsing
        if validation_result["file_type"] not in [FileType.TEXT, FileType.MARKDOWN]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Unsupported file type for FAQ parsing",
                    "supported_types": ["text", "markdown"]
                }
            )
        
        # Read file content for parsing
        file_content = faq_file.file.read().decode('utf-8', errors='ignore')
        faq_file.file.seek(0)  # Reset to beginning
        
        # Parse FAQ content securely
        try:
            parsed_faq = parse_faq_file_securely(file_content, faq_file.filename)
        except Exception as e:
            logger.error(f"Error parsing FAQ file {faq_file.filename}: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "FAQ parsing failed",
                    "details": str(e)
                }
            )
        
        # Save file if validation and parsing successful
        secure_filename = validation_result["secure_filename"]
        file_path = save_uploaded_file(faq_file, secure_filename, current_user.id)
        
        logger.info(f"FAQ file uploaded successfully: {faq_file.filename} -> {file_path}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "FAQ file uploaded and parsed successfully",
                "file_info": {
                    "original_filename": faq_file.filename,
                    "secure_filename": secure_filename,
                    "file_path": file_path,
                    "file_size": validation_result["file_size"],
                    "file_hash": validation_result["file_hash"],
                    "file_type": validation_result["file_type"]
                },
                "parsed_faq": parsed_faq
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading FAQ file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file upload"
        )


@router.post("/upload/document")
async def upload_document(
    request: Request,
    document_file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Upload and validate document file securely.
    
    This endpoint allows users to upload document files with comprehensive
    security validation.
    """
    try:
        # CSRF validation is handled by middleware
        
        # Validate file upload
        validation_result = validate_file_upload(document_file, current_user.id)
        
        if not validation_result["valid"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "File validation failed",
                    "details": validation_result["errors"],
                    "warnings": validation_result.get("warnings", [])
                }
            )
        
        # Check if file type is supported for document upload
        if validation_result["file_type"] not in [FileType.DOCUMENT, FileType.TEXT, FileType.MARKDOWN]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Unsupported file type for document upload",
                    "supported_types": ["document", "text", "markdown"]
                }
            )
        
        # Save file if validation successful
        secure_filename = validation_result["secure_filename"]
        file_path = save_uploaded_file(document_file, secure_filename, current_user.id)
        
        logger.info(f"Document uploaded successfully: {document_file.filename} -> {file_path}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Document uploaded successfully",
                "file_info": {
                    "original_filename": document_file.filename,
                    "secure_filename": secure_filename,
                    "file_path": file_path,
                    "file_size": validation_result["file_size"],
                    "file_hash": validation_result["file_hash"],
                    "file_type": validation_result["file_type"]
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during document upload"
        )


@router.get("/upload/config")
async def get_upload_config(current_user: AuthUser = Depends(get_current_user)):
    """
    Get file upload configuration for client-side implementation.
    
    Returns configuration information needed for client-side
    file upload handling.
    """
    try:
        config = FileUploadConfig()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "max_file_size_mb": config.get_settings()["max_file_size_mb"],
                "max_files_per_request": config.get_settings()["max_files_per_request"],
                "allowed_extensions": config.get_settings()["allowed_extensions"],
                "allowed_mime_types": config.get_settings()["allowed_mime_types"],
                "supported_file_types": [ft.value for ft in FileType],
                "upload_directory": config.get_upload_directory(),
                "scan_for_malware": config.should_scan_for_malware(),
                "quarantine_suspicious_files": config.should_quarantine_suspicious_files()
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting upload config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upload configuration"
        )


@router.get("/upload/status/{file_hash}")
async def get_upload_status(
    file_hash: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get upload status for a specific file.
    
    Returns information about a previously uploaded file.
    """
    try:
        # In a real implementation, you would query the database for file information
        # For now, we'll return a placeholder response
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "file_hash": file_hash,
                "status": "uploaded",
                "message": "File upload status retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting upload status for file {file_hash}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upload status"
        )


@router.delete("/upload/{file_hash}")
async def delete_uploaded_file(
    file_hash: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Delete an uploaded file.
    
    Allows users to delete files they have uploaded.
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the user owns the file
        # 2. Delete the file from storage
        # 3. Remove the file record from database
        
        logger.info(f"File deletion requested for hash {file_hash} by user {current_user.id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "File deletion requested successfully",
                "file_hash": file_hash
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting file {file_hash}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.get("/upload/quarantine")
async def get_quarantined_files(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get list of quarantined files (admin only).
    
    Returns information about files that were quarantined due to
    security concerns.
    """
    try:
        # Only allow admin users to view quarantined files
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # In a real implementation, you would query the database for quarantined files
        # For now, we'll return a placeholder response
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "quarantined_files": [],
                "total_count": 0,
                "message": "Quarantined files retrieved successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quarantined files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quarantined files"
        )
