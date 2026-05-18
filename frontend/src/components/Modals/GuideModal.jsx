import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, BookOpen, Music, Video, Sparkles } from 'lucide-react';

export default function GuideModal({ isOpen, activeGuideTab, onClose }) {
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
            className="glass-morphism w-full max-w-2xl p-6 md:p-8 text-left max-h-[85vh] overflow-y-auto relative border border-white/10"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 md:top-6 md:right-6 text-zinc-400 hover:text-white transition-colors w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center cursor-pointer"
            >
              <X size={18} />
            </button>

            {/* Dynamic Header */}
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 flex items-center justify-center text-purple-400">
                {activeGuideTab === 'how-to' && <BookOpen size={22} />}
                {activeGuideTab === 'audio' && <Music size={22} />}
                {activeGuideTab === 'video' && <Video size={22} />}
                {activeGuideTab === 'platforms' && <Sparkles size={22} />}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">
                  {activeGuideTab === 'how-to' && "Panduan Penggunaan"}
                  {activeGuideTab === 'audio' && "Fitur Unduhan Audio"}
                  {activeGuideTab === 'video' && "Panduan Kualitas Video"}
                  {activeGuideTab === 'platforms' && "Platform yang Didukung"}
                </h3>
                <p className="text-xs text-zinc-500">
                  {activeGuideTab === 'how-to' && "Langkah demi langkah mengunduh video dan audio secara instan."}
                  {activeGuideTab === 'audio' && "Informasi format dan kualitas ekstraksi audio premium."}
                  {activeGuideTab === 'video' && "Penjelasan detail resolusi tinggi, ukuran file, dan penggabungan sistem."}
                  {activeGuideTab === 'platforms' && "Daftar situs web populer yang kompatibel dengan pengunduh."}
                </p>
              </div>
            </div>

            <div className="space-y-6">
              {/* 1. How to Use Section */}
              {activeGuideTab === 'how-to' && (
                <motion.section
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <span className="text-2xl font-black text-purple-500/40 block mb-1">01</span>
                      <h5 className="font-bold text-sm text-zinc-200 mb-1">Salin Tautan</h5>
                      <p className="text-xs text-zinc-400">Copy URL video/audio dari platform kesukaan Anda.</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <span className="text-2xl font-black text-purple-500/40 block mb-1">02</span>
                      <h5 className="font-bold text-sm text-zinc-200 mb-1">Klik Analisa</h5>
                      <p className="text-xs text-zinc-400">Tempel URL ke kolom pencarian lalu klik tombol Analisa.</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <span className="text-2xl font-black text-purple-500/40 block mb-1">03</span>
                      <h5 className="font-bold text-sm text-zinc-200 mb-1">Unduh File</h5>
                      <p className="text-xs text-zinc-400">Pilih kualitas, tunggu proses, dan file akan terunduh otomatis.</p>
                    </div>
                  </div>
                </motion.section>
              )}

              {/* 2. Audio Features Section */}
              {activeGuideTab === 'audio' && (
                <motion.section
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-4"
                >
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    MediaDownloader dapat mengkonversi video dari platform favorit Anda secara instan menjadi format audio berkualitas tinggi (Lossless conversion). Sangat cocok untuk mendengarkan lagu, podcast, atau sound effect secara offline.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h5 className="font-bold text-sm text-purple-400 mb-1">MP3 (Kualitas Terbaik)</h5>
                      <p className="text-xs text-zinc-400">Audio diekstraksi langsung dengan bitrate tinggi (192kbps - 320kbps) untuk kepuasan musik maksimal.</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h5 className="font-bold text-sm text-purple-400 mb-1">M4A & Kompatibilitas</h5>
                      <p className="text-xs text-zinc-400">Format M4A didukung secara native oleh perangkat iOS (iPhone/iPad) dan MacOS untuk performa hemat baterai.</p>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-purple-600/10 border border-purple-500/20 text-xs text-purple-300">
                    <strong>💡 Kecepatan Konversi:</strong> Proses ekstraksi audio dilakukan di sisi server super cepat hanya dalam hitungan detik sebelum file dikirimkan ke browser Anda.
                  </div>
                </motion.section>
              )}

              {/* 3. Video Format Guide Section */}
              {activeGuideTab === 'video' && (
                <motion.section
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-4"
                >
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Kami berkomitmen menghadirkan kualitas terbaik yang tersedia di server aslinya. Resolusi yang ditampilkan adalah representasi jujur dari apa yang tersedia dari platform tersebut.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h5 className="font-bold text-sm text-purple-400 mb-1">Penggabungan Video + Audio</h5>
                      <p className="text-xs text-zinc-400">Pada resolusi tinggi (1080p ke atas), platform biasanya memisahkan file video dan audio. Backend kami otomatis menggabungkannya secara real-time menjadi satu MP4 yang utuh.</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h5 className="font-bold text-sm text-purple-400 mb-1">Keterbatasan Platform</h5>
                      <p className="text-xs text-zinc-400">Beberapa platform seperti Instagram atau Twitter memiliki batas kualitas maksimal video (biasanya 640p - 720p), sedangkan YouTube mendukung hingga 4K.</p>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-purple-600/10 border border-purple-500/20 text-xs text-purple-300">
                    <strong>💡 Info Ukuran File:</strong> Sebelum mengunduh, sistem akan mencoba menaksir estimasi ukuran file agar Anda dapat menyesuaikan ruang penyimpanan memori perangkat Anda.
                  </div>
                </motion.section>
              )}

              {/* 4. Supported Platforms Section */}
              {activeGuideTab === 'platforms' && (
                <motion.section
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <p className="text-xs text-zinc-400 mb-4">
                    Didukung penuh oleh engine tangguh <code className="bg-white/5 px-1.5 py-0.5 rounded font-mono text-zinc-300">yt-dlp</code>, Anda bisa mengunduh dari 1000+ platform populer termasuk:
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {['YouTube', 'TikTok', 'Instagram', 'Facebook', 'Twitter / X', 'SoundCloud', 'Twitch', 'Vimeo', 'DailyMotion'].map((p, idx) => (
                      <span key={idx} className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/5 text-xs text-zinc-300 font-medium">
                        {p}
                      </span>
                    ))}
                    <span className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-xs text-purple-300 font-medium">
                      dan 1000+ lainnya...
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-500 leading-relaxed">
                    * Catatan: Tautan harus bersifat publik dan tidak memerlukan login untuk memutar konten. Beberapa video dengan batasan umur atau wilayah geografis tertentu mungkin gagal diunduh demi mematuhi kebijakan keamanan platform bersangkutan.
                  </p>
                </motion.section>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
