import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import JobResults from './components/JobResults';
import MessageContainer from './components/MessageContainer';
import { searchJobs } from './services/api';

function App() {
  const [jobs, setJobs] = useState([]);
  const [searchParams, setSearchParams] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSearch = async (searchData) => {
    setLoading(true);
    setMessage(null);
    
    try {
      const result = await searchJobs(searchData);
      
      if (result.success) {
        setJobs(result.data);
        setSearchParams(result.search_params);
        setMessage({ type: 'success', text: result.message });
      } else {
        setMessage({ type: 'error', text: result.message });
        setJobs([]);
        setSearchParams(null);
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
      setJobs([]);
      setSearchParams(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <div className="container">
        <SearchForm onSearch={handleSearch} loading={loading} />
        <MessageContainer message={message} />
        {jobs.length > 0 && (
          <JobResults 
            jobs={jobs} 
            searchParams={searchParams}
            onExport={() => {
              // Export functionality will be implemented in JobResults component
            }}
          />
        )}
      </div>
    </div>
  );
}

export default App;
