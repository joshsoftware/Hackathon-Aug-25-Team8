import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/linkedin';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchJobs = async (searchData) => {
  try {
    const response = await api.post('/jobs', {
      email: searchData.email,
      password: searchData.password,
      job_title: searchData.jobTitle,
      max_jobs: parseInt(searchData.maxJobs),
      search_method: searchData.searchMethod
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
};

export const loginToLinkedIn = async (credentials) => {
  try {
    const response = await api.post('/login', credentials);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Login failed');
    } else if (error.request) {
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend is not responding');
  }
};
