'use client';

import { type ReceivedChatMessage } from '@livekit/components-react';
import { ChatEntry } from '@/components/livekit/chat-entry';
import { cn } from '@/lib/utils';

interface ChatTranscriptProps {
  hidden?: boolean;
  messages?: ReceivedChatMessage[];
  className?: string;
}

export function ChatTranscript({
  hidden = false,
  messages = [],
  className,
}: ChatTranscriptProps) {
  if (hidden) return null;

  return (
    <div className={cn('transition-opacity duration-300', className)}>
      {messages.map(({ id, timestamp, from, message, editTimestamp }: ReceivedChatMessage) => {
        const locale = navigator?.language ?? 'en-US';
        const messageOrigin = from?.isLocal ? 'local' : 'remote';
        const hasBeenEdited = !!editTimestamp;

        return (
          <ChatEntry
            key={id}
            locale={locale}
            timestamp={timestamp}
            message={message}
            messageOrigin={messageOrigin}
            hasBeenEdited={hasBeenEdited}
          />
        );
      })}
    </div>
  );
}
