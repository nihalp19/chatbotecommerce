import { create } from 'zustand';
import { chatAPI } from '../services/api';

export const useChatStore = create((set, get) => ({
  messages: [],
  loading: false,
  sessionId: undefined,

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message]
    }));
  },

  sendMessage: async (content) => {
    const { sessionId, addMessage } = get();
    
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
    };
    
    addMessage(userMessage);
    set({ loading: true });

    try {
      const response = await chatAPI.sendMessage(content, sessionId);
      
      const botMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
        products: response.products,
      };

      addMessage(botMessage);
      set({ sessionId: response.session_id });
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      set({ loading: false });
    }
  },

  resetChat: (username) => {
    const welcomeMessage = {
      id: 'welcome-' + Date.now(),
      content: username 
        ? `Hi ${username}! 👋 I'm your personal shopping assistant. I can help you find products, compare items, get recommendations, and answer any questions about our inventory. What are you looking for today?`
        : `Hi! 👋 How can I help you with your shopping today?`,
      sender: 'bot',
      timestamp: new Date(),
    };
    
    set({
      messages: [welcomeMessage],
      sessionId: undefined,
      loading: false
    });
  },

  setLoading: (loading) => {
    set({ loading });
  },
}));
