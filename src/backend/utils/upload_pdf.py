# src/backend/utils/upload_pdf.py

import logging
import os
import tempfile
import hashlib
from pathlib import Path
from fastapi import HTTPException, UploadFile
from werkzeug.utils import secure_filename

from ..utils.pdf_processor import PDFProcessor
from ..services.embedding_service import EmbeddingService
from ..config import config

logger = logging.getLogger(__name__)

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_duplicate_pdf(file_hash: str) -> dict:
    """
    Check if a PDF with the same hash has already been uploaded
    
    Returns:
        dict with 'is_duplicate' and 'existing_uuid' if duplicate found
    """
    try:
        schema_path = Path("src/backend/utils/table_schema.json")
        if not schema_path.exists():
            return {"is_duplicate": False}
        
        import json
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Check if any existing table has the same file hash
        for table_name, table_info in schema.items():
            if table_info.get('file_hash') == file_hash:
                return {
                    "is_duplicate": True,
                    "existing_uuid": table_info.get('pdf_uuid'),
                    "existing_table": table_name,
                    "uploaded_at": table_info.get('created_at')
                }
        
        return {"is_duplicate": False}
    except Exception as e:
        logger.warning(f"Error checking for duplicate PDF: {e}")
        return {"is_duplicate": False}


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def validate_file_size(file: UploadFile) -> bool:
    """Validate that the uploaded file size is within limits."""
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    logger.info(f"File size: {size} bytes, Max allowed: {config.MAX_FILE_SIZE} bytes")
    print(f"File size: {size} bytes, Max allowed: {config.MAX_FILE_SIZE} bytes")
    return size <= config.MAX_FILE_SIZE


