/**
 * ChatFastAPI Client-Side JavaScript
 * 
 * This script handles real-time chat functionality using WebSocket connections.
 * It manages the chat interface, message sending/receiving, and UI updates.
 * 
 * Features:
 * - WebSocket connection management
 * - Real-time message display with sender identification
 * - Message input handling (Enter key and button click)
 * - Auto-scroll to latest messages
 * - Visual distinction between own and others' messages
 */

// Extract room and user data from the hidden data container
// This data is populated by the server-side template rendering
const roomData = document.getElementById("room-data");
const roomId = roomData.getAttribute("data-room-id");
const username = roomData.getAttribute("data-username");
const userId = roomData.getAttribute("data-user-id");

// Establish WebSocket connection to the chat server
// The URL includes room ID, user ID, and username for server-side identification
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/${userId}?username=${username}`);

// WebSocket connection event handlers
ws.onopen = () => {
    console.log("WebSocket connection established successfully");
};

ws.onclose = () => {
    console.log("WebSocket connection closed");
};

// Handle incoming messages from the server
ws.onmessage = (event) => {
    // Parse the JSON message data (structured by Pydantic ChatMessage schema)
    const messageData = JSON.parse(event.data);
    
    // Get the messages container element
    const messages = document.getElementById("messages");
    
    // Create a new message element
    const message = document.createElement("div");
    
    // Apply different styling based on whether the message is from the current user
    // Own messages appear on the right (blue), others' messages on the left (gray)
    if (messageData.is_self) {
        // Own message styling: blue background, right-aligned
        message.className = "p-2 my-1 bg-blue-500 text-white rounded-md max-w-xs ml-auto";
    } else {
        // Other user's message styling: gray background, left-aligned
        message.className = "p-2 my-1 bg-gray-200 text-black rounded-md max-w-xs mr-auto";
    }
    
    // Set the message content and add to the chat
    message.textContent = messageData.text;
    messages.appendChild(message);
    
    // Auto-scroll to the bottom to show the latest message
    messages.scrollTop = messages.scrollHeight;
};

/**
 * Send a message through the WebSocket connection
 * 
 * This function:
 * 1. Gets the message input field
 * 2. Checks if there's actual content (not just whitespace)
 * 3. Sends the message via WebSocket
 * 4. Clears the input field for the next message
 */
function sendMessage() {
    const input = document.getElementById("messageInput");
    
    // Only send non-empty messages (trimmed of whitespace)
    if (input.value.trim()) {
        // Send the message through the WebSocket connection
        ws.send(input.value);
        // Clear the input field for the next message
        input.value = "";
    }
}

// Add keyboard event listener for Enter key
// This allows users to send messages by pressing Enter instead of clicking the button
document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});


