/**
 * Production-Grade Contact Service
 * Handles contact form submissions and integrates with admin dashboard
 */

import mockBackend from './mockBackend';

class ContactService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.websocket = null;
    this.listeners = new Map();
    this.useMockBackend = process.env.NODE_ENV === 'development' || !process.env.REACT_APP_API_URL;
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
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json'
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
      console.error('Contact API request failed:', error);
      throw error;
    }
  }

  // Contact Form Submission
  async submitContactForm(formData) {
    try {
      // Validate form data
      this.validateContactForm(formData);

      let response;
      if (this.useMockBackend) {
        response = await mockBackend.submitContactRequest({
          ...formData,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          ip: await this.getClientIP()
        });
      } else {
        response = await this.makeRequest('/contact/submit', {
          method: 'POST',
          body: JSON.stringify({
            ...formData,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            ip: await this.getClientIP()
          })
        });
      }

      // Emit success event
      this.emit('contact_submitted', {
        success: true,
        data: response,
        timestamp: new Date().toISOString()
      });

      return response;
    } catch (error) {
      // Emit error event
      this.emit('contact_submitted', {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
      
      throw error;
    }
  }

  // Form Validation
  validateContactForm(formData) {
    const errors = {};

    // Name validation
    if (!formData.fullName || formData.fullName.trim().length < 2) {
      errors.fullName = 'Full name must be at least 2 characters long';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Subject validation
    if (!formData.subject || formData.subject.trim().length < 5) {
      errors.subject = 'Subject must be at least 5 characters long';
    }

    // Regarding validation
    const validRegardings = ['technical', 'collaboration', 'feedback', 'academic', 'mesonet', 'other'];
    if (!formData.regarding || !validRegardings.includes(formData.regarding)) {
      errors.regarding = 'Please select a valid topic';
    }

    // Message validation
    if (!formData.message || formData.message.trim().length < 10) {
      errors.message = 'Message must be at least 10 characters long';
    } else if (formData.message.trim().length > 1000) {
      errors.message = 'Message cannot exceed 1000 characters';
    }

    if (Object.keys(errors).length > 0) {
      throw new Error(`Validation failed: ${JSON.stringify(errors)}`);
    }
  }

  // Get client IP (for analytics)
  async getClientIP() {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      console.warn('Could not fetch client IP:', error);
      return 'unknown';
    }
  }

  // Get contact request status
  async getContactRequestStatus(requestId) {
    return await this.makeRequest(`/contact/status/${requestId}`);
  }

  // Get all contact requests (admin only)
  async getAllContactRequests() {
    const token = localStorage.getItem('ifake_access_token');
    return await this.makeRequest('/admin/contact-requests', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  // Contact Analytics
  async getContactAnalytics(timeRange = '30d') {
    const token = localStorage.getItem('ifake_access_token');
    return await this.makeRequest(`/admin/contact/analytics?range=${timeRange}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  // Auto-response configuration
  async configureAutoResponse(settings) {
    const token = localStorage.getItem('ifake_access_token');
    return await this.makeRequest('/admin/contact/auto-response', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(settings)
    });
  }

  // Get auto-response settings
  async getAutoResponseSettings() {
    const token = localStorage.getItem('ifake_access_token');
    return await this.makeRequest('/admin/contact/auto-response', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  // Send manual response
  async sendManualResponse(requestId, response) {
    const token = localStorage.getItem('ifake_access_token');
    return await this.makeRequest(`/admin/contact/respond/${requestId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(response)
    });
  }

  // Export contact data
  async exportContactData(format = 'csv', filters = {}) {
    const token = localStorage.getItem('ifake_access_token');
    const response = await this.makeRequest('/admin/contact/export', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ format, filters })
    });

    // Trigger download
    const blob = new Blob([response.data], { type: response.contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = response.filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    return response;
  }

  // Cleanup
  destroy() {
    this.listeners.clear();
  }
}

// Create singleton instance
const contactService = new ContactService();

export default contactService;
