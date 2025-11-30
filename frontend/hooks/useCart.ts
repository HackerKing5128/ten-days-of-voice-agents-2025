import { useCallback, useState } from 'react';
import type { Product } from './useShopData';

export interface CartItem extends Product {
  quantity: number;
}

export function useCart() {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const addToCart = useCallback((product: Product) => {
    setCart((prev) => {
      const existing = prev.find((p) => p.id === product.id);
      if (existing) {
        return prev.map((p) => (p.id === product.id ? { ...p, quantity: p.quantity + 1 } : p));
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true); // Open cart to show user
  }, []);

  const removeFromCart = useCallback((productId: number) => {
    setCart((prev) => prev.filter((p) => p.id !== productId));
  }, []);

  const clearCart = useCallback(() => setCart([]), []);

  const cartTotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);

  return { cart, addToCart, removeFromCart, clearCart, cartTotal, isCartOpen, setIsCartOpen };
}
