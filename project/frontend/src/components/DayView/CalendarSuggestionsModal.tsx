import React, { useState } from 'react';
import { format, parseISO } from 'date-fns';
import { X, Calendar, Clock, MapPin, Check, Trash2, Loader2 } from 'lucide-react';
import type { CalendarSuggestion } from '../../services/api';

interface CalendarSuggestionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  suggestions: CalendarSuggestion[];
  onAccept: (suggestion: CalendarSuggestion) => Promise<void>;
  onReject: (suggestion: CalendarSuggestion) => void;
  loading?: boolean;
}

const CalendarSuggestionsModal: React.FC<CalendarSuggestionsModalProps> = ({
  isOpen,
  onClose,
  suggestions,
  onAccept,
  onReject,
  loading = false
}) => {
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

  if (!isOpen) return null;

  const handleAccept = async (suggestion: CalendarSuggestion) => {
    const timeForId = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc || 'unknown';
    const suggestionId = `${suggestion.event_title}-${timeForId}`;
    setProcessingIds(prev => new Set(prev).add(suggestionId));
    
    try {
      await onAccept(suggestion);
    } catch (error) {
      console.error('Error accepting suggestion:', error);
      // Could show an error notification here
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(suggestionId);
        return newSet;
      });
    }
  };

  const handleReject = (suggestion: CalendarSuggestion) => {
    onReject(suggestion);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActivityIcon = (activityType: string) => {
    switch (activityType.toLowerCase()) {
      case 'walk':
        return '🚶‍♂️';
      case 'feeding':
        return '🍽️';
      case 'medication':
        return '💊';
      case 'play':
        return '🎾';
      case 'grooming':
        return '✂️';
      case 'training':
        return '🎯';
      default:
        return '📅';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full mx-4 overflow-hidden" style={{ height: '80vh', marginTop: '10vh', marginBottom: '10vh' }}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              🐕 Calendar Suggestions for Pet Care
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Review and accept suggestions that work for your schedule
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto" style={{ height: 'calc(80vh - 180px)' }}>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
                <p className="text-gray-600">Generating personalized suggestions...</p>
                <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
              </div>
            </div>
          ) : suggestions.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No suggestions available</h3>
              <p className="text-gray-600">
                Try again or check that your agent server is running.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {suggestions
                .sort((a, b) => {
                  const aTime = a.event_start_time_local || (a as any).event_start_time_utc || '';
                  const bTime = b.event_start_time_local || (b as any).event_start_time_utc || '';
                  
                  // Create full datetime strings for sorting
                  const aFullTime = aTime.includes('T') ? aTime : `${a.date}T${aTime}`;
                  const bFullTime = bTime.includes('T') ? bTime : `${b.date}T${bTime}`;
                  
                  return new Date(aFullTime).getTime() - new Date(bFullTime).getTime();
                })
                                .map((suggestion, index) => {
                                  const timeForId = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc || 'unknown';
                                  const suggestionId = `${suggestion.event_title}-${timeForId}`;
                 const isProcessing = processingIds.has(suggestionId);
                 
                                   // Debug: Check what we're actually getting from the agent server
                  console.log('Full suggestion object:', suggestion);
                  
                  // Defensive parsing - check if fields exist and have valid values
                  const startTimeString = suggestion.event_start_time_local || (suggestion as any).event_start_time_utc;
                  const endTimeString = suggestion.event_end_time_local || (suggestion as any).event_end_time_utc;
                  
                  if (!startTimeString || !endTimeString) {
                    console.error('Missing time fields in suggestion:', {
                      suggestion,
                      startTimeString,
                      endTimeString
                    });
                    return null; // Skip this suggestion if times are missing
                  }
                  
                  // Handle case where LLM returns just time portion (e.g., "06:30:00") instead of full datetime
                  const createFullDateTime = (timeStr: string, date: string) => {
                    if (timeStr.includes('T')) {
                      // Already a full datetime string
                      return timeStr;
                    } else {
                      // Just time portion, combine with date
                      return `${date}T${timeStr}`;
                    }
                  };
                  
                  const fullStartTime = createFullDateTime(startTimeString, suggestion.date);
                  const fullEndTime = createFullDateTime(endTimeString, suggestion.date);
                  
                  let startTimeLocal, endTimeLocal;
                  try {
                    startTimeLocal = parseISO(fullStartTime);
                    endTimeLocal = parseISO(fullEndTime);
                  } catch (error) {
                    console.error('Error parsing time strings:', {
                      startTimeString,
                      endTimeString,
                      fullStartTime,
                      fullEndTime,
                      error
                    });
                    return null; // Skip this suggestion if parsing fails
                  }
                  
                  console.log('Debug local timezone display:', {
                    originalStartTime: startTimeString,
                    parsedStartTime: startTimeLocal,
                    formattedLocal: format(startTimeLocal, 'h:mm a'),
                    browserTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                  });
                 
                 return (
                   <div
                     key={index}
                     className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                   >
                     <div className="w-full">
                       {/* Title and Activity Type */}
                       <div className="flex items-center space-x-2 mb-2">
                         <span className="text-lg">
                           {getActivityIcon(suggestion.activity_type)}
                         </span>
                         <h3 className="text-lg font-medium text-gray-900">
                           {suggestion.event_title}
                         </h3>
                         <span
                           className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(
                             suggestion.priority
                           )}`}
                         >
                           {suggestion.priority} priority
                         </span>
                       </div>

                                                {/* Time and Date */}
                         <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                           <div className="flex items-center space-x-1">
                             <Calendar className="w-4 h-4" />
                             <span>{format(parseISO(suggestion.date), 'MMM d, yyyy')}</span>
                           </div>
                           <div className="flex items-center space-x-1">
                             <Clock className="w-4 h-4" />
                             <span>
                               {format(startTimeLocal, 'h:mm a')} - {format(endTimeLocal, 'h:mm a')}
                             </span>
                           </div>
                           <div className="flex items-center space-x-1 text-xs text-gray-500">
                             <span>🌍 Your timezone: {Intl.DateTimeFormat().resolvedOptions().timeZone}</span>
                           </div>
                         </div>

                       {/* Description */}
                       <p className="text-gray-700 mb-3">{suggestion.event_description}</p>

                       {/* Pet Names and Activity Type */}
                       <div className="flex items-center space-x-4 text-sm mb-4">
                         <div className="flex items-center space-x-1">
                           <span className="font-medium text-gray-700">Pets:</span>
                           <span className="text-gray-600">
                             {suggestion.pet_names.join(', ')}
                           </span>
                         </div>
                         <div className="flex items-center space-x-1">
                           <span className="font-medium text-gray-700">Type:</span>
                           <span className="text-gray-600 capitalize">
                             {suggestion.activity_type}
                           </span>
                         </div>
                       </div>

                       {/* Action Buttons - Now at the bottom */}
                       <div className="flex items-center justify-end space-x-2 pt-3 border-t border-gray-100">
                         <button
                           onClick={() => handleReject(suggestion)}
                           disabled={isProcessing}
                           className="flex items-center space-x-1 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                         >
                           <Trash2 className="w-4 h-4" />
                           <span>Reject</span>
                         </button>
                         <button
                           onClick={() => handleAccept(suggestion)}
                           disabled={isProcessing}
                           className="flex items-center space-x-1 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                         >
                           {isProcessing ? (
                             <Loader2 className="w-4 h-4 animate-spin" />
                           ) : (
                             <Check className="w-4 h-4" />
                           )}
                           <span>{isProcessing ? 'Adding...' : 'Accept'}</span>
                         </button>
                       </div>
                     </div>
                   </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-5 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {suggestions.length > 0 ? (
                <span>{suggestions.length} suggestions available</span>
              ) : (
                <span>No suggestions to review</span>
              )}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarSuggestionsModal; 