import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, CheckCircle2 } from 'lucide-react';

export default function DownloadProgress({ downloading, progress, dlStatus, dlStats }) {
  return (
    <AnimatePresence>
      {downloading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-xl z-[100] flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            className="glass-morphism w-full max-w-md p-8 text-center"
          >
            <div className="w-16 h-16 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
              <Loader2 className="text-purple-500 animate-spin" size={32} />
              {progress === 100 && <CheckCircle2 className="text-green-500 absolute inset-0 m-auto" size={32} />}
            </div>

            <h3 className="text-2xl font-bold mb-1">{progress === 100 ? 'Selesai!' : 'Mendownload...'}</h3>
            <p className="text-zinc-400 text-sm mb-8">{dlStatus}</p>

            <div className="relative h-3 w-full bg-white/5 rounded-full overflow-hidden mb-6">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-600 to-pink-600 shadow-[0_0_20px_rgba(139,92,246,0.5)]"
              />
            </div>

            <div className="grid grid-cols-3 gap-4 text-xs font-mono text-zinc-500 uppercase tracking-widest">
              <div>
                <p className="mb-1">Progress</p>
                <p className="text-white text-base font-bold">{progress}%</p>
              </div>
              <div>
                <p className="mb-1">Speed</p>
                <p className="text-white text-base font-bold">{dlStats.speed}</p>
              </div>
              <div>
                <p className="mb-1">ETA</p>
                <p className="text-white text-base font-bold">{dlStats.eta}</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
