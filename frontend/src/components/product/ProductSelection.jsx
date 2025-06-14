import React, { useEffect, useState } from 'react';
import { ShoppingBag, Filter, Grid, List, Star, TrendingUp } from 'lucide-react';
import { ProductGrid } from './ProductGrid';
import { useProductStore } from '../../stores/productStore';

export const ProductSelection = ({ onStartChat }) => {
  const [activeTab, setActiveTab] = useState('featured');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const { categories, brands, getBrands, getCategories, searchProducts, products } = useProductStore();

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        getCategories(),
        getBrands(),
        loadFeaturedProducts(),
        loadTrendingProducts()
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadFeaturedProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/products/featured', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setFeaturedProducts(data);
    } catch (error) {
      console.error('Failed to load featured products:', error);
    }
  };

  const loadTrendingProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/products/trending', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setTrendingProducts(data);
    } catch (error) {
      console.error('Failed to load trending products:', error);
    }
  };

  const handleCategorySelect = async (category) => {
    setSelectedCategory(category);
    setActiveTab('categories');
    await searchProducts('', { category });
  };

  const renderCategoryStats = () => {
    if (!Array.isArray(categories)) return null;
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {categories.map((cat) => (
          <div
            key={cat.category}
            onClick={() => handleCategorySelect(cat.category)}
            className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-105"
          >
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <ShoppingBag className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{cat.category}</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <p>{cat.count} products</p>
                <div className="flex items-center justify-center">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 mr-1" />
                  <span>{cat.avg_rating}</span>
                </div>
                <p className="font-medium text-blue-600">${cat.avg_price}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderProducts = () => {
    let productsToShow = [];
    switch (activeTab) {
      case 'featured':
        productsToShow = featuredProducts;
        break;
      case 'trending':
        productsToShow = trendingProducts;
        break;
      case 'categories':
        productsToShow = products;
        break;
      default:
        productsToShow = [];
    }

    if (productsToShow.length === 0 && !loading) {
      return (
        <div className="text-center py-12">
          <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No products found</p>
        </div>
      );
    }

    return <ProductGrid products={productsToShow} compact={viewMode === 'grid'} />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Product Catalog</h1>
              <p className="text-gray-600 mt-1">Explore our collection before chatting with our AI assistant</p>
            </div>
            <button
              onClick={onStartChat}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <span>Start Shopping Chat</span>
              <ShoppingBag className="w-5 h-5" />
            </button>
          </div>
          {/* Navigation Tabs */}
          <div className="flex items-center justify-between">
            <div className="flex space-x-8">
              <button
                onClick={() => setActiveTab('featured')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'featured'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Star className="w-4 h-4" />
                  <span>Featured</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('categories')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'categories'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4" />
                  <span>Categories</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('trending')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'trending'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4" />
                  <span>Trending</span>
                </div>
              </button>
            </div>
            {activeTab !== 'categories' && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <Grid className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <List className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'categories' && !selectedCategory ? (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Browse by Category</h2>
              <p className="text-gray-600">Choose a category to explore our products</p>
            </div>
            {renderCategoryStats()}
          </div>
        ) : (
          <div>
            {selectedCategory && (
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedCategory}</h2>
                  <p className="text-gray-600">{products.length} products found</p>
                </div>
                <button
                  onClick={() => {
                    setSelectedCategory('');
                    setActiveTab('featured');
                  }}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  ← Back to Categories
                </button>
              </div>
            )}
            {activeTab === 'featured' && (
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Featured Products</h2>
                <p className="text-gray-600">Our top-rated products with excellent reviews</p>
              </div>
            )}
            {activeTab === 'trending' && (
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Trending Now</h2>
                <p className="text-gray-600">Popular products that customers love</p>
              </div>
            )}
            {renderProducts()}
          </div>
        )}
      </div>
    </div>
  );
};
