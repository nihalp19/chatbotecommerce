import React from 'react';
import { ProductCard } from './ProductCard';

export function ProductGrid({ products, compact = false }) {
  if (products.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No products found</p>
      </div>
    );
  }

  return (
    <div className={`grid gap-4 ${
      compact 
        ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4' 
        : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
    }`}>
      {products.map((product) => (
        <ProductCard 
          key={product.id} 
          product={product} 
          compact={compact} 
        />
      ))}
    </div>
  );
}
