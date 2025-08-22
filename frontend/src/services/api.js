import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const scraperAPI = {
  // Scrape a single website
  scrapeWebsite: async (scrapeData) => {
    try {
      const response = await api.post('/scrape', scrapeData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Scrape multiple websites in batch
  scrapeBatch: async (scrapeRequests) => {
    try {
      const response = await api.post('/scrape/batch', scrapeRequests);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/scrape/health');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default api;

