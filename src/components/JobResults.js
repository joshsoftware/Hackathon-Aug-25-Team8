import React from 'react';
import { Download, ExternalLink, MapPin, Building, Clock, Briefcase, DollarSign } from 'lucide-react';
import JobCard from './JobCard';

const JobResults = ({ jobs, searchParams, onExport }) => {
  const handleExport = () => {
    const csvContent = convertToCSV(jobs);
    downloadCSV(csvContent, 'linkedin_jobs.csv');
  };

  const convertToCSV = (jobs) => {
    const headers = ['Title', 'Company', 'Location', 'URL'];
    const csvRows = [headers.join(',')];
    
    jobs.forEach(job => {
      const row = [
        `"${job.title.replace(/"/g, '""')}"`,
        `"${job.company.replace(/"/g, '""')}"`,
        `"${job.location.replace(/"/g, '""')}"`,
        `"${job.url}"`
      ];
      csvRows.push(row.join(','));
    });
    
    return csvRows.join('\n');
  };

  const downloadCSV = (csvContent, filename) => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="results-section">
      <div className="results-header">
        <div className="results-count">
          Found {jobs.length} jobs for "{searchParams?.job_title}"
        </div>
        <button className="export-btn" onClick={handleExport}>
          <Download size={16} />
          Export to CSV
        </button>
      </div>
      
      <div className="jobs-grid">
        {jobs.map((job, index) => (
          <JobCard key={index} job={job} />
        ))}
      </div>
    </div>
  );
};

export default JobResults;
