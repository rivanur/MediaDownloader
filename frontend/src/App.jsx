import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Import Components
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import VideoResult from './components/VideoResult';
import DownloadProgress from './components/DownloadProgress';
import FeatureGuides from './components/FeatureGuides';
import Footer from './components/Footer';

// Import Modals
import HelpModal from './components/Modals/HelpModal';
import GuideModal from './components/Modals/GuideModal';
import LegalModal from './components/Modals/LegalModal';

const API_BASE = "https://mediadownloader-t994.onrender.com/api";

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [videoInfo, setVideoInfo] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dlStats, setDlStats] = useState({ speed: '0 MB/s', eta: '--:--', size: '' });
  const [dlStatus, setDlStatus] = useState('');
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  
  const [showHelp, setShowHelp] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [activeGuideTab, setActiveGuideTab] = useState('how-to'); // 'how-to' | 'audio' | 'video' | 'platforms'
  const [showLegal, setShowLegal] = useState(false);
  const [legalType, setLegalType] = useState('copyright'); // 'copyright' | 'privacy' | 'terms'

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await axios.get(`${API_BASE}/ping`);
        setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
      }
    };
    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const analyzeUrl = async (e) => {
    e?.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setVideoInfo(null);
    setError('');

    try {
      const response = await axios.post(`${API_BASE}/info`, { url: url.trim() }, { timeout: 120000 });
      if (response.data.success) {
        setVideoInfo(response.data.data);
      } else {
        setError(response.data.error || "Gagal menganalisa URL");
      }
    } catch (err) {
      console.error("API Error:", err);
      const msg = err.response?.data?.error || err.message || "Koneksi ke backend gagal.";
      setError(`Backend Error: ${msg}. Pastikan API sudah dijalankan.`);
    } finally {
      setLoading(false);
    }
  };

  const startDownload = async (fmt, type) => {
    try {
      const payload = {
        url: url.trim(),
        format_id: fmt.format_id,
        output_type: type,
        output_ext: fmt.ext,
        title: videoInfo.title,
        thumbnail: videoInfo.thumbnail,
        duration: videoInfo.duration,
        uploader: videoInfo.uploader,
        platform: videoInfo.platform,
        format_label: fmt.label
      };

      const response = await axios.post(`${API_BASE}/start`, payload);
      if (response.data.success) {
        trackProgress(response.data.task_id);
      } else {
        alert("Gagal memulai download: " + response.data.error);
      }
    } catch (err) {
      alert("Terjadi kesalahan saat memulai download.");
    }
  };

  const trackProgress = (taskId) => {
    setDownloading(true);
    setProgress(0);
    setDlStatus('Menyiapkan download...');

    const eventSource = new EventSource(`${API_BASE}/stream/${taskId}`);

    eventSource.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'progress') {
        setProgress(msg.data.progress);
        setDlStats({
          speed: msg.data.speed,
          eta: msg.data.eta,
          size: msg.data.file_size
        });
        setDlStatus(`Mendownload ${msg.data.file_size}...`);
      } else if (msg.type === 'completed') {
        setProgress(100);
        setDlStatus('Hampir selesai...');

        // Trigger browser download
        setTimeout(() => {
          window.location.href = `${API_BASE}/download-file/${taskId}`;
          setDownloading(false);
          eventSource.close();
        }, 1000);
      } else if (msg.type === 'failed') {
        alert("Download gagal: " + msg.data.error);
        setDownloading(false);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setDownloading(false);
    };
  };

  const handleOpenGuide = (tab) => {
    setActiveGuideTab(tab);
    setShowGuide(true);
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Background elements */}
      <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-600/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <Header />

        {/* Search Input Bar */}
        <SearchForm 
          url={url} 
          setUrl={setUrl} 
          loading={loading} 
          onAnalyze={analyzeUrl} 
          error={error} 
        />

        {/* Video Results Content */}
        <VideoResult 
          videoInfo={videoInfo} 
          onDownload={startDownload} 
          formatDuration={formatDuration} 
          API_BASE={API_BASE} 
        />

        {/* Feature Descriptions & Guide Grid */}
        <FeatureGuides onOpenGuide={handleOpenGuide} />

        {/* Footer Navigation */}
        <Footer 
          onOpenHelp={() => setShowHelp(true)} 
          onOpenLegal={(type) => { setLegalType(type); setShowLegal(true); }} 
        />
      </div>

      {/* Download Progress Overlay */}
      <DownloadProgress 
        downloading={downloading} 
        progress={progress} 
        dlStatus={dlStatus} 
        dlStats={dlStats} 
      />

      {/* Help Modal (FAQ only) */}
      <HelpModal 
        isOpen={showHelp} 
        onClose={() => setShowHelp(false)} 
      />

      {/* Guide & Feature Detailed Modal */}
      <GuideModal 
        isOpen={showGuide} 
        activeGuideTab={activeGuideTab} 
        onClose={() => setShowGuide(false)} 
      />

      {/* Legal terms of use Modal */}
      <LegalModal 
        isOpen={showLegal} 
        legalType={legalType} 
        onClose={() => setShowLegal(false)} 
      />
    </div>
  );
}

function formatDuration(seconds) {
  if (!seconds) return "0:00";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default App;
