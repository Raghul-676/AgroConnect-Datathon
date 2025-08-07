/**
 * AgroBot Chat Widget
 * Reusable floating chat interface for all pages
 */

// Chat widget HTML template
const chatWidgetHTML = `
  <!-- Floating AgroBot -->
  <div class="floating-agrobot" onclick="toggleChat()">
    <div class="bot-icon">🤖</div>
  </div>

  <!-- Chat Panel -->
  <div id="chatPanel" class="chat-panel">
    <div class="chat-header">
      <span>🤖 AgroBot Assistant</span>
      <button class="chat-close" onclick="toggleChat()">×</button>
    </div>
    
    <div id="chatBody" class="chat-body">
      <div class="chat-message bot">
        Hi! 👋 I'm AgroBot, your smart farming assistant. Ask me about crops, soil, fertilizers, pests, or farming practices!
      </div>
    </div>
    
    <div class="chat-footer">
      <input 
        id="chatInput" 
        class="chat-input" 
        type="text" 
        placeholder="Ask about crops, soil, fertilizers, pests..."
        onkeypress="handleKeyPress(event)"
      />
      <button id="sendBtn" class="chat-send-btn" onclick="sendMessage()">Send</button>
    </div>
  </div>
`;

// Chat widget CSS
const chatWidgetCSS = `
  /* Floating AgroBot Styles */
  .floating-agrobot {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #2e7d32, #4caf50);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(46, 125, 50, 0.3);
    transition: all 0.3s ease;
    z-index: 1000;
    border: 3px solid white;
  }

  .floating-agrobot:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(46, 125, 50, 0.4);
  }

  .floating-agrobot .bot-icon {
    font-size: 24px;
    color: white;
    animation: bounce 2s infinite;
  }

  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-5px);
    }
    60% {
      transform: translateY(-3px);
    }
  }

  /* Chat Panel Styles */
  .chat-panel {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    display: none;
    flex-direction: column;
    overflow: hidden;
    z-index: 1001;
    border: 2px solid #4caf50;
  }

  .chat-header {
    background: #2e7d32;
    color: white;
    padding: 1rem;
    font-weight: bold;
    text-align: center;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chat-close {
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .chat-body {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    background: #f9fafb;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .chat-message {
    padding: 0.75rem;
    border-radius: 10px;
    max-width: 80%;
    word-wrap: break-word;
  }

  .chat-message.bot {
    background: #e5e7eb;
    align-self: flex-start;
  }

  .chat-message.user {
    background: #d1fae5;
    align-self: flex-end;
  }

  .chat-footer {
    display: flex;
    padding: 0.75rem;
    border-top: 1px solid #e5e7eb;
    background: white;
    gap: 8px;
  }

  .chat-input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    outline: none;
    font-size: 14px;
  }

  .chat-input:focus {
    border-color: #4caf50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
  }

  .chat-send-btn {
    background: #4caf50;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
  }

  .chat-send-btn:hover {
    background: #2e7d32;
  }

  .chat-send-btn:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

// Initialize chat widget
function initAgroBotChat() {
  // Add CSS
  const style = document.createElement('style');
  style.textContent = chatWidgetCSS;
  document.head.appendChild(style);

  // Add HTML
  document.body.insertAdjacentHTML('beforeend', chatWidgetHTML);

  // Initialize variables
  window.chatPanel = document.getElementById("chatPanel");
  window.chatBody = document.getElementById("chatBody");
  window.chatInput = document.getElementById("chatInput");
  window.sendBtn = document.getElementById("sendBtn");
}

// Chat functions
function toggleChat() {
  if (window.chatPanel.style.display === "flex") {
    window.chatPanel.style.display = "none";
  } else {
    window.chatPanel.style.display = "flex";
    window.chatInput.focus();
  }
}

function handleKeyPress(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
}

function sendMessage() {
  const message = window.chatInput.value.trim();
  if (!message) return;

  // Add user message
  addMessage(message, 'user');
  window.chatInput.value = '';
  
  // Disable send button temporarily
  window.sendBtn.disabled = true;
  window.sendBtn.textContent = 'Sending...';

  // Connect to real AgroBot API
  setTimeout(async () => {
    try {
      // Call the actual AgroBot API
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
      });

      if (response.ok) {
        const data = await response.json();
        addMessage(data.response, 'bot');
      } else {
        // Fallback response if API returns error
        const fallbackResponse = getFallbackResponse(message);
        addMessage(fallbackResponse, 'bot');
      }
    } catch (error) {
      console.log('AgroBot API not available, using fallback response');
      // Fallback response if server is not running
      const fallbackResponse = getFallbackResponse(message);
      addMessage(fallbackResponse, 'bot');
    }

    // Re-enable send button
    window.sendBtn.disabled = false;
    window.sendBtn.textContent = 'Send';
  }, 1000);
}

function getFallbackResponse(message) {
  const messageLower = message.toLowerCase();

  // Handle greetings
  if (messageLower.includes('hello') || messageLower.includes('hi') || messageLower.includes('hey')) {
    return "Hello! I'm AgroBot, your farming assistant. How can I help you with agriculture today?";
  }

  // Handle non-agricultural questions
  if (messageLower.includes('capital') || messageLower.includes('math') || messageLower.includes('programming') ||
      messageLower.includes('movie') || messageLower.includes('sport') || messageLower.includes('music')) {
    return "I'm AgroBot, I only help with farming and agriculture questions. Please ask about crops, soil, fertilizers, pests, livestock, or farming practices.";
  }

  // Agricultural responses
  if (messageLower.includes('tomato')) {
    return "Tomatoes need well-drained soil, spring planting after frost, and regular watering. Common diseases are early blight and late blight.";
  } else if (messageLower.includes('rice')) {
    return "Rice is planted during monsoon season in flooded fields. Transplant 25-30 day old seedlings with 2-3 cm water level.";
  } else if (messageLower.includes('wheat')) {
    return "Wheat is sown in October-November, needs well-prepared soil and balanced fertilizer. Harvest when grains turn golden.";
  } else if (messageLower.includes('fertilizer')) {
    return "Use balanced NPK (10-10-10) for most crops. Apply organic compost and split nitrogen application for best results.";
  } else if (messageLower.includes('pest')) {
    return "Use integrated pest management with beneficial insects and targeted pesticides. Monitor crops regularly.";
  } else if (messageLower.includes('soil')) {
    return "Test soil pH and nutrients before planting. Add organic matter and ensure good drainage for healthy crops.";
  } else {
    return "I help with agriculture topics like crop cultivation, planting timing, fertilizers, and pest control. Ask specific farming questions.";
  }
}

function addMessage(message, type) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${type}`;
  messageDiv.textContent = message;
  window.chatBody.appendChild(messageDiv);
  window.chatBody.scrollTop = window.chatBody.scrollHeight;
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAgroBotChat);
