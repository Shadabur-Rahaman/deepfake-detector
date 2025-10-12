// Simple JavaScript Authentication Service
class AuthService {
  constructor() {
    this.users = this.loadUsers();
    this.currentUser = this.getCurrentUser();
  }

  // Load users from localStorage
  loadUsers() {
    const users = localStorage.getItem('ifake_users');
    const defaultUsers = users ? JSON.parse(users) : [];
    
    // Check if admin user exists, if not create it
    const adminExists = defaultUsers.find(user => user.email === 'admin@ifake.com');
    if (!adminExists) {
      const adminUser = {
        id: 'admin_001',
        email: 'admin@ifake.com',
        password: 'Admin123!@#',
        fullName: 'System Administrator',
        username: 'admin',
        roles: ['admin'],
        permissions: ['detection:create', 'detection:read', 'detection:update', 'detection:delete', 'try:access', 'admin:access', 'user:manage', 'system:manage'],
        createdAt: new Date().toISOString(),
        isActive: true
      };
      defaultUsers.push(adminUser);
    }
    
    // Check if demo user exists, if not create it
    const demoExists = defaultUsers.find(user => user.email === 'demo@ifake.com');
    if (!demoExists) {
      const demoUser = {
        id: 'demo_001',
        email: 'demo@ifake.com',
        password: 'Demo123!@#',
        fullName: 'Demo User',
        username: 'demo',
        roles: ['user'],
        permissions: ['try:access', 'detection:create'],
        createdAt: new Date().toISOString(),
        isActive: true
      };
      defaultUsers.push(demoUser);
    }
    
    if (!adminExists || !demoExists) {
      localStorage.setItem('ifake_users', JSON.stringify(defaultUsers));
    }
    
    return defaultUsers;
  }

  // Save users to localStorage
  saveUsers() {
    localStorage.setItem('ifake_users', JSON.stringify(this.users));
  }

  // Get current user from localStorage
  getCurrentUser() {
    const user = localStorage.getItem('ifake_current_user');
    return user ? JSON.parse(user) : null;
  }

  // Set current user in localStorage
  setCurrentUser(user) {
    if (user) {
      localStorage.setItem('ifake_current_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('ifake_current_user');
    }
    this.currentUser = user;
  }

  // Check if user is authenticated
  isAuthenticated() {
    return this.currentUser !== null;
  }

  // Register new user
  register(userData) {
    return new Promise((resolve, reject) => {
      try {
        // Validate input
        if (!userData.email || !userData.password || !userData.fullName) {
          throw new Error('All fields are required');
        }

        // Check if user already exists
        const existingUser = this.users.find(user => user.email === userData.email);
        if (existingUser) {
          throw new Error('User with this email already exists');
        }

        // Create new user
        const newUser = {
          id: Date.now().toString(),
          email: userData.email,
          password: userData.password, // In real app, this should be hashed
          fullName: userData.fullName,
          username: userData.username || userData.email.split('@')[0],
          createdAt: new Date().toISOString(),
          isActive: true
        };

        // Add to users array
        this.users.push(newUser);
        this.saveUsers();

        resolve({
          success: true,
          message: 'User registered successfully',
          user: {
            id: newUser.id,
            email: newUser.email,
            fullName: newUser.fullName,
            username: newUser.username
          }
        });
      } catch (error) {
        reject({
          success: false,
          message: error.message
        });
      }
    });
  }

  // Login user
  login(email, password) {
    return new Promise((resolve, reject) => {
      try {
        // Find user by email
        const user = this.users.find(u => u.email === email);
        
        if (!user) {
          throw new Error('User not found');
        }

        if (user.password !== password) {
          throw new Error('Invalid password');
        }

        if (!user.isActive) {
          throw new Error('Account is inactive');
        }

        // Set current user
        this.setCurrentUser({
          id: user.id,
          email: user.email,
          fullName: user.fullName,
          username: user.username,
          roles: user.roles || [],
          permissions: user.permissions || []
        });

        resolve({
          success: true,
          message: 'Login successful',
          user: {
            id: user.id,
            email: user.email,
            fullName: user.fullName,
            username: user.username,
            roles: user.roles || [],
            permissions: user.permissions || []
          }
        });
      } catch (error) {
        reject({
          success: false,
          message: error.message
        });
      }
    });
  }

  // Logout user
  logout() {
    this.setCurrentUser(null);
    return Promise.resolve({
      success: true,
      message: 'Logged out successfully'
    });
  }

  // Get current user info
  getCurrentUserInfo() {
    return this.currentUser;
  }

  // Update user profile
  updateProfile(updates) {
    return new Promise((resolve, reject) => {
      try {
        if (!this.currentUser) {
          throw new Error('No user logged in');
        }

        // Find user in users array
        const userIndex = this.users.findIndex(u => u.id === this.currentUser.id);
        if (userIndex === -1) {
          throw new Error('User not found');
        }

        // Update user data
        this.users[userIndex] = {
          ...this.users[userIndex],
          ...updates,
          id: this.currentUser.id, // Preserve ID
          email: this.currentUser.email // Preserve email
        };

        // Update current user
        this.currentUser = {
          ...this.currentUser,
          ...updates
        };

        this.saveUsers();
        this.setCurrentUser(this.currentUser);

        resolve({
          success: true,
          message: 'Profile updated successfully',
          user: this.currentUser
        });
      } catch (error) {
        reject({
          success: false,
          message: error.message
        });
      }
    });
  }

  // Change password
  changePassword(currentPassword, newPassword) {
    return new Promise((resolve, reject) => {
      try {
        if (!this.currentUser) {
          throw new Error('No user logged in');
        }

        // Find user in users array
        const userIndex = this.users.findIndex(u => u.id === this.currentUser.id);
        if (userIndex === -1) {
          throw new Error('User not found');
        }

        // Verify current password
        if (this.users[userIndex].password !== currentPassword) {
          throw new Error('Current password is incorrect');
        }

        // Update password
        this.users[userIndex].password = newPassword;
        this.saveUsers();

        resolve({
          success: true,
          message: 'Password changed successfully'
        });
      } catch (error) {
        reject({
          success: false,
          message: error.message
        });
      }
    });
  }
}

// Create singleton instance
const authService = new AuthService();

// Export for use in other files
export default authService;
