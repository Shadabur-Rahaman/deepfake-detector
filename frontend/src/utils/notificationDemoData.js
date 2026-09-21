/**
 * Demo notification data for development and testing
 */

export const demoNotifications = [
  {
    id: 'notif_001',
    userId: 'user_123',
    userEmail: 'john.doe@example.com',
    userName: 'John Doe',
    requestType: 'detection_access',
    status: 'pending',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    message: 'Requesting access to the detection API for my research project.',
    adminNotes: null,
    isGenuine: true,
    priority: 'medium',
    source: 'web',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    ipAddress: '192.168.1.100',
    location: {
      country: 'United States',
      city: 'New York'
    },
    metadata: {
      previousRequests: 0,
      userTier: 'free',
      accountAge: 1
    }
  },
  {
    id: 'notif_002',
    userId: 'user_456',
    userEmail: 'jane.smith@university.edu',
    userName: 'Jane Smith',
    requestType: 'try_access',
    status: 'approved',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    message: 'Academic research request for deepfake detection testing.',
    adminNotes: 'Approved - legitimate academic user with proper credentials.',
    isGenuine: true,
    priority: 'high',
    source: 'web',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ipAddress: '203.0.113.45',
    location: {
      country: 'Canada',
      city: 'Toronto'
    },
    metadata: {
      previousRequests: 2,
      userTier: 'academic',
      accountAge: 30
    }
  },
  {
    id: 'notif_003',
    userId: 'user_789',
    userEmail: 'bob.wilson@techcorp.com',
    userName: 'Bob Wilson',
    requestType: 'premium_upgrade',
    status: 'pending',
    timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    message: 'Requesting premium upgrade for enterprise integration.',
    adminNotes: null,
    isGenuine: true,
    priority: 'urgent',
    source: 'api',
    userAgent: 'TechCorp-API-Client/1.0',
    ipAddress: '198.51.100.25',
    location: {
      country: 'United Kingdom',
      city: 'London'
    },
    metadata: {
      previousRequests: 5,
      userTier: 'premium',
      accountAge: 90
    }
  }
];

export const generateDemoNotifications = (count = 5) => {
  const requestTypes = ['try_access', 'detection_access', 'premium_upgrade', 'signup_verification'];
  const statuses = ['pending', 'approved', 'rejected'];
  const priorities = ['low', 'medium', 'high', 'urgent'];
  const sources = ['web', 'api', 'mobile'];
  const countries = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Australia'];
  const cities = ['New York', 'Toronto', 'London', 'Berlin', 'Paris', 'Sydney'];
  const userTiers = ['free', 'basic', 'premium', 'academic', 'enterprise'];
  
  const names = [
    'John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis',
    'Diana Miller', 'Eve Johnson', 'Frank Garcia', 'Grace Lee', 'Henry Taylor'
  ];
  
  const domains = ['example.com', 'university.edu', 'techcorp.com', 'research.org', 'company.net'];
  
  const notifications = [];
  
  for (let i = 0; i < count; i++) {
    const name = names[Math.floor(Math.random() * names.length)];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    const email = `${name.toLowerCase().replace(' ', '.')}@${domain}`;
    const country = countries[Math.floor(Math.random() * countries.length)];
    const city = cities[Math.floor(Math.random() * cities.length)];
    
    const notification = {
      id: `notif_${Date.now()}_${i}`,
      userId: `user_${Math.random().toString(36).substr(2, 9)}`,
      userEmail: email,
      userName: name,
      requestType: requestTypes[Math.floor(Math.random() * requestTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      message: `Demo request ${i + 1} - ${Math.random() > 0.5 ? 'Legitimate' : 'Suspicious'} request for ${requestTypes[Math.floor(Math.random() * requestTypes.length)].replace('_', ' ')}.`,
      adminNotes: Math.random() > 0.7 ? `Admin note for request ${i + 1}` : null,
      isGenuine: Math.random() > 0.2, // 80% genuine users
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
      userAgent: `Mozilla/5.0 (${Math.random() > 0.5 ? 'Windows' : 'Macintosh'}) AppleWebKit/537.36`,
      ipAddress: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      location: {
        country: country,
        city: city
      },
      metadata: {
        previousRequests: Math.floor(Math.random() * 10),
        userTier: userTiers[Math.floor(Math.random() * userTiers.length)],
        accountAge: Math.floor(Math.random() * 365)
      }
    };
    
    notifications.push(notification);
  }
  
  return notifications;
};

export const getNotificationStats = (notifications) => {
  const total = notifications.length;
  const pending = notifications.filter(n => n.status === 'pending').length;
  const approved = notifications.filter(n => n.status === 'approved').length;
  const rejected = notifications.filter(n => n.status === 'rejected').length;
  const genuine = notifications.filter(n => n.isGenuine).length;
  const urgent = notifications.filter(n => n.priority === 'urgent').length;
  const high = notifications.filter(n => n.priority === 'high').length;
  
  return {
    total,
    pending,
    approved,
    rejected,
    genuine,
    urgent,
    high,
    genuineRatio: total > 0 ? (genuine / total * 100).toFixed(1) : 0,
    pendingRatio: total > 0 ? (pending / total * 100).toFixed(1) : 0
  };
};

export const getNotificationsByType = (notifications) => {
  const types = {};
  notifications.forEach(notification => {
    if (!types[notification.requestType]) {
      types[notification.requestType] = 0;
    }
    types[notification.requestType]++;
  });
  return types;
};

export const getNotificationsByPriority = (notifications) => {
  const priorities = {};
  notifications.forEach(notification => {
    if (!priorities[notification.priority]) {
      priorities[notification.priority] = 0;
    }
    priorities[notification.priority]++;
  });
  return priorities;
};

export const filterNotifications = (notifications, filters) => {
  return notifications.filter(notification => {
    if (filters.status && notification.status !== filters.status) return false;
    if (filters.priority && notification.priority !== filters.priority) return false;
    if (filters.type && notification.requestType !== filters.type) return false;
    if (filters.genuine !== undefined && notification.isGenuine !== filters.genuine) return false;
    if (filters.search && !notification.userName.toLowerCase().includes(filters.search.toLowerCase()) && 
        !notification.userEmail.toLowerCase().includes(filters.search.toLowerCase())) return false;
    if (filters.dateFrom && new Date(notification.timestamp) < new Date(filters.dateFrom)) return false;
    if (filters.dateTo && new Date(notification.timestamp) > new Date(filters.dateTo)) return false;
    return true;
  });
};

export const sortNotifications = (notifications, sortBy = 'timestamp', sortOrder = 'desc') => {
  return [...notifications].sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];
    
    if (sortBy === 'timestamp') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
};

export default {
  demoNotifications,
  generateDemoNotifications,
  getNotificationStats,
  getNotificationsByType,
  getNotificationsByPriority,
  filterNotifications,
  sortNotifications
};
