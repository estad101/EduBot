import axios, { AxiosInstance, AxiosError } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIClient {
  private client: AxiosInstance;
  private csrfToken: string | null = null;
  private sessionId: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 10000,
      withCredentials: true,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add auth token and CSRF token
    this.client.interceptors.request.use((config) => {
      const token = typeof window !== "undefined" ? localStorage.getItem("admin_token") : null;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // Add CSRF token for state-changing requests
      if (["POST", "PUT", "DELETE"].includes(config.method?.toUpperCase() || "") && this.csrfToken) {
        config.headers["X-CSRF-Token"] = this.csrfToken;
      }
      
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          if (typeof window !== "undefined") {
            localStorage.removeItem("admin_token");
            localStorage.removeItem("session_id");
            window.location.href = "/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string) {
    const response = await this.client.post("/api/admin/login", { username, password });
    
    // Store session info and CSRF token
    if (response.data.session_id) {
      this.sessionId = response.data.session_id;
      localStorage.setItem("session_id", response.data.session_id);
    }
    
    if (response.data.csrf_token) {
      this.csrfToken = response.data.csrf_token;
      localStorage.setItem("csrf_token", response.data.csrf_token);
    }
    
    return response.data;
  }
  
  // Get new CSRF token
  async refreshCsrfToken() {
    const sessionId = this.sessionId || localStorage.getItem("session_id");
    if (!sessionId) return;
    
    try {
      const response = await this.client.post(`/api/admin/csrf-token?session_id=${sessionId}`);
      if (response.data.csrf_token) {
        this.csrfToken = response.data.csrf_token;
        localStorage.setItem("csrf_token", response.data.csrf_token);
      }
    } catch (error) {
      console.error("Failed to refresh CSRF token:", error);
    }
  }

  async logout() {
    const sessionId = this.sessionId || localStorage.getItem("session_id");
    await this.client.post("/api/admin/logout", { session_id: sessionId });
  }

  // Student endpoints
  async getStudents(skip: number = 0, limit: number = 50) {
    const response = await this.client.get("/api/admin/students", {
      params: { skip, limit },
    });
    return response.data;
  }

  async searchStudents(query: string, status?: string) {
    const response = await this.client.get("/api/admin/students/search", {
      params: { query, status },
    });
    return response.data;
  }

  async getStudent(id: number) {
    const response = await this.client.get(`/api/admin/students/${id}`);
    return response.data;
  }

  // Payment endpoints
  async getPayments(skip: number = 0, limit: number = 50) {
    const response = await this.client.get("/api/admin/payments", {
      params: { skip, limit },
    });
    return response.data;
  }

  async getPaymentStats() {
    const response = await this.client.get("/api/admin/payments/stats");
    return response.data;
  }

  // Subscription endpoints
  async getSubscriptions(skip: number = 0, limit: number = 50) {
    const response = await this.client.get("/api/admin/subscriptions", {
      params: { skip, limit },
    });
    return response.data;
  }

  // Homework endpoints
  async getHomework(skip: number = 0, limit: number = 50) {
    const response = await this.client.get("/api/admin/homework", {
      params: { skip, limit },
    });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats() {
    const response = await this.client.get("/api/admin/dashboard/stats");
    return response.data;
  }

  async getMonitoringStats() {
    const response = await this.client.get("/api/admin/monitoring/stats");
    return response.data;
  }

  // Settings endpoints
  async getSettings() {
    const response = await this.client.get("/api/admin/settings");
    return response.data;
  }

  async updateSettings(settings: Record<string, string>) {
    const response = await this.client.post("/api/admin/settings/update", settings);
    return response.data;
  }

  // Reports endpoints
  async getReports() {
    const response = await this.client.get("/api/admin/reports");
    return response.data;
  }

  // WhatsApp testing endpoint
  async testWhatsAppMessage(phoneNumber: string, message: string) {
    const response = await this.client.post('/api/admin/whatsapp/test', {
      phone_number: phoneNumber,
      message: message
    });
    return response.data;
  }

  // Test WhatsApp configuration
  async testWhatsAppConfig() {
    const response = await this.client.post('/api/admin/whatsapp/test-config', {});
    return response.data;
  }
}

export const apiClient = new APIClient();
