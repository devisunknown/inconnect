import Constants from 'expo-constants';

const debuggerHost =
  Constants.expoConfig?.hostUri ??
  (Constants as any).manifest?.debuggerHost ??
  (Constants as any).expoGoConfig?.debuggerHost ??
  'localhost:8000';
const host = debuggerHost.split(':')[0];
const API_BASE = `http://${host}:8000/api`;

export interface Match {
  user_id: number;
  username: string;
  full_name: string;
  bio: string;
  avatar: string | null;
  shared_interests: Array<{ id: number; name: string; icon: string; category: string }>;
  score: number;
  existing_chat_id: number | null;
}

interface ApiOptions {
  method?: string;
  body?: any;
  token?: string;
}

async function apiRequest<T = any>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.detail || JSON.stringify(error));
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  auth: {
    signup: (data: {
      first_name: string;
      username: string;
      email: string;
      password1: string;
      password2: string;
    }) => apiRequest<{ token: string; user: any }>('/auth/signup/', { method: 'POST', body: data }),

    login: (username: string, password: string) =>
      apiRequest<{ token: string; user: any }>('/auth/login/', {
        method: 'POST',
        body: { username, password },
      }),

    me: (token: string) => apiRequest<any>('/auth/me/', { token }),

    logout: (token: string) =>
      apiRequest<void>('/auth/logout/', { method: 'POST', token }),
  },

  interests: {
    list: () => apiRequest<any[]>('/interests/'),
    select: (interestIds: number[], token: string) =>
      apiRequest<any>('/interests/select/', { method: 'POST', body: { interest_ids: interestIds }, token }),
  },

  matches: {
    list: (token: string) => apiRequest<Match[]>('/matches/', { token }),
  },
};
