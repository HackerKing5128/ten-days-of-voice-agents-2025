'use client';

import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

const MotionDiv = motion.create('div');

interface OrderReceiptProps {
  drinkType: string;
  size: string;
  milk: string;
  extras: string[];
  name: string;
  orderNumber?: string;
  className?: string;
}

export function OrderReceipt({
  drinkType,
  size,
  milk,
  extras,
  name,
  orderNumber,
  className,
}: OrderReceiptProps) {
  // Simple price calculation (mock)
  const basePrice = 3.50;
  const sizeMultiplier = size.toLowerCase() === 'small' ? 0.8 : size.toLowerCase() === 'large' ? 1.2 : 1.0;
  const extrasPrice = extras.length * 0.50;
  const total = (basePrice * sizeMultiplier + extrasPrice).toFixed(2);

  return (
    <MotionDiv
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg p-6 shadow-lg border border-primary/20',
        className
      )}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="border-b border-primary/20 pb-3">
          <h2 className="text-2xl font-bold text-primary">THE RUSTY MUG</h2>
          <p className="text-sm text-muted-foreground">ORDER RECEIPT</p>
        </div>

        {/* Order Details */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Drink:</span>
            <span className="font-semibold capitalize">{drinkType}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Size:</span>
            <span className="font-semibold capitalize">{size}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Milk:</span>
            <span className="font-semibold capitalize">{milk}</span>
          </div>

          <div className="flex justify-between items-start">
            <span className="text-muted-foreground">Extras:</span>
            <div className="text-right">
              {extras.length > 0 ? (
                extras.map((extra, idx) => (
                  <div
                    key={idx}
                    className="bg-primary/20 px-2 py-1 rounded-md mb-1 text-sm font-medium capitalize"
                  >
                    {extra}
                  </div>
                ))
              ) : (
                <span className="text-sm text-muted-foreground italic">None</span>
              )}
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Name:</span>
            <span className="font-semibold capitalize">{name}</span>
          </div>
        </div>

        {/* Total */}
        <div className="border-t border-primary/20 pt-3">
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Total:</span>
            <span className="text-primary">${total}</span>
          </div>
          {orderNumber && (
            <p className="text-xs text-muted-foreground text-center mt-2">
              Order #{orderNumber}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="text-center pt-2">
          <p className="text-sm text-muted-foreground">
            Thank you, {name}! Your order will be ready soon.
          </p>
        </div>
      </div>
    </MotionDiv>
  );
}
