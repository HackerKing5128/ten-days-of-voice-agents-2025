'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { useSession } from '@/components/app/session-provider';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ImprovVisualizer } from './improv-visualizer';
import { ImprovTranscript } from './improv-transcript';
import { ImprovControlBar } from './improv-control-bar';

const MotionDiv = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const { playerName } = useSession();
  const messages = useChatMessages();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [sessionTime, setSessionTime] = useState(0);

  // Session timer
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll transcript
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <section
      className="relative z-10 flex h-full w-full overflow-hidden bg-zinc-950"
      {...props}
    >
      {/* ============ ANIMATED BACKGROUND ============ */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        {/* Purple glow - top left */}
        <div className="absolute -top-32 -left-32 h-[600px] w-[600px] rounded-full bg-purple-600/20 blur-[180px]" />
        {/* Cyan glow - bottom right */}
        <div className="absolute -right-32 -bottom-32 h-[600px] w-[600px] rounded-full bg-cyan-500/20 blur-[180px]" />
        {/* Lime accent - center left */}
        <div className="absolute top-1/3 left-1/4 h-[400px] w-[400px] rounded-full bg-lime-500/10 blur-[150px]" />

        {/* Animated sound wave lines */}
        <svg className="absolute inset-0 h-full w-full opacity-[0.03]">
          <defs>
            <pattern id="soundWaves" x="0" y="0" width="100" height="20" patternUnits="userSpaceOnUse">
              <path
                d="M0 10 Q25 0 50 10 T100 10"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-cyan-500"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#soundWaves)" />
        </svg>

        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* ============ TOP STATUS BAR ============ */}
      <MotionDiv
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="fixed top-16 left-1/2 z-60 -translate-x-1/2 md:top-20"
      >
        <div className="flex items-center gap-4 rounded-full border border-white/10 bg-black/60 px-6 py-2.5 backdrop-blur-xl">
          {/* JAX Live Indicator */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="h-2 w-2 rounded-full bg-cyan-400" />
              <div className="absolute inset-0 animate-ping rounded-full bg-cyan-400 opacity-75" />
            </div>
            <span className="font-mono text-[10px] font-bold tracking-widest text-cyan-400 uppercase">
              JAX Live
            </span>
          </div>

          {/* Divider */}
          <div className="h-4 w-px bg-white/20" />

          {/* Session Timer */}
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] tracking-wider text-gray-500 uppercase">
              Session
            </span>
            <span className="font-mono text-sm font-bold tabular-nums text-white">
              {formatTime(sessionTime)}
            </span>
          </div>

          {/* Divider */}
          <div className="h-4 w-px bg-white/20" />

          {/* Player Name */}
          {playerName && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-lime-400" />
              <span className="text-sm font-medium text-lime-400">{playerName}</span>
            </div>
          )}
        </div>
      </MotionDiv>

      {/* ============ MAIN CONTENT AREA ============ */}
      <div className="flex flex-1 flex-col lg:flex-row">
        {/* LEFT: Visualizer Area */}
        <div className="relative flex flex-1 items-center justify-center">
          <ImprovVisualizer />
        </div>

        {/* RIGHT: Always-Visible Transcript Sidebar */}
        <MotionDiv
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="z-30 flex w-full flex-col border-l border-purple-500/20 bg-black/40 backdrop-blur-md lg:w-[380px]"
        >
          {/* Transcript Header */}
          <div className="flex items-center justify-between border-b border-purple-500/20 bg-black/30 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="relative">
                <div className="h-2 w-2 rounded-full bg-red-500" />
                <div className="absolute inset-0 animate-pulse rounded-full bg-red-500 opacity-50" />
              </div>
              <span className="font-mono text-[10px] font-bold tracking-widest text-red-400 uppercase">
                Live Transcript
              </span>
            </div>
            <span className="font-mono text-[9px] tracking-wider text-gray-600">
              {messages.length} messages
            </span>
          </div>

          {/* Transcript Content */}
          <div
            ref={scrollAreaRef}
            className={cn(
              'flex-1 overflow-y-auto p-4',
              // Hide scrollbar
              '[-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden'
            )}
          >
            <ImprovTranscript messages={messages} />
          </div>
        </MotionDiv>
      </div>

      {/* ============ BOTTOM CONTROLS ============ */}
      <MotionDiv
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="fixed inset-x-4 bottom-4 z-50 md:inset-x-auto md:bottom-8 md:left-1/2 md:-translate-x-1/2"
      >
        <ImprovControlBar appConfig={appConfig} />
      </MotionDiv>
    </section>
  );
};
