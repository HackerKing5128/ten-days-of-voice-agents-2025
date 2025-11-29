import { useEffect, useState, useCallback } from 'react';
import { useRoomContext } from '@livekit/components-react';

export interface Product {
  id: number;
  title: string;
  price: number;
  description: string;
  category: string;
  image: string;
  rating: {
    rate: number;
    count: number;
  };
}

export interface OrderLineItem {
  product_id: number;
  title: string;
  quantity: number;
  unit_price: number;
  image: string;
}

export interface Order {
  id: string;
  line_items: OrderLineItem[];
  total: number;
  currency: string;
  status: string;
  customer_name: string;
  created_at: string;
}

interface ShopData {
  products: Product[];
  order: Order | null;
  clearProducts: () => void;
  clearOrder: () => void;
}

export function useShopData(): ShopData {
  const room = useRoomContext();
  const [products, setProducts] = useState<Product[]>([]);
  const [order, setOrder] = useState<Order | null>(null);

  useEffect(() => {
    if (!room) return;

    const handleTextStream = async (
      reader: any,
      participantInfo: { identity: string }
    ) => {
      try {
        const text = await reader.readAll();
        const data = JSON.parse(text);

        if (data.type === 'products') {
          setProducts(data.data);
          console.log('Received products:', data.data.length);
        } else if (data.type === 'order') {
          setOrder(data.data);
          console.log('Received order:', data.data.id);
        }
      } catch (error) {
        console.error('Failed to parse shop data:', error);
      }
    };

    room.registerTextStreamHandler('shop-data', handleTextStream);

    return () => {
      // Cleanup the handler on unmount if needed
      room.unregisterTextStreamHandler('shop-data', handleTextStream);
    };
  }, [room]);

  const clearProducts = useCallback(() => setProducts([]), []);
  const clearOrder = useCallback(() => setOrder(null), []);

  return { products, order, clearProducts, clearOrder };
}