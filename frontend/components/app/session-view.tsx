'use client';

import React, { useEffect, useRef, useState } from 'react';
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

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'div'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const { playerName } = useSession();
  const messages = useChatMessages();
  const [chatInputOpen, setChatInputOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: false,
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      className="flex h-screen w-full overflow-hidden bg-zinc-950 font-sans text-white"
      {...props}
    >
      {/* ================= LEFT: MAIN CONTENT (Agent Visualizer) ================= */}
      <div className="relative flex min-w-0 flex-1 flex-col">
        {/* Animated Background */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -left-40 h-96 w-96 animate-pulse rounded-full bg-purple-600/20 blur-[120px]" />
          <div
            className="absolute -right-40 -bottom-40 h-96 w-96 animate-pulse rounded-full bg-cyan-500/20 blur-[120px]"
            style={{ animationDelay: '1s' }}
          />
          <div
            className="absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 animate-pulse rounded-full bg-lime-500/10 blur-[100px]"
            style={{ animationDelay: '2s' }}
          />
        </div>

        {/* Player Badge - Top Left */}
        {playerName && (
          <div className="absolute top-6 left-6 z-20">
            <div className="flex items-center gap-2 rounded-full border border-lime-500/30 bg-black/60 px-4 py-2 backdrop-blur-md">
              <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-lime-400 shadow-[0_0_10px_rgba(163,230,53,0.5)]" />
              <span className="text-sm font-medium text-gray-200">
                Playing as <span className="font-bold text-lime-400">{playerName}</span>
              </span>
            </div>
          </div>
        )}

        {/* Center: Large Agent Visualizer */}
        <div className="relative flex flex-1 items-center justify-center">
          <div className="scale-150 md:scale-[2]">
            <TileLayout chatOpen={false} />
          </div>
        </div>

        {/* Bottom: Pre-connect Message */}
        {appConfig.isPreConnectBufferEnabled && (
          <div className="absolute inset-x-0 bottom-8 z-10 px-6">
            <PreConnectMessage messages={messages} className="mx-auto max-w-xl text-center" />
          </div>
        )}
      </div>

      {/* ================= RIGHT: SIDEBAR ================= */}
      <div className="z-30 flex w-80 shrink-0 flex-col border-l border-purple-500/20 bg-zinc-900/50 backdrop-blur-sm lg:w-96">
        {/* Header */}
        <div className="flex h-14 items-center justify-center border-b border-purple-500/20 bg-black/30">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-cyan-400" />
            <span className="font-mono text-xs tracking-widest text-cyan-400/80 uppercase">
              JAX is Live
            </span>
          </div>
        </div>

        {/* Mini Agent Visualizer */}
        <div className="relative flex h-28 items-center justify-center overflow-hidden border-b border-purple-500/20 bg-black/20">
          <div className="scale-75 opacity-80">
            <TileLayout chatOpen={true} />
          </div>
        </div>

        {/* Transcript Header */}
        <div className="flex items-center justify-between border-b border-purple-500/20 bg-black/20 px-4 py-2">
          <h3 className="font-mono text-[10px] tracking-widest text-purple-400/70 uppercase">
            Live Transcript
          </h3>
          <div className="flex items-center gap-1">
            <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-purple-400" />
            <span className="font-mono text-[9px] text-purple-400/50">RECORDING</span>
          </div>
        </div>

        {/* Transcript Content - Hidden Scrollbar */}
        <ScrollArea
          ref={scrollAreaRef}
          className={cn(
            'flex-1 p-4',
            // Hide scrollbar across all browsers
            '[-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden'
          )}
        >
          <ChatTranscript messages={messages} className="space-y-3" />
        </ScrollArea>

        {/* Bottom: Controls */}
        <div className="border-t border-purple-500/20 bg-black/30 p-4">
          <AgentControlBar controls={controls} onChatOpenChange={setChatInputOpen} />
        </div>
      </div>
    </div>
  );
};
