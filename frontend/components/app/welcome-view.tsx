import { Button } from '@/components/livekit/button';

function ShopIcon() {
  return (
    <div className="mb-6 relative">
      <div className="text-7xl animate-pulse">🛒</div>
      <div className="absolute inset-0 bg-orange-500/20 blur-3xl rounded-full" />
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
        <ShopIcon />

        <h1 className="text-2xl md:text-3xl font-bold text-orange-100 mb-2">
          ShopVoice
        </h1>

        <p className="text-orange-300 max-w-md pt-1 leading-6 text-sm md:text-base">
          Meet Ava, your voice shopping assistant. Browse products,
          get recommendations, and place orders—all by voice!
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 font-bold bg-orange-600 hover:bg-orange-500 text-white border-orange-500"
        >
          🛍️ {startButtonText}
        </Button>

        <p className="text-orange-400/60 text-xs mt-4 max-w-xs">
          Tip: Try "Show me electronics" or "I'm looking for a jacket"
        </p>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center px-4">
        <p className="text-orange-400/50 max-w-prose pt-1 text-xs leading-5 font-normal text-pretty">
          Day 9 Challenge: E-commerce Voice Agent (ACP-Inspired)
        </p>
      </div>
    </div>
  );
};
