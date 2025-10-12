/**
 * Production-Grade Admin Service
 * Handles all admin-related operations including user management, system monitoring, and contact requests
 */

class AdminService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsURL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    this.websocket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.listeners = new Map();
    this.isConnected = false;
  }

  // WebSocket Connection Management
  connectWebSocket() {
    try {
      this.websocket = new WebSocket(this.wsURL);
      
      this.websocket.onopen = () => {
        console.log('Admin WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.authenticate();
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.websocket.onclose = (event) => {
        console.log('Admin WebSocket disconnected');
        this.isConnected = false;
        this.handleReconnection();
      };

      this.websocket.onerror = (error) => {
        console.error('Admin WebSocket error:', error);
        this.isConnected = false;
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleReconnection();
    }
  }

  authenticate() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      const token = localStorage.getItem('ifake_access_token');
      const user = JSON.parse(localStorage.getItem('ifake_user') || '{}');
      
      this.websocket.send(JSON.stringify({
        type: 'admin_auth',
        token: token,
        userId: user.id,
        role: user.roles?.[0] || 'admin'
      }));
    }
  }

  handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      this.reconnectAttempts++;
      
      setTimeout(() => {
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
        this.connectWebSocket();
      }, delay);
    }
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'admin_auth_success':
        console.log('Admin authentication successful');
        this.emit('auth_success', data);
        break;
      case 'system_stats_update':
        this.emit('stats_update', data.stats);
        break;
      case 'new_contact_request':
        this.emit('new_contact', data.request);
        break;
      case 'new_auth_request':
        this.emit('new_auth_request', data.request);
        break;
      case 'request_updated':
        this.emit('request_updated', data);
        break;
      case 'system_health_update':
        this.emit('health_update', data.health);
        break;
      default:
        console.log('Unknown admin message type:', data.type);
    }
  }

  // Event System
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  // API Methods
  async makeRequest(endpoint, options = {}) {
    const token = localStorage.getItem('ifake_access_token');
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: { ...defaultOptions.headers, ...options.headers }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // System Health & Monitoring
  async getSystemHealth() {
    return await this.makeRequest('/admin/system/health');
  }

  async getSystemStats() {
    return await this.makeRequest('/admin/system/stats');
  }

  async refreshSystemData() {
    const [health, stats] = await Promise.all([
      this.getSystemHealth(),
      this.getSystemStats()
    ]);
    
    return { health, stats };
  }

  // User Management
  async getAllUsers() {
    return await this.makeRequest('/admin/users');
  }

  async getUserById(userId) {
    return await this.makeRequest(`/admin/users/${userId}`);
  }

  async updateUserStatus(userId, status) {
    return await this.makeRequest(`/admin/users/${userId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  async deleteUser(userId) {
    return await this.makeRequest(`/admin/users/${userId}`, {
      method: 'DELETE'
    });
  }

  // Contact Requests Management
  async getContactRequests() {
    return await this.makeRequest('/admin/contact-requests');
  }

  async updateContactRequest(requestId, status, adminNotes) {
    return await this.makeRequest(`/admin/contact-requests/${requestId}`, {
      method: 'PUT',
      body: JSON.stringify({ status, adminNotes })
    });
  }

  async deleteContactRequest(requestId) {
    return await this.makeRequest(`/admin/contact-requests/${requestId}`, {
      method: 'DELETE'
    });
  }

  // Auth Requests Management
  async getAuthRequests() {
    return await this.makeRequest('/admin/auth-requests');
  }

  async approveAuthRequest(requestId, adminNotes) {
    return await this.makeRequest(`/admin/auth-requests/${requestId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ adminNotes })
    });
  }

  async rejectAuthRequest(requestId, adminNotes) {
    return await this.makeRequest(`/admin/auth-requests/${requestId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ adminNotes })
    });
  }

  // System Settings
  async getSystemSettings() {
    return await this.makeRequest('/admin/settings');
  }

  async updateSystemSettings(settings) {
    return await this.makeRequest('/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  // Access Control Settings
  async getAccessControlSettings() {
    return await this.makeRequest('/admin/access-control');
  }

  async updateAccessControlSettings(settings) {
    return await this.makeRequest('/admin/access-control', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  // Email Notification Settings
  async getEmailSettings() {
    return await this.makeRequest('/admin/email-settings');
  }

  async updateEmailSettings(settings) {
    return await this.makeRequest('/admin/email-settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  // Test Email
  async testEmailConfiguration() {
    return await this.makeRequest('/admin/email-settings/test', {
      method: 'POST'
    });
  }

  // Analytics & Reports
  async getAnalytics(timeRange = '7d') {
    return await this.makeRequest(`/admin/analytics?range=${timeRange}`);
  }

  async generateReport(type, options = {}) {
    return await this.makeRequest('/admin/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ type, options })
    });
  }

  // Bulk Operations
  async bulkUpdateUsers(userIds, updates) {
    return await this.makeRequest('/admin/users/bulk-update', {
      method: 'POST',
      body: JSON.stringify({ userIds, updates })
    });
  }

  async bulkDeleteUsers(userIds) {
    return await this.makeRequest('/admin/users/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ userIds })
    });
  }

  // System Maintenance
  async performSystemMaintenance(operation) {
    return await this.makeRequest('/admin/maintenance', {
      method: 'POST',
      body: JSON.stringify({ operation })
    });
  }

  async getMaintenanceLogs() {
    return await this.makeRequest('/admin/maintenance/logs');
  }

  // Cleanup
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.listeners.clear();
    this.isConnected = false;
  }
}

// Create singleton instance
const adminService = new AdminService();

export default adminService;
