import { useEffect, useState } from 'react';
import { type ReceivedChatMessage } from '@livekit/components-react';

interface OrderState {
  drinkType: string;
  size: string;
  milk: string;
  extras: string[];
  name: string;
  orderNumber?: string;
  isComplete: boolean;
}

export function useOrderState(messages: ReceivedChatMessage[]) {
  const [orderState, setOrderState] = useState<OrderState>({
    drinkType: '',
    size: '',
    milk: '',
    extras: [],
    name: '',
    isComplete: false,
  });

  useEffect(() => {
    // Look for the order confirmation message from the agent
    const lastAgentMessage = [...messages]
      .reverse()
      .find((msg) => msg.from?.isLocal === false);

    if (!lastAgentMessage) return;

    const messageText = lastAgentMessage.message.toLowerCase();

    // Check if this is the "order saved" confirmation message
    if (
      messageText.includes('order has been saved') ||
      messageText.includes('order number')
    ) {
      // Extract order number if present
      const orderNumberMatch = lastAgentMessage.message.match(/order number (\d+)/i);
      const orderNumber = orderNumberMatch ? orderNumberMatch[1] : undefined;

      // Parse the order details from the conversation history
      const parsedOrder = parseOrderFromMessages(messages);

      setOrderState({
        ...parsedOrder,
        orderNumber,
        isComplete: true,
      });
    }
  }, [messages]);

  return orderState;
}

function parseOrderFromMessages(messages: ReceivedChatMessage[]): Omit<OrderState, 'orderNumber' | 'isComplete'> {
  const order: Omit<OrderState, 'orderNumber' | 'isComplete'> = {
    drinkType: '',
    size: '',
    milk: '',
    extras: [],
    name: '',
  };

  // Look through messages to extract order details
  messages.forEach((msg) => {
    const text = msg.message.toLowerCase();

    // Extract drink type
    const drinkTypes = ['latte', 'cappuccino', 'espresso', 'americano', 'mocha', 'flat white', 'cold brew'];
    drinkTypes.forEach((drink) => {
      if (text.includes(drink) && !order.drinkType) {
        order.drinkType = drink;
      }
    });

    // Extract size
    if ((text.includes('small') || text.includes('grande')) && !order.size) {
      order.size = text.includes('small') ? 'small' : 'grande';
    } else if (text.includes('medium') && !order.size) {
      order.size = 'medium';
    } else if (text.includes('large') && !order.size) {
      order.size = 'large';
    }

    // Extract milk
    const milkTypes = ['whole milk', 'oat milk', 'almond milk', 'skim milk', 'soy milk'];
    milkTypes.forEach((milk) => {
      if (text.includes(milk) && !order.milk) {
        order.milk = milk;
      }
    });

    // Extract extras
    const extrasTypes = [
      'whipped cream',
      'extra shot',
      'vanilla syrup',
      'caramel syrup',
      'hazelnut syrup',
      'chocolate drizzle',
    ];
    extrasTypes.forEach((extra) => {
      if (text.includes(extra) && !order.extras.includes(extra)) {
        order.extras.push(extra);
      }
    });
  });

  // Extract name from user messages
  const userMessages = messages.filter((msg) => msg.from?.isLocal === true);
  if (userMessages.length > 0) {
    const lastUserMsg = userMessages[userMessages.length - 1];
    // Simple heuristic: if message is a short single word, it might be the name
    const words = lastUserMsg.message.trim().split(/\s+/);
    if (words.length === 1 && words[0].length > 1 && words[0].length < 20) {
      order.name = words[0];
    }
  }

  // Fallback: look for "saved" message pattern
  const savedMessage = messages.find((msg) =>
    msg.message.toLowerCase().includes('order has been saved')
  );
  if (savedMessage) {
    const nameMatch = savedMessage.message.match(/saved,?\s+(\w+)/i);
    if (nameMatch) {
      order.name = nameMatch[1];
    }
  }

  return order;
}
