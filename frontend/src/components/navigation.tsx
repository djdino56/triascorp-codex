'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
  { href: '/', label: 'Dashboard' },
  { href: '/strategies', label: 'Strategies' },
  { href: '/reports', label: 'Reports' }
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link href="/">
          <span style={{ fontWeight: 600 }}>Deribit Backtester</span>
        </Link>
        <nav className="nav-links">
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  color: isActive ? '#38bdf8' : 'rgba(226, 232, 240, 0.8)',
                  fontWeight: isActive ? 600 : 400
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
        <span className="badge">
          <span role="img" aria-label="rocket">
            🚀
          </span>
          Alpha
        </span>
      </div>
    </header>
  );
}
