// API utility functions
console.log("Config is:", CONFIG);

const API = {
    // Helper for making API requests
    async fetch(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        
        // Set default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add authorization token if available
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const url = `${CONFIG.API_URL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle unauthorized responses
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
            throw new Error('Unauthorized - Please log in again');
        }
        
        // Parse JSON response
        const data = await response.json();
        
        // Handle error responses
        if (!response.ok) {
            let errorMsg = 'Something went wrong';
            if (data && data.error) {
                errorMsg = data.error.message || errorMsg;
                // Optionally, you can use data.error.code for more specific handling
            } else if (data.detail) {
                errorMsg = data.detail;
            }
            throw new Error(errorMsg);
        }
        
        return data;
    },
    
    // Authentication
    async login(username, password) {
        return this.fetch('/v1/users/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },
    
    async register(name, username, password) {
        return this.fetch('/v1/users/register', {
            method: 'POST',
            body: JSON.stringify({ name, username, password })
        });
    },
    
    async getCurrentUser() {
        return this.fetch('/v1/users/me');
    },
    
    // Conversations
    async getConversations() {
        return this.fetch('/v1/conversations');
    },
    
    // Users
    async getAllUsers() {
        return this.fetch('/v1/users');
    },

    async createConversation(name, memberIds) {
        return this.fetch('/v1/conversations', {
            method: 'POST',
            body: JSON.stringify({ name, member_ids: memberIds })
        });
    },
    
    async getConversationMessages(conversationId) {
        return this.fetch(`/v1/conversations/${conversationId}/messages`);
    },
    
    // WebSocket connection
    createWebSocket(conversationId) {
        const token = localStorage.getItem('token');
        if (!token) throw new Error('No authentication token found');
        
        const ws = new WebSocket(`${CONFIG.WS_URL}/ws/${conversationId}?token=${token}`);
        return ws;
    }
};