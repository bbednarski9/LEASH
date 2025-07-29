import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';
const AGENT_SERVER_URL = 'http://localhost:5002';

// Configure axios to include credentials (cookies) in requests
axios.defaults.withCredentials = true;

export interface User {
  name: string;
  email: string;
  'yard-access': boolean;
  'preferred-walk-times': string[];
  'exercise-level': string;
}

export interface Medication {
  name: string;
  start_date: string;
  end_date: string;
  'count-per-day': number;
  'mg-per-serving': number;
  'give-with-food': boolean;
  notes: string;
}

export interface Pet {
  id: string;
  name: string;
  age: string;
  breed: string;
  weight: string;
  gender: string;
  color: string;
  'walk-time-per-day': string;
  'energy-level': string;
  'training-level': string;
  current_medications: Medication[];
  'dietary-restrictions': string[];
  'favorite-activities': string[];
  'behavioral-notes': string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  description?: string;
  color_id?: string;
  background_color?: string;
  foreground_color?: string;
}

export interface AuthStatus {
  authenticated: boolean;
  user_email?: string;
  expires_at?: string;
}

export interface CalendarEventRequest {
  events: {
    date: string;
    'event-start-time-UTC': string;
    'event-end-time-UTC': string;
    'event-title': string;
    'event-description': string;
  }[];
}

// Agent Server Types
export interface AgentCalendarEvent {
  date: string;
  event_start_time_local: string;
  event_end_time_local: string;
  event_title: string;
  event_description: string;
}

export interface AgentPetDetails {
  name: string;
  age: string;
  breed: string;
  weight: string;
  walk_time_per_day: string;
  current_medications?: any[];
  special_needs?: string;
  activity_level: string;
}

export interface AgentOwnerDetails {
  owner_name: string;
  yard_access: boolean;
  preferred_walk_times: string[];
  work_schedule?: string;
  availability_notes?: string;
  preferred_activity_duration?: string;
}

export interface AgentCalendarFillRequest {
  current_calendar: AgentCalendarEvent[];
  pet_details: AgentPetDetails[];
  owner_details: AgentOwnerDetails;
  target_date?: string;
  user_timezone?: string;
  model?: string;
  temperature?: number;
}

export interface CalendarSuggestion {
  date: string;
  event_start_time_local: string;
  event_end_time_local: string;
  event_title: string;
  event_description: string;
  priority: string;
  activity_type: string;
  pet_names: string[];
}

export interface AgentCalendarResponse {
  success: boolean;
  suggestions: CalendarSuggestion[];
  execution_time_ms?: number;
  model_used?: string;
  error?: string;
  metadata?: any;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Authentication endpoints
  async getAuthStatus(): Promise<AuthStatus> {
    const response = await axios.get(`${this.baseURL}/auth/status`);
    return response.data;
  }

  async login(): Promise<void> {
    // Redirect to login endpoint
    window.location.href = `${this.baseURL}/auth/login`;
  }

  async logout(): Promise<void> {
    await axios.post(`${this.baseURL}/auth/logout`);
  }

  // Calendar endpoints
  async getCalendarEvents(date: string): Promise<CalendarEvent[]> {
    const response = await axios.get(`${this.baseURL}/calendar/events`, {
      params: { date }
    });
    return response.data.events || [];
  }

  async createCalendarEvents(eventRequest: CalendarEventRequest): Promise<any> {
    const response = await axios.post(`${this.baseURL}/calendar/events`, eventRequest);
    return response.data;
  }

  async getCalendarEventsBulk(startDate: string, endDate: string): Promise<CalendarEvent[]> {
    const response = await axios.get(`${this.baseURL}/calendar/events/bulk`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data.events || [];
  }

  // Profile endpoints
  async getUserProfile(): Promise<User> {
    const response = await axios.get(`${this.baseURL}/profiles/users`);
    return response.data.user || response.data.users?.[0];
  }

  async getPetProfiles(): Promise<Pet[]> {
    const response = await axios.get(`${this.baseURL}/profiles/pets`);
    return response.data.pets || [];
  }

  // Agent Server endpoints
  async getCalendarSuggestions(request: AgentCalendarFillRequest): Promise<AgentCalendarResponse> {
    const response = await axios.post(`${AGENT_SERVER_URL}/leash-daily-calendar-fill`, request, {
      params: { verbose: false },
      timeout: 30000, // 30 second timeout for AI processing
      withCredentials: false // Agent server doesn't need auth
    });
    return response.data;
  }

  // Profile helper methods
  async loadProfilesFromFiles(): Promise<{ user: User, pets: Pet[] }> {
    try {
      // Load from local files since profiles moved to frontend
      const userResponse = await fetch('/profiles/users.json');
      const petResponse = await fetch('/profiles/pets.json');
      
      const userData = await userResponse.json();
      const petData = await petResponse.json();
      
      return {
        user: userData.userDetails[0],
        pets: petData.pets
      };
    } catch (error) {
      console.error('Error loading profiles from files:', error);
      throw error;
    }
  }

  // Helper method to convert UTC/timezone-aware dates to local timezone for LLM
  private convertToLocalTime(dateTimeString: string): string {
    const date = new Date(dateTimeString);
    // Return in local timezone ISO format (removes timezone info for LLM clarity)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
  }

  // Convert frontend profiles to agent server format
  convertToAgentFormat(user: User, pets: Pet[], currentEvents: CalendarEvent[], targetDate: string): AgentCalendarFillRequest {
    // Convert current events to agent format using LOCAL timezone for LLM
    const agentEvents: AgentCalendarEvent[] = currentEvents.map(event => ({
      date: event.start_time.split('T')[0],
      event_start_time_local: this.convertToLocalTime(event.start_time),
      event_end_time_local: this.convertToLocalTime(event.end_time),
      event_title: event.title,
      event_description: event.description || ''
    }));

    // Convert pets to agent format
    const agentPets: AgentPetDetails[] = pets.map(pet => ({
      name: pet.name,
      age: pet.age,
      breed: pet.breed,
      weight: pet.weight,
      walk_time_per_day: pet['walk-time-per-day'],
      current_medications: pet.current_medications || [],
      special_needs: pet['behavioral-notes'] || '',
      activity_level: pet['energy-level'] || 'moderate'
    }));

    // Convert user to agent format
    const agentOwner: AgentOwnerDetails = {
      owner_name: user.name,
      yard_access: user['yard-access'],
      preferred_walk_times: user['preferred-walk-times'],
      work_schedule: 'Standard business hours', // Could be enhanced
      availability_notes: `Exercise preference: ${user['exercise-level']}`,
      preferred_activity_duration: '30-60 minutes'
    };

    return {
      current_calendar: agentEvents,
      pet_details: agentPets,
      owner_details: agentOwner,
      target_date: targetDate,
      user_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      model: 'llama3.2',
      temperature: 0.7
    };
  }

  // Utility methods
  formatDateForAPI(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  formatDateTimeForAPI(date: Date): string {
    return date.toISOString();
  }
}

export const apiService = new ApiService();
export default apiService; 