import React from 'react';
import { motion } from 'framer-motion';
import { Play, Music, Video, Clock, User, ChevronRight } from 'lucide-react';

export default function VideoResult({ videoInfo, onDownload, formatDuration, API_BASE }) {
  if (!videoInfo) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-12"
    >
      {/* Thumbnail Card */}
      <div className="md:col-span-5">
        <div className="glass-morphism overflow-hidden relative group">
          <img src={videoInfo.thumbnail} alt="Thumbnail" className="w-full aspect-video object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60" />
          <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
            <div className="bg-black/60 backdrop-blur-md px-2 py-1 rounded-lg text-xs font-medium flex items-center gap-1">
              <Clock size={12} />
              {formatDuration(videoInfo.duration)}
            </div>
            {videoInfo.preview_url && (
              <a 
                href={API_BASE + videoInfo.preview_url} 
                target="_blank" 
                rel="noreferrer" 
                className="w-10 h-10 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center hover:bg-white/20 transition-all"
              >
                <Play size={18} fill="white" />
              </a>
            )}
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center border border-white/5">
            <User size={20} className="text-zinc-400" />
          </div>
          <div>
            <h4 className="font-semibold text-sm line-clamp-1">{videoInfo.uploader}</h4>
            <p className="text-xs text-zinc-500 uppercase tracking-wider">{videoInfo.platform}</p>
          </div>
        </div>
      </div>

      {/* Formats Card */}
      <div className="md:col-span-7 flex flex-col gap-6">
        <div>
          <h2 className="text-2xl font-bold mb-2 line-clamp-2">{videoInfo.title}</h2>
          <div className="h-1 w-20 bg-purple-600 rounded-full" />
        </div>

        <div className="space-y-6">
          {/* Video Formats */}
          <section>
            <div className="flex items-center gap-2 mb-3 text-zinc-400 text-sm font-semibold uppercase tracking-widest">
              <Play size={14} />
              <span>Video Quality</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {videoInfo.video_formats?.slice(0, 6).map((fmt, i) => (
                <button
                  key={i}
                  onClick={() => onDownload(fmt, 'video')}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 hover:border-purple-500/30 hover:bg-white/10 transition-all text-left group cursor-pointer"
                >
                  <div>
                    <p className="font-bold text-sm">{fmt.label}</p>
                    <p className="text-[10px] text-zinc-500">{fmt.filesize_approx}</p>
                  </div>
                  <ChevronRight size={16} className="text-zinc-600 group-hover:text-purple-400 transition-colors" />
                </button>
              ))}
            </div>
          </section>

          {/* Audio Formats */}
          <section>
            <div className="flex items-center gap-2 mb-3 text-zinc-400 text-sm font-semibold uppercase tracking-widest">
              <Music size={14} />
              <span>Audio Only</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {videoInfo.audio_formats?.map((fmt, i) => (
                <button
                  key={i}
                  onClick={() => onDownload(fmt, 'audio')}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 hover:border-pink-500/30 hover:bg-white/10 transition-all text-left group cursor-pointer"
                >
                  <div>
                    <p className="font-bold text-sm">{fmt.label}</p>
                    <p className="text-[10px] text-zinc-500">{fmt.filesize_approx}</p>
                  </div>
                  <Music size={16} className="text-zinc-600 group-hover:text-pink-400 transition-colors" />
                </button>
              ))}
            </div>
          </section>
        </div>
      </div>
    </motion.div>
  );
}
