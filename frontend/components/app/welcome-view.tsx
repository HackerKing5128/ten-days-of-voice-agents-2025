'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/livekit/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (playerName: string) => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [playerName, setPlayerName] = useState('');
  const [isHovered, setIsHovered] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const name = playerName.trim() || 'Mysterious Stranger';
    onStartCall(name);
  };

  const isNameValid = playerName.trim().length > 0;

  return (
    <div ref={ref} className="relative min-h-screen">
      {/* Animated background gradients */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-80 w-80 animate-pulse rounded-full bg-purple-600/20 blur-[100px]" />
        <div
          className="absolute -right-40 -bottom-40 h-80 w-80 animate-pulse rounded-full bg-cyan-500/20 blur-[100px]"
          style={{ animationDelay: '1s' }}
        />
        <div
          className="absolute top-1/2 left-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 animate-pulse rounded-full bg-lime-400/10 blur-[120px]"
          style={{ animationDelay: '0.5s' }}
        />
      </div>

      <section className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 py-8">
        {/* Logo */}
        <div className="mb-6 transform transition-transform duration-300 hover:scale-105">
          <Image
            src="/day10-jax.svg"
            alt="IMPROV BATTLE - Hosted by JAX"
            width={400}
            height={120}
            priority
            className="h-auto w-full max-w-[400px] drop-shadow-2xl"
          />
        </div>

        {/* Tagline */}
        <p className="mb-8 max-w-md text-center text-sm text-gray-400 md:text-base">
          The wildest voice improv game show on the internet!
          <br />
          <span className="text-cyan-400">Think you can improv your way out?</span>
        </p>

        {/* Name Input Form */}
        <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-6">
          {/* Stage Name Input */}
          <div className="group relative">
            <label
              htmlFor="stageName"
              className="mb-2 block text-xs font-medium tracking-wider text-gray-500 uppercase"
            >
              Your Stage Name
            </label>
            <div className="relative">
              <input
                id="stageName"
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Enter your name..."
                maxLength={30}
                className="w-full rounded-lg border border-gray-700 bg-black/50 px-4 py-3 text-lg text-white placeholder-gray-500 transition-all duration-300 group-hover:border-gray-600 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 focus:outline-none"
                autoComplete="off"
                autoFocus
              />
              {/* Glow effect on focus */}
              <div className="absolute inset-0 -z-10 rounded-lg bg-linear-to-r from-purple-600/20 via-cyan-500/20 to-lime-400/20 opacity-0 blur-xl transition-opacity duration-300 group-focus-within:opacity-100" />
            </div>
          </div>

          {/* Enter Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={!isNameValid}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className={`relative w-full overflow-hidden py-4 font-mono text-lg transition-all duration-300 ${
              isNameValid
                ? 'bg-linear-to-r from-purple-600 via-cyan-500 to-purple-600 text-white shadow-lg shadow-purple-500/25 hover:from-purple-500 hover:via-cyan-400 hover:to-purple-500'
                : 'cursor-not-allowed bg-gray-800 text-gray-500'
            } ${isHovered && isNameValid ? 'scale-[1.02] shadow-xl shadow-cyan-500/30' : ''} `}
            style={{
              backgroundSize: isNameValid ? '200% 100%' : '100% 100%',
              animation: isNameValid ? 'gradient-shift 3s ease infinite' : 'none',
            }}
          >
            <span className="relative z-10 flex items-center justify-center gap-2">
              🎤 {startButtonText}
            </span>
          </Button>
        </form>

        {/* Bottom hint */}
        <p className="mt-8 max-w-xs text-center text-xs text-gray-600">
          JAX is waiting in the arena...
          <br />
          Voice your way to improv glory!
        </p>
      </section>

      {/* Footer */}
      <div className="fixed right-0 bottom-4 left-0 flex justify-center">
        <p className="text-xs text-gray-600">
          Powered by{' '}
          <a
            href="https://murf.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="text-lime-400 transition-colors hover:text-lime-300"
          >
            Murf AI
          </a>{' '}
          ×{' '}
          <a
            href="https://livekit.io"
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400 transition-colors hover:text-cyan-300"
          >
            LiveKit
          </a>
        </p>
      </div>

      {/* CSS for gradient animation */}
      <style jsx>{`
        @keyframes gradient-shift {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
      `}</style>
    </div>
  );
};
