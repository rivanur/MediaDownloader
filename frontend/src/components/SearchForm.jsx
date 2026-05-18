import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link as LinkIcon, Loader2, Search, AlertCircle } from 'lucide-react';

export default function SearchForm({ url, setUrl, loading, onAnalyze, error }) {
  return (
    <>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="glass-morphism p-2 md:p-3 mb-12 flex flex-col md:flex-row gap-3"
      >
        <form onSubmit={onAnalyze} className="flex-1 flex flex-col md:flex-row gap-3 w-full">
          <div className="flex-1 relative w-full">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500">
              <LinkIcon size={20} />
            </div>
            <input
              type="text"
              placeholder="Tempel tautan video di sini..."
              className="w-full bg-black/20 border border-white/5 rounded-xl py-4 pl-12 pr-4 outline-none focus:border-purple-500/50 transition-all text-white placeholder:text-zinc-600"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !url}
            className="glow-button px-8 py-4 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group cursor-pointer"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Search size={20} className="group-hover:scale-110 transition-transform" />
            )}
            {loading ? 'Menganalisa...' : 'Analisa'}
          </button>
        </form>
      </motion.div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8 bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex items-center gap-3 text-red-400"
          >
            <AlertCircle size={20} />
            <p>{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
