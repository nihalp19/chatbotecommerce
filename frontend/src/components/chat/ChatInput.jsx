import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';

export function ChatInput() {
  const [message, setMessage] = useState('');
  const { sendMessage, loading } = useChatStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      await sendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <div className="border-t border-gray-200 p-4 bg-white">
      <form onSubmit={handleSubmit} className="flex items-center space-x-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me about products, search for items, or get recommendations..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </form>
    </div>
  );
}
