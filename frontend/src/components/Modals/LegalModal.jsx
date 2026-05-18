import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink } from 'lucide-react';

export default function LegalModal({ isOpen, legalType, onClose }) {
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
            className="glass-morphism w-full max-w-lg p-6 md:p-8 text-left relative border border-white/10"
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
                <ExternalLink size={20} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">
                  {legalType === 'copyright' && 'Copyright'}
                  {legalType === 'privacy' && 'Privacy Policy'}
                  {legalType === 'terms' && 'Terms of Use'}
                </h3>
                <p className="text-xs text-zinc-500">Kebijakan hukum dan ketentuan MediaDownloader.</p>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-4 text-zinc-300 text-sm leading-relaxed max-h-[50vh] overflow-y-auto pr-2">
              {legalType === 'copyright' && (
                <>
                  <p>
                    <strong>MediaDownloader</strong> sangat menghormati hak kekayaan intelektual dan hak cipta pihak ketiga.
                  </p>
                  <p>
                    Layanan ini murni bersifat teknis untuk membantu pengguna memfasilitasi pengunduhan media yang di-hosting secara publik oleh platform pihak ketiga untuk keperluan cadangan pribadi.
                  </p>
                  <p>
                    Kami <strong>tidak menyimpan, menghosting kembali, atau mendistribusikan</strong> media apa pun di server kami. Segala hak cipta tetap sepenuhnya milik pembuat konten asli dan platform penyedia layanan. Pengguna bertanggung jawab penuh atas penggunaan materi yang diunduh.
                  </p>
                </>
              )}

              {legalType === 'privacy' && (
                <>
                  <p>
                    Komitmen kami terhadap privasi Anda sangatlah ketat:
                  </p>
                  <ul className="list-disc pl-5 space-y-2 text-zinc-400">
                    <li>
                      <strong>Tanpa Pelacakan</strong>: Kami tidak menggunakan cookie pelacak komersial pihak ketiga atau melacak aktivitas pencarian Anda.
                    </li>
                    <li>
                      <strong>Penyimpanan Lokal</strong>: Informasi tugas dan riwayat unduhan hanya disimpan secara lokal di dalam database perangkat Anda sendiri.
                    </li>
                    <li>
                      <strong>Pemrosesan Instan</strong>: Semua permintaan analisis URL dikirim langsung ke engine pengolah internal kami untuk memastikan kerahasiaan data Anda tetap terjaga.
                    </li>
                  </ul>
                </>
              )}

              {legalType === 'terms' && (
                <>
                  <p>
                    Dengan mengakses dan menggunakan MediaDownloader, Anda menyetujui ketentuan berikut:
                  </p>
                  <ul className="list-disc pl-5 space-y-2 text-zinc-400">
                    <li>
                      <strong>Penggunaan Pribadi</strong>: Alat ini ditujukan hanya untuk keperluan pengunduhan non-komersial dan penggunaan edukasi/pribadi saja.
                    </li>
                    <li>
                      <strong>Tanggung Jawab Hukum</strong>: Pengguna membebaskan MediaDownloader dari segala tuntutan hukum yang timbul akibat pengunduhan atau distribusi materi yang dilindungi hak cipta tanpa izin.
                    </li>
                    <li>
                      <strong>Kepatuhan Layanan</strong>: Anda setuju untuk selalu mematuhi Ketentuan Layanan (Terms of Service) dari masing-masing situs penyedia konten asal (seperti YouTube, TikTok, dll.).
                    </li>
                  </ul>
                </>
              )}
            </div>

            {/* Footer Button */}
            <div className="mt-6 pt-4 border-t border-white/5 flex justify-end">
              <button
                onClick={onClose}
                className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs transition-colors cursor-pointer"
              >
                Saya Mengerti
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
