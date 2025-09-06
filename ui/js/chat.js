document.addEventListener('DOMContentLoaded', function() {
    let currentUser = null;
    let currentConversationId = null;
    let currentWebSocket = null;
    let allUsers = [];
    
    // DOM elements
    const conversationsList = document.getElementById('conversations-list');
    const messagesContainer = document.getElementById('messages-container');
    const conversationView = document.getElementById('conversation-view');
    const noConversationMessage = document.getElementById('no-conversation-selected');
    const conversationNameElement = document.getElementById('conversation-name');
    const conversationMembersElement = document.getElementById('conversation-members');
    const messageInput = document.getElementById('message-input');
    const sendMessageBtn = document.getElementById('send-message-btn');
    const usernameElement = document.getElementById('username');
    let oldestMessageTimestamp = null; // Track oldest loaded message timestamp
    
    // Modal elements
    const newConversationBtn = document.getElementById('new-conversation-btn');
    const newConversationModal = document.getElementById('new-conversation-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const usersList = document.getElementById('users-list');
    const conversationNameInput = document.getElementById('conversation-name-input');
    const createConversationBtn = document.getElementById('create-conversation-btn');
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    });
    
    // Check if logged in and load user data
    async function initialize() {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }
        
        try {
            // Load current user
            currentUser = await API.getCurrentUser();
            console.log('Current user:', currentUser);
            usernameElement.textContent = currentUser.username;
            
            // Load conversations
            loadConversations();
        } catch (error) {
            console.error('Initialization error:', error);
        }
    }
    
    // Load and display conversations
    async function loadConversations() {
        try {
            const conversations = await API.getConversations();
            conversationsList.innerHTML = '';
            
            if (!conversations || conversations.length === 0) {
                conversationsList.innerHTML = '<div class="loading-indicator">No conversations yet</div>';
                return;
            }
            
            conversations.forEach(conversation => {
                const item = document.createElement('div');
                item.className = 'conversation-item';
                item.dataset.id = conversation.id;
                
                const memberCount = conversation.members.length;
                const memberNames = conversation.members
                    .map(member => member.name)
                    .join(', ');
                
                item.innerHTML = `
                    <h3>${conversation.name}</h3>
                    <p>${memberCount} member${memberCount !== 1 ? 's' : ''}</p>
                `;
                
                item.addEventListener('click', () => selectConversation(conversation));
                conversationsList.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading conversations:', error);
            conversationsList.innerHTML = '<div class="loading-indicator">Failed to load conversations</div>';
        }
    }
    
    // Select and display a conversation
    async function selectConversation(conversation) {
        // Update UI
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`.conversation-item[data-id="${conversation.id}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Close previous WebSocket connection
        if (currentWebSocket) {
            currentWebSocket.close();
            currentWebSocket = null;
        }
        
        // Update conversation display
        currentConversationId = conversation.id;
        conversationNameElement.textContent = conversation.name;
        
        // Display members
        const memberNames = conversation.members
            .map(member => member.name)
            .join(', ');
        conversationMembersElement.textContent = `Members: ${memberNames}`;
        
        // Show conversation view
        noConversationMessage.style.display = 'none';
        conversationView.style.display = 'flex';
        
        // Load messages
        await loadMessages(conversation.id);
        
        // Connect WebSocket
        connectWebSocket(conversation.id);
    }
    
    // Load messages for a conversation
    async function loadMessages(conversationId, before = null, append = false) {
        try {
            if (!append) {
                messagesContainer.innerHTML = '<div class="loading-indicator">Loading messages...</div>';
                oldestMessageTimestamp = null;
            }
            
            // Add query parameters for pagination if 'before' is provided
            const messages = await API.getConversationMessages(conversationId, before ? { limit: 20, before } : { limit: 20 });
            
            if (!append) {
                messagesContainer.innerHTML = '';
            } else {
                // Remove load more button if it exists
                const loadMoreBtn = document.getElementById('load-more-btn');
                if (loadMoreBtn) {
                    loadMoreBtn.remove();
                }
            }
            
            if (!messages || messages.length === 0) {
                if (!append) {
                    messagesContainer.innerHTML = '<div class="loading-indicator">No messages yet</div>';
                }
                return;
            }
            
            // Sort messages by timestamp (oldest first for proper display order)
            messages.sort((a, b) => a.timestamp - b.timestamp);
            
            // Keep track of oldest message for pagination
            if (messages.length > 0) {
                const oldestMessage = messages[0];
                oldestMessageTimestamp = oldestMessage.timestamp;
            }
            
            // Create a document fragment to batch DOM operations
            const fragment = document.createDocumentFragment();
            
            if (messages.length >= 20) {  // If we got a full page, there might be more
                // Add "Load More" button at the beginning (top)
                const loadMoreBtn = document.createElement('div');
                loadMoreBtn.id = 'load-more-btn';
                loadMoreBtn.className = 'load-more-btn';
                loadMoreBtn.textContent = 'Load More Messages';
                loadMoreBtn.addEventListener('click', () => loadOlderMessages(conversationId));
                fragment.appendChild(loadMoreBtn);
            }
            
            // Add messages to fragment
            messages.forEach(message => {
                const messageElement = createMessageElement(message);
                fragment.appendChild(messageElement);
            });
            
            // If appending (loading more), add to top of container
            if (append) {
                messagesContainer.prepend(fragment);
            } else {
                messagesContainer.appendChild(fragment);
                // Scroll to bottom for initial load
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
        } catch (error) {
            console.error('Error loading messages:', error);
            if (!append) {
                messagesContainer.innerHTML = '<div class="loading-indicator">Failed to load messages</div>';
            }
        }
    }
    
    // Load older messages
    async function loadOlderMessages(conversationId) {
        if (oldestMessageTimestamp) {
            await loadMessages(conversationId, oldestMessageTimestamp, true);
        }
    }
    
    // Create a message element
    function createMessageElement(message) {
        const isCurrentUser = message.sender.id === currentUser.id;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isCurrentUser ? 'sent' : 'received'}`;
        messageElement.dataset.id = message.id;
        messageElement.dataset.timestamp = message.timestamp; // Store timestamp for reference
        
        // Format timestamp
        const date = new Date(message.timestamp * 1000);
        const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            ${!isCurrentUser ? `<div class="message-sender">${message.sender.name}</div>` : ''}
            <div class="message-content">${message.content}</div>
            <div class="message-time">${timeString}</div>
        `;
        
        return messageElement;
    }
    
    // Add a message to the UI (for new incoming messages via WebSocket)
    function addMessageToUI(message) {
        const messageElement = createMessageElement(message);
        messagesContainer.appendChild(messageElement); // Add to the bottom (newest)
        
        // Scroll to bottom to see the newest message
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Connect to WebSocket for real-time messaging
    function connectWebSocket(conversationId) {
        try {
            currentWebSocket = API.createWebSocket(conversationId);
            
            currentWebSocket.onopen = () => {
                console.log('WebSocket connection established');
            };
            
            currentWebSocket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    addMessageToUI(message);
                } catch (error) {
                    console.error('Error processing WebSocket message:', error);
                }
            };
            
            currentWebSocket.onclose = () => {
                console.log('WebSocket connection closed');
            };
            
            currentWebSocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            alert('Failed to connect to chat. Please try again later.');
        }
    }
    
    // Send a message
    function sendMessage() {
        const content = messageInput.value.trim();
        
        if (!content || !currentConversationId || !currentWebSocket) {
            return;
        }
        
        try {
            const message = {
                content,
                timestamp: Math.floor(Date.now() / 1000)
            };
            
            currentWebSocket.send(JSON.stringify(message));
            
            // Clear input
            messageInput.value = '';
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
        }
    }
    
    // Handle send button click
    sendMessageBtn.addEventListener('click', sendMessage);
    
    // Handle enter key press
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Modal for creating new conversations
    newConversationBtn.addEventListener('click', () => {
        newConversationModal.style.display = 'block';
        loadUsers();
    });
    
    closeModalBtn.addEventListener('click', () => {
        newConversationModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === newConversationModal) {
            newConversationModal.style.display = 'none';
        }
    });
    
   // Load users for new conversation
    async function loadUsers() {
        try {
            usersList.innerHTML = '<div class="loading-indicator">Loading users...</div>';

            // Fetch all users from the endpoint
            const users = await API.getAllUsers();

            if (!users || users.length === 0) {
                usersList.innerHTML = '<div class="loading-indicator">No other users available</div>';
                return;
            }

            // Display users
            usersList.innerHTML = '';

            users.forEach(user => {
                if (user.id === currentUser.id) 
                    return; 
                
                const userItem = document.createElement('div');
                userItem.className = 'user-item';

                userItem.innerHTML = `
                    <label>
                        <input type="checkbox" name="selected-user" value="${user.id}">
                        ${user.name} (${user.username})
                    </label>
                `;

                usersList.appendChild(userItem);
            });
        } catch (error) {
            console.error('Error loading users:', error.message);
            usersList.innerHTML = '<div class="loading-indicator">Failed to load users</div>';
        }
    }
    
    // Create new conversation
    createConversationBtn.addEventListener('click', async () => {
        const name = conversationNameInput.value.trim();
        
        if (!name) {
            alert('Please enter a conversation name');
            return;
        }
        
        const selectedUsers = Array.from(document.querySelectorAll('input[name="selected-user"]:checked'))
            .map(checkbox => checkbox.value);
        
        if (selectedUsers.length === 0) {
            alert('Please select at least one user');
            return;
        }
        
        try {
            createConversationBtn.disabled = true;
            createConversationBtn.textContent = 'Creating...';
            
            const conversation = await API.createConversation(name, selectedUsers);
            
            // Close modal and reset form
            newConversationModal.style.display = 'none';
            conversationNameInput.value = '';
            document.querySelectorAll('input[name="selected-user"]:checked')
                .forEach(checkbox => checkbox.checked = false);
            
            // Reload conversations
            await loadConversations();
            
            // Select the new conversation
            selectConversation(conversation);
        } catch (error) {
            console.error('Error creating conversation:', error);
            alert('Failed to create conversation. Please try again.');
        } finally {
            createConversationBtn.disabled = false;
            createConversationBtn.textContent = 'Create Conversation';
        }
    });
    
    // Initialize the app
    initialize();
});