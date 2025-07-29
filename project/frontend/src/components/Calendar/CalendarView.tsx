import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar, LogOut } from 'lucide-react';
import { useAuth } from '../Auth/AuthProvider';
import type { CalendarEvent } from '../../services/api';
import { apiService } from '../../services/api';

interface CalendarViewProps {
  onDateSelect: (date: Date) => void;
  selectedDate: Date;
  monthEvents: { [date: string]: CalendarEvent[] };
  setMonthEvents: React.Dispatch<React.SetStateAction<{ [date: string]: CalendarEvent[] }>>;
}

const CalendarView: React.FC<CalendarViewProps> = ({ 
  onDateSelect, 
  selectedDate,
  monthEvents,
  setMonthEvents 
}) => {
  const { user, logout } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [loading, setLoading] = useState(false);

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  // Removed unused calendarDays variable

  // Generate calendar grid with proper week alignment
  const generateCalendarGrid = () => {
    const startOfFirstWeek = new Date(monthStart);
    startOfFirstWeek.setDate(startOfFirstWeek.getDate() - monthStart.getDay());
    
    const endOfLastWeek = new Date(monthEnd);
    const daysToAdd = 6 - monthEnd.getDay();
    endOfLastWeek.setDate(endOfLastWeek.getDate() + daysToAdd);
    
    return eachDayOfInterval({ start: startOfFirstWeek, end: endOfLastWeek });
  };

  const calendarGrid = generateCalendarGrid();

  // Update the fetchMonthEvents function
  const fetchMonthEvents = async (date: Date) => {
    setLoading(true);
    try {
      const start = startOfMonth(date);
      const end = endOfMonth(date);
      
      // Format dates for API
      const startStr = apiService.formatDateForAPI(start);
      const endStr = apiService.formatDateForAPI(end);
      
      // Fetch all events for the month in one request
      const events = await apiService.getCalendarEventsBulk(startStr, endStr);
      
      // Group events by date
      const eventsByDate: { [date: string]: CalendarEvent[] } = {};
      events.forEach(event => {
        const eventDate = event.start_time.split('T')[0]; // Get YYYY-MM-DD from ISO string
        if (!eventsByDate[eventDate]) {
          eventsByDate[eventDate] = [];
        }
        eventsByDate[eventDate].push(event);
      });
      
      setMonthEvents(eventsByDate);
    } catch (error) {
      console.error('Error fetching month events:', error);
      setMonthEvents({});
    } finally {
      setLoading(false);
    }
  };

  // Fetch events when month changes
  useEffect(() => {
    fetchMonthEvents(currentDate);
  }, [currentDate]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    onDateSelect(today);
  };

  const handleLogout = async () => {
    await logout();
  };

  const getEventCountForDate = (date: Date): number => {
    const dateStr = apiService.formatDateForAPI(date);
    return monthEvents[dateStr]?.length || 0;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-900">Pet Calendar</h1>
            </div>
            {user && (
              <div className="text-sm text-gray-600">
                Welcome, {user.name}
              </div>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      <div className="p-4 max-w-4xl mx-auto">
        {/* Calendar Navigation */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <h2 className="text-2xl font-bold text-gray-900">
                {format(currentDate, 'MMMM yyyy')}
              </h2>
              <button
                onClick={goToToday}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
              >
                Today
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateMonth('prev')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() => navigateMonth('next')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {/* Day headers */}
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="p-3 text-center text-sm font-medium text-gray-500">
                {day}
              </div>
            ))}
            
            {/* Calendar days */}
            {calendarGrid.map((day) => {
              const isCurrentMonth = isSameMonth(day, currentDate);
              const isSelected = isSameDay(day, selectedDate);
              const isTodayDate = isToday(day);
              const eventCount = getEventCountForDate(day);
              
              return (
                <button
                  key={day.toISOString()}
                  onClick={() => onDateSelect(day)}
                  className={`
                    relative p-3 h-16 text-left transition-colors duration-200
                    ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                    ${isSelected ? 'bg-blue-100 border-2 border-blue-500' : 'border border-gray-200'}
                    ${isTodayDate ? 'bg-blue-50' : 'bg-white'}
                    hover:bg-gray-50 rounded-lg
                  `}
                >
                  <span className={`text-sm ${isTodayDate ? 'font-bold' : ''}`}>
                    {format(day, 'd')}
                  </span>
                  {eventCount > 0 && (
                    <div className="absolute bottom-1 right-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      {eventCount > 1 && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                          {eventCount > 9 ? '9+' : eventCount}
                        </div>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="inline-flex items-center space-x-2 text-gray-600">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Loading calendar events...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CalendarView; 