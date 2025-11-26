import { Button } from '@/components/livekit/button';

function ZoyaAvatar() {
  return (
    <div className="zoya-pulse relative mb-6 flex items-center justify-center rounded-full">
      {/* Outer glow ring */}
      <div className="absolute inset-0 -m-2 rounded-full bg-primary/10 blur-md" />
      
      {/* Avatar container */}
      <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-linear-to-br from-primary to-primary/80 shadow-lg shadow-primary/30">
        {/* Z letter for Zoya */}
        <svg
          width="40"
          height="40"
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-white"
        >
          <path
            d="M8 10H32L12 30H32"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        </svg>
      </div>
    </div>
  );
}

function RazorpayBadge() {
  return (
    <div className="flex items-center gap-2 opacity-60 transition-opacity hover:opacity-100">
      <svg width="16" height="16" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="40" height="40" rx="8" fill="currentColor" className="text-primary"/>
        <path d="M14 14H34L18 34H34" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      </svg>
      <span className="text-xs font-medium">Powered by Razorpay</span>
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
      <section className="bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center text-center px-6">
        <ZoyaAvatar />

        <h1 className="text-foreground text-2xl font-bold tracking-tight mb-2">
          Hi! I'm Zoya
        </h1>
        
        <p className="text-foreground/80 max-w-md text-base leading-relaxed font-medium mb-1">
          Your AI Sales Assistant from Razorpay
        </p>
        
        <p className="text-muted-foreground max-w-sm text-sm leading-relaxed mb-8">
          Ask me about payments, pricing, or how Razorpay can help your business grow
        </p>

        <Button 
          variant="primary" 
          size="lg" 
          onClick={onStartCall} 
          className="btn-razorpay w-64 py-4 text-base font-semibold tracking-wide"
        >
          {startButtonText}
        </Button>
        
        <p className="text-muted-foreground mt-4 text-xs">
          No account needed • Free consultation
        </p>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <RazorpayBadge />
      </div>
    </div>
  );
};
