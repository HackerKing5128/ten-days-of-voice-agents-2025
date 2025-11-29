'use client';

import { motion } from 'motion/react';
import type { Product } from '@/hooks/useShopData';

const MotionDiv = motion.create('div');

interface ProductGridProps {
  products: Product[];
}

export function ProductGrid({ products }: ProductGridProps) {
  if (products.length === 0) return null;

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      className="space-y-3"
    >
      <h2 className="text-lg font-semibold text-orange-400 flex items-center gap-2">
        <span>🛍️</span> Products
      </h2>
      
      <div className="grid grid-cols-1 gap-3 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
        {products.map((product, index) => (
          <MotionDiv
            key={product.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
            className="bg-card border border-orange-500/20 rounded-lg p-3 flex gap-3 hover:border-orange-500/40 transition-colors"
          >
            {/* Product Image */}
            <div className="w-16 h-16 flex-shrink-0 bg-white rounded-md overflow-hidden">
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-full object-contain p-1"
              />
            </div>
            
            {/* Product Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-medium text-sm text-foreground line-clamp-2">
                  <span className="text-orange-400 mr-1">{index + 1}.</span>
                  {product.title}
                </h3>
              </div>
              
              <div className="flex items-center gap-2 mt-1">
                <span className="text-orange-400 font-bold">
                  ${product.price.toFixed(2)}
                </span>
                <span className="text-xs text-muted-foreground">
                  ⭐ {product.rating.rate} ({product.rating.count})
                </span>
              </div>
              
              <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                {product.category}
              </p>
            </div>
          </MotionDiv>
        ))}
      </div>
      
      <p className="text-xs text-muted-foreground text-center">
        Say a number to learn more or "buy number X"
      </p>
    </MotionDiv>
  );
}