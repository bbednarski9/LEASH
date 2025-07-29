# Pet Calendar Manager - Frontend

A responsive React TypeScript application for managing pet care calendars with Google Calendar integration. Built with Vite, React 18, TypeScript, and Tailwind CSS.

## Features

### 🗓️ Calendar Management
- **Monthly Calendar View**: Navigate through months with proper 2025 date alignment
- **Day View**: Detailed 24-hour vertical scroll interface with event visualization
- **Event Display**: Shows calendar events from Google Calendar API
- **Current Date Navigation**: Quick access to today's date
- **Event Overlap Handling**: Smart positioning for overlapping calendar events

### 🔐 Authentication
- **Google OAuth Integration**: Secure login through email_server backend
- **Session Management**: Cookie-based authentication with automatic status checking
- **User Profile Display**: Shows authenticated user information

### 🐕 Pet Management
- **Pet Profiles**: Expandable cards showing detailed pet information
- **Medication Tracking**: Display current medications with dosage and timing
- **Activity Management**: Show favorite activities and behavioral notes
- **Health Information**: Track dietary restrictions and training levels

### 📱 Mobile-First Design
- **Responsive Layout**: Optimized for iPhone/iPad that scales to web browsers
- **Touch-Friendly**: Proper tap targets and smooth scrolling
- **Modern UI**: Clean, professional design with consistent theming

## Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom components
- **HTTP Client**: Axios with cookie-based authentication
- **Date Handling**: date-fns for robust date manipulation
- **Icons**: Lucide React for consistent iconography
- **State Management**: React Context for authentication state

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── AuthProvider.tsx    # Authentication context provider
│   │   │   └── LoginScreen.tsx     # Google OAuth login interface
│   │   ├── Calendar/
│   │   │   └── CalendarView.tsx    # Monthly calendar with navigation
│   │   ├── DayView/
│   │   │   └── DayView.tsx         # 24-hour day view with events
│   │   └── Profile/
│   │       └── ProfilePanel.tsx    # User and pet profile display
│   ├── services/
│   │   └── api.ts                  # Email server API integration
│   ├── App.tsx                     # Main application component
│   ├── index.css                   # Tailwind CSS and custom styles
│   └── main.tsx                    # Application entry point
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.ts
└── README.md
```

## API Integration

The frontend integrates with the email_server backend (running on port 5001) using the following endpoints:

### Authentication
- `GET /auth/status` - Check authentication status
- `GET /auth/login` - Initiate Google OAuth flow
- `POST /auth/logout` - End user session

### Calendar
- `GET /calendar/events?date=YYYY-MM-DD` - Fetch events for specific date
- `POST /calendar/events` - Add new events to calendar

### Profiles
- `GET /profiles/users` - Get user profile data
- `GET /profiles/pets` - Get pet profile data

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Email server running on port 5001

### Installation

1. Navigate to the frontend directory:
```bash
cd project/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Usage Flow

1. **Authentication**: User is redirected to Google OAuth if not logged in
2. **Calendar View**: Default view showing monthly calendar with event indicators
3. **Date Selection**: Click any date to enter detailed day view
4. **Day View**: 24-hour scroll with visual event blocks and time navigation
5. **Profile Access**: Floating action button to view user and pet profiles
6. **Navigation**: Easy navigation between calendar and day views

## Component Architecture

### AuthProvider
- Manages authentication state throughout the application
- Handles login/logout operations
- Provides user context to child components

### CalendarView
- Renders monthly calendar grid with proper week alignment
- Shows event indicators for dates with scheduled events
- Handles month navigation and date selection

### DayView
- 24-hour vertical scroll interface
- Intelligent event positioning for overlaps
- Highlighted business hours (8 AM - 8 PM)
- Current time indicator for today's view

### ProfilePanel
- User information display
- Expandable pet profile cards
- Medication and activity tracking
- Responsive grid layout

## Styling Approach

- **Mobile-First**: Designed primarily for mobile devices
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Components**: Consistent design system
- **Responsive Design**: Adapts to various screen sizes
- **Accessibility**: Proper focus states and ARIA labels

## Future Enhancements

- **Event Editing**: Add/edit/delete calendar events (CRUD operations)
- **AI Integration**: Calendar updates with pet care recommendations
- **Offline Support**: Service worker for offline functionality
- **Push Notifications**: Reminders for pet care activities
- **Multi-Pet Management**: Enhanced support for multiple pets

## Browser Support

- Modern browsers with ES2020+ support
- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Maintain responsive design principles
4. Write self-documenting code with appropriate comments
5. Test on multiple screen sizes and devices
