# LinkedIn Job Scraper with Background Crawling

This project provides a robust LinkedIn job scraping solution with background crawling capabilities. It allows you to search for jobs on LinkedIn and then crawl the detailed job pages in the background to extract comprehensive information.

## Features

- **Job Search**: Search for jobs on LinkedIn using various methods
- **Basic Job Data Extraction**: Extract basic job information from search results
- **Background Crawling**: Crawl detailed job pages in the background
- **Detailed Job Information**: Extract comprehensive job details including description, requirements, and more
- **API Integration**: FastAPI endpoints for all functionality
- **Caching**: In-memory caching of job data

## Architecture

The system consists of the following components:

1. **LinkedIn Scraper Service**: Core scraping functionality using Playwright
2. **FastAPI Endpoints**: RESTful API for interacting with the scraper
3. **Background Tasks**: Asynchronous processing of job links
4. **In-Memory Cache**: Storage for job data

## API Endpoints

### Search for Jobs

```
POST /api/linkedin/jobs
```

**Request Body:**
```json
{
  "email": "your_linkedin_email@example.com",
  "password": "your_linkedin_password",
  "job_title": "Software Engineer",
  "max_jobs": 10,
  "search_method": "direct_url"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully scraped 10 jobs from LinkedIn jobs search page",
  "data": [...],  // Array of job objects with basic information
  "search_id": "search_1629123456",  // Unique ID for this search
  "search_params": {...}
}
```

### Crawl Job Details for a Previous Search

```
POST /api/linkedin/crawl-search-jobs
```

**Request Body:**
```json
{
  "search_id": "search_1629123456",
  "email": "your_linkedin_email@example.com",
  "password": "your_linkedin_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Started background crawling of 10 job URLs from search ID: search_1629123456",
  "job_urls": [...]  // Array of URLs being crawled
}
```

### Crawl Specific Job URLs

```
POST /api/linkedin/crawl-job-details
```

**Request Body:**
```json
{
  "email": "your_linkedin_email@example.com",
  "password": "your_linkedin_password",
  "job_urls": [
    "https://www.linkedin.com/jobs/view/12345",
    "https://www.linkedin.com/jobs/view/67890"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Started background crawling of 2 job URLs",
  "job_urls": [...]  // Array of URLs being crawled
}
```

### Get Job Details by Search ID

```
GET /api/linkedin/job-details/{search_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 10 jobs for search ID: search_1629123456",
  "status_summary": {
    "pending": 0,
    "processing": 2,
    "completed": 8,
    "failed": 0
  },
  "data": [...]  // Array of job objects with detailed information
}
```

### Get Job Details by URL

```
GET /api/linkedin/job-details-url?url=https://www.linkedin.com/jobs/view/12345
```

**Response:**
```json
{
  "success": true,
  "message": "Found job details for URL: https://www.linkedin.com/jobs/view/12345",
  "data": {...}  // Job object with detailed information
}
```

## Usage Example

Here's a typical workflow:

1. Search for jobs using the `/jobs` endpoint
2. Get the `search_id` from the response
3. Start background crawling using the `/crawl-search-jobs` endpoint
4. Periodically check the status using the `/job-details/{search_id}` endpoint
5. Once all jobs are processed, retrieve the complete data

## Testing

You can use the provided test script to verify the functionality:

```bash
python test_background_crawling.py
```

Make sure to update the LinkedIn credentials in the script before running.

## Implementation Details

### Job Search Flow

1. User provides LinkedIn credentials and job search parameters
2. The scraper logs in to LinkedIn
3. It searches for jobs based on the provided title
4. It extracts basic job data from the search results page
5. It returns this data to the user along with a unique search ID

### Background Crawling Flow

1. User provides a search ID or specific job URLs
2. The system starts a background task to process these URLs
3. For each URL, it:
   - Navigates to the job page
   - Extracts detailed information
   - Stores the data in the cache
4. The user can check the status and retrieve the data at any time

### Detailed Job Information

The system extracts the following information from job pages:

- Job title
- Company name
- Location
- Full job description
- Job criteria/requirements
- Application type
- Posted date
- Number of applicants
- Company details (size, industry)
- And more...

## Notes

- LinkedIn's structure may change over time, requiring updates to the selectors
- The system uses multiple selectors for each element to increase robustness
- Background crawling helps avoid timeouts and provides a better user experience
- In-memory caching is used for simplicity; in a production environment, consider using a database
