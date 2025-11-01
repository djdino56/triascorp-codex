import type { Metadata } from 'next';
import './globals.css';
import { Navigation } from '@/components/navigation';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Deribit Backtester Dashboard',
  description: 'Visual interface for configuring and reviewing Deribit spot backtests.'
};

export default function RootLayout({
  children
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <main>
          <div className="container">{children}</div>
        </main>
        <footer>Data and backtesting powered by the Python backend.</footer>
      </body>
    </html>
  );
}
