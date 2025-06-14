import React from 'react';
import { Star, ShoppingCart } from 'lucide-react';

export function ProductCard({ product, compact = false }) {
  const { name, price, rating, image_url, brand, stock } = product;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 ${
      compact ? 'hover:scale-[1.02]' : 'hover:scale-[1.05]'
    }`}>
      <div className={`relative ${compact ? 'h-32' : 'h-48'}`}>
        <img
          src={image_url}
          alt={name}
          className="w-full h-full object-cover"
        />
        {stock === 0 && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="text-white font-medium">Out of Stock</span>
          </div>
        )}
      </div>
      
      <div className={`p-${compact ? '3' : '4'}`}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <p className="text-xs text-gray-500 mb-1">{brand}</p>
            <h3 className={`font-medium text-gray-900 leading-tight ${
              compact ? 'text-sm line-clamp-2' : 'text-base line-clamp-2'
            }`}>
              {name}
            </h3>
          </div>
        </div>
        
        <div className="flex items-center mb-2">
          <div className="flex items-center">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm text-gray-600 ml-1">{rating}</span>
          </div>
          <span className="text-sm text-gray-400 ml-2">({Math.floor(Math.random() * 1000) + 100} reviews)</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-baseline">
            <span className={`font-bold text-gray-900 ${compact ? 'text-lg' : 'text-xl'}`}>
              ${price}
            </span>
          </div>
          
          {!compact && (
            <button 
              disabled={stock === 0}
              className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ShoppingCart className="w-4 h-4" />
            </button>
          )}
        </div>
        
        {stock > 0 && stock < 10 && (
          <p className="text-xs text-orange-600 mt-2">Only {stock} left in stock!</p>
        )}
      </div>
    </div>
  );
}
