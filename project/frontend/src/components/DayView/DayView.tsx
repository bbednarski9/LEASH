import React, { useState, useEffect, useRef } from 'react';
import { format, parseISO } from 'date-fns';
import { ArrowLeft, Plus, RefreshCw, Info, X } from 'lucide-react';
import type { CalendarEvent, CalendarSuggestion, User, Pet } from '../../services/api';
import { apiService } from '../../services/api';
import CalendarSuggestionsModal from './CalendarSuggestionsModal';

// Google Calendar color mapping based on colorId
const GOOGLE_CALENDAR_COLORS: { [key: string]: { background: string; foreground: string; border: string } } = {
  '1': { background: '#7986cb', foreground: '#ffffff', border: '#5c6bc0' }, // Lavender
  '2': { background: '#33b679', foreground: '#ffffff', border: '#2e7d32' }, // Sage
  '3': { background: '#8e24aa', foreground: '#ffffff', border: '#6a1b9a' }, // Grape
  '4': { background: '#e67c73', foreground: '#ffffff', border: '#d32f2f' }, // Flamingo
  '5': { background: '#f6c026', foreground: '#000000', border: '#f57f17' }, // Banana
  '6': { background: '#f5511d', foreground: '#ffffff', border: '#e65100' }, // Tangerine
  '7': { background: '#039be5', foreground: '#ffffff', border: '#0277bd' }, // Peacock
  '8': { background: '#616161', foreground: '#ffffff', border: '#424242' }, // Graphite
  '9': { background: '#3f51b5', foreground: '#ffffff', border: '#303f9f' }, // Blueberry
  '10': { background: '#0b8043', foreground: '#ffffff', border: '#2e7d32' }, // Basil
  '11': { background: '#d50000', foreground: '#ffffff', border: '#c62828' }, // Tomato
};

// Default color if no colorId is provided
const DEFAULT_COLOR = GOOGLE_CALENDAR_COLORS['1'];

interface DayViewProps {
  selectedDate: Date;
  onBackToCalendar: () => void;
  prefetchedEvents?: CalendarEvent[]; // Add this prop
}

