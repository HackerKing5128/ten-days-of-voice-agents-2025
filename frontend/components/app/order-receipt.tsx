'use client';

import { motion } from 'motion/react';
import type { Order } from '@/hooks/useShopData';

const MotionDiv = motion.create('div');

interface OrderReceiptProps {
  order: Order;
}

export function OrderReceipt({ order }: OrderReceiptProps) {
  const item = order.line_items[0];

  return (
    <MotionDiv
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="rounded-lg border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-orange-600/5 p-5 shadow-lg"
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="border-b border-orange-500/20 pb-3 text-center">
          <h2 className="text-xl font-bold text-orange-400">🛒 SHOPVOICE</h2>
          <p className="text-muted-foreground text-sm">ORDER CONFIRMED</p>
        </div>

        {/* Order ID & Status */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Order ID:</span>
          <span className="font-mono text-orange-300">{order.id}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Status:</span>
          <span className="rounded bg-green-500/20 px-2 py-0.5 text-xs font-medium text-green-400">
            ✓ {order.status}
          </span>
        </div>

        {/* Product */}
        <div className="border-t border-b border-orange-500/20 py-3">
          <div className="flex gap-3">
            <div className="h-14 w-14 flex-shrink-0 overflow-hidden rounded-md bg-white">
              <img src={item.image} alt={item.title} className="h-full w-full object-contain p-1" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="line-clamp-2 text-sm font-medium">{item.title}</p>
              <p className="text-muted-foreground mt-1 text-xs">
                Qty: {item.quantity} × ${item.unit_price.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Total */}
        <div className="flex items-center justify-between text-lg font-bold">
          <span>Total:</span>
          <span className="text-orange-400">
            ${order.total.toFixed(2)} {order.currency}
          </span>
        </div>

        {/* Customer */}
        <div className="border-t border-orange-500/20 pt-2 text-center">
          <p className="text-muted-foreground text-sm">
            Thank you, <span className="font-medium text-orange-300">{order.customer_name}</span>!
          </p>
          <p className="text-muted-foreground mt-1 text-xs">
            {new Date(order.created_at).toLocaleString()}
          </p>
        </div>
      </div>
    </MotionDiv>
  );
}
