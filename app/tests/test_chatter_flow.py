#!/usr/bin/env python3
# filepath: test_chatter_flow.py

import requests
import json
import time
import sys
from typing import Dict, Any, List
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update if your server is on a different host/port
TEST_USERS = [
    {"name": "John Doe", "username": "johndoe", "password": "password123"},
    {"name": "Jane Smith", "username": "janesmith", "password": "password123"},
    {"name": "Alice Wonder", "username": "alicew", "password": "password123"},
]
VERBOSE = True  # Set to True for detailed output
PRETTY_PRINT = True  # Pretty print JSON responses

# ANSI colors for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

# Helper Functions
def log(message: str, color: str = None) -> None:
    """Print a message with timestamp if verbose mode is on"""
    timestamp = time.strftime('%H:%M:%S')
    if VERBOSE:
        if color:
            print(f"{color}[{timestamp}] {message}{ENDC}")
        else:
            print(f"[{timestamp}] {message}")

def pretty_json(data: Any) -> str:
    """Return a pretty-printed JSON string"""
    if PRETTY_PRINT:
        return json.dumps(data, indent=2)
    return json.dumps(data)

def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, token: str = None) -> Dict[str, Any]:
    """Make an HTTP request to the API and return the response"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add authorization header if token is provided
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Log the request
    log(f"{BOLD}{method.upper()} {url}{ENDC}", BLUE)
    log(f"Headers: {pretty_json(headers)}")
    if data:
        log(f"Request Body: {pretty_json(data)}")
    
    # Make the request with the appropriate HTTP method
    start_time = time.time()
    if method.lower() == "get":
        response = requests.get(url, headers=headers)
    elif method.lower() == "post":
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif method.lower() == "put":
        response = requests.put(url, headers=headers, data=json.dumps(data))
    elif method.lower() == "delete":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    elapsed = time.time() - start_time
    
    # Try to parse response as JSON
    try:
        json_data = response.json()
                
        # If the response is a list, convert it to a special format
        if isinstance(json_data, list):
            result = {"items": json_data}
        else:
            result = json_data
            
        # Mask sensitive data like tokens if present
        if "access_token" in result:
            display_result = result.copy()
            token_length = len(result["access_token"])
            display_result["access_token"] = result["access_token"][:10] + "..." + result["access_token"][-5:] if token_length > 15 else result["access_token"]
        else:
            display_result = result
    except json.JSONDecodeError:
        result = {"text": response.text}
        display_result = result
    
    # Add status code to result
    result["status_code"] = response.status_code
    display_result["status_code"] = response.status_code
    
    # Log the response
    if 200 <= response.status_code < 300:
        status_color = GREEN
    elif 400 <= response.status_code < 500:
        status_color = YELLOW
    else:
        status_color = RED
        
    log(f"Response Status: {status_color}{response.status_code} ({response.reason}){ENDC} - {elapsed:.3f}s")
    log(f"Response Body: {pretty_json(display_result)}")
    log("-----------------------------------------------------------")
    
    return result

def test_health_check() -> bool:
    """Test the health check endpoint"""
    log("Testing health check...", GREEN)
    response = make_request("GET", "/health")
    
    success = response.get("status") == "ok" and response.get("status_code") == 200
    status = "passed" if success else "failed"
    log(f"Health check {status}")
    return success

def register_user(user_data: Dict[str, str]) -> Dict[str, Any]:
    """Register a new user and return the response"""
    log(f"Registering user {user_data['username']}...", GREEN)
    response = make_request("POST", "/v1/users/register", user_data)
    
    if response.get("status_code") == 201:
        log(f"User {user_data['username']} registered successfully with ID: {response.get('id', 'unknown')}")
    else:
        log(f"Failed to register user {user_data['username']}")
    
    return response

def login_user(username: str, password: str) -> str:
    """Login a user and return the access token"""
    log(f"Logging in as {username}...", GREEN)
    login_data = {
        "username": username,
        "password": password
    }
    response = make_request("POST", "/v1/users/login", login_data)
    
    if response.get("status_code") == 200:
        token = response.get("access_token")
        token_preview = token[:10] + "..." + token[-5:] if len(token) > 15 else token
        log(f"Login successful for {username}, token received: {token_preview}")
        return token
    else:
        log(f"Login failed for {username}")
        return None

def get_current_user(token: str) -> Dict[str, Any]:
    """Get the current user's information"""
    log("Fetching current user information...", GREEN)
    response = make_request("GET", "/v1/users/me", token=token)
    
    if response.get("status_code") == 200:
        log(f"Current user: {response.get('name')} ({response.get('username')})")
    else:
        log(f"Failed to get current user")
    
    return response

def create_conversation(token: str, name: str, member_ids: List[str]) -> Dict[str, Any]:
    """Create a new conversation"""
    log(f"Creating conversation '{name}' with {len(member_ids)} members...", GREEN)
    
    conversation_data = {
        "name": name,
        "member_ids": member_ids
    }
    
    response = make_request("POST", "/v1/conversations", conversation_data, token)
    
    if response.get("status_code") == 201:
        log(f"Conversation created with ID: {response.get('id', 'unknown')}")
    else:
        log(f"Failed to create conversation")
    
    return response

def create_one_on_one_conversation(token: str, other_user_id: str) -> Dict[str, Any]:
    """Create a one-on-one conversation with another user"""
    log(f"Creating one-on-one conversation with user ID: {other_user_id}...", GREEN)
    
    # For one-on-one conversations, typically only need the other user's ID
    # and a default name that can be overridden later
    conversation_data = {
        "name": "Private Chat",
        "member_ids": [other_user_id]
    }
    
    response = make_request("POST", "/v1/conversations", conversation_data, token)
    
    if response.get("status_code") == 201:
        log(f"One-on-one conversation created with ID: {response.get('id', 'unknown')}")
    else:
        log(f"Failed to create one-on-one conversation")
    
    return response

def list_conversations(token: str) -> Dict[str, Any]:
    """List all conversations for the current user"""
    log("Listing user conversations...", GREEN)
    
    response = make_request("GET", "/v1/conversations", token=token)
    if response.get("status_code") == 200:
        conversations = response.get("items", [])
        
        if "status_code" in conversations:
            del conversations["status_code"]
            
        log(f"Retrieved {len(conversations)} conversations")
        
        # Print a summary of each conversation
        for i, conv in enumerate(conversations):
            conv_type = conv.get("type", "unknown")
            name = conv.get("name", "Unnamed")
            member_count = len(conv.get("members", []))
            log(f"  {i+1}. {name} ({conv_type}) - {member_count} members")
    else:
        log(f"Failed to list conversations")
    
    return response

def run_tests() -> None:
    """Run all tests in sequence"""
    
    print(f"{BOLD}=== CHATTER API TEST SCRIPT ==={ENDC}")
    print(f"Target API: {API_BASE_URL}")
    print("============================")
    
    # Test health check
    if not test_health_check():
        print(f"{RED}Health check failed. Is the server running?{ENDC}")
        sys.exit(1)
    
    # Keep track of registered users and their IDs
    registered_users = {}
    tokens = {}
    
    # Register test users
    log(f"{BOLD}===== User Registration ====={ENDC}", GREEN)
    for user in TEST_USERS:
        result = register_user(user)
        if result.get("status_code") == 201:
            registered_users[user["username"]] = result.get("id")
        elif result.get("status_code") == 409:
            log(f"User {user['username']} already exists, continuing...")
            # User already exists, continue with tests
        else:
            log(f"Error registering user {user['username']}, skipping...")
            continue
    
    # Login test users
    log(f"{BOLD}===== User Login ====={ENDC}", GREEN)
    for user in TEST_USERS:
        token = login_user(user["username"], user["password"])
        if token:
            tokens[user["username"]] = token
    
    # Verify user information with tokens
    log(f"{BOLD}===== Verifying Authentication ====={ENDC}", GREEN)
    for username, token in tokens.items():
        user_info = get_current_user(token)
        if user_info.get("status_code") != 200:
            log(f"Failed to verify user {username}")
    
    # Create a group conversation
    log(f"{BOLD}===== Creating Group Conversation ====={ENDC}", GREEN)
    group_conversation_id = None
    if len(tokens) >= 2:
        main_user = TEST_USERS[0]["username"]
        token = tokens.get(main_user)
        
        if token:
            # Use the user IDs if available, otherwise skip this test
            member_ids = list(registered_users.values())
            if member_ids:
                conversation = create_conversation(
                    token=token,
                    name="Test Group Chat",
                    member_ids=member_ids
                )
                
                if conversation.get("status_code") == 201:
                    group_conversation_id = conversation.get("id")
                    log("Group conversation test passed!", GREEN)
                else:
                    log("Group conversation test failed!", RED)
            else:
                log("No registered user IDs available, skipping group conversation test", YELLOW)
        else:
            log(f"No token for {main_user}, skipping group conversation test", YELLOW)
    else:
        log("Not enough logged-in users, skipping group conversation test", YELLOW)
    
    # Create one-on-one conversations between users
    log(f"{BOLD}===== Creating One-on-One Conversations ====={ENDC}", GREEN)
    one_on_one_ids = []
    
    if len(registered_users) >= 2:
        # Get the first user's token
        main_user = TEST_USERS[0]["username"]
        main_token = tokens.get(main_user)
        
        if main_token:
            # Create one-on-one conversations with each other user
            other_users = list(registered_users.keys())
            other_users.remove(main_user)
            
            for other_user in other_users:
                other_id = registered_users.get(other_user)
                if other_id:
                    conversation = create_one_on_one_conversation(
                        token=main_token,
                        other_user_id=other_id
                    )
                    
                    if conversation.get("status_code") == 201:
                        one_on_one_ids.append(conversation.get("id"))
                        log(f"One-on-one conversation with {other_user} created successfully", GREEN)
                    else:
                        log(f"Failed to create one-on-one conversation with {other_user}", RED)
        else:
            log(f"No token for {main_user}, skipping one-on-one conversation tests", YELLOW)
    else:
        log("Not enough registered users, skipping one-on-one conversation tests", YELLOW)
    
    # List conversations for each user
    log(f"{BOLD}===== Listing User Conversations ====={ENDC}", GREEN)
    for username, token in tokens.items():
        log(f"Listing conversations for user: {username}", BLUE)
        list_conversations(token)
    
    print("============================")
    print(f"{GREEN}Test run completed!{ENDC}")
    
    # Print a summary of created resources
    print(f"{BOLD}===== Test Summary ====={ENDC}")
    print(f"Registered Users: {len(registered_users)}")
    print(f"Created Group Conversations: {1 if group_conversation_id else 0}")
    print(f"Created One-on-One Conversations: {len(one_on_one_ids)}")

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test execution interrupted.{ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Error occurred: {e}{ENDC}")
        sys.exit(1)