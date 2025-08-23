# LinkedIn Job Scraper - React Frontend

A modern, responsive React frontend for the LinkedIn Job Scraper application. This frontend provides a beautiful user interface to interact with the scraping API and display results.

## Features

- **Modern React Architecture**: Built with React 18 and functional components
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Beautiful UI**: Modern design with gradients, shadows, and smooth animations
- **Icon Integration**: Lucide React icons for enhanced visual appeal
- **State Management**: React hooks for efficient state management
- **Error Handling**: Comprehensive error handling and user feedback
- **Export Functionality**: CSV export of scraped job data
- **Loading States**: Visual feedback during API calls

## Tech Stack

- **React 18** - Modern React with hooks
- **CSS3** - Custom CSS with CSS variables and Grid/Flexbox
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful, customizable icons
- **Create React App** - Zero-configuration build tool

## Project Structure

```
src/
├── components/           # React components
│   ├── Header.js        # Application header
│   ├── SearchForm.js    # Job search form
│   ├── JobResults.js    # Results display container
│   ├── JobCard.js       # Individual job card
│   └── MessageContainer.js # Success/error messages
├── services/            # API services
│   └── api.js          # API communication layer
├── App.js              # Main application component
├── App.css             # Main component styles
├── index.js            # Application entry point
└── index.css           # Global styles
```

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Backend API running (FastAPI server)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd Hackathon-Aug-25-Team8
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files.

## 🔧 Configuration

### API Configuration

The frontend is configured to connect to your FastAPI backend at `http://localhost:8000`. You can modify this in:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/linkedin';
```

### Environment Variables

Create a `.env` file in the root directory to customize settings:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_PREFIX=/api/linkedin
```

## Component Details

### Header Component
- Displays application title and description
- Features a search icon and gradient background
- Responsive design for all screen sizes

### SearchForm Component
- LinkedIn credentials input (email/password)
- Job search parameters (title, max jobs, search method)
- Form validation and error handling
- Loading states during API calls

### JobResults Component
- Displays scraped jobs in a responsive grid
- Export functionality (CSV download)
- Results count and search parameters display

### JobCard Component
- Individual job information display
- All job fields from the API response
- Hover effects and smooth animations
- Direct links to LinkedIn job postings

### MessageContainer Component
- Success and error message display
- Icon integration for better UX
- Auto-dismiss functionality

## Styling

### CSS Architecture
- **CSS Variables**: Consistent color scheme and spacing
- **CSS Grid**: Responsive layout system
- **Flexbox**: Component alignment and spacing
- **CSS Transitions**: Smooth animations and hover effects

### Design System
- **Color Palette**: Professional blue gradient theme
- **Typography**: Clean, readable fonts with proper hierarchy
- **Spacing**: Consistent spacing using CSS variables
- **Shadows**: Subtle shadows for depth and modern feel

### Responsive Breakpoints
- **Desktop**: 1200px+ (full grid layout)
- **Tablet**: 768px - 1199px (adjusted grid)
- **Mobile**: < 768px (single column layout)

## 🔌 API Integration

### Available Endpoints

- `POST /api/linkedin/jobs` - Search and scrape jobs
- `POST /api/linkedin/login` - LinkedIn authentication
- `GET /api/linkedin/health` - Health check

### Error Handling

The frontend includes comprehensive error handling:
- Network errors (server not responding)
- API errors (authentication failures, scraping errors)
- User input validation
- Graceful fallbacks and user feedback

## Data Flow

1. **User Input**: Form data collected from SearchForm
2. **API Call**: Data sent to backend via axios
3. **Response Processing**: Success/error handling
4. **State Update**: Jobs data stored in React state
5. **UI Update**: Components re-render with new data
6. **Export**: CSV generation and download

## Performance Features

- **Lazy Loading**: Components load only when needed
- **Optimized Re-renders**: Efficient state management
- **CSS Optimization**: Minimal CSS with efficient selectors
- **Icon Optimization**: SVG icons for crisp display at all sizes

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for `localhost:3000`
2. **API Connection**: Verify backend is running on port 8000
3. **Build Errors**: Clear `node_modules` and reinstall dependencies
4. **Port Conflicts**: Change port in package.json if 3000 is occupied

### Development Tips

- Use React Developer Tools for debugging
- Check browser console for error messages
- Verify API endpoints with tools like Postman
- Test responsive design with browser dev tools

## Future Enhancements

- **Dark Mode**: Toggle between light and dark themes
- **Job Filtering**: Filter jobs by company, location, or date
- **Job Bookmarks**: Save interesting jobs for later
- **Advanced Search**: Multiple job titles, salary ranges
- **Real-time Updates**: WebSocket integration for live results
- **PWA Support**: Progressive Web App capabilities

## License

This project is created for educational and hackathon purposes.

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs or issues
- Suggest new features
- Improve the UI/UX
- Add new functionality
- Optimize performance

