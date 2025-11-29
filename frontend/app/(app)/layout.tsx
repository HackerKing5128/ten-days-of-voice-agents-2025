import { headers } from 'next/headers';
import { getAppConfig } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row justify-between p-6 md:flex">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🛒</span>
          <span className="text-orange-300 font-bold text-sm tracking-wide">
            ShopVoice
          </span>
        </div>
        <span className="text-orange-400/70 font-mono text-xs tracking-wider">
          Day 9: E-commerce Agent
        </span>
      </header>

      {children}
    </>
  );
}
