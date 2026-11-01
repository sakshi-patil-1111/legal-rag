import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';

export default function PageContainer({ children, className = '' }) {
  return (
    <div className="min-h-screen bg-paper ledger-grid text-ink flex flex-col font-sans antialiased overflow-x-hidden">
      <Navbar />
      <main className={`flex-grow pt-[80px] pb-20 max-w-7xl w-full mx-auto px-4 sm:px-6 ${className}`}>
        {children}
      </main>
      <Footer />
    </div>
  );
}
