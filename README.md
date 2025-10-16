# 🗺️ Locography

A personal inventory manager app with AI-powered cataloging and smart search capabilities.

## Features

### Core Functionality
- **Smart Cataloging**: Semi-automatic item cataloging using local LLM with vision capabilities
- **Flexible Organization**: Hierarchical categories and storage locations
- **Multi-Modal Search**: Search by text, image, or even sketches
- **Location Awareness**: Track items with physical and GPS coordinates
- **3D Model Support**: Infrastructure for 3D splat sensors and AR visualization
- **Visual Search**: Find items by uploading similar images

### Technology Stack
- **Backend**: FastAPI (Python async web framework)
- **Database**: SQLite with SQLAlchemy ORM (async)
- **AI Integration**: Local LLM support (Ollama/llava) for vision and text generation
- **Image Processing**: PIL/OpenCV for image analysis and feature extraction
- **Search**: Vector embeddings for similarity search
- **Frontend**: Vanilla JavaScript with modern CSS

## Installation

### Prerequisites
- Python 3.9 or higher
- (Optional) Ollama with llava model for AI features

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/okrg/locography.git
cd locography
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env to configure your settings
```

5. **Run the application**
```bash
python -m app.main
```

The application will start at `http://localhost:8000`

## Configuration

Edit `.env` file to customize settings:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./locography.db

# LLM Integration (optional)
LLM_API_URL=http://localhost:11434
LLM_MODEL=llava
ENABLE_LLM=true

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Uploads
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads
```

## LLM Setup (Optional)

To enable AI-powered cataloging:

1. **Install Ollama**
```bash
# Visit https://ollama.ai for installation instructions
curl -fsSL https://ollama.ai/install.sh | sh
```

2. **Download vision model**
```bash
ollama pull llava
```

3. **Start Ollama service**
```bash
ollama serve
```

The application will automatically use the LLM for:
- Analyzing uploaded images
- Generating item descriptions
- Suggesting tags and categories

## Usage

### Web Interface

Access the web interface at `http://localhost:8000` to:
- Add and manage inventory items
- Create storage locations
- Organize with categories
- Upload item photos for AI analysis
- Search by text or image

### API Endpoints

#### Items
- `POST /api/v1/items` - Create new item
- `GET /api/v1/items` - List all items
- `GET /api/v1/items/{id}` - Get item details
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item
- `POST /api/v1/items/{id}/images` - Upload item image

#### Locations
- `POST /api/v1/locations` - Create location
- `GET /api/v1/locations` - List locations
- `GET /api/v1/locations/{id}` - Get location
- `PUT /api/v1/locations/{id}` - Update location
- `DELETE /api/v1/locations/{id}` - Delete location

#### Categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{id}` - Get category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

#### Search
- `GET /api/v1/search/items?q=query` - Text search
- `POST /api/v1/search/by-image` - Image-based search

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

### Database Models
- **Items**: Core inventory items with metadata
- **Locations**: Storage locations with 3D coordinates
- **Categories**: Hierarchical item categorization
- **ItemImages**: Photos with AI analysis and embeddings

### Services
- **LLM Service**: Interfaces with local LLM for AI features
- **Image Service**: Handles image processing and embeddings
- **Search Service**: Multi-modal search functionality

## Future Enhancements

- [ ] Mobile app for on-the-go inventory access
- [ ] Barcode/QR code scanning
- [ ] Advanced 3D model visualization with AR
- [ ] Real-time location tracking via IoT devices
- [ ] Sharing and collaboration features
- [ ] Import/export functionality
- [ ] Advanced analytics and reporting
- [ ] Natural language queries

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.