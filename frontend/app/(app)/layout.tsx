import { headers } from 'next/headers';
import { getAppConfig } from '@/lib/utils';

// FreshMart Logo Component
function FreshMartLogo() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100" className="h-16 w-auto">
      <g transform="translate(10, 15)">
        <path d="M5,25 L15,25 L25,45 L55,15 L62,22 L25,58 L0,25 Z" fill="#00e676"/>
        <circle cx="20" cy="65" r="6" fill="#00e676"/>
        <circle cx="45" cy="65" r="6" fill="#00e676"/>
        <path d="M45,10 L65,10" stroke="#00e676" strokeWidth="3" strokeLinecap="round"/>
        <path d="M50,5 L60,5" stroke="#00e676" strokeWidth="3" strokeLinecap="round" opacity="0.6"/>
      </g>
      <g transform="translate(90, 20)" fontFamily="Arial, sans-serif">
        <text x="0" y="35" fontSize="36" fontWeight="bold" fill="#00e676" letterSpacing="0.5">FreshMart</text>
        <text x="0" y="60" fontSize="14" fill="#ffffff">Hi! I'm Sam 🛒</text>
      </g>
    </svg>
  );
}

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  const hdrs = await headers();
  const { companyName, logo, logoDark } = await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row justify-between p-4 md:flex">
        <FreshMartLogo />
        <span className="text-foreground font-mono text-xs font-bold tracking-wider uppercase self-center">
          Built with{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents"
            className="underline underline-offset-4"
          >
            LiveKit Agents
          </a>
        </span>
      </header>

      {children}
    </>
  );
}
