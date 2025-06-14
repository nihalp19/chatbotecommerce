import React from 'react';
import { Bot, User } from 'lucide-react';
import { ProductGrid } from '../product/ProductGrid';

export function ChatMessage({ message }) {
  const isBot = message.sender === 'bot';

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`flex items-start max-w-[80%] ${isBot ? '' : 'flex-row-reverse'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isBot ? 'bg-blue-100 mr-3' : 'bg-emerald-100 ml-3'
        }`}>
          {isBot ? (
            <Bot className="w-5 h-5 text-blue-600" />
          ) : (
            <User className="w-5 h-5 text-emerald-600" />
          )}
        </div>
        
        <div className="flex flex-col">
          <div className={`rounded-2xl px-4 py-2 ${
            isBot 
              ? 'bg-gray-100 text-gray-800' 
              : 'bg-blue-600 text-white'
          }`}>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
          
          <div className={`text-xs text-gray-500 mt-1 ${isBot ? 'text-left' : 'text-right'}`}>
            {new Date(message.timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
          
          {message.products && message.products.length > 0 && (
            <div className="mt-3">
              <ProductGrid products={message.products} compact />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
