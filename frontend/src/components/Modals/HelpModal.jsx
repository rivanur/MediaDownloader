import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ShieldQuestion } from 'lucide-react';

export default function HelpModal({ isOpen, onClose }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/85 backdrop-blur-xl z-[100] flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            className="glass-morphism w-full max-w-xl p-6 md:p-8 text-left max-h-[85vh] overflow-y-auto relative border border-white/10"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 md:top-6 md:right-6 text-zinc-400 hover:text-white transition-colors w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center cursor-pointer"
            >
              <X size={18} />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 flex items-center justify-center text-purple-400">
                <ShieldQuestion size={22} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Pusat Bantuan & FAQ</h3>
                <p className="text-xs text-zinc-500">Pertanyaan umum dan solusi seputar MediaDownloader.</p>
              </div>
            </div>

            {/* FAQ Section */}
            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-zinc-900/50 border border-white/5">
                <h5 className="font-bold text-xs text-zinc-200 mb-1">Di mana file hasil unduhan disimpan?</h5>
                <p className="text-xs text-zinc-400">
                  File diunduh secara lokal oleh server terlebih dahulu, kemudian secara otomatis di-stream dan disimpan langsung ke folder <strong className="text-zinc-300">Unduhan (Downloads)</strong> bawaan dari browser web Anda.
                </p>
              </div>
              <div className="p-3.5 rounded-xl bg-zinc-900/50 border border-white/5">
                <h5 className="font-bold text-xs text-zinc-200 mb-1">Mengapa status indikator koneksi sempat berwarna merah?</h5>
                <p className="text-xs text-zinc-400">
                  Hal ini terjadi karena frontend tidak dapat berkomunikasi dengan backend API. Pastikan Anda sudah menjalankan server backend dengan mengetikkan perintah <code className="bg-white/5 px-1 py-0.5 rounded font-mono text-zinc-300">python api/main.py</code> di terminal Anda.
                </p>
              </div>
              <div className="p-3.5 rounded-xl bg-zinc-900/50 border border-white/5">
                <h5 className="font-bold text-xs text-zinc-200 mb-1">Kenapa proses analisa tautan kadang gagal?</h5>
                <p className="text-xs text-zinc-400">
                  Beberapa kemungkinan penyebabnya adalah tautan video bersifat pribadi/privat, dibatasi wilayah geografisnya, atau link tersebut sudah kedaluwarsa. Pastikan tautan dapat diakses secara publik.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
