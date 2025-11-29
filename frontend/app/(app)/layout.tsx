interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row justify-between p-6 md:flex">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🐉</span>
          <span className="text-purple-300 font-bold text-sm tracking-wide">
            Voice Game Master
          </span>
        </div>
        <span className="text-purple-400/70 font-mono text-xs tracking-wider">
          Day 8: D&D-Style Adventure
        </span>
      </header>

      {children}
    </>
  );
}
