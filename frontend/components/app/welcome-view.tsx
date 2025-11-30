import { Button } from '@/components/livekit/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="relative flex h-screen w-full flex-col overflow-hidden bg-zinc-950 font-sans text-white"
    >
      {/* BACKGROUND ACCENTS */}
      <div className="pointer-events-none absolute top-0 left-0 z-0 h-full w-full overflow-hidden">
        <div className="absolute -top-[20%] -left-[10%] h-[50%] w-[50%] rounded-full bg-purple-900/20 blur-[120px]" />
        <div className="absolute top-[20%] -right-[10%] h-[40%] w-[40%] rounded-full bg-blue-900/10 blur-[100px]" />
      </div>

      {/* HEADER with SVG Logo */}
      <header className="absolute top-0 left-0 z-20 flex w-full justify-center p-6 md:justify-start">
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
      </header>

      {/* MAIN CONTENT */}
      <main className="relative z-10 -mt-16 flex flex-1 flex-col items-center justify-center px-4 text-center">
        {/* Hero Visual */}
        <div className="group relative mb-8 cursor-pointer">
          <div className="text-8xl transition-transform duration-500 group-hover:scale-110 md:text-9xl">
            🛍️
          </div>
          <div className="absolute inset-0 rounded-full bg-orange-500/20 opacity-50 blur-[60px] transition-opacity duration-500 group-hover:opacity-80" />
        </div>

        <h1 className="mb-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
          Shopping Reimagined
        </h1>

        <p className="mb-10 max-w-md text-lg leading-relaxed text-zinc-400">
          Meet <span className="font-semibold text-orange-400">Ava</span>, your intelligent voice
          shopping assistant. Browse, search, and buy—completely hands-free.
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="h-14 rounded-full border-0 bg-gradient-to-r from-orange-600 to-amber-600 px-8 text-lg font-bold text-white shadow-lg shadow-orange-900/20 transition-all hover:scale-105 hover:from-orange-500 hover:to-amber-500 active:scale-95"
        >
          Start Shopping
        </Button>

        <div className="mt-8 flex gap-3 rounded-full border border-white/5 bg-white/5 px-4 py-2 font-mono text-xs text-zinc-500">
          <span>Try saying:</span>
          <span className="text-orange-300">"Show me running shoes"</span>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="absolute bottom-6 z-10 w-full text-center">
        <p className="text-xs tracking-wider text-zinc-600 uppercase">
          Day 9 Challenge • E-commerce Agent
        </p>
      </footer>
    </div>
  );
};
