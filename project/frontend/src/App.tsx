import React, { useState } from 'react';
import { AuthProvider, useAuth } from './components/Auth/AuthProvider';
import LoginScreen from './components/Auth/LoginScreen';
import CalendarView from './components/Calendar/CalendarView';
import DayView from './components/DayView/DayView';
import ProfilePanel from './components/Profile/ProfilePanel';
import type { CalendarEvent } from './services/api';
import { format } from 'date-fns';

type ViewMode = 'calendar' | 'day' | 'profile';

const AppContent: React.FC = () => {
  const { authStatus, loading } = useAuth();
  const [currentView, setCurrentView] = useState<ViewMode>('calendar');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [monthEvents, setMonthEvents] = useState<{ [date: string]: CalendarEvent[] }>({});

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!authStatus?.authenticated) {
    return <LoginScreen />;
  }

  // Helper to get events for a specific date
  const getEventsForDate = (date: Date): CalendarEvent[] => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return monthEvents[dateStr] || [];
  };

  // Handle date selection from calendar view
  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setCurrentView('day');
  };

  // Handle navigation back to calendar
  const handleBackToCalendar = () => {
    setCurrentView('calendar');
  };

  // Render based on current view
  switch (currentView) {
    case 'day':
      return (
        <DayView 
          selectedDate={selectedDate} 
          onBackToCalendar={handleBackToCalendar}
          prefetchedEvents={getEventsForDate(selectedDate)}
        />
      );
    
    case 'profile':
      return (
        <div className="min-h-screen bg-gray-50">
          <div className="p-4 max-w-4xl mx-auto">
            <ProfilePanel />
            <div className="text-center">
              <button
                onClick={() => setCurrentView('calendar')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Back to Calendar
              </button>
            </div>
          </div>
        </div>
      );
    
    case 'calendar':
      return (
        <CalendarView
          selectedDate={selectedDate}
          onDateSelect={handleDateSelect}
          monthEvents={monthEvents}
          setMonthEvents={setMonthEvents}
        />
      );
    
    default:
      return null;
  }
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
