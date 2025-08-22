import React, { useState } from 'react';
import { Globe, AlertCircle, CheckCircle } from 'lucide-react';
import ScraperForm from './components/ScraperForm';
import ResultsDisplay from './components/ResultsDisplay';
import { scraperAPI } from './services/api';
import './index.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleScrape = async (formData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Prepare the request data
      const requestData = {
        url: formData.url,
        username: formData.username || null,
        password: formData.password || null,
        search_filter: formData.searchFilter || null,
        category_filter: formData.categoryFilter || null,
        data_types: formData.dataTypes
      };

      const response = await scraperAPI.scrapeWebsite(requestData);
      setResult(response);
    } catch (err) {
      setError(err.detail || err.message || 'An error occurred while scraping');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Globe className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Web Scraper
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              Hackathon Project
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <div>
            <ScraperForm onSubmit={handleScrape} isLoading={isLoading} />
            
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                  <h3 className="text-red-800 font-medium">Error</h3>
                </div>
                <p className="text-red-600 mt-1">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {result && result.success && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                  <h3 className="text-green-800 font-medium">Scraping Completed Successfully!</h3>
                </div>
                <p className="text-green-600 mt-1">
                  Data has been extracted from {result.url}
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Results */}
          <div>
            {result && <ResultsDisplay result={result} />}
          </div>
        </div>

        {/* Instructions */}
        {!result && !isLoading && (
          <div className="mt-12 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">How to Use</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-800 mb-2">1. Enter Website URL</h3>
                <p className="text-gray-600 text-sm">
                  Provide the complete URL of the website you want to scrape. Make sure to include the protocol (http:// or https://).
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-800 mb-2">2. Optional Credentials</h3>
                <p className="text-gray-600 text-sm">
                  If the website requires login, provide your username and password. The scraper will attempt to log in automatically.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-800 mb-2">3. Apply Filters</h3>
                <p className="text-gray-600 text-sm">
                  Use search and category filters to narrow down the content you want to extract from the website.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-800 mb-2">4. Select Data Types</h3>
                <p className="text-gray-600 text-sm">
                  Choose which types of data to extract: text content, links, images, tables, or forms.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-500 text-sm">
            <p>Built with FastAPI, Playwright, and React</p>
            <p className="mt-1">Hackathon Project - Team 8</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

