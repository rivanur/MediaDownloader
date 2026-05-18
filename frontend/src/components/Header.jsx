import React from 'react';
import { motion } from 'framer-motion';
import { Download } from 'lucide-react';

export default function Header() {
  return (
    <header className="text-center mb-12">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-center gap-3 mb-4"
      >
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <Download className="text-white w-7 h-7" />
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Media<span className="text-purple-500">Downloader</span>
        </h1>
      </motion.div>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-zinc-400 text-lg"
      >
        Download video & audio dari berbagai platform populer dengan kualitas terbaik.
      </motion.p>
    </header>
  );
}
