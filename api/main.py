from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response, HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Thumbnail Service</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4a5568;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #718096;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .feature {
                background: #f7fafc;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }
            .endpoints {
                background: #1a202c;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .endpoint {
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }
            .method {
                background: #48bb78;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                margin-right: 10px;
            }
            .method.post {
                background: #ed8936;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                margin: 10px 10px 10px 0;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #5a67d8;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PDF Thumbnail Service</h1>
            <p class="subtitle">Convert PDF first page to optimized PNG thumbnails</p>
            
            <div class="feature">
                <h3>Features</h3>
                <ul>
                    <li><strong>High Quality:</strong> 150 DPI rendering for crisp thumbnails</li>
                    <li><strong>Smart Optimization:</strong> Optional scaling and compression</li>
                    <li><strong>Secure:</strong> In-memory processing, no file storage</li>
                    <li><strong>Fast:</strong> Serverless deployment on Vercel</li>
                </ul>
            </div>
            <div class="endpoints">
                <h3>API Endpoints</h3>
                <div class="endpoint"><span class="method post">POST</span>/pdf - Convert PDF to PNG</div>
                <div class="endpoint"><span class="method">GET</span>/health - Health check</div>
                <div class="endpoint"><span class="method">GET</span>/info - Service info</div>
                <div class="endpoint"><span class="method">GET</span>/docs - API documentation</div>
            </div>

            <div style="margin-top: 30px;">
                <a href="/docs" class="btn">API Documentation</a>
                <a href="https://github.com/nngel/PDF-thumbnail-service" class="btn">GitHub</a>
            </div>

            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.9em;">
                <p><strong>Quick Test:</strong></p>
                <code style="background: #f7fafc; padding: 10px; display: block; border-radius: 4px; margin: 10px 0;">
                curl -X POST -F "file=@document.pdf" {request.url}pdf?optimize=true --output thumbnail.png
                </code>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

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
    return {"status": "healthy", "service": "pdf-thumbnail", "deployment": "vercel"}

@app.get("/info")
async def service_info():
    """Service information and capabilities"""
    return {
        "service": "PDF Thumbnail Service",
        "version": "1.0.0",
        "description": "Convert first page of PDF files to optimized PNG thumbnails",
        "endpoints": {
            "POST /pdf": "Convert PDF to PNG (supports ?optimize=true parameter)",
            "GET /": "Service homepage",
            "GET /health": "Health check",
            "GET /info": "Service information",
            "GET /docs": "API documentation"
        },
        "features": [
            "High quality 150 DPI rendering",
            "Optional optimization and scaling",
            "In-memory processing (no file storage)",
            "CORS enabled",
            "10MB file size limit"
        ],
        "tech_stack": ["FastAPI", "PyMuPDF", "Pillow", "Vercel"]
    }

# Vercel specific configuration
app = app
