'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { useSession } from '@/components/app/session-provider';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut' as const,
  },
} as const;

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'pointer-events-none h-4 to-transparent',
        top && 'bg-gradient-to-b from-zinc-950',
        bottom && 'bg-gradient-to-t from-zinc-950',
        className
      )}
    />
  );
}

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
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section
      className="relative z-10 h-full w-full overflow-hidden bg-zinc-950"
      {...props}
    >
      {/* ============ ANIMATED BACKGROUND ============ */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        {/* Purple glow - top left */}
        <div className="absolute -top-32 -left-32 h-[500px] w-[500px] rounded-full bg-purple-600/15 blur-[150px]" />
        {/* Cyan glow - bottom right */}
        <div className="absolute -right-32 -bottom-32 h-[500px] w-[500px] rounded-full bg-cyan-500/15 blur-[150px]" />
        {/* Lime accent - center */}
        <div className="absolute top-1/2 left-1/2 h-[300px] w-[300px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-lime-500/5 blur-[120px]" />
        
        {/* Subtle grid pattern */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* ============ PLAYER BADGE - TOP RIGHT ============ */}
      {playerName && (
        <div className="fixed top-20 right-4 z-[60] md:top-24 md:right-6">
          <div className="flex items-center gap-2.5 rounded-full border border-lime-500/30 bg-black/70 px-4 py-2 shadow-lg shadow-lime-500/5 backdrop-blur-md">
            <div className="relative">
              <div className="h-2.5 w-2.5 rounded-full bg-lime-400" />
              <div className="absolute inset-0 animate-ping rounded-full bg-lime-400 opacity-75" />
            </div>
            <span className="text-sm font-medium text-gray-300">
              Playing as{' '}
              <span className="font-bold text-lime-400">{playerName}</span>
            </span>
          </div>
        </div>
      )}

      {/* ============ JAX STATUS INDICATOR - TOP LEFT ============ */}
      <div className="fixed top-20 left-4 z-[60] md:top-24 md:left-6">
        <div className="flex items-center gap-2.5 rounded-full border border-cyan-500/30 bg-black/70 px-4 py-2 shadow-lg shadow-cyan-500/5 backdrop-blur-md">
          <div className="relative">
            <div className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
            <div className="absolute inset-0 animate-pulse rounded-full bg-cyan-400 opacity-50" />
          </div>
          <span className="font-mono text-xs font-medium tracking-wider text-cyan-400 uppercase">
            JAX is Live
          </span>
        </div>
      </div>

      {/* ============ CHAT TRANSCRIPT (TOGGLE-ABLE) ============ */}
      <div
        className={cn(
          'fixed inset-0 z-20 grid grid-cols-1 grid-rows-1',
          !chatOpen && 'pointer-events-none'
        )}
      >
        <Fade top className="absolute inset-x-4 top-0 h-40" />
        <ScrollArea
          ref={scrollAreaRef}
          className={cn(
            'px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px]',
            // Custom scrollbar styling
            '[&::-webkit-scrollbar]:w-1.5',
            '[&::-webkit-scrollbar-track]:bg-transparent',
            '[&::-webkit-scrollbar-thumb]:rounded-full',
            '[&::-webkit-scrollbar-thumb]:bg-purple-500/30',
            '[&::-webkit-scrollbar-thumb:hover]:bg-purple-500/50'
          )}
        >
          <ChatTranscript
            hidden={!chatOpen}
            messages={messages}
            className="mx-auto max-w-2xl space-y-3 transition-opacity duration-300 ease-out"
          />
        </ScrollArea>
      </div>

      {/* ============ AGENT VISUALIZER (TILE LAYOUT) ============ */}
      <TileLayout chatOpen={chatOpen} />

      {/* ============ BOTTOM CONTROLS ============ */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          
          {/* Control bar with subtle background */}
          <div className="rounded-2xl border border-white/5 bg-black/40 p-2 backdrop-blur-xl">
            <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
          </div>
        </div>
      </MotionBottom>
    </section>
  );
};
