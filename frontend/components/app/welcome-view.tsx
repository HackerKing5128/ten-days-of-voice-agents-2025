import { Button } from '@/components/livekit/button';

// Shopping Cart Icon
function ShoppingCartIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-emerald-500 mb-4 size-16"
    >
      <path
        d="M9 22C9.55228 22 10 21.5523 10 21C10 20.4477 9.55228 20 9 20C8.44772 20 8 20.4477 8 21C8 21.5523 8.44772 22 9 22Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M20 22C20.5523 22 21 21.5523 21 21C21 20.4477 20.5523 20 20 20C19.4477 20 19 20.4477 19 21C19 21.5523 19.4477 22 20 22Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M1 1H5L7.68 14.39C7.77144 14.8504 8.02191 15.264 8.38755 15.5583C8.75318 15.8526 9.2107 16.009 9.68 16H19.4C19.8693 16.009 20.3268 15.8526 20.6925 15.5583C21.0581 15.264 21.3086 14.8504 21.4 14.39L23 6H6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// Leaf/Fresh Icon
function FreshIcon() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-emerald-400 size-6"
    >
      <path
        d="M12 2C6.5 2 2 6.5 2 12C2 17.5 6.5 22 12 22C17.5 22 22 17.5 22 12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M12 2C12 2 16 6 16 12C16 18 12 22 12 22"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M22 2L12 12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
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
      <section className="bg-background flex flex-col items-center justify-center text-center">
        {/* FreshMart Logo */}
        <div className="flex items-center gap-2 mb-6">
          <FreshIcon />
          <span className="text-2xl font-bold text-emerald-500">FreshMart</span>
        </div>

        <ShoppingCartIcon />

        <h1 className="text-foreground text-xl font-bold mb-2">
          Hi! I'm Sam 👋
        </h1>

        <p className="text-muted-foreground max-w-prose pt-1 leading-6 font-medium">
          Your personal shopping assistant. I can help you find groceries,
          build recipes, and place orders!
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-64 font-mono bg-emerald-600 hover:bg-emerald-700"
        >
          🛒 Start Shopping
        </Button>

        <p className="text-muted-foreground text-xs mt-4 max-w-xs">
          Try saying: "I need ingredients for a peanut butter sandwich"
        </p>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Powered by{' '}
          <span className="text-emerald-500 font-semibold">Murf Falcon TTS</span>
          {' '}• The fastest text-to-speech API
        </p>
      </div>
    </div>
  );
};
