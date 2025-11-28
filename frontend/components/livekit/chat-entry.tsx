import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });
  const isUser = messageOrigin === 'local';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn(
        'group flex w-full flex-col gap-1 mb-3',
        isUser ? 'items-end' : 'items-start',
        className
      )}
      {...props}
    >
      <header
        className={cn(
          'text-muted-foreground flex items-center gap-2 text-xs px-1',
          isUser ? 'flex-row-reverse' : 'flex-row'
        )}
      >
        <strong className="text-xs font-medium">
          {isUser ? 'You' : 'Sam'}
        </strong>
        <span className="font-mono opacity-0 transition-opacity ease-linear group-hover:opacity-100">
          {hasBeenEdited && '*'}
          {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
        </span>
      </header>
      <span
        className={cn(
          'max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed',
          isUser
            ? 'bg-emerald-600 text-white rounded-br-sm'
            : 'bg-muted text-foreground rounded-bl-sm'
        )}
      >
        {message}
      </span>
    </li>
  );
};
