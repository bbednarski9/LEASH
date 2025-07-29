import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

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