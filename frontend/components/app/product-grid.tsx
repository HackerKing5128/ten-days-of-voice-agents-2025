'use client';

import { motion } from 'motion/react';
import { ShoppingCartIcon } from '@phosphor-icons/react/dist/ssr';
import { toast } from 'sonner';
import type { Product } from '@/hooks/useShopData';

const MotionDiv = motion.create('div');

interface ProductGridProps {
  products: Product[];
}

export function ProductGrid({ products }: ProductGridProps) {
  // EMPTY STATE: Show this when no products are loaded yet
  if (!products || products.length === 0) {
    return (
      <div className="relative z-50 flex h-full flex-col items-center justify-center text-center space-y-6 pt-32 opacity-50 pointer-events-none">
        <div className="text-8xl animate-pulse">🛍️</div>
        <div className="space-y-2">
          <h2 className="text-2xl font-light text-white">Your Shop is Ready</h2>
          <p className="text-sm text-zinc-400">Try saying:</p>
          <div className="flex gap-2 justify-center text-xs text-orange-300 font-mono">
            <span className="bg-white/5 px-2 py-1 rounded">"Show smartphones"</span>
            <span className="bg-white/5 px-2 py-1 rounded">"I need a laptop"</span>
          </div>
        </div>
      </div>
    );
  }

  // DATA STATE: Show the grid
  return (
    <MotionDiv
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 pb-32"
    >
      
      
      {/* RESPONSIVE GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product, index) => (
          <MotionDiv
            key={`${product.id}-${index}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative flex flex-col overflow-hidden rounded-xl bg-white shadow-lg ring-1 ring-white/10"
          >
            {/* Image Area - White Background */}
            <div className="relative aspect-[4/3] w-full bg-white p-6 flex items-center justify-center overflow-hidden">
              <img
                src={product.thumbnail}
                alt={product.title}
                className="h-full w-full object-contain transition-transform duration-500 group-hover:scale-110"
              />
              {/* Badge */}
              <div className="absolute top-3 left-3 bg-zinc-900/90 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-sm uppercase tracking-wider">
                #{index + 1}
              </div>
            </div>
            
            {/* Content Area */}
            <div className="flex flex-1 flex-col justify-between bg-zinc-50 p-4 border-t border-zinc-100">
              <div>
                <h3 className="line-clamp-2 text-sm font-semibold text-zinc-900 group-hover:text-orange-600 transition-colors">
                  {product.title}
                </h3>
                <p className="mt-1 text-xs text-zinc-500 capitalize">{product.category}</p>
              </div>
              
              <div className="mt-3 flex items-end justify-between">
                <div className="text-lg font-bold text-zinc-900">
                  ${product.price.toFixed(2)}
                </div>
                
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs font-medium text-amber-500 bg-amber-50 px-1.5 py-0.5 rounded">
                    <span>★</span>
                    <span>{product.rating}</span>
                  </div>

                  {/* ADD TO CART BUTTON */}
                  <button 
                    onClick={() => {
                      console.log("Added to cart:", product.title);
                      // Visual feedback for the demo
                      toast.success(`Added ${product.title} to cart`);
                    }}
                    className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-900 text-white transition-all hover:bg-orange-500 hover:scale-110 active:scale-95"
                    title="Add to cart"
                  >
                    <ShoppingCartIcon weight="bold" size={16} />
                  </button>
                </div>
              </div>
            </div>
          </MotionDiv>
        ))}
      </div>
    </MotionDiv>
  );
}