import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Zomato AI Restaurant Recommender',
  description: 'Helping you find the best places to eat in Bangalore city.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
