import React, { useState } from 'react';
import { Search, Mail, Lock, Briefcase, Hash, Settings } from 'lucide-react';

const SearchForm = ({ onSearch, loading }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    jobTitle: '',
    maxJobs: 10,
    searchMethod: 'direct_url'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(formData);
  };

  return (
    <div className="search-section">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">
            <Mail size={16} />
            LinkedIn Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            placeholder="your.email@example.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">
            <Lock size={16} />
            LinkedIn Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            placeholder="Your password"
          />
        </div>

        <div className="form-group">
          <label htmlFor="jobTitle">
            <Briefcase size={16} />
            Job Title
          </label>
          <input
            type="text"
            id="jobTitle"
            name="jobTitle"
            value={formData.jobTitle}
            onChange={handleInputChange}
            required
            placeholder="e.g., Data Entry, Software Engineer"
          />
        </div>

        <div className="form-group">
          <label htmlFor="maxJobs">
            <Hash size={16} />
            Max Jobs
          </label>
          <select
            id="maxJobs"
            name="maxJobs"
            value={formData.maxJobs}
            onChange={handleInputChange}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="searchMethod">
            <Settings size={16} />
            Search Method
          </label>
          <select
            id="searchMethod"
            name="searchMethod"
            value={formData.searchMethod}
            onChange={handleInputChange}
          >
            <option value="direct_url">Direct URL</option>
            <option value="direct">Direct Search</option>
            <option value="feed">Feed Search</option>
          </select>
        </div>

        <button 
          type="submit" 
          className="search-btn" 
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="spinner"></div>
              Searching...
            </>
          ) : (
            <>
              <Search size={20} />
              Search Jobs
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;
