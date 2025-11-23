import { Button } from '@/components/livekit/button';

function CoffeeMugIcon() {
  return (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      {/* Coffee Mug Body */}
      <path
        d="M25 40 L25 85 C25 92 30 97 37 97 L73 97 C80 97 85 92 85 85 L85 40 Z"
        fill="#8B4513"
        stroke="#654321"
        strokeWidth="2"
      />
      
      {/* Mug Handle */}
      <path
        d="M85 50 C95 50 100 55 100 65 C100 75 95 80 85 80"
        fill="none"
        stroke="#654321"
        strokeWidth="3"
        strokeLinecap="round"
      />
      
      {/* Coffee Surface */}
      <ellipse
        cx="55"
        cy="42"
        rx="28"
        ry="6"
        fill="#6B4423"
      />
      
      {/* Steam Lines */}
      <path
        d="M45 25 Q42 15 45 10"
        stroke="#A0826D"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.7"
      />
      <path
        d="M55 20 Q52 10 55 5"
        stroke="#A0826D"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.7"
      />
      <path
        d="M65 25 Q68 15 65 10"
        stroke="#A0826D"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.7"
      />
      
      {/* Rustic Texture Lines on Mug */}
      <line x1="30" y1="50" x2="80" y2="50" stroke="#654321" strokeWidth="1" opacity="0.3" />
      <line x1="30" y1="65" x2="80" y2="65" stroke="#654321" strokeWidth="1" opacity="0.3" />
      <line x1="30" y1="80" x2="80" y2="80" stroke="#654321" strokeWidth="1" opacity="0.3" />
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
        <CoffeeMugIcon />

        <h1 className="text-foreground text-4xl md:text-5xl font-bold" style={{ color: '#8B4513' }}>
          The Rusty Mug
        </h1>

        <p className="text-muted-foreground max-w-prose pt-3 text-sm md:text-base italic">
          "Where every cup tells a story"
        </p>

        <p className="text-foreground max-w-prose pt-4 leading-6 font-medium text-lg">
          Welcome! Chat with Lara, your friendly barista
        </p>

        <p className="text-muted-foreground max-w-prose pt-2 text-sm">
          Order your perfect coffee via voice or text
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
