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

  // Determine if this is the Game Master (agent) or Player (user)
  const isGameMaster = messageOrigin === 'remote';
  const displayName = isGameMaster ? '🐉 Quest Master' : '⚔️ You';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn(
        'group flex w-full flex-col gap-1',
        isGameMaster ? 'items-start' : 'items-end',
        className
      )}
      {...props}
    >
      <header
        className={cn(
          'text-xs font-medium flex items-center gap-2',
          isGameMaster ? 'text-purple-400' : 'text-blue-400'
        )}
      >
        <strong>{displayName}</strong>
        <span className="font-mono opacity-0 transition-opacity ease-linear group-hover:opacity-60">
          {hasBeenEdited && '*'}
          {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
        </span>
      </header>
      <span
        className={cn(
          'max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed',
          isGameMaster
            ? 'bg-purple-900/50 text-purple-100 border border-purple-700/50 mr-auto'
            : 'bg-blue-900/50 text-blue-100 border border-blue-700/50 ml-auto'
        )}
      >
        {message}
      </span>
    </li>
  );
};
