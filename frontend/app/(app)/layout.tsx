import { headers } from 'next/headers';
import Image from 'next/image';
import { getAppConfig } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  const hdrs = await headers();
  const { companyName } = await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row items-center justify-between p-4 md:flex">
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="/"
          className="scale-100 transition-transform duration-300 hover:scale-105"
        >
          <Image
            src="/day10-jax.svg"
            alt={`${companyName} Logo`}
            width={200}
            height={60}
            className="h-10 w-auto"
          />
        </a>
        <div className="flex items-center gap-4">
          <span className="font-mono text-xs tracking-wider text-gray-500 uppercase">
            Powered by{' '}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://murf.ai"
              className="text-lime-400 transition-colors hover:text-lime-300"
            >
              Murf AI
            </a>{' '}
            ×{' '}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://livekit.io"
              className="text-cyan-400 transition-colors hover:text-cyan-300"
            >
              LiveKit
            </a>
          </span>
        </div>
      </header>

      {children}
    </>
  );
}
