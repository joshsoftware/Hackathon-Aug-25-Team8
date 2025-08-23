import React from 'react';
import { Search } from 'lucide-react';

const Header = () => {
  return (
    <div className="header">
      <div className="header-content">
        <Search className="header-icon" size={48} />
        <h1>LinkedIn Job Scraper</h1>
        <p>Search and scrape job listings from LinkedIn</p>
      </div>
    </div>
  );
};

export default Header;