const DayView: React.FC<DayViewProps> = ({ 
  selectedDate, 
  onBackToCalendar,
  prefetchedEvents 
}) => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [hourHeight, setHourHeight] = useState(80);
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showSuggestionsModal, setShowSuggestionsModal] = useState(false);
  const [suggestions, setSuggestions] = useState<CalendarSuggestion[]>([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [profiles, setProfiles] = useState<{ user: User; pets: Pet[] } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Generate hours array (24 hours)
  const hours = Array.from({ length: 24 }, (_, i) => i);

  useEffect(() => {
    if (prefetchedEvents) {
      // Use pre-fetched events if available
      setEvents(prefetchedEvents);
    } else {
      // Fall back to loading events if not provided
      loadDayEvents();
    }
    
    // Load profiles for agent server
    loadProfiles();
    
    // Scroll to 8 AM on mount after hour height is set
    setTimeout(() => {
      if (scrollRef.current && hourHeight > 0) {
        const eightAMPosition = 8 * hourHeight;
        scrollRef.current.scrollTo({ top: eightAMPosition, behavior: 'smooth' });
      }
    }, 150);
  }, [selectedDate, hourHeight, prefetchedEvents]);

  useEffect(() => {
    // Calculate responsive hour height based on screen size
    const calculateHourHeight = () => {
      const screenHeight = window.innerHeight;
      const headerHeight = 80; // Header height
      const buttonHeight = 80; // Bottom button height
      const availableHeight = screenHeight - headerHeight - buttonHeight;
      
      // Try to fit 12 hours on screen comfortably, minimum 60px per hour
      const idealHeight = Math.max(60, Math.floor(availableHeight / 12));
      setHourHeight(idealHeight);
    };

    calculateHourHeight();
    
    // Recalculate on window resize
    const handleResize = () => calculateHourHeight();
    window.addEventListener('resize', handleResize);
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadDayEvents = async () => {
    setLoading(true);
    try {
      const dateStr = apiService.formatDateForAPI(selectedDate);
      const dayEvents = await apiService.getCalendarEvents(dateStr);
      setEvents(dayEvents);
    } catch (error) {
      console.error('Error loading day events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const loadProfiles = async () => {
    try {
      const profileData = await apiService.loadProfilesFromFiles();
      setProfiles(profileData);
    } catch (error) {
      console.error('Error loading profiles:', error);
    }
  };

  const handleRefresh = async () => {
    await loadDayEvents();
  };

  const formatHour = (hour: number): string => {
    if (hour === 0) return '12 AM';
    if (hour === 12) return '12 PM';
    if (hour < 12) return `${hour} AM`;
    return `${hour - 12} PM`;
  };

  const getEventPosition = (event: CalendarEvent) => {
    const startTime = parseISO(event.start_time);
    const endTime = parseISO(event.end_time);
    
    const startHour = startTime.getHours();
    const startMinute = startTime.getMinutes();
    const endHour = endTime.getHours();
    const endMinute = endTime.getMinutes();
    
    const top = (startHour + startMinute / 60) * hourHeight;
    const height = ((endHour + endMinute / 60) - (startHour + startMinute / 60)) * hourHeight;
    
    return { top, height };
  };

  const isHighlightedHour = (hour: number): boolean => {
    return hour >= 8 && hour <= 20; // 8 AM to 8 PM
  };

  // Group overlapping events for better display
  const processEventsForDisplay = () => {
    // Sort events by start time and duration
    const sortedEvents = [...events].sort((a, b) => {
      const aStart = parseISO(a.start_time);
      const bStart = parseISO(b.start_time);
      if (aStart.getTime() !== bStart.getTime()) {
        return aStart.getTime() - bStart.getTime();
      }
      const aDuration = parseISO(a.end_time).getTime() - aStart.getTime();
      const bDuration = parseISO(b.end_time).getTime() - bStart.getTime();
      return bDuration - aDuration; // Longer events first
    });

    // Create columns for overlapping events
    const columns: CalendarEvent[][] = [];
    
    sortedEvents.forEach(event => {
      const eventStart = parseISO(event.start_time).getTime();
      const eventEnd = parseISO(event.end_time).getTime();
      
      // Find a column where the event doesn't overlap
      let columnIndex = 0;
      let placed = false;
      
      while (!placed) {
        if (!columns[columnIndex]) {
          columns[columnIndex] = [event];
          placed = true;
        } else {
          // Check if event overlaps with any event in this column
          const hasOverlap = columns[columnIndex].some(existingEvent => {
            const existingStart = parseISO(existingEvent.start_time).getTime();
            const existingEnd = parseISO(existingEvent.end_time).getTime();
            return !(eventEnd <= existingStart || eventStart >= existingEnd);
          });
          
          if (!hasOverlap) {
            columns[columnIndex].push(event);
            placed = true;
          } else {
            columnIndex++;
          }
        }
      }
    });

    // Calculate positions for each event
    return sortedEvents.map(event => {
      const position = getEventPosition(event);
      
      // Find which column contains this event
      const columnIndex = columns.findIndex(col => col.some(e => e.id === event.id));
      
      // Calculate overlapping events for this specific time slot
      const eventStart = parseISO(event.start_time).getTime();
      const eventEnd = parseISO(event.end_time).getTime();
      
      const overlappingColumns = columns.filter(col => 
        col.some(existingEvent => {
          const existingStart = parseISO(existingEvent.start_time).getTime();
          const existingEnd = parseISO(existingEvent.end_time).getTime();
          return !(eventEnd <= existingStart || eventStart >= existingEnd);
        })
      ).length;

      return {
        ...event,
        position,
        width: `${95 / overlappingColumns}%`, // Leave small gap between events
        left: `${(columnIndex * 95) / overlappingColumns}%`,
      };
    });
  };

  const processedEvents = processEventsForDisplay();

  // Debug logging
  console.log('DayView Debug Info:');
  console.log('Raw events:', events);
  console.log('Processed events:', processedEvents);
  console.log('Hour height:', hourHeight);
  console.log('Selected date:', selectedDate);

  const handleScheduleDogCare = async () => {
    if (!profiles) {
      alert('Profile data not loaded. Please refresh the page.');
      return;
    }

    setSuggestionsLoading(true);
    setShowSuggestionsModal(true);
    
    try {
      // Convert profiles and current events to agent server format
      const targetDate = apiService.formatDateForAPI(selectedDate);
      const agentRequest = apiService.convertToAgentFormat(
        profiles.user,
        profiles.pets,
        events,
        targetDate
      );

      console.log('Sending request to agent server:', agentRequest);

      // Call agent server for suggestions
      const response = await apiService.getCalendarSuggestions(agentRequest);
      
      if (response.success) {
        setSuggestions(response.suggestions);
        console.log('Received suggestions:', response.suggestions);
      } else {
        throw new Error(response.error || 'Failed to get suggestions');
      }
    } catch (error) {
      console.error('Error getting calendar suggestions:', error);
      // Show error message but keep modal open
      setSuggestions([]);
      alert('Failed to get calendar suggestions. Please make sure the agent server is running on port 5002.');
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const handleAcceptSuggestion = async (suggestion: CalendarSuggestion) => {
    try {
      // Convert suggestion to the email server's expected format
      // Note: suggestion times are in local timezone, need to convert to UTC for Google Calendar
      const startTimeString = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc;
      const endTimeString = suggestion.event_end_time_local || (suggestion as any).event_end_time_utc;
      
      if (!startTimeString || !endTimeString) {
        console.error('Missing time fields when accepting suggestion:', suggestion);
        return;
      }
      
      // Handle case where LLM returns just time portion instead of full datetime
      const createFullDateTime = (timeStr: string, date: string) => {
        if (timeStr.includes('T')) {
          return timeStr;
        } else {
          return `${date}T${timeStr}`;
        }
      };
      
      const fullStartTime = createFullDateTime(startTimeString, suggestion.date);
      const fullEndTime = createFullDateTime(endTimeString, suggestion.date);
      
      const startTimeLocal = new Date(fullStartTime);
      const endTimeLocal = new Date(fullEndTime);
      
      const eventRequest = {
        events: [{
          date: suggestion.date,
          'event-start-time-UTC': startTimeLocal.toISOString(),
          'event-end-time-UTC': endTimeLocal.toISOString(),
          'event-title': suggestion.event_title,
          'event-description': suggestion.event_description
        }]
      };

      console.log('Creating calendar event:', eventRequest);

      // Create the event via email server
      await apiService.createCalendarEvents(eventRequest);
      
      // Remove the suggestion from the list
      const suggestionTime = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc;
      setSuggestions(prev => prev.filter(s => {
        const sTime = s.event_start_time_local || (s as any).event_start_time_utc;
        return sTime !== suggestionTime || s.event_title !== suggestion.event_title;
      }));
      
      // Refresh events to show the new one
      await loadDayEvents();
      
      console.log('Successfully added event to calendar');
    } catch (error) {
      console.error('Error accepting suggestion:', error);
      alert('Failed to add event to calendar. Please try again.');
      throw error; // Re-throw to handle in modal
    }
  };

  const handleRejectSuggestion = (suggestion: CalendarSuggestion) => {
    // Simply remove from suggestions list
    const suggestionTime = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc;
    setSuggestions(prev => prev.filter(s => {
      const sTime = s.event_start_time_local || (s as any).event_start_time_utc;
      return sTime !== suggestionTime || s.event_title !== suggestion.event_title;
    }));
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Fixed Header */}
      <div className="bg-white shadow-sm border-b z-10">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={onBackToCalendar}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Calendar</span>
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {format(selectedDate, 'EEEE, MMMM d, yyyy')}
              </h1>
            </div>
          </div>
          <div className="flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              <button
                onClick={() => setShowInfoModal(true)}
                className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Info className="w-4 h-4" />
                <span>Info</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Info Modal */}
      {showInfoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Debug Information</h3>
              <button
                onClick={() => setShowInfoModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div><strong>Events count:</strong> {events.length}</div>
              <div><strong>Processed events:</strong> {processedEvents.length}</div>
              <div><strong>Hour height:</strong> {hourHeight}px</div>
              <div><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</div>
              <div><strong>Selected date:</strong> {format(selectedDate, 'yyyy-MM-dd')}</div>
              {events.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div><strong>First event:</strong></div>
                  <div className="ml-2 space-y-1">
                    <div><strong>Title:</strong> {events[0].title}</div>
                    <div><strong>Start:</strong> {events[0].start_time}</div>
                    <div><strong>End:</strong> {events[0].end_time}</div>
                    {processedEvents.length > 0 && (
                      <>
                        <div className="mt-2"><strong>Calculated position:</strong></div>
                        <div className="ml-2 space-y-1">
                          <div>Top: {processedEvents[0].position.top}px</div>
                          <div>Height: {processedEvents[0].position.height}px</div>
                          <div>Width: {processedEvents[0].width}</div>
                          <div>Left: {processedEvents[0].left}</div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Scrollable Day View */}
      <div className="flex-1 overflow-hidden">
        <div 
          ref={scrollRef}
          className="h-full overflow-y-auto relative"
        >
          <div className="relative bg-transparent" style={{ height: `${24 * hourHeight}px` }}>
            {/* Time grid */}
            {hours.map((hour) => (
              <div
                key={hour}
                className={`relative border-b border-gray-200 z-0 ${
                  isHighlightedHour(hour) ? 'bg-blue-50' : 'bg-white'
                } bg-transparent`}
                style={{ height: `${hourHeight}px`, background: 'transparent' }}
              >
                {/* Hour label */}
                <div className="absolute left-0 top-0 w-20 h-full flex items-start justify-center pt-2 bg-transparent z-0"
                     style={{ background: 'transparent' }}>
                  <span className="text-sm text-gray-500 font-medium">
                    {formatHour(hour)}
                  </span>
                </div>
                
                {/* Time slot area */}
                <div className="ml-20 h-full border-l border-gray-200 relative bg-transparent z-0"
                     style={{ background: 'transparent' }}>
                  {/* Quarter-hour lines (subtle) */}
                  <div 
                    className="absolute left-0 right-0 h-px bg-gray-50 z-0"
                    style={{ top: `${hourHeight / 4}px` }}
                  ></div>
                  <div 
                    className="absolute left-0 right-0 h-px bg-gray-50 z-0"
                    style={{ top: `${(hourHeight * 3) / 4}px` }}
                  ></div>
                </div>
              </div>
            ))}

            {/* Current time indicator (only for today) */}
            {format(selectedDate, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd') && (
              <div
                className="absolute left-20 right-0 h-0.5 bg-red-500 z-20"
                style={{
                  top: `${(new Date().getHours() + new Date().getMinutes() / 60) * hourHeight}px`,
                }}
              >
                <div className="absolute left-0 top-0 w-3 h-3 bg-red-500 rounded-full -translate-x-1.5 -translate-y-1"></div>
              </div>
            )}
          </div>

          {/* Events overlay - moved outside the time grid container */}
          <div className="absolute top-0 left-20 right-0 pointer-events-none z-50" style={{ height: `${24 * hourHeight}px` }}>
            {loading ? (
              <div className="flex items-center justify-center pointer-events-auto z-50" style={{ height: `${hourHeight * 4}px` }}>
                <div className="flex items-center space-x-2 text-gray-600">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span>Loading events...</span>
                </div>
              </div>
            ) : processedEvents.length === 0 ? (
              <div className="flex items-center justify-center pointer-events-auto z-50" style={{ height: `${hourHeight * 4}px` }}>
                <div className="text-gray-500 text-center">
                  <div>No events found for this day</div>
                  <div className="text-xs mt-1">({format(selectedDate, 'yyyy-MM-dd')})</div>
                </div>
              </div>
            ) : (
              processedEvents.map((event) => {
                const eventColor = GOOGLE_CALENDAR_COLORS[event.color_id || '1'] || DEFAULT_COLOR;
                return (
                  <div
                    key={event.id}
                    className="absolute rounded-lg overflow-hidden pointer-events-auto hover:opacity-90 transition-opacity cursor-pointer group z-50 shadow-md"
                    style={{
                      top: `${event.position.top}px`,
                      height: `${Math.max(event.position.height, 30)}px`,
                      width: event.width,
                      left: event.left,
                      minHeight: '30px',
                      backgroundColor: eventColor.background,
                      borderColor: eventColor.border,
                      borderWidth: '1px',
                      borderStyle: 'solid',
                    }}
                  >
                    <div className="p-2 h-full flex flex-col overflow-y-auto">
                      <div 
                        className="text-sm font-medium mb-1 flex-shrink-0"
                        style={{ color: eventColor.foreground }}
                      >
                        {event.title}
                      </div>
                      <div 
                        className="text-xs opacity-90 mb-1 flex-shrink-0"
                        style={{ color: eventColor.foreground }}
                      >
                        {format(parseISO(event.start_time), 'h:mm a')} - {format(parseISO(event.end_time), 'h:mm a')}
                      </div>
                      {event.description && (
                        <div 
                          className="text-xs opacity-75 flex-1 overflow-y-auto"
                          style={{ color: eventColor.foreground }}
                        >
                          {event.description}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Calendar Suggestions Modal */}
      <CalendarSuggestionsModal
        isOpen={showSuggestionsModal}
        onClose={() => setShowSuggestionsModal(false)}
        suggestions={suggestions}
        onAccept={handleAcceptSuggestion}
        onReject={handleRejectSuggestion}
        loading={suggestionsLoading}
      />

      {/* Fixed Bottom Button */}
      <div className="bg-white border-t shadow-lg p-4">
        <button
          onClick={handleScheduleDogCare}
          disabled={suggestionsLoading || !profiles}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:cursor-not-allowed"
        >
          <Plus className="w-5 h-5" />
          <span>
            {suggestionsLoading ? 'Generating Suggestions...' : 'Schedule Dog Care'}
          </span>
        </button>
      </div>
    </div>
  );
};

export default DayView; 