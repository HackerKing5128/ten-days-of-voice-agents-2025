import { Button } from '@/components/livekit/button';

function OrionIcon() {
  return (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      {/* Constellation Stars */}
      <circle cx="30" cy="25" r="3" fill="#2C7A7B" />
      <circle cx="50" cy="20" r="4" fill="#2C7A7B" />
      <circle cx="70" cy="25" r="3" fill="#2C7A7B" />
      <circle cx="90" cy="30" r="3" fill="#2C7A7B" />
      <circle cx="40" cy="50" r="3.5" fill="#38B2AC" />
      <circle cx="60" cy="55" r="5" fill="#38B2AC" opacity="0.9" />
      <circle cx="80" cy="50" r="3.5" fill="#38B2AC" />
      
      {/* Connecting Lines */}
      <line x1="30" y1="25" x2="50" y2="20" stroke="#2C7A7B" strokeWidth="1.5" opacity="0.6" />
      <line x1="50" y1="20" x2="70" y2="25" stroke="#2C7A7B" strokeWidth="1.5" opacity="0.6" />
      <line x1="70" y1="25" x2="90" y2="30" stroke="#2C7A7B" strokeWidth="1.5" opacity="0.6" />
      <line x1="40" y1="50" x2="60" y2="55" stroke="#38B2AC" strokeWidth="2" opacity="0.7" />
      <line x1="60" y1="55" x2="80" y2="50" stroke="#38B2AC" strokeWidth="2" opacity="0.7" />
      <line x1="50" y1="20" x2="60" y2="55" stroke="#319795" strokeWidth="1.5" opacity="0.5" />
      
      {/* Central Wellness Symbol - Zen Circle */}
      <circle 
        cx="60" 
        cy="75" 
        r="25" 
        stroke="#2C7A7B" 
        strokeWidth="3" 
        fill="none"
        opacity="0.8"
      />
      <circle 
        cx="60" 
        cy="75" 
        r="15" 
        stroke="#38B2AC" 
        strokeWidth="2" 
        fill="none"
        opacity="0.6"
      />
      
      {/* Inner peaceful dot */}
      <circle cx="60" cy="75" r="5" fill="#2C7A7B" opacity="0.7" />
    </svg>
  );
}

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
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center px-4">
        <OrionIcon />

        <h1 className="text-foreground text-4xl md:text-5xl font-bold" style={{ color: '#2C7A7B' }}>
          Orion
        </h1>

        <p className="text-muted-foreground max-w-prose pt-3 text-sm md:text-base italic">
          "Find your center. One day at a time."
        </p>

        <p className="text-foreground max-w-prose pt-4 leading-6 font-medium text-lg">
          Your supportive wellness companion
        </p>

        <p className="text-muted-foreground max-w-prose pt-2 text-sm">
          Daily check-ins for mood, energy, and intentions
        </p>

        <Button variant="primary" size="lg" onClick={onStartCall} className="mt-8 w-64 font-mono text-lg">
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Powered by Murf Falcon TTS ⚡ |{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            LiveKit Voice AI
          </a>
        </p>
      </div>
    </div>
  );
};
