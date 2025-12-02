'use client';

import React, { useCallback, useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { useChat, useRemoteParticipants, useVoiceAssistant } from '@livekit/components-react';
import {
  MicrophoneIcon,
  VideoCameraIcon,
  PhoneXMarkIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/solid';
import type { AppConfig } from '@/app-config';
import { useSession } from '@/components/app/session-provider';
import { cn } from '@/lib/utils';
import { useInputControls } from '@/components/livekit/agent-control-bar/hooks/use-input-controls';

const MotionButton = motion.create('button');

interface ImprovControlBarProps {
  appConfig: AppConfig;
}

export function ImprovControlBar({ appConfig }: ImprovControlBarProps) {
  const { send } = useChat();
  const participants = useRemoteParticipants();
  const { state: agentState } = useVoiceAssistant();
  const { isSessionActive, endSession } = useSession();
  
  // Chat input state
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    cameraToggle,
    microphoneToggle,
  } = useInputControls({ saveUserChoices: true });

  const handleDisconnect = useCallback(() => {
    endSession();
  }, [endSession]);

  const handleSendScene = useCallback(async () => {
    await send('End scene!');
  }, [send]);

  const handleSendMessage = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isSending) return;
    
    try {
      setIsSending(true);
      await send(message);
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  }, [message, isSending, send]);

  const isAgentAvailable = participants.some((p) => p.isAgent);
  const isAgentSpeaking = agentState === 'speaking';
  const canSendMessage = message.trim().length > 0 && isAgentAvailable && !isSending;

  return (
    <div className="flex flex-col items-center gap-3 w-full max-w-2xl mx-auto px-4">
      {/* Chat Input Area */}
      <form 
        onSubmit={handleSendMessage}
        className={cn(
          'flex items-center gap-2 w-full rounded-full p-1.5 pl-4',
          'bg-black/60 backdrop-blur-xl',
          'border transition-all duration-300',
          isAgentSpeaking
            ? 'border-cyan-500/40 shadow-lg shadow-cyan-500/10'
            : 'border-white/10'
        )}
      >
        <input
          ref={inputRef}
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message to JAX..."
          disabled={!isAgentAvailable}
          className={cn(
            'flex-1 bg-transparent text-sm text-white placeholder-zinc-500',
            'focus:outline-none disabled:cursor-not-allowed disabled:opacity-50'
          )}
        />
        <MotionButton
          type="submit"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={!canSendMessage}
          className={cn(
            'flex h-10 w-10 items-center justify-center rounded-full transition-all duration-300',
            canSendMessage
              ? [
                  'bg-lime-500/20 text-lime-400',
                  'hover:bg-lime-500/30',
                ]
              : 'bg-zinc-800/50 text-zinc-600 cursor-not-allowed'
          )}
        >
          <PaperAirplaneIcon className="h-4 w-4" />
        </MotionButton>
      </form>
      
      {/* Controls Row */}
      <div className="flex items-center justify-center gap-3">
      {/* Main Control Pill */}
      <div
        className={cn(
          'flex items-center gap-2 rounded-full p-2',
          'bg-black/60 backdrop-blur-xl',
          'border transition-all duration-500',
          isAgentSpeaking
            ? 'border-cyan-500/30 shadow-lg shadow-cyan-500/10'
            : 'border-white/10'
        )}
      >
        {/* Microphone Toggle */}
        <MotionButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => microphoneToggle.toggle()}
          disabled={microphoneToggle.pending}
          className={cn(
            'relative flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300',
            microphoneToggle.enabled
              ? [
                  'bg-lime-500/20 text-lime-400',
                  'ring-2 ring-lime-500/50',
                  'shadow-lg shadow-lime-500/20',
                ]
              : 'bg-zinc-800/80 text-zinc-500 hover:bg-zinc-700/80'
          )}
        >
          <MicrophoneIcon className={cn(
            'h-5 w-5 transition-all duration-300',
            !microphoneToggle.enabled && 'opacity-50'
          )} />
          
          {/* Muted slash indicator */}
          {!microphoneToggle.enabled && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-8 w-0.5 rotate-45 bg-red-500" />
            </div>
          )}

          {/* ON AIR indicator */}
          {microphoneToggle.enabled && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute -top-1 -right-1"
            >
              <div className="relative">
                <div className="h-3 w-3 rounded-full bg-red-500" />
                <div className="absolute inset-0 animate-ping rounded-full bg-red-500 opacity-75" />
              </div>
            </motion.div>
          )}
        </MotionButton>

        {/* Camera Toggle (if supported) */}
        {appConfig.supportsVideoInput && (
          <MotionButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => cameraToggle.toggle()}
            disabled={cameraToggle.pending}
            className={cn(
              'relative flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300',
              cameraToggle.enabled
                ? [
                    'bg-purple-500/20 text-purple-400',
                    'ring-2 ring-purple-500/50',
                  ]
                : 'bg-zinc-800/80 text-zinc-500 hover:bg-zinc-700/80'
            )}
          >
            <VideoCameraIcon className={cn(
              'h-5 w-5 transition-all duration-300',
              !cameraToggle.enabled && 'opacity-50'
            )} />
            
            {/* Muted slash indicator */}
            {!cameraToggle.enabled && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-8 w-0.5 rotate-45 bg-red-500" />
              </div>
            )}
          </MotionButton>
        )}

        {/* Divider */}
        <div className="h-8 w-px bg-white/10" />

        {/* SCENE! Button */}
        <MotionButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSendScene}
          disabled={!isAgentAvailable}
          className={cn(
            'flex h-12 items-center gap-2 rounded-full px-4 font-mono text-xs font-bold tracking-wider transition-all duration-300',
            'bg-linear-to-r from-purple-600/30 to-cyan-600/30',
            'border border-purple-500/30',
            'text-white',
            'hover:from-purple-600/50 hover:to-cyan-600/50',
            'hover:border-purple-400/50',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <span>🎬</span>
          <span>SCENE!</span>
        </MotionButton>
      </div>

      {/* Exit Arena Button */}
      <MotionButton
        whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(239, 68, 68, 0.3)' }}
        whileTap={{ scale: 0.95 }}
        onClick={handleDisconnect}
        disabled={!isSessionActive}
        className={cn(
          'flex h-12 items-center gap-2 rounded-full px-5 font-mono text-xs font-bold tracking-wider uppercase transition-all duration-300',
          'bg-linear-to-r from-red-600/80 to-red-700/80',
          'border border-red-500/50',
          'text-white',
          'shadow-lg shadow-red-500/20',
          'hover:from-red-500/90 hover:to-red-600/90',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        <PhoneXMarkIcon className="h-4 w-4" />
        <span className="hidden md:inline">Exit Arena</span>
        <span className="inline md:hidden">Exit</span>
      </MotionButton>
      </div>
    </div>
  );
}
