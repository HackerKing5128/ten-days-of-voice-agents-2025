'use client';

import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { type ReceivedChatMessage } from '@livekit/components-react';
import { cn } from '@/lib/utils';

const MotionDiv = motion.create('div');

interface ImprovTranscriptProps {
  messages: ReceivedChatMessage[];
}

export function ImprovTranscript({ messages }: ImprovTranscriptProps) {
  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
        <div className="flex gap-1">
          <div className="h-2 w-2 animate-bounce rounded-full bg-cyan-500/50" style={{ animationDelay: '0ms' }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-purple-500/50" style={{ animationDelay: '150ms' }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-lime-500/50" style={{ animationDelay: '300ms' }} />
        </div>
        <p className="font-mono text-xs text-gray-600">Waiting for JAX to speak...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <AnimatePresence initial={false}>
        {messages.map((msg, index) => (
          <ImprovMessage key={msg.id} message={msg} isLatest={index === messages.length - 1} />
        ))}
      </AnimatePresence>
    </div>
  );
}

interface ImprovMessageProps {
  message: ReceivedChatMessage;
  isLatest: boolean;
}

function ImprovMessage({ message, isLatest }: ImprovMessageProps) {
  const { timestamp, from, message: text } = message;
  const isLocal = from?.isLocal ?? false;
  const isJax = !isLocal;
  const time = new Date(timestamp);
  const locale = typeof navigator !== 'undefined' ? navigator.language : 'en-US';

  return (
    <MotionDiv
      initial={{ opacity: 0, x: isJax ? -20 : 20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 500, damping: 40 }}
      className={cn('flex flex-col gap-1', isJax ? 'items-start' : 'items-end')}
    >
      {/* Header: Name + Time */}
      <div className={cn('flex items-center gap-2', isJax ? 'flex-row' : 'flex-row-reverse')}>
        {/* Avatar/Icon */}
        <div
          className={cn(
            'flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold',
            isJax
              ? 'bg-cyan-500/20 text-cyan-400 ring-1 ring-cyan-500/30'
              : 'bg-lime-500/20 text-lime-400 ring-1 ring-lime-500/30'
          )}
        >
          {isJax ? '🎤' : '🎭'}
        </div>

        {/* Name */}
        <span
          className={cn(
            'font-mono text-[10px] font-bold tracking-wider uppercase',
            isJax ? 'text-cyan-400' : 'text-lime-400'
          )}
        >
          {isJax ? 'JAX' : 'YOU'}
        </span>

        {/* Timestamp */}
        <span className="font-mono text-[9px] tabular-nums text-gray-600">
          {time.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {/* Message Bubble */}
      <div
        className={cn(
          'relative max-w-[90%] rounded-2xl px-4 py-2.5',
          'transition-all duration-300',
          isJax
            ? [
                'rounded-tl-sm',
                'bg-linear-to-br from-cyan-950/80 to-cyan-900/40',
                'border border-cyan-500/20',
                isLatest && 'shadow-lg shadow-cyan-500/10',
              ]
            : [
                'rounded-tr-sm',
                'bg-linear-to-br from-lime-950/80 to-lime-900/40',
                'border border-lime-500/20',
                isLatest && 'shadow-lg shadow-lime-500/10',
              ]
        )}
      >
        {/* Message Text */}
        <p
          className={cn(
            'text-sm leading-relaxed',
            isJax ? 'text-cyan-50' : 'text-lime-50'
          )}
        >
          {text}
        </p>

        {/* Typing indicator for latest JAX message */}
        {isLatest && isJax && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute -bottom-1 left-4"
          >
            <div className="flex gap-0.5">
              <div className="h-1 w-1 animate-pulse rounded-full bg-cyan-400/60" />
            </div>
          </motion.div>
        )}
      </div>

      {/* Special highlight for exciting moments */}
      {isJax && containsExcitement(text) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-1 flex items-center gap-1"
        >
          <span className="text-xs">✨</span>
          <span className="font-mono text-[9px] font-bold text-yellow-400">IMPROV MOMENT!</span>
        </motion.div>
      )}
    </MotionDiv>
  );
}

// Helper to detect exciting feedback from JAX
function containsExcitement(text: string): boolean {
  const excitementKeywords = [
    'legendary',
    'gold',
    'amazing',
    'incredible',
    'brilliant',
    'perfect',
    'love it',
    'fantastic',
    'excellent',
    'bravo',
    'wow',
    'that was',
    'nicely done',
    'well played',
  ];
  const lowerText = text.toLowerCase();
  return excitementKeywords.some((keyword) => lowerText.includes(keyword));
}
