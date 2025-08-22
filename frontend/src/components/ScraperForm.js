import React, { useState } from 'react';
import { Globe, User, Lock, Search, Filter, Play, Loader } from 'lucide-react';

const ScraperForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    url: '',
    username: '',
    password: '',
    searchFilter: '',
    categoryFilter: '',
    dataTypes: ['all']
  });

  const [showCredentials, setShowCredentials] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const dataTypeOptions = [
    { value: 'all', label: 'All Data' },
    { value: 'text_content', label: 'Text Content' },
    { value: 'links', label: 'Links' },
    { value: 'images', label: 'Images' },
    { value: 'tables', label: 'Tables' },
    { value: 'forms', label: 'Forms' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDataTypeChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => {
      if (value === 'all') {
        return { ...prev, dataTypes: checked ? ['all'] : [] };
      } else {
        const newDataTypes = checked 
          ? prev.dataTypes.filter(type => type !== 'all').concat(value)
          : prev.dataTypes.filter(type => type !== value);
        return { ...prev, dataTypes: newDataTypes.length ? newDataTypes : ['all'] };
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const isFormValid = () => {
    return formData.url.trim() !== '' && formData.dataTypes.length > 0;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        <Globe className="mr-2 text-primary-600" />
        Web Scraper
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            Website URL *
          </label>
          <div className="relative">
            <input
              type="url"
              id="url"
              name="url"
              value={formData.url}
              onChange={handleInputChange}
              placeholder="https://example.com"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Credentials Section */}
        <div>
          <button
            type="button"
            onClick={() => setShowCredentials(!showCredentials)}
            className="flex items-center text-sm font-medium text-gray-700 mb-2 hover:text-primary-600"
          >
            <User className="mr-2 h-4 w-4" />
            Login Credentials (Optional)
            <span className={`ml-2 transform transition-transform ${showCredentials ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          {showCredentials && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username/Email
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="Enter username or email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter password"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
        </div>

        {/* Filters Section */}
        <div>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center text-sm font-medium text-gray-700 mb-2 hover:text-primary-600"
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters (Optional)
            <span className={`ml-2 transform transition-transform ${showFilters ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          {showFilters && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="searchFilter" className="block text-sm font-medium text-gray-700 mb-2">
                    Search Filter
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      id="searchFilter"
                      name="searchFilter"
                      value={formData.searchFilter}
                      onChange={handleInputChange}
                      placeholder="Search term"
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="categoryFilter" className="block text-sm font-medium text-gray-700 mb-2">
                    Category Filter
                  </label>
                  <input
                    type="text"
                    id="categoryFilter"
                    name="categoryFilter"
                    value={formData.categoryFilter}
                    onChange={handleInputChange}
                    placeholder="Category name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Data Types */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Types to Extract
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {dataTypeOptions.map(option => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="checkbox"
                        value={option.value}
                        checked={formData.dataTypes.includes(option.value)}
                        onChange={handleDataTypeChange}
                        className="mr-2 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!isFormValid() || isLoading}
            className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
              isFormValid() && !isLoading
                ? 'bg-primary-600 text-white hover:bg-primary-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Scraping...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Start Scraping
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ScraperForm;

