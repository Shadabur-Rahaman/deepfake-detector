/**
 * Mock Backend Service for Admin Dashboard
 * Provides realistic data and API responses for development and testing
 */

// Mock data storage
const mockData = {
  contactRequests: [
    {
      id: 'contact_001',
      fullName: 'John Smith',
      email: 'john.smith@example.com',
      subject: 'Technical Support Request',
      regarding: 'technical',
      message: 'I need help with the MesoNet CNN detection system. The API is returning inconsistent results.',
      status: 'pending',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      adminNotes: null
    },
    {
      id: 'contact_002',
      fullName: 'Sarah Johnson',
      email: 'sarah.j@university.edu',
      subject: 'Research Collaboration Inquiry',
      regarding: 'collaboration',
      message: 'Our research team is interested in collaborating on deepfake detection research. We have access to a large dataset.',
      status: 'approved',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      adminNotes: 'Approved for collaboration - team has strong academic credentials'
    },
    {
      id: 'contact_003',
      fullName: 'Mike Chen',
      email: 'mike.chen@techcorp.com',
      subject: 'Integration Support',
      regarding: 'technical',
      message: 'We want to integrate your deepfake detection API into our video processing pipeline.',
      status: 'pending',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
      adminNotes: null
    }
  ],
  
  authRequests: [
    {
      id: 'auth_001',
      userId: 'user_123',
      userEmail: 'alice@example.com',
      userName: 'Alice Wilson',
      requestType: 'detection_access',
      status: 'pending',
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
      message: 'I need access to the detection API for my research project on media authenticity.',
      adminNotes: null,
      isGenuine: true
    },
    {
      id: 'auth_002',
      userId: 'user_456',
      userEmail: 'bob@university.edu',
      userName: 'Bob Anderson',
      requestType: 'try_access',
      status: 'approved',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
      message: 'Requesting access to try the deepfake detection features.',
      adminNotes: 'Approved - legitimate academic user',
      isGenuine: true
    }
  ],

  systemStats: {
    totalUsers: 1247,
    activeUsers: 89,
    genuineUsers: 1180,
    pendingRequests: 3,
    totalRequests: 15,
    totalDetections: 5643,
    systemUptime: 72 * 3600, // 72 hours
    memoryUsage: 65.2,
    cpuUsage: 23.8
  },

  systemHealth: {
    status: 'healthy',
    database: 'healthy',
    authentication: 'healthy',
    detectionAPI: 'healthy',
    websocket: 'connected',
    lastCheck: new Date().toISOString()
  },

  systemSettings: {
    autoApproveTryAccess: false,
    autoApproveDetectionAccess: false,
    emailNotifications: true,
    maintenanceMode: false,
    maxFileSize: 10485760, // 10MB
    allowedFileTypes: ['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
    rateLimiting: {
      enabled: true,
      maxRequestsPerMinute: 60,
      maxRequestsPerHour: 1000
    }
  }
};

// Simulate network delay
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

// Mock API responses
export const mockBackend = {
  // System Health & Stats
  async getSystemHealth() {
    await delay(200);
    return { ...mockData.systemHealth };
  },

  async getSystemStats() {
    await delay(300);
    return { ...mockData.systemStats };
  },

  async refreshSystemData() {
    await delay(500);
    return {
      health: { ...mockData.systemHealth },
      stats: { ...mockData.systemStats }
    };
  },

  // Contact Requests
  async getContactRequests() {
    await delay(400);
    return {
      requests: [...mockData.contactRequests],
      pending: mockData.contactRequests.filter(req => req.status === 'pending').length
    };
  },

  async submitContactRequest(requestData) {
    await delay(800);
    const newRequest = {
      id: `contact_${Date.now()}`,
      ...requestData,
      status: 'pending',
      timestamp: new Date().toISOString(),
      adminNotes: null
    };
    mockData.contactRequests.unshift(newRequest);
    return {
      success: true,
      requestId: newRequest.id,
      message: 'Contact request submitted successfully'
    };
  },

  async updateContactRequest(requestId, status, adminNotes) {
    await delay(300);
    const request = mockData.contactRequests.find(req => req.id === requestId);
    if (request) {
      request.status = status;
      request.adminNotes = adminNotes;
      request.updatedAt = new Date().toISOString();
    }
    return { success: true, request };
  },

  async deleteContactRequest(requestId) {
    await delay(300);
    const index = mockData.contactRequests.findIndex(req => req.id === requestId);
    if (index > -1) {
      mockData.contactRequests.splice(index, 1);
    }
    return { success: true };
  },

  // Auth Requests
  async getAuthRequests() {
    await delay(400);
    return {
      requests: [...mockData.authRequests],
      pending: mockData.authRequests.filter(req => req.status === 'pending').length
    };
  },

  async approveAuthRequest(requestId, adminNotes) {
    await delay(300);
    const request = mockData.authRequests.find(req => req.id === requestId);
    if (request) {
      request.status = 'approved';
      request.adminNotes = adminNotes;
      request.updatedAt = new Date().toISOString();
    }
    return { success: true, request };
  },

  async rejectAuthRequest(requestId, adminNotes) {
    await delay(300);
    const request = mockData.authRequests.find(req => req.id === requestId);
    if (request) {
      request.status = 'rejected';
      request.adminNotes = adminNotes;
      request.updatedAt = new Date().toISOString();
    }
    return { success: true, request };
  },

  // System Settings
  async getSystemSettings() {
    await delay(300);
    return { ...mockData.systemSettings };
  },

  async updateSystemSettings(settings) {
    await delay(400);
    Object.assign(mockData.systemSettings, settings);
    return { success: true, settings: mockData.systemSettings };
  },

  async getAccessControlSettings() {
    await delay(300);
    return {
      autoApproveTryAccess: mockData.systemSettings.autoApproveTryAccess,
      autoApproveDetectionAccess: mockData.systemSettings.autoApproveDetectionAccess
    };
  },

  async updateAccessControlSettings(settings) {
    await delay(400);
    Object.assign(mockData.systemSettings, settings);
    return { success: true, settings };
  },

  // Email Settings
  async getEmailSettings() {
    await delay(300);
    return {
      enabled: mockData.systemSettings.emailNotifications,
      smtpHost: 'smtp.example.com',
      smtpPort: 587,
      fromEmail: 'admin@ifake.com',
      fromName: 'iFake Admin'
    };
  },

  async updateEmailSettings(settings) {
    await delay(400);
    Object.assign(mockData.systemSettings, settings);
    return { success: true, settings };
  },

  async testEmailConfiguration() {
    await delay(1000);
    return {
      success: true,
      message: 'Test email sent successfully'
    };
  },

  // Analytics
  async getAnalytics(timeRange = '7d') {
    await delay(500);
    return {
      timeRange,
      totalRequests: mockData.systemStats.totalRequests,
      totalUsers: mockData.systemStats.totalUsers,
      totalDetections: mockData.systemStats.totalDetections,
      dailyStats: [
        { date: '2024-01-01', requests: 12, users: 45, detections: 234 },
        { date: '2024-01-02', requests: 8, users: 38, detections: 189 },
        { date: '2024-01-03', requests: 15, users: 52, detections: 312 },
        { date: '2024-01-04', requests: 11, users: 41, detections: 267 },
        { date: '2024-01-05', requests: 9, users: 35, detections: 198 },
        { date: '2024-01-06', requests: 13, users: 48, detections: 289 },
        { date: '2024-01-07', requests: 7, users: 32, detections: 156 }
      ]
    };
  },

  // Bulk Operations
  async bulkUpdateUsers(userIds, updates) {
    await delay(600);
    return {
      success: true,
      updated: userIds.length,
      message: `Updated ${userIds.length} users`
    };
  },

  async bulkDeleteUsers(userIds) {
    await delay(800);
    return {
      success: true,
      deleted: userIds.length,
      message: `Deleted ${userIds.length} users`
    };
  },

  // System Maintenance
  async performSystemMaintenance(operation) {
    await delay(2000);
    return {
      success: true,
      operation,
      message: `Maintenance operation '${operation}' completed successfully`
    };
  },

  async getMaintenanceLogs() {
    await delay(400);
    return {
      logs: [
        {
          id: 'log_001',
          operation: 'Database cleanup',
          status: 'completed',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          details: 'Removed 1,234 expired sessions'
        },
        {
          id: 'log_002',
          operation: 'Cache refresh',
          status: 'completed',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          details: 'Refreshed model cache'
        }
      ]
    };
  },

  // Export Functions
  async exportContactData(format = 'csv', filters = {}) {
    await delay(1000);
    const data = mockData.contactRequests.filter(req => {
      if (filters.status && req.status !== filters.status) return false;
      if (filters.dateFrom && new Date(req.timestamp) < new Date(filters.dateFrom)) return false;
      if (filters.dateTo && new Date(req.timestamp) > new Date(filters.dateTo)) return false;
      return true;
    });

    if (format === 'csv') {
      const csvContent = [
        'ID,Full Name,Email,Subject,Regarding,Status,Timestamp,Admin Notes',
        ...data.map(req => 
          `"${req.id}","${req.fullName}","${req.email}","${req.subject}","${req.regarding}","${req.status}","${req.timestamp}","${req.adminNotes || ''}"`
        ).join('\n')
      ].join('\n');

      return {
        data: csvContent,
        contentType: 'text/csv',
        filename: `contact_requests_${new Date().toISOString().split('T')[0]}.csv`
      };
    }

    return {
      data: JSON.stringify(data, null, 2),
      contentType: 'application/json',
      filename: `contact_requests_${new Date().toISOString().split('T')[0]}.json`
    };
  },

  // Utility Functions
  generateMockContactRequest() {
    const names = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'];
    const emails = ['john@example.com', 'jane@university.edu', 'bob@company.com', 'alice@research.org', 'charlie@tech.com'];
    const subjects = ['Technical Support', 'Research Inquiry', 'Integration Help', 'Feature Request', 'Bug Report'];
    const regardings = ['technical', 'collaboration', 'feedback', 'academic', 'other'];
    const messages = [
      'I need help with the API integration.',
      'We are interested in collaborating on this project.',
      'Could you please add this feature?',
      'I found a bug in the detection system.',
      'Great work on this project!'
    ];

    const random = (arr) => arr[Math.floor(Math.random() * arr.length)];
    
    return {
      id: `contact_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      fullName: random(names),
      email: random(emails),
      subject: random(subjects),
      regarding: random(regardings),
      message: random(messages),
      status: 'pending',
      timestamp: new Date().toISOString(),
      adminNotes: null
    };
  },

  addMockContactRequest() {
    const newRequest = this.generateMockContactRequest();
    mockData.contactRequests.unshift(newRequest);
    return newRequest;
  },

  addMockAuthRequest() {
    const newRequest = {
      id: `auth_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: `user_${Math.random().toString(36).substr(2, 9)}`,
      userEmail: `user${Math.floor(Math.random() * 1000)}@example.com`,
      userName: `User ${Math.floor(Math.random() * 1000)}`,
      requestType: Math.random() > 0.5 ? 'try_access' : 'detection_access',
      status: 'pending',
      timestamp: new Date().toISOString(),
      message: 'Requesting access to the system.',
      adminNotes: null,
      isGenuine: Math.random() > 0.1 // 90% genuine users
    };
    mockData.authRequests.unshift(newRequest);
    return newRequest;
  },

  // Simulate real-time updates
  simulateRealtimeUpdates() {
    setInterval(() => {
      // Randomly add new contact requests
      if (Math.random() < 0.1) { // 10% chance every interval
        this.addMockContactRequest();
      }
      
      // Randomly add new auth requests
      if (Math.random() < 0.05) { // 5% chance every interval
        this.addMockAuthRequest();
      }
      
      // Update system stats
      mockData.systemStats.totalUsers += Math.floor(Math.random() * 3);
      mockData.systemStats.activeUsers = Math.floor(Math.random() * 100) + 50;
      mockData.systemStats.totalDetections += Math.floor(Math.random() * 10);
      mockData.systemStats.memoryUsage = Math.random() * 100;
      mockData.systemStats.cpuUsage = Math.random() * 100;
    }, 30000); // Update every 30 seconds
  }
};

export default mockBackend;
