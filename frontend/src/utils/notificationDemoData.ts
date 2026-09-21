import { NotificationRequest } from '@/contexts/EnhancedNotificationContext';

const countries = ['United States', 'United Kingdom', 'Germany', 'France', 'Canada', 'Australia', 'Japan', 'Brazil', 'India', 'China'];
const cities = ['New York', 'London', 'Berlin', 'Paris', 'Toronto', 'Sydney', 'Tokyo', 'São Paulo', 'Mumbai', 'Beijing'];

const userNames = [
  'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson',
  'Lisa Anderson', 'Robert Taylor', 'Jennifer Thomas', 'Christopher Jackson', 'Amanda White',
  'Matthew Harris', 'Ashley Martin', 'Daniel Thompson', 'Jessica Garcia', 'Andrew Martinez',
  'Stephanie Robinson', 'Joshua Clark', 'Nicole Rodriguez', 'Ryan Lewis', 'Elizabeth Lee'
];

const userEmails = userNames.map(name => 
  name.toLowerCase().replace(' ', '.') + '@example.com'
);

const messages = [
  'Requesting access to platform features',
  'Need to test the deepfake detection system',
  'Would like to upgrade to premium features',
  'Interested in API access for research purposes',
  'Need access for academic project',
  'Looking to integrate detection capabilities',
  'Requesting trial access for evaluation',
  'Need premium features for business use',
  'Interested in advanced detection models',
  'Requesting API access for mobile app'
];

const userAgents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0'
];

export const generateDemoNotification = (id: string): NotificationRequest => {
  const randomName = userNames[Math.floor(Math.random() * userNames.length)];
  const randomEmail = userEmails[Math.floor(Math.random() * userEmails.length)];
  const randomMessage = messages[Math.floor(Math.random() * messages.length)];
  const randomCountry = countries[Math.floor(Math.random() * countries.length)];
  const randomCity = cities[Math.floor(Math.random() * cities.length)];
  const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
  
  const requestTypes: Array<NotificationRequest['requestType']> = [
    'try_access', 'detection_access', 'premium_upgrade', 'signup_verification'
  ];
  
  const priorities: Array<NotificationRequest['priority']> = ['urgent', 'high', 'medium', 'low'];
  const sources: Array<NotificationRequest['source']> = ['web', 'mobile', 'api'];
  const statuses: Array<NotificationRequest['status']> = ['pending', 'approved', 'rejected'];
  
  const requestType = requestTypes[Math.floor(Math.random() * requestTypes.length)];
  const priority = priorities[Math.floor(Math.random() * priorities.length)];
  const source = sources[Math.floor(Math.random() * sources.length)];
  const status = statuses[Math.floor(Math.random() * statuses.length)];
  
  // Generate timestamp within the last 7 days
  const now = new Date();
  const randomTime = new Date(now.getTime() - Math.random() * 7 * 24 * 60 * 60 * 1000);
  
  // Generate updated timestamp if not pending
  const updatedAt = status !== 'pending' 
    ? new Date(randomTime.getTime() + Math.random() * 24 * 60 * 60 * 1000).toISOString()
    : undefined;
  
  // Generate admin notes if not pending
  const adminNotes = status !== 'pending' 
    ? `${status === 'approved' ? 'Approved' : 'Rejected'} by admin after review`
    : undefined;
  
  // Determine if user is genuine (85% chance)
  const isGenuine = Math.random() < 0.85;
  
  // Generate metadata
  const metadata = {
    previousRequests: Math.floor(Math.random() * 5),
    userTier: ['free', 'premium', 'enterprise'][Math.floor(Math.random() * 3)],
    accountAge: Math.floor(Math.random() * 365) // days
  };

  return {
    id,
    userId: `user-${Math.floor(Math.random() * 10000)}`,
    userEmail: randomEmail,
    userName: randomName,
    requestType,
    status,
    timestamp: randomTime.toISOString(),
    updatedAt,
    message: randomMessage,
    adminNotes,
    isGenuine,
    priority,
    source,
    userAgent: randomUserAgent,
    ipAddress: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    location: {
      country: randomCountry,
      city: randomCity
    },
    metadata
  };
};

export const generateDemoNotifications = (count: number): NotificationRequest[] => {
  return Array.from({ length: count }, (_, index) => 
    generateDemoNotification(`demo-${Date.now()}-${index}`)
  );
};

// Pre-generated demo data for consistent testing
export const demoNotifications: NotificationRequest[] = [
  {
    id: 'demo-1',
    userId: 'user-705',
    userEmail: 'user147@example.com',
    userName: 'User 705',
    requestType: 'try_access',
    status: 'pending',
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
    message: 'Requesting access to platform features',
    isGenuine: true,
    priority: 'high',
    source: 'web',
    userAgent: userAgents[0],
    ipAddress: '192.168.1.100',
    location: { country: 'United States', city: 'New York' },
    metadata: { previousRequests: 2, userTier: 'free', accountAge: 45 }
  },
  {
    id: 'demo-2',
    userId: 'user-147',
    userEmail: 'user942@example.com',
    userName: 'User 147',
    requestType: 'premium_upgrade',
    status: 'pending',
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
    message: 'Requesting access to platform features',
    isGenuine: true,
    priority: 'medium',
    source: 'mobile',
    userAgent: userAgents[3],
    ipAddress: '192.168.1.101',
    location: { country: 'United Kingdom', city: 'London' },
    metadata: { previousRequests: 1, userTier: 'premium', accountAge: 120 }
  },
  {
    id: 'demo-3',
    userId: 'user-590',
    userEmail: 'user752@example.com',
    userName: 'User 590',
    requestType: 'premium_upgrade',
    status: 'pending',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(), // 3 minutes ago
    message: 'Requesting access to platform features',
    isGenuine: true,
    priority: 'high',
    source: 'web',
    userAgent: userAgents[1],
    ipAddress: '192.168.1.102',
    location: { country: 'Germany', city: 'Berlin' },
    metadata: { previousRequests: 0, userTier: 'free', accountAge: 30 }
  },
  {
    id: 'demo-4',
    userId: 'user-629',
    userEmail: 'user970@example.com',
    userName: 'User 629',
    requestType: 'detection_access',
    status: 'pending',
    timestamp: new Date(Date.now() - 4 * 60 * 1000).toISOString(), // 4 minutes ago
    message: 'Requesting access to platform features',
    isGenuine: true,
    priority: 'urgent',
    source: 'api',
    userAgent: userAgents[2],
    ipAddress: '192.168.1.103',
    location: { country: 'France', city: 'Paris' },
    metadata: { previousRequests: 3, userTier: 'enterprise', accountAge: 200 }
  }
];
