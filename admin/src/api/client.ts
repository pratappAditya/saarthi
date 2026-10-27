const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

export async function adminFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('saarthi_admin_token');
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = endpoint.startsWith('http')
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers
    });

    if (res.status === 401 && !endpoint.includes('/auth/login')) {
      localStorage.removeItem('saarthi_admin_token');
      localStorage.removeItem('saarthi_admin_user');
      window.dispatchEvent(new CustomEvent('saarthi-admin-unauthorized'));
    }

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = data?.detail || data?.message || `Request failed with status ${res.status}`;
      throw new ApiError(res.status, msg, data);
    }

    return data as T;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(0, err.message || 'Network error connecting to Saarthi Control Plane.');
  }
}
