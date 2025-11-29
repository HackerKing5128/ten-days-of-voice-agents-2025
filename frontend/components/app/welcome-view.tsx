import { Button } from '@/components/livekit/button';

function DragonIcon() {
  return (
    <div className="mb-6 relative">
      <div className="text-7xl animate-pulse">🐉</div>
      <div className="absolute inset-0 bg-purple-500/20 blur-3xl rounded-full" />
    </div>
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
        <DragonIcon />

        <h1 className="text-2xl md:text-3xl font-bold text-purple-100 mb-2">
          Voice Game Master
        </h1>
        
        <p className="text-purple-300 max-w-md pt-1 leading-6 text-sm md:text-base">
          Embark on an epic fantasy adventure guided by Aldric, the Quest Master.
          Speak your actions aloud and shape your destiny!
        </p>

        <Button 
          variant="primary" 
          size="lg" 
          onClick={onStartCall} 
          className="mt-8 w-64 font-bold bg-purple-600 hover:bg-purple-500 text-white border-purple-500"
        >
          ⚔️ {startButtonText}
        </Button>
        
        <p className="text-purple-400/60 text-xs mt-4 max-w-xs">
          Tip: Use your voice to describe your actions and make choices in the story
        </p>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center px-4">
        <p className="text-purple-400/50 max-w-prose pt-1 text-xs leading-5 font-normal text-pretty">
          Day 8 Challenge: D&D-Style Voice Adventure
        </p>
      </div>
    </div>
  );
};
