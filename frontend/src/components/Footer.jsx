import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function Footer({ onOpenHelp, onOpenLegal }) {
  return (
    <footer className="mt-20 pt-8 border-t border-white/5 flex flex-col items-center gap-4 text-zinc-500 text-sm">
      {/* Row 1: Main Tautan Utama (Centered) */}
      <div className="flex flex-wrap items-center justify-center gap-3 md:gap-4 text-xs">
        <button
          onClick={onOpenHelp}
          className="hover:text-white transition-colors text-zinc-500 hover:underline flex items-center gap-1 cursor-pointer"
        >
          <HelpCircle size={14} />
          Bantuan
        </button>
        <span className="text-zinc-700">|</span>
        <button
          onClick={() => onOpenLegal('copyright')}
          className="hover:text-white transition-colors text-zinc-500 hover:underline cursor-pointer"
        >
          Copyright
        </button>
        <span className="text-zinc-700">|</span>
        <button
          onClick={() => onOpenLegal('privacy')}
          className="hover:text-white transition-colors text-zinc-500 hover:underline cursor-pointer"
        >
          Privacy Policy
        </button>
        <span className="text-zinc-700">|</span>
        <button
          onClick={() => onOpenLegal('terms')}
          className="hover:text-white transition-colors text-zinc-500 hover:underline cursor-pointer"
        >
          Terms of Use
        </button>
      </div>

      {/* Row 2: Copyright */}
      <div className="text-zinc-600 text-xs font-medium tracking-wide select-none">
        © {new Date().getFullYear()} MediaDownloader. All rights reserved.
      </div>
    </footer>
  );
}