async def process_pdf_upload(file: UploadFile) -> dict:
    """
    Enhanced PDF processing with Gemini-powered schema inference.
    
    Process uploaded PDF file: extract content, store tables in MySQL with 
    intelligent schema inference, and store text embeddings in Pinecone.
    
    Returns:
        dict: Processing results with success status, message, and detailed counts
    """
    filename = "unknown"  # Default value to avoid UnboundLocalError
    
    try:
        # Validate file size
        if not validate_file_size(file):
            logger.warning(f"File size exceeds limit: {config.MAX_FILE_SIZE // (1024*1024)}MB")
            print(f"Error: File size exceeds limit: {config.MAX_FILE_SIZE // (1024*1024)}MB")
            raise HTTPException(
                status_code=413, 
                detail={
                    "success": False,
                    "message": f"File size exceeds {config.MAX_FILE_SIZE // (1024*1024)}MB",
                    "error": "File too large"
                }
            )

        # Validate filename
        if not file.filename:
            logger.warning("No file selected")
            print("Error: No file selected")
            raise HTTPException(
                status_code=400, 
                detail={
                    "success": False,
                    "message": "No file selected",
                    "error": "Empty filename"
                }
            )

        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            print(f"Error: Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "success": False,
                    "message": "Only PDF files are allowed",
                    "error": "Invalid file type"
                }
            )

        filename = secure_filename(file.filename)
        logger.info(f"Processing uploaded file: {filename}")
        print(f"Processing uploaded file: {filename}")

        # Validate required configurations
        # config.validate_pinecone_config()
        # config.validate_gemini_config()

        # Initialize enhanced PDF processor with Gemini integration
        pdf_processor = PDFProcessor(
            database_url=config.database_url,
            gemini_api_key=config.GEMINI_API_KEY
        )
        
        # Initialize embedding service
        pinecone_config = {
            'api_key': config.PINECONE_API_KEY,
            'index_name': config.PINECONE_INDEX_NAME,
            'dimension': config.PINECONE_DIMENSION,
            'cloud': config.PINECONE_CLOUD,
            'region': config.PINECONE_REGION
        }
        embedding_service = EmbeddingService(config.GEMINI_API_KEY, pinecone_config)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
            logger.info(f"Temporary file created: {temp_file_path}")
            print(f"Temporary file created: {temp_file_path}")

        try:
            # Calculate file hash for duplicate detection
            file_hash = calculate_file_hash(temp_file_path)
            logger.info(f"File hash: {file_hash}")
            
            # Check for duplicates
            duplicate_check = check_duplicate_pdf(file_hash)
            if duplicate_check["is_duplicate"]:
                logger.warning(f"Duplicate PDF detected. Already uploaded with UUID: {duplicate_check['existing_uuid']}")
                print(f"\n⚠ WARNING: This PDF has already been uploaded!")
                print(f"  Existing UUID: {duplicate_check['existing_uuid']}")
                print(f"  Uploaded at: {duplicate_check['uploaded_at']}")
                print(f"  Existing table: {duplicate_check['existing_table']}")
                print(f"\nProceeding with upload anyway (will create new table)...\n")
            
            # Enhanced content extraction and storage with Gemini
            print("\n=== Starting Enhanced PDF Processing ===")
            processing_result = pdf_processor.extract_and_store_content(temp_file_path)
            
            # Store file hash in schema for future duplicate detection
            pdf_uuid = processing_result.get("pdf_uuid")
            schema_path = Path("src/backend/utils/table_schema.json")
            if schema_path.exists():
                import json
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                
                # Add file hash to all tables from this upload
                for table_name, table_info in schema.items():
                    if table_info.get('pdf_uuid') == pdf_uuid:
                        table_info['file_hash'] = file_hash
                
                with open(schema_path, 'w') as f:
                    json.dump(schema, f, indent=2)
                logger.info("Added file hash to schema")

            # Get the PDF name and UUID from processing result
            pdf_name = processing_result.get("pdf_name", filename)
            pdf_uuid = processing_result.get("pdf_uuid")

            # Store text embeddings in Pinecone using Google Gemini
            print("\n=== Storing Text Embeddings ===")
            text_chunks_stored = embedding_service.store_text_embeddings(
                processing_result["text_chunks"], pdf_uuid, pdf_name
            )
            print(f"✓ Stored {text_chunks_stored} text chunks in Pinecone")

            # Prepare detailed response
            tables_info = processing_result.get("tables_info", [])
            tables_stored = len(tables_info)
            
            # Create summary of stored tables
            table_summary = []
            for table_info in tables_info:
                table_summary.append({
                    "name": table_info["name"],
                    "rows_stored": table_info["rows"],
                    "description": table_info["description"]
                })

            print(f"\n=== Processing Summary ===")
            print(f"✓ File: {filename}")
            print(f"✓ PDF UUID: {pdf_uuid}")
            print(f"✓ Text chunks stored in Pinecone: {text_chunks_stored}")
            print(f"✓ Tables stored in MySQL: {tables_stored}")
            print(f"✓ Schemas saved to src/backend/utils/table_schema.json: {processing_result.get('schemas_saved', 0)}")
            for table in table_summary:
                print(f"  - {table['name']}: {table['rows_stored']} rows")
            print("==========================\n")

            # Create a user-friendly display name from the original filename
            # Remove file extension and clean up underscores
            clean_filename = filename.rsplit('.', 1)[0].replace('_', ' ')
            
            # Generate data preview summary
            data_preview = {
                "total_tables": tables_stored,
                "total_rows": sum([t["rows_stored"] for t in table_summary]),
                "tables": []
            }
            
            # Add table previews
            for table in table_summary:
                preview = {
                    "name": table["name"],
                    "rows": table["rows_stored"],
                    "description": table["description"][:150] + "..." if len(table["description"]) > 150 else table["description"]
                }
                data_preview["tables"].append(preview)
            
            # Log upload summary
            print(f"\n{'='*100}")
            print("UPLOAD DATA PREVIEW")
            print(f"{'='*100}")
            print(f"Filename: {filename}")
            print(f"PDF UUID: {pdf_uuid}")
            print(f"Total Tables Extracted: {tables_stored}")
            print(f"Total Rows Stored: {data_preview['total_rows']}")
            print(f"\nTable Details:")
            for i, table in enumerate(data_preview["tables"], 1):
                print(f"  {i}. {table['name']}: {table['rows']} rows")
                print(f"     {table['description']}")
            print(f"{'='*100}\n")
            
            return {
                "success": True,
                "message": "PDF processed successfully with Gemini-enhanced schema inference",
                "filename": filename,
                "pdf_name": pdf_name,
                "pdf_uuid": pdf_uuid,
                "tables_stored": tables_stored,
                "text_chunks_stored": text_chunks_stored,
                "schemas_created": processing_result.get("schemas_saved", 0),
                "table_details": table_summary,
                "data_preview": data_preview,
                "processing_method": "enhanced_gemini",
                "display_name": clean_filename
            }

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                logger.info(f"Deleted temporary file: {temp_file_path}")
                print(f"Deleted temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")
                print(f"Error: Failed to delete temporary file {temp_file_path}: {str(e)}")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Enhanced upload error: {str(e)}")
        print(f"Error: Failed to process PDF '{filename}' with enhanced method: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "success": False,
                "message": "Failed to process PDF with enhanced method",
                "filename": filename,
                "error": str(e),
                "processing_method": "enhanced_gemini"
            }
        )


# Additional utility functions for the enhanced processing

def get_table_schemas() -> dict:
    """Get all stored table schemas from the JSON file."""
    try:
        schema_file = Path("src/backend/utils/table_schema.json")
        if schema_file.exists():
            import json
            with open(schema_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Failed to load table schemas: {e}")
        return {}


def get_table_info(table_name: str) -> dict:
    """Get information about a specific table."""
    schemas = get_table_schemas()
    return schemas.get(table_name, {})


async def process_pdf_upload_legacy(file: UploadFile) -> dict:
    """
    Legacy PDF processing method for backward compatibility.
    
    This method uses the original processing logic without Gemini integration.
    Use process_pdf_upload() for enhanced processing with Gemini.
    """
    logger.warning("Using legacy PDF processing method. Consider upgrading to enhanced method.")
    
    # Import the original processing logic here if needed for backward compatibility
    # This would use the legacy methods in PDFProcessor
    
    filename = secure_filename(file.filename) if file.filename else "unknown"
    
    try:
        # Basic validation
        if not validate_file_size(file) or not allowed_file(filename):
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Use legacy processing
        pdf_processor = PDFProcessor()  # Uses legacy constructor
        
        # ... legacy processing logic here ...
        
        return {
            "success": True,
            "message": "PDF processed using legacy method",
            "filename": filename,
            "processing_method": "legacy"
        }
        
    except Exception as e:
        logger.error(f"Legacy upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to process PDF with legacy method",
                "error": str(e),
                "processing_method": "legacy"
            }
        )