import { headers } from 'next/headers';
import { getAppConfig } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  return (
    // NO HEADER HERE. Just a dark background wrapper.
    <div className="min-h-screen bg-zinc-950">{children}</div>
  );
}
