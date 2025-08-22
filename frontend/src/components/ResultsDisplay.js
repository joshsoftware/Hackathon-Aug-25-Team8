import React, { useState } from 'react';
import { 
  FileText, 
  Link, 
  Image, 
  Table, 
  FormInput, 
  ChevronDown, 
  ChevronRight, 
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';

const ResultsDisplay = ({ result }) => {
  const [expandedSections, setExpandedSections] = useState({
    text_content: true,
    links: true,
    images: true,
    tables: true,
    forms: true
  });
  const [copiedText, setCopiedText] = useState('');

  if (!result) return null;

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(label);
      setTimeout(() => setCopiedText(''), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const renderTextContent = () => {
    if (!result.data?.text_content) return null;
    
    return (
      <div className="space-y-3">
        {result.data.text_content.map((item, index) => (
          <div key={index} className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600 uppercase">
                {item.type} {item.level && `(${item.level})`}
              </span>
              <button
                onClick={() => copyToClipboard(item.text, `text-${index}`)}
                className="text-gray-400 hover:text-gray-600"
              >
                {copiedText === `text-${index}` ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
            <p className="text-gray-800">{item.text}</p>
          </div>
        ))}
      </div>
    );
  };

  const renderLinks = () => {
    if (!result.data?.links) return null;
    
    return (
      <div className="space-y-2">
        {result.data.links.map((link, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800 truncate"
                >
                  {link.text || link.url}
                </a>
                <ExternalLink className="h-3 w-3 text-gray-400" />
              </div>
              {link.title && (
                <p className="text-sm text-gray-600 mt-1">{link.title}</p>
              )}
            </div>
            <button
              onClick={() => copyToClipboard(link.url, `link-${index}`)}
              className="ml-2 text-gray-400 hover:text-gray-600"
            >
              {copiedText === `link-${index}` ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </button>
          </div>
        ))}
      </div>
    );
  };

  const renderImages = () => {
    if (!result.data?.images) return null;
    
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {result.data.images.map((image, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-3">
            <img
              src={image.src}
              alt={image.alt}
              className="w-full h-32 object-cover rounded-md mb-2"
              onError={(e) => {
                e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlPC90ZXh0Pjwvc3ZnPg==';
              }}
            />
            <div className="space-y-1">
              {image.alt && (
                <p className="text-sm font-medium text-gray-800">{image.alt}</p>
              )}
              {image.title && (
                <p className="text-xs text-gray-600">{image.title}</p>
              )}
              <div className="flex items-center justify-between">
                <a
                  href={image.src}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:text-primary-800"
                >
                  View Image
                </a>
                <button
                  onClick={() => copyToClipboard(image.src, `image-${index}`)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {copiedText === `image-${index}` ? (
                    <Check className="h-3 w-3 text-green-500" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTables = () => {
    if (!result.data?.tables) return null;
    
    return (
      <div className="space-y-6">
        {result.data.tables.map((table, tableIndex) => (
          <div key={tableIndex} className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-lg font-medium text-gray-800 mb-3">
              Table {tableIndex + 1}
            </h4>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                <thead>
                  <tr>
                    {table.headers.map((header, index) => (
                      <th key={index} className="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-sm font-medium text-gray-700">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {table.rows.slice(1).map((row, rowIndex) => (
                    <tr key={rowIndex} className="hover:bg-gray-50">
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex} className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderForms = () => {
    if (!result.data?.forms) return null;
    
    return (
      <div className="space-y-6">
        {result.data.forms.map((form, formIndex) => (
          <div key={formIndex} className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-lg font-medium text-gray-800 mb-3">
              Form {formIndex + 1}
            </h4>
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Action:</span> {form.action || 'N/A'}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Method:</span> {form.method.toUpperCase()}
              </p>
            </div>
            <div className="space-y-2">
              <h5 className="text-sm font-medium text-gray-700">Fields:</h5>
              {form.fields.map((field, fieldIndex) => (
                <div key={fieldIndex} className="flex items-center space-x-4 p-2 bg-white rounded border">
                  <span className="text-xs font-medium text-gray-600 min-w-0 flex-1">
                    {field.name || field.id || `Field ${fieldIndex + 1}`}
                  </span>
                  <span className="text-xs text-gray-500">{field.type}</span>
                  {field.placeholder && (
                    <span className="text-xs text-gray-400">"{field.placeholder}"</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const sections = [
    { key: 'text_content', label: 'Text Content', icon: FileText, render: renderTextContent },
    { key: 'links', label: 'Links', icon: Link, render: renderLinks },
    { key: 'images', label: 'Images', icon: Image, render: renderImages },
    { key: 'tables', label: 'Tables', icon: Table, render: renderTables },
    { key: 'forms', label: 'Forms', icon: FormInput, render: renderForms }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Scraping Results</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>URL: {result.url}</span>
          <span>•</span>
          <span>Timestamp: {new Date(result.timestamp).toLocaleString()}</span>
        </div>
        {result.metadata?.page_title && (
          <p className="text-lg text-gray-700 mt-2">{result.metadata.page_title}</p>
        )}
      </div>

      {/* Error Display */}
      {!result.success && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <h3 className="text-red-800 font-medium">Scraping Failed</h3>
          <p className="text-red-600 mt-1">{result.error}</p>
        </div>
      )}

      {/* Success Display */}
      {result.success && result.data && (
        <div className="space-y-6">
          {sections.map(({ key, label, icon: Icon, render }) => {
            const data = result.data[key];
            if (!data || (Array.isArray(data) && data.length === 0)) return null;
            
            return (
              <div key={key} className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleSection(key)}
                  className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-t-lg"
                >
                  <div className="flex items-center space-x-2">
                    <Icon className="h-5 w-5 text-gray-600" />
                    <span className="font-medium text-gray-800">{label}</span>
                    <span className="text-sm text-gray-500">({Array.isArray(data) ? data.length : '1'})</span>
                  </div>
                  {expandedSections[key] ? (
                    <ChevronDown className="h-5 w-5 text-gray-600" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-gray-600" />
                  )}
                </button>
                
                {expandedSections[key] && (
                  <div className="p-4">
                    {render()}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
