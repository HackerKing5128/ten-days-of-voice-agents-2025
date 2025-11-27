import { Button } from '@/components/livekit/button';

// Phone icon for incoming call
function PhoneIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path
        fillRule="evenodd"
        d="M1.5 4.5a3 3 0 013-3h1.372c.86 0 1.61.586 1.819 1.42l1.105 4.423a1.875 1.875 0 01-.694 1.955l-1.293.97c-.135.101-.164.249-.126.352a11.285 11.285 0 006.697 6.697c.103.038.25.009.352-.126l.97-1.293a1.875 1.875 0 011.955-.694l4.423 1.105c.834.209 1.42.959 1.42 1.82V19.5a3 3 0 01-3 3h-2.25C8.552 22.5 1.5 15.448 1.5 6.75V4.5z"
        clipRule="evenodd"
      />
    </svg>
  );
}

// Shield icon for security
function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path
        fillRule="evenodd"
        d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 00.374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 00-.722-.516 11.209 11.209 0 01-7.877-3.08z"
        clipRule="evenodd"
      />
    </svg>
  );
}

// Bank building icon
function BankIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M11.584 2.376a.75.75 0 01.832 0l9 6a.75.75 0 01-.832 1.248L12 3.901 3.416 9.624a.75.75 0 01-.832-1.248l9-6z" />
      <path
        fillRule="evenodd"
        d="M20.25 10.332v9.918H21a.75.75 0 010 1.5H3a.75.75 0 010-1.5h.75v-9.918a.75.75 0 01.634-.74A49.109 49.109 0 0112 9c2.59 0 5.134.202 7.616.592a.75.75 0 01.634.74zm-7.5 2.418a.75.75 0 00-1.5 0v6.75a.75.75 0 001.5 0v-6.75zm3-.75a.75.75 0 01.75.75v6.75a.75.75 0 01-1.5 0v-6.75a.75.75 0 01.75-.75zM9 12.75a.75.75 0 00-1.5 0v6.75a.75.75 0 001.5 0v-6.75z"
        clipRule="evenodd"
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
    <div ref={ref} className="w-full max-w-md mx-auto">
      <section className="bg-background flex flex-col items-center justify-center text-center">
        {/* Incoming Call Header */}
        <div className="flex items-center gap-2 mb-6">
          <div className="relative">
            <PhoneIcon className="w-5 h-5 text-emerald-500 animate-pulse" />
          </div>
          <span className="text-emerald-500 font-semibold tracking-wide text-sm uppercase">
            Incoming Call
          </span>
        </div>

        {/* Call Card */}
        <div className="relative mb-8">
          {/* Pulsing ring animation */}
          <div className="absolute inset-0 rounded-3xl bg-blue-500/20 animate-ping" style={{ animationDuration: '2s' }} />
          <div className="absolute inset-0 rounded-3xl bg-blue-500/10 animate-pulse" />
          
          {/* Card content */}
          <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-3xl p-8 shadow-2xl">
            {/* Bank logo area */}
            <div className="flex items-center justify-center mb-4">
              <div className="bg-blue-600 p-3 rounded-2xl">
                <BankIcon className="w-10 h-10 text-white" />
              </div>
            </div>
            
            {/* Bank name */}
            <h1 className="text-2xl font-bold text-white mb-1">
              SecureBank
            </h1>
            <p className="text-blue-400 font-medium mb-4">
              Fraud Protection Department
            </p>
            
            {/* Divider */}
            <div className="w-16 h-0.5 bg-gradient-to-r from-transparent via-slate-600 to-transparent mx-auto mb-4" />
            
            {/* Call reason */}
            <p className="text-slate-400 text-sm">
              Calling about suspicious activity on your account
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-8">
          {/* Decline button (optional - just visual) */}
          <button
            className="w-16 h-16 rounded-full bg-red-500/20 border-2 border-red-500 flex items-center justify-center hover:bg-red-500/30 transition-all group"
            onClick={() => {}}
            title="Decline"
          >
            <PhoneIcon className="w-6 h-6 text-red-500 rotate-[135deg] group-hover:scale-110 transition-transform" />
          </button>
          
          {/* Answer button */}
          <button
            className="w-16 h-16 rounded-full bg-emerald-500 flex items-center justify-center hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/30 group animate-pulse"
            onClick={onStartCall}
            title="Answer Call"
            style={{ animationDuration: '2s' }}
          >
            <PhoneIcon className="w-6 h-6 text-white group-hover:scale-110 transition-transform" />
          </button>
        </div>

        {/* Alternative text button */}
        <Button 
          variant="primary" 
          size="lg" 
          onClick={onStartCall} 
          className="w-64 font-mono bg-emerald-600 hover:bg-emerald-500 border-emerald-500"
        >
          {startButtonText || "Answer Call"}
        </Button>
      </section>

      {/* Security Disclaimer */}
      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center px-4">
        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-2">
          <ShieldIcon className="w-4 h-4 text-amber-500 flex-shrink-0" />
          <p className="text-amber-500/90 text-xs leading-5 font-medium">
            SecureBank will <strong>NEVER</strong> ask for your PIN, password, or full card number
          </p>
        </div>
      </div>
    </div>
  );
};
