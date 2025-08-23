import React from 'react';
import { ExternalLink, MapPin, Building, Clock, Briefcase, DollarSign, Calendar } from 'lucide-react';

const JobCard = ({ job }) => {
  const formatDate = (dateString) => {
    if (dateString === 'N/A') return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  };

  const formatField = (value) => {
    return value === 'N/A' ? 'Not specified' : value;
  };

  return (
    <div className="job-card">
      <div className="scraped-time">
        <Calendar size={14} />
        {formatDate(job.scraped_at)}
      </div>
      
      <h3 className="job-title">{formatField(job.title)}</h3>
      
      <div className="job-company">
        <Building size={16} />
        {formatField(job.company)}
      </div>
      
      <div className="job-location">
        <MapPin size={16} />
        {formatField(job.location)}
      </div>
      
      <div className="job-meta">
        <div className="meta-item">
          <span className="meta-label">
            <Clock size={14} />
            Posted Time
          </span>
          <span className="meta-value">{formatField(job.posted_time)}</span>
        </div>
        
        <div className="meta-item">
          <span className="meta-label">
            <Briefcase size={14} />
            Job Type
          </span>
          <span className="meta-value">{formatField(job.job_type)}</span>
        </div>
        
        <div className="meta-item">
          <span className="meta-label">
            <DollarSign size={14} />
            Salary
          </span>
          <span className="meta-value">{formatField(job.salary)}</span>
        </div>
      </div>
      
      <a 
        href={job.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="job-url"
      >
        <ExternalLink size={16} />
        View Job on LinkedIn
      </a>
    </div>
  );
};

export default JobCard;
