# Web Scraper API & Frontend

A powerful web scraping solution built with FastAPI, Playwright, and React for the Hackathon project.

## 🚀 Features

- **Web Scraping with Authentication**: Automatically log into websites and extract data
- **Flexible Data Extraction**: Extract text content, links, images, tables, and forms
- **Advanced Filtering**: Apply search and category filters to target specific content
- **Modern UI**: Beautiful React frontend with Tailwind CSS
- **Real-time Results**: View scraped data in a structured, organized format
- **Batch Processing**: Scrape multiple websites at once
- **Copy to Clipboard**: Easy copying of extracted data

## 🏗️ Project Structure

```
Hackathon-Aug-25-Team8/
├── api/                    # API endpoints
│   ├── login.py           # Login endpoint
│   └── scraper.py         # Scraper API endpoints
├── core/                   # Core configuration
│   ├── config.py          # Settings and configuration
│   └── core.py            # Package initialization
├── models/                 # Data models
│   ├── models..py         # Package initialization
│   └── scraper_models.py  # Pydantic models for API
├── services/              # Business logic
│   ├── service.py         # Package initialization
│   └── scraper_service.py # Web scraping service
├── utils/                 # Utility functions
│   └── helper.py          # Package initialization
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── App.js         # Main app component
│   ├── public/            # Static files
│   └── package.json       # Frontend dependencies
├── app.py                 # FastAPI application
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## 🛠️ Setup Instructions

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

3. **Run the backend server**:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## 📖 API Documentation

### Endpoints

#### POST `/api/scrape`
Scrape a single website with authentication and filters.

**Request Body**:
```json
{
  "url": "https://example.com",
  "username": "user@example.com",
  "password": "password123",
  "search_filter": "search term",
  "category_filter": "category name",
  "data_types": ["text_content", "links", "images"]
}
```

**Response**:
```json
{
  "success": true,
  "url": "https://example.com",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "title": "Page Title",
    "text_content": [...],
    "links": [...],
    "images": [...],
    "tables": [...],
    "forms": [...]
  },
  "metadata": {
    "page_title": "Page Title",
    "url": "https://example.com",
    "filters_applied": {}
  }
}
```

#### POST `/api/scrape/batch`
Scrape multiple websites in batch.

#### GET `/api/scrape/health`
Health check endpoint.

### Data Types

- `text_content`: Headings and paragraphs
- `links`: All links with text and URLs
- `images`: Images with src, alt, and title
- `tables`: Table data with headers and rows
- `forms`: Form fields and metadata

## 🎯 Usage Examples

### Basic Scraping
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "data_types": ["text_content", "links"]
  }'
```

### Scraping with Authentication
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login",
    "username": "user@example.com",
    "password": "password123",
    "data_types": ["all"]
  }'
```

### Scraping with Filters
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "search_filter": "technology",
    "category_filter": "news",
    "data_types": ["text_content", "links"]
  }'
```

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Loading states and error handling
- **Collapsible Sections**: Organize results by data type
- **Copy to Clipboard**: One-click copying of extracted data
- **Image Preview**: View extracted images with fallbacks
- **Table Display**: Formatted table data with headers
- **Form Analysis**: Detailed form field information

## 🔧 Configuration

### Environment Variables

Create `.env` files for different environments:

- `.env.sample` - Development (default)
- `.env.staging` - Staging environment
- `.env.prod` - Production environment

**Available Settings**:
- `ENV`: Environment name
- `API_V1_STR`: API version string
- `PROJECT_NAME`: Project name
- `DATABASE_URL`: Database connection string
- `HEADLESS`: Browser headless mode
- `BROWSER`: Browser type (chromium, firefox, webkit)

## 🚀 Deployment

### Backend Deployment
1. Install dependencies
2. Set environment variables
3. Run with production server (e.g., Gunicorn)

### Frontend Deployment
1. Build the project: `npm run build`
2. Serve static files from a web server
3. Configure API endpoint in environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is created for the Hackathon and is open source.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the console logs for error details
3. Ensure all dependencies are properly installed

---

**Built with ❤️ for Hackathon Team 8**

