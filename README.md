# PDF Thumbnail Service

[![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-Swagger-blue?logo=swagger)](https://lor-service-pdfthumbnail.vercel.app/docs)
[![Vercel](https://img.shields.io/badge/deployed%20on-Vercel-black?logo=vercel)](https://lor-service-pdfhumbnail.vercel.app)

A production-ready FastAPI microservice that functions as a PDF thumbnail generator, converting the first page of PDF files to optimized PNG thumbnails.

🌐 **Live API**: [https://lor-service-pdfhumbnail.vercel.app](https://lor-service-pdfhumbnail.vercel.app) | **API Docs**: [/docs](https://lor-service-pdfthumbnail.vercel.app/docs)

## Features
- **PDF to Image Conversion**: Converts the first page of any PDF to PNG format
- **High Quality Output**: 150 DPI rendering for crisp, clear thumbnails
- **Smart Optimization**: Optional 60% scaling and PNG compression for smaller file sizes
- **Comprehensive Error Handling**: Validates file type, size, and PDF integrity
- **CORS Support**: Ready for frontend and cross-origin integration
- **Serverless Ready**: Optimized for Vercel deployment (Python 3.9 runtime)
- **No File Storage**: All processing is in-memory; files are cleaned up after processing
- **Health & Info Endpoints**: For monitoring and service introspection

## API Reference

#### Convert PDF to PNG

```http
POST /pdf
```

| Parameter   | Type     | Description                                      |
| :---------- | :------- | :----------------------------------------------- |
| `file`      | `file`   | **Required**. PDF file to convert                |
| `optimize`  | `bool`   | Optional. If true, applies scaling/compression   |

Converts the first page of a PDF to a PNG image. Returns the PNG file.

#### Health Check

```http
GET /health
```

Returns service health status (to check if the service is online).

#### Service Capabilities

```http
GET /info
```

Returns service capabilities and available endpoints.

#### API Documentation

```http
GET /docs
```

Swagger/OpenAPI documentation for the API

## Testing the API
- **Swagger UI**: [https://lor-service-pdfthumbnail.vercel.app/docs](https://lor-service-pdfthumbnail.vercel.app/docs)
- **Example cURL:**
  ```bash
  curl -X POST \
    -F "file=@document.pdf" \
    'https://lor-service-pdfthumbnail.vercel.app/pdf?optimize=true' \
    --output thumbnail.png
  ```

## Local Deployment

1. **Clone the repository:**
  ```bash
  git clone https://github.com/nngel/PDF-thumbnail-service.git
  cd PDF-thumbnail-service
  ```

2. **Create and activate virtual environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

3. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
4. **Run the development server (change port if needed):**
  ```bash
  uvicorn api.main:app --reload --port 8000
  ```

5. **Test the API locally:**
  ```bash
  curl -X POST \
    -F "file=@test.pdf" \
    http://localhost:8000/pdf \
    --output thumbnail.png
  ```

## Tech Stack
- **FastAPI**: Modern async Python web framework
- **Uvicorn**: ASGI server for local development
- **PyMuPDF (fitz)**: Fast PDF rendering and manipulation
- **Pillow**: Image processing and optimization
- **Vercel**: Serverless deployment platform

## Error Handling
The service includes robust error handling for:
- Invalid file types (non-PDF uploads)
- Corrupted or unreadable PDF files
- Empty PDF files (no pages)
- Files exceeding the 10MB limit
- Processing timeouts or memory errors
- Internal server errors (with logging)

## Security Considerations
- Strict file type and size validation
- All processing is performed in-memory (no files are written to disk)
- No persistent storage: files and images are cleaned up immediately after processing
- Input sanitization and error handling to prevent abuse

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.