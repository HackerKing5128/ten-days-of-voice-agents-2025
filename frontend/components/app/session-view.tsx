'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { OrderReceipt } from '@/components/app/order-receipt';
import { ProductGrid } from '@/components/app/product-grid';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { useShopData } from '@/hooks/useShopData';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

export function SessionView({ appConfig }: { appConfig: AppConfig }) {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: process.env.NODE_ENV !== 'production' });

  const messages = useChatMessages();
  const { products, order } = useShopData();
  const [chatInputOpen, setChatInputOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: true,
    camera: appConfig.supportsVideoInput,
    screenShare: false,
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-zinc-950 font-sans text-white">
      

      {/* ================= LEFT: MAIN CONTENT ================= */}
      <div className="relative flex min-w-0 flex-1 flex-col">
        {/* Sticky Header */}
        <div className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/5 bg-zinc-950/90 px-6 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <div className="w-[160px] md:w-[200px]">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="100%" height="auto">
            <defs>
              <linearGradient id="avaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#b066ff', stopOpacity: 1 }} />
                <stop offset="100%" style={{ stopColor: '#00d4ff', stopOpacity: 1 }} />
              </linearGradient>
            </defs>
            <g transform="translate(35, 25)">
              <path
                d="M15,25 L65,25 L75,75 L5,75 Z"
                fill="none"
                stroke="url(#avaGradient)"
                strokeWidth="4"
                strokeLinejoin="round"
              />
              <rect x="25" y="35" width="4" height="20" rx="2" fill="#b066ff">
                <animate
                  attributeName="height"
                  values="20;10;25;15;20"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="y"
                  values="35;40;32;38;35"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
              </rect>
              <rect x="38" y="30" width="4" height="30" rx="2" fill="#00d4ff">
                <animate
                  attributeName="height"
                  values="30;15;35;20;30"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="y"
                  values="30;38;28;35;30"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
              </rect>
              <rect x="51" y="35" width="4" height="20" rx="2" fill="#b066ff">
                <animate
                  attributeName="height"
                  values="20;10;25;15;20"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="y"
                  values="35;40;32;38;35"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
              </rect>
              <path
                d="M25,25 C25,10 55,10 55,25"
                stroke="url(#avaGradient)"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
              />
              <circle cx="40" cy="15" r="3" fill="#ffffff" opacity="0.8" />
            </g>
            <g
              transform="translate(125, 40)"
              fontFamily="'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
            >
              <text x="0" y="30" fontSize="38" fontWeight="700" fill="#ffffff" letterSpacing="1">
                ShopVoice
              </text>
              <g transform="translate(2, 55)">
                <text x="0" y="0" fontSize="14" fill="#a0a0a0" fontWeight="400" letterSpacing="1.5">
                  POWERED BY AVA
                </text>
                <circle cx="135" cy="-4" r="3" fill="#00d4ff">
                  <animate
                    attributeName="opacity"
                    values="1;0.3;1"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
              </g>
            </g>
          </svg>
        </div>
          </div>
          {products.length > 0 && (
            <span className="rounded-full border border-orange-400/20 bg-orange-400/10 px-2 py-1 font-mono text-xs text-orange-400">
              {products.length} items
            </span>
          )}
        </div>

        {/* Scrollable Product Grid */}
        <div className="custom-scrollbar flex-1 overflow-y-auto p-6 pb-32">
          <div className="mx-auto max-w-6xl">
            <ProductGrid products={products} />
          </div>
        </div>

        {/* Order Modal */}
        <AnimatePresence>
          {order && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
              <div className="w-full max-w-md">
                <OrderReceipt order={order} />
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* ================= RIGHT: SIDEBAR ================= */}
      <div className="z-30 flex w-80 shrink-0 flex-col border-l border-white/5 bg-zinc-900/30">
        {/* Header Matcher (Empty to align with left header) */}
        <div className="flex h-16 items-center justify-center border-b border-white/5 bg-white/5">
          <span className="font-mono text-[10px] tracking-widest text-white/40 uppercase">
            Live Agent
          </span>
        </div>

        {/* Top: Agent Visualizer */}
        <div className="relative flex h-32 items-center justify-center overflow-hidden border-b border-white/5 bg-black/20">
          {/* Force chatOpen=true for small scale */}
          <div className="scale-75 opacity-90">
            <TileLayout chatOpen={true} />
          </div>
        </div>

        {/* Middle: Transcript */}
        <div className="group relative flex min-h-0 flex-1 flex-col">
          <div className="flex items-center justify-between border-b border-white/5 bg-white/5 p-2">
            <h3 className="pl-2 font-mono text-[10px] tracking-widest text-white/50 uppercase">
              Transcript
            </h3>
          </div>

          {/* Scrollbar Hiding applied here */}
          <ScrollArea
            ref={scrollAreaRef}
            className="flex-1 p-4 [-ms-overflow-style:'none'] [scrollbar-width:'none'] [&::-webkit-scrollbar]:hidden"
          >
            <ChatTranscript messages={messages} />
          </ScrollArea>
        </div>

        {/* Bottom: Controls (Clean - No extra box) */}
        <div className="flex justify-center border-t border-white/5 bg-zinc-900/50 p-4">
          <AgentControlBar controls={controls} onChatOpenChange={setChatInputOpen} />
        </div>
      </div>
    </div>
  );
}
