import React from 'react';
import { motion } from 'framer-motion';

export default function FeatureGuides({ onOpenGuide }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="mt-16 pt-16 border-t border-white/5 text-center max-w-3xl mx-auto"
    >
      <h2 className="text-3xl font-extrabold text-white mb-6 tracking-tight">
        Tentang <span className="bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent font-black">MediaDownloader</span>
      </h2>
      <div className="space-y-4 text-zinc-400 leading-relaxed text-sm md:text-base">
        <p>
          <strong>MediaDownloader</strong> adalah pengunduh video dan audio premium <strong>gratis tanpa iklan</strong> yang bekerja secara instan di browser Anda tanpa instalasi tambahan. Unduh dari YouTube, TikTok, Instagram, Facebook, X (Twitter), Vimeo, Dailymotion, dan ratusan situs lainnya. Dapatkan video resolusi penuh hingga kualitas terbaik, atau ekstrak audio sebagai file berkualitas tinggi. Semua dikelola melalui satu alat sederhana.
        </p>
        <p>
          Aplikasi ini mendukung berbagai pilihan format audio (MP3, M4A, WAV, FLAC) dan opsi resolusi video tinggi tergantung ketersediaan sumber aslinya. Dilengkapi visualisasi progress download real-time, kecepatan unduh tinggi, dan dukungan penuh di semua perangkat modern termasuk Windows, Mac, Android, dan iOS.
        </p>
      </div>

      <h3 className="text-sm font-bold text-zinc-300 mt-12 mb-6 uppercase tracking-wider text-purple-400/80">
        Jelajahi Panduan & Fitur
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto mb-16">
        <button
          onClick={() => onOpenGuide('how-to')}
          className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-purple-500/30 hover:bg-white/10 transition-all font-semibold text-zinc-300 text-sm text-center flex items-center justify-center gap-2 group cursor-pointer"
        >
          Cara Menggunakan MediaDownloader
        </button>
        <button
          onClick={() => onOpenGuide('audio')}
          className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-purple-500/30 hover:bg-white/10 transition-all font-semibold text-zinc-300 text-sm text-center flex items-center justify-center gap-2 group cursor-pointer"
        >
          Fitur Unduhan Audio
        </button>
        <button
          onClick={() => onOpenGuide('video')}
          className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-purple-500/30 hover:bg-white/10 transition-all font-semibold text-zinc-300 text-sm text-center flex items-center justify-center gap-2 group cursor-pointer"
        >
          Panduan Kualitas Video
        </button>
        <button
          onClick={() => onOpenGuide('platforms')}
          className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-purple-500/30 hover:bg-white/10 transition-all font-semibold text-zinc-300 text-sm text-center flex items-center justify-center gap-2 group cursor-pointer"
        >
          Platform yang Didukung
        </button>
      </div>
    </motion.div>
  );
}
