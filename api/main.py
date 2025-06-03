from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from PIL import Image
import io
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def FILE_LIMIT():
    return 10 * 1024 * 1024  # 10 MB

app = FastAPI(
    title="PDF Thumbnail Service",
    description="Convert first page of PDF to image with high quality rendering",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    contact={
        "name": "PDF Thumbnail Service",
        "url": "https://github.com/nngel/PDF-thumbnail-service",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PDF Thumbnail Service", "version": "1.0.0"}

@app.post("/pdf")
async def convert_pdf_to_image(file: UploadFile = File(...), optimize: Optional[bool] = False):
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('application/pdf'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a PDF"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > FILE_LIMIT():
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Open PDF with PyMuPDF
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file or corrupted file"
            )
        
        # Check if PDF has pages
        if pdf_document.page_count == 0:
            pdf_document.close()
            raise HTTPException(
                status_code=400,
                detail="PDF file has no pages"
            )
        
        # Get first page
        first_page = pdf_document[0]
        
        # Convert page to image (pixmap)
        # Use higher DPI for better quality (150 DPI is a good balance)
        matrix = fitz.Matrix(150/72, 150/72)  # 150 DPI
        pixmap = first_page.get_pixmap(matrix=matrix)
        
        # Convert pixmap to PIL Image
        img_data = pixmap.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Apply optimization if requested
        if optimize:
            # Scale to 60% of original size
            new_width = int(pil_image.width * 0.6)
            new_height = int(pil_image.height * 0.6)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            # Optimize image size if too large (only when not already optimized)
            max_dimension = 1200
            if pil_image.width > max_dimension or pil_image.height > max_dimension:
                pil_image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Convert to PNG bytes with optimization settings
        img_buffer = io.BytesIO()
        if optimize:
            # Apply additional optimizations for smaller file size
            pil_image.save(img_buffer, format='PNG', optimize=True, compress_level=9)
        else:
            # Standard PNG without additional optimization
            pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Clean up
        pdf_document.close()
        
        # Return image as response
        return Response(
            content=img_buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=thumbnail.png"}
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing PDF"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-thumbnail"}

# Vercel specific configuration
app = app
