'use client';

import React, { useMemo } from 'react';
import { Track } from 'livekit-client';
import { AnimatePresence, motion } from 'motion/react';
import {
  BarVisualizer,
  type TrackReference,
  VideoTrack,
  useLocalParticipant,
  useTracks,
  useVoiceAssistant,
} from '@livekit/components-react';
import { cn } from '@/lib/utils';

const MotionContainer = motion.create('div');

const ANIMATION_TRANSITION = {
  type: 'spring' as const,
  stiffness: 400,
  damping: 40,
  mass: 1,
};

export function useLocalTrackRef(source: Track.Source) {
  const { localParticipant } = useLocalParticipant();
  const publication = localParticipant.getTrackPublication(source);
  const trackRef = useMemo<TrackReference | undefined>(
    () => (publication ? { source, participant: localParticipant, publication } : undefined),
    [source, publication, localParticipant]
  );
  return trackRef;
}

export function ImprovVisualizer() {
  const {
    state: agentState,
    audioTrack: agentAudioTrack,
    videoTrack: agentVideoTrack,
  } = useVoiceAssistant();
  const [screenShareTrack] = useTracks([Track.Source.ScreenShare]);
  const cameraTrack: TrackReference | undefined = useLocalTrackRef(Track.Source.Camera);

  const isCameraEnabled = cameraTrack && !cameraTrack.publication.isMuted;
  const isScreenShareEnabled = screenShareTrack && !screenShareTrack.publication.isMuted;
  const isAvatar = agentVideoTrack !== undefined;
  const videoWidth = agentVideoTrack?.publication.dimensions?.width ?? 0;
  const videoHeight = agentVideoTrack?.publication.dimensions?.height ?? 0;

  // Determine if agent is speaking based on state
  const isAgentSpeaking = agentState === 'speaking';
  const isAgentListening = agentState === 'listening';

  return (
    <div className="relative flex flex-col items-center justify-center gap-8">
      {/* JAX Label */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex flex-col items-center gap-2"
      >
        <span className="font-mono text-xs tracking-[0.3em] text-gray-500 uppercase">
          Your Host
        </span>
        <h2
          className={cn(
            'text-4xl font-black tracking-wider transition-all duration-500 md:text-5xl',
            isAgentSpeaking
              ? 'text-cyan-400 drop-shadow-[0_0_30px_rgba(34,211,238,0.5)]'
              : 'text-white/80'
          )}
        >
          JAX
        </h2>
      </motion.div>

      {/* Main Visualizer Container */}
      <div className="relative">
        {/* Outer Glow Ring */}
        <div
          className={cn(
            'absolute -inset-8 rounded-full opacity-50 blur-2xl transition-all duration-500',
            isAgentSpeaking
              ? 'bg-cyan-500/30'
              : isAgentListening
                ? 'bg-purple-500/20'
                : 'bg-white/5'
          )}
        />

        {/* Pulsing Ring Animation */}
        <motion.div
          animate={{
            scale: isAgentSpeaking ? [1, 1.1, 1] : 1,
            opacity: isAgentSpeaking ? [0.3, 0.6, 0.3] : 0.2,
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={cn(
            'absolute -inset-4 rounded-full border-2 transition-colors duration-500',
            isAgentSpeaking
              ? 'border-cyan-400/50'
              : isAgentListening
                ? 'border-purple-400/30'
                : 'border-white/10'
          )}
        />

        {/* Inner Ring */}
        <div
          className={cn(
            'absolute -inset-2 rounded-full border transition-colors duration-500',
            isAgentSpeaking
              ? 'border-cyan-400/30'
              : isAgentListening
                ? 'border-purple-400/20'
                : 'border-white/5'
          )}
        />

        {/* Visualizer */}
        <AnimatePresence mode="wait">
          {!isAvatar && (
            <MotionContainer
              key="agent-audio"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={ANIMATION_TRANSITION}
              className={cn(
                'relative flex h-40 w-40 items-center justify-center rounded-full md:h-56 md:w-56',
                'bg-linear-to-br from-zinc-900 to-black',
                'border transition-all duration-500',
                isAgentSpeaking
                  ? 'border-cyan-500/50 shadow-[0_0_60px_rgba(34,211,238,0.3)]'
                  : isAgentListening
                    ? 'border-purple-500/30 shadow-[0_0_40px_rgba(168,85,247,0.2)]'
                    : 'border-white/10'
              )}
            >
              <BarVisualizer
                barCount={5}
                state={agentState}
                options={{ minHeight: 8 }}
                trackRef={agentAudioTrack}
                className="flex h-full w-full items-center justify-center gap-2 p-8"
              >
                <span
                  className={cn([
                    'min-h-4 w-3 rounded-full md:w-4',
                    'origin-center transition-all duration-150 ease-out',
                    isAgentSpeaking
                      ? 'bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.8)]'
                      : isAgentListening
                        ? 'bg-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.6)]'
                        : 'bg-zinc-700',
                    'data-[lk-highlighted=true]:scale-y-150',
                    'data-[lk-muted=true]:bg-zinc-800',
                  ])}
                />
              </BarVisualizer>
            </MotionContainer>
          )}

          {isAvatar && (
            <MotionContainer
              key="agent-avatar"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={ANIMATION_TRANSITION}
              className={cn(
                'relative overflow-hidden rounded-2xl',
                'border-2 transition-all duration-500',
                isAgentSpeaking
                  ? 'border-cyan-500/50 shadow-[0_0_60px_rgba(34,211,238,0.3)]'
                  : 'border-white/10'
              )}
            >
              <VideoTrack
                width={videoWidth}
                height={videoHeight}
                trackRef={agentVideoTrack}
                className="h-56 w-56 object-cover md:h-72 md:w-72"
              />
            </MotionContainer>
          )}
        </AnimatePresence>
      </div>

      {/* Status Text */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex items-center gap-2"
      >
        <div
          className={cn(
            'h-1.5 w-1.5 rounded-full transition-colors duration-300',
            isAgentSpeaking ? 'bg-cyan-400 animate-pulse' : isAgentListening ? 'bg-purple-400' : 'bg-gray-600'
          )}
        />
        <span
          className={cn(
            'font-mono text-xs tracking-wider transition-colors duration-300',
            isAgentSpeaking ? 'text-cyan-400' : isAgentListening ? 'text-purple-400' : 'text-gray-600'
          )}
        >
          {isAgentSpeaking ? 'JAX IS SPEAKING...' : isAgentListening ? 'LISTENING TO YOU...' : 'CONNECTING...'}
        </span>
      </motion.div>

      {/* Camera Preview (if enabled) */}
      <AnimatePresence>
        {((cameraTrack && isCameraEnabled) || (screenShareTrack && isScreenShareEnabled)) && (
          <MotionContainer
            key="camera-preview"
            initial={{ opacity: 0, scale: 0, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0, y: 20 }}
            transition={ANIMATION_TRANSITION}
            className="absolute right-4 bottom-4 overflow-hidden rounded-xl border border-lime-500/30 shadow-lg shadow-lime-500/10"
          >
            <VideoTrack
              trackRef={cameraTrack || screenShareTrack}
              width={(cameraTrack || screenShareTrack)?.publication.dimensions?.width ?? 0}
              height={(cameraTrack || screenShareTrack)?.publication.dimensions?.height ?? 0}
              className="h-20 w-28 object-cover md:h-28 md:w-40"
            />
            <div className="absolute inset-x-0 bottom-0 bg-linear-to-t from-black/80 to-transparent px-2 py-1">
              <span className="font-mono text-[9px] text-lime-400">YOU</span>
            </div>
          </MotionContainer>
        )}
      </AnimatePresence>
    </div>
  );
}
