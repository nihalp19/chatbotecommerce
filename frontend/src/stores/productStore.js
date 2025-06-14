import { create } from 'zustand';
import { productAPI } from '../services/api';

export const useProductStore = create((set) => ({
  products: [],
  categories: [],
  brands: [],
  loading: false,
  error: null,

  searchProducts: async (query, filters) => {
    set({ loading: true, error: null });
    try {
      const products = await productAPI.search(query, filters);
      set({ products, loading: false });
    } catch (error) {
      set({ 
        error: 'Failed to search products', 
        loading: false,
        products: [] 
      });
    }
  },

  getCategories: async () => {
    try {
      const categories = await productAPI.getCategories();
      set({ categories });
    } catch (error) {
      set({ error: 'Failed to load categories' });
    }
  },

  getBrands: async () => {
    try {
      const brands = await productAPI.getBrands();
      set({ brands });
    } catch (error) {
      set({ error: 'Failed to load brands' });
    }
  },

  clearProducts: () => {
    set({ products: [], error: null });
  },
}));
