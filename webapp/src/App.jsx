import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const emotions = ['NEUTRAL', 'ANGER', 'CONTEMPT', 'DISGUST', 'FEAR', 'HAPPINESS', 'SADNESS', 'SURPRISE'];
const allAUs = [
  { id: 'AU1', label: 'AU1' },
  { id: 'AU2', label: 'AU2' },
  { id: 'AU4', label: 'AU4' },
  { id: 'AU5', label: 'AU5' },
  { id: 'AU6', label: 'AU6' },
  { id: 'AU7', label: 'AU7' },
  { id: 'AU9', label: 'AU9' },
  { id: 'AU10', label: 'AU10' },
  { id: 'AU17', label: 'AU17' },
];

const ConnectionInstructions = () => (
  <div className="connection-instructions" style={{ textAlign: 'left' }}>
    <h2 style={{ color: 'var(--accent-blue)', marginBottom: '16px', marginTop: 0 }}>UNREAL ENGINE CONNECTION ARCHITECTURE</h2>

    <div className="instruction-step">
      <h3>Step 1: Launch the Backend Broker (FastAPI)</h3>
      <ol>
        <li>Open a terminal (PowerShell/Command Prompt) and navigate to the project directory:</li>
        <pre><code>cd "C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend"</code></pre>
        <li>Start the FastAPI server using Uvicorn:</li>
        <pre><code>uvicorn main:app --port 8123</code></pre>
      </ol>
      <div className="note">*Note: This terminal must remain open. You should see it state that it is listening for Unreal Engine connections on 127.0.0.1:8890.*</div>
    </div>

    <div className="instruction-step">
      <h3>Step 2: Connect Unreal Engine</h3>
      <ol>
        <li>Launch <strong>Unreal Engine 5</strong> and open the <code>Metahuman.uproject</code> project.</li>
        <li>Open the foundational Level Sequence and Map (ensure you are loaded into <code>final_level.umap</code>).</li>
        <li>Open the <strong>Output Log</strong> panel inside Unreal Engine. At the bottom, change the command bar from <code>Cmd</code> to <code>Python</code>.</li>
        <li>Run the TCP connection script. You can execute this by typing:</li>
        <pre><code>{`import sys
import importlib
# Append the backend directory so Unreal can find the scripts
sys.path.append(r"C:\\Users\\Amirhosein\\Documents\\Unreal Projects\\Metahuman\\backend")

import ue_mrp_client
importlib.reload(ue_mrp_client)

import mrq_batch_dataset
importlib.reload(mrq_batch_dataset)

server = ue_mrp_client.UEMRQServer()
server.connect()`}</code></pre>
      </ol>
      <div className="note">*You should see a success log in Unreal and the FastAPI terminal stating "Unreal Engine connected!".*</div>
    </div>

    <div className="instruction-step">
      <h3>Step 3: Launch the Frontend Web App (React)</h3>
      <ol>
        <li>Open a <em>new</em> terminal and navigate to the web application directory:</li>
        <pre><code>cd "C:\\Users\\Amirhosein\\Documents\\Unreal Projects\\Metahuman\\webapp"</code></pre>
        <li>Start the Vite development server:</li>
        <pre><code>npm run dev</code></pre>
        <li>Open your browser and navigate to the local URL provided (usually <code>http://localhost:5173</code>).</li>
      </ol>
    </div>
  </div>
);

function App() {
  const getNeutralUrl = (cache) => {
    if (!cache || cache.length === 0) return "";
    const neutralEntry = cache.find(entry => entry.emotions.length === 0 || entry.emotions.includes("NEUTRAL")) || cache[0];
    return neutralEntry ? `/dataset/${neutralEntry.image}` : "";
  };

  const [activeTab, setActiveTab] = useState('FLASHCARDS');
  const [selectedEmotions, setSelectedEmotions] = useState([]);
  const [selectedAUs, setSelectedAUs] = useState([]);
  const [displayMode, setDisplayMode] = useState('Comparison'); // 'Comparison', 'Static', 'Timed'
  const [flashDuration, setFlashDuration] = useState(300); // ms exposure duration
  const [isFlashing, setIsFlashing] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [sliderValue, setSliderValue] = useState(50);
  const flashTimeoutRef = useRef(null);
  const isFlashingRef = useRef(false);

  // Settings Configuration State
  const [intensityMin, setIntensityMin] = useState(4);
  const [intensityMax, setIntensityMax] = useState(7);
  const [speed, setSpeed] = useState(300);
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [theme, setTheme] = useState('Dark');

  // Lighting Settings for Unreal
  const [lightYaw, setLightYaw] = useState(45);
  const [lightPitch, setLightPitch] = useState(45);

  // Batch Generation State
  const [batchSize, setBatchSize] = useState("50");
  const [batchIntensityMin, setBatchIntensityMin] = useState(1);
  const [batchIntensityMax, setBatchIntensityMax] = useState(10);
  const [batchQuality, setBatchQuality] = useState("720p");
  const [emotionWeights, setEmotionWeights] = useState({
    ANGER: 10,
    CONTEMPT: 10,
    DISGUST: 10,
    FEAR: 10,
    HAPPINESS: 10,
    SADNESS: 10,
    SURPRISE: 10
  });
  const [isBatching, setIsBatching] = useState(false);
  const [isDeckCompleted, setIsDeckCompleted] = useState(false);
  const [isRangeEmpty, setIsRangeEmpty] = useState(false);
  const [poolSize, setPoolSize] = useState(0);

  const [viewingImage, setViewingImage] = useState('EXPRESSION');
  const [isLoading, setIsLoading] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [activeSettingsTab, setActiveSettingsTab] = useState('Flashcards');
  const [zoomMain, setZoomMain] = useState(2.2);
  const [zoomGuide, setZoomGuide] = useState(2.2);
  const [batchProgress, setBatchProgress] = useState(null);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [autoFlashEnabled, setAutoFlashEnabled] = useState(true);
  const [autoFlashDelay, setAutoFlashDelay] = useState(1.0);
  const [drawnIndices, setDrawnIndices] = useState([]);

  const [currentFlashcard, setCurrentFlashcard] = useState({
    imgExpression: "",
    imgNeutral: "",
    correctEmotions: ["NEUTRAL"],
    correctAUs: []
  });

  const [datasetCache, setDatasetCache] = useState([]);
  const [globalNeutral, setGlobalNeutral] = useState("");

  const [deck, setDeck] = useState([]);
  const [reviewedCount, setReviewedCount] = useState(1);

  const handleWheel = (e, setZoom) => {
    if (e.deltaY < 0) {
      setZoom(z => Math.min(5.0, z + 0.15));
    } else if (e.deltaY > 0) {
      setZoom(z => Math.max(1.0, z - 0.15));
    }
  };

  const shuffleDeck = (size) => {
    let arr = Array.from({ length: size }, (_, i) => i);
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  };

  // Progress Polling Hook
  useEffect(() => {
    let interval;
    if (isBatching) {
      interval = setInterval(() => {
        fetch("http://localhost:8123/api/batch_progress")
          .then(res => res.json())
          .then(data => {
            if (data.status === "generating") setBatchProgress(data);
          }).catch(() => { });
      }, 500);
    } else {
      setBatchProgress(null);
    }
    return () => clearInterval(interval);
  }, [isBatching]);

  // Apply Theme globally
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme.toLowerCase());
  }, [theme]);

  const reshuffleDeckWithFilters = (customCache = null) => {
    const cache = customCache || datasetCache;
    if (cache.length === 0) return;

    const filteredIndices = cache
      .map((entry, index) => ({ entry, index }))
      .filter(({ entry }) => {
        const isNeutral = entry.emotions.length === 0 || entry.emotions.includes("NEUTRAL");
        if (isNeutral) return false; // Strictly exclude neutral entries from active test deck
        const intVal = entry.intensity * 10;
        return intVal >= (intensityMin - 0.05) && intVal <= (intensityMax + 0.05);
      })
      .map(({ index }) => index);

    if (filteredIndices.length === 0) {
      setPoolSize(0);
      setDeck([]);
      setDrawnIndices([]);
      setReviewedCount(0);
      setIsRangeEmpty(true);
      setIsDeckCompleted(false);
      setHasSubmitted(false);

      setCurrentFlashcard({
        imgNeutral: getNeutralUrl(cache),
        imgExpression: "",
        correctEmotions: ["NEUTRAL"],
        correctAUs: [],
        dbIndex: undefined
      });
    } else {
      setPoolSize(filteredIndices.length);
      setIsRangeEmpty(false);
      let arr = [...filteredIndices];
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      const firstIndex = arr.pop();
      setDeck(arr);
      setDrawnIndices([]);
      setReviewedCount(1);
      setIsDeckCompleted(false);
      setHasSubmitted(false);
      setViewingImage('NEUTRAL');
      setSliderValue(50);

      const firstEntry = cache[firstIndex];
      setCurrentFlashcard({
        imgNeutral: getNeutralUrl(cache),
        imgExpression: `/dataset/${firstEntry.image}`,
        correctEmotions: firstEntry.emotions.length ? firstEntry.emotions : ["NEUTRAL"],
        correctAUs: firstEntry.controls_applied ? Object.keys(firstEntry.controls_applied) : [],
        dbIndex: firstIndex
      });
    }
  };

  const loadDataset = () => {
    // Append timestamp cache-buster to completely bypass browser disk caching
    fetch('/dataset/database.json?_=' + new Date().getTime())
      .then(res => res.json())
      .then(data => {
        if (!data || data.length === 0) return;
        setDatasetCache(data);
        
        // Find foundational Neutral state for the slider baseline
        const neutralEntry = data.find(entry => entry.emotions.length === 0 || entry.emotions.includes("NEUTRAL")) || data[0];
        const neutralUrl = `/dataset/${neutralEntry.image}`;
        setGlobalNeutral(neutralUrl);

        reshuffleDeckWithFilters(data);
      })
      .catch(err => console.log('Offline Database not found. Generate a batch first!', err));
  };

  const handleReshuffleDeck = () => {
    reshuffleDeckWithFilters();
  };

  const handleReshuffleFromSettings = () => {
    reshuffleDeckWithFilters();
    setIsSettingsOpen(false);
  };

  const handleDifficultyChange = (diff) => {
    setDifficulty(diff);
    if (diff === 'Very Easy') {
      setIntensityMin(9);
      setIntensityMax(10);
    } else if (diff === 'Easy') {
      setIntensityMin(7);
      setIntensityMax(9);
    } else if (diff === 'Novice') {
      setIntensityMin(6);
      setIntensityMax(8);
    } else if (diff === 'Beginner') {
      setIntensityMin(5);
      setIntensityMax(7);
    } else if (diff === 'Intermediate') {
      setIntensityMin(4);
      setIntensityMax(7);
    } else if (diff === 'Advanced') {
      setIntensityMin(3);
      setIntensityMax(5);
    } else if (diff === 'Expert') {
      setIntensityMin(2);
      setIntensityMax(4);
    } else if (diff === 'Master') {
      setIntensityMin(1);
      setIntensityMax(3);
    } else if (diff === 'Grandmaster') {
      setIntensityMin(1);
      setIntensityMax(2);
    }
  };

  // Reshuffle deck when Settings modal is closed to apply new intensity/difficulty filters
  useEffect(() => {
    if (!isSettingsOpen && datasetCache.length > 0) {
      reshuffleDeckWithFilters();
    }
  }, [isSettingsOpen]);

  // Auto-Reveal Timer Hook
  useEffect(() => {
    let timer;
    if (activeTab === 'FLASHCARDS' && displayMode === 'Comparison' && autoFlashEnabled && !hasSubmitted && viewingImage === 'NEUTRAL') {
      timer = setTimeout(() => setViewingImage('EXPRESSION'), autoFlashDelay * 1000);
    }
    return () => clearTimeout(timer);
  }, [viewingImage, hasSubmitted, autoFlashEnabled, autoFlashDelay, activeTab, currentFlashcard, displayMode]);

  // Load Offline Dataset
  useEffect(() => {
    loadDataset();
  }, []);

  // Handle escape key to close settings
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setIsSettingsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const configLimits = { intensityMin: 1, intensityMax: 10, speedMin: 50, speedMax: 1000, angleMin: 0, angleMax: 360 };

  const toggleAU = (id) => {
    if (selectedAUs.includes(id)) setSelectedAUs(selectedAUs.filter(au => au !== id));
    else setSelectedAUs([...selectedAUs, id]);
  };

  const toggleEmotion = (emo) => {
    if (selectedEmotions.includes(emo)) setSelectedEmotions(selectedEmotions.filter(e => e !== emo));
    else setSelectedEmotions([...selectedEmotions, emo]);
  };

  const triggerFlash = () => {
    if (isLoading || isFlashingRef.current) return;
    isFlashingRef.current = true;
    setIsFlashing(true);
    setViewingImage('EXPRESSION');
    if (flashTimeoutRef.current) clearTimeout(flashTimeoutRef.current);
    flashTimeoutRef.current = setTimeout(() => {
      setViewingImage('NEUTRAL');
      setIsFlashing(false);
      isFlashingRef.current = false;
    }, flashDuration);
  };

  // Clean up any pending flash timers on component unmount
  useEffect(() => {
    return () => {
      if (flashTimeoutRef.current) clearTimeout(flashTimeoutRef.current);
      isFlashingRef.current = false;
    };
  }, []);

  const handleCheckAnswer = () => {
    setHasSubmitted(true);
    setSliderValue(50);
  };

  const handleNextImage = async () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (flashTimeoutRef.current) clearTimeout(flashTimeoutRef.current);
    setIsFlashing(false);
    isFlashingRef.current = false;
    setHasSubmitted(false);
    setSelectedEmotions([]);
    setSelectedAUs([]);
    setViewingImage('NEUTRAL'); // Force neutral first
    setSliderValue(50);

    if (datasetCache.length === 0) {
      alert("No dataset generated yet! Please go to Settings -> Database and generate a batch first.");
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      let currentDeck = [...deck];
      if (currentDeck.length === 0) {
        setIsDeckCompleted(true);
        setIsLoading(false);
        return;
      }

      const nextIndex = currentDeck.pop();
      setDeck(currentDeck);

      if (currentFlashcard.dbIndex !== undefined) {
        setDrawnIndices(prev => [...prev, currentFlashcard.dbIndex]);
      }
      
      setReviewedCount(prev => prev + 1);

      const randomEntry = datasetCache[nextIndex];
      setCurrentFlashcard(prev => ({
        ...prev,
        imgExpression: `/dataset/${randomEntry.image}`,
        imgNeutral: getNeutralUrl(datasetCache),
        correctEmotions: randomEntry.emotions.length ? randomEntry.emotions : ["NEUTRAL"],
        correctAUs: randomEntry.controls_applied ? Object.keys(randomEntry.controls_applied) : [],
        dbIndex: nextIndex
      }));
      setIsLoading(false);
    }, 400);
  };

  const handlePrevImage = () => {
    if (drawnIndices.length === 0) return;

    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (flashTimeoutRef.current) clearTimeout(flashTimeoutRef.current);
    setIsFlashing(false);
    isFlashingRef.current = false;
    setHasSubmitted(false);
    setSelectedEmotions([]);
    setSelectedAUs([]);
    setViewingImage('NEUTRAL');
    setSliderValue(50);
    setIsLoading(true);

    setTimeout(() => {
      const prevArr = [...drawnIndices];
      const prevIndex = prevArr.pop();

      if (currentFlashcard.dbIndex !== undefined) {
        setDeck(prevDeck => [...prevDeck, currentFlashcard.dbIndex]);
      }
      setDrawnIndices(prevArr);
      setReviewedCount(prev => Math.max(1, prev - 1));

      const entry = datasetCache[prevIndex];
      setCurrentFlashcard(prev => ({
        ...prev,
        imgExpression: `/dataset/${entry.image}`,
        imgNeutral: getNeutralUrl(datasetCache),
        correctEmotions: entry.emotions.length ? entry.emotions : ["NEUTRAL"],
        correctAUs: entry.controls_applied ? Object.keys(entry.controls_applied) : [],
        dbIndex: prevIndex
      }));
      setIsLoading(false);
    }, 400);
  };

  const isEmotionCorrect = selectedEmotions.length === currentFlashcard.correctEmotions.length && selectedEmotions.every(v => currentFlashcard.correctEmotions.includes(v));
  const isAUsCorrect = selectedAUs.length === currentFlashcard.correctAUs.length && selectedAUs.every(v => currentFlashcard.correctAUs.includes(v));

  return (
    <div className="app-container">
      {/* Settings Modal Hook */}
      {isSettingsOpen && (
        <div className="settings-overlay" onClick={() => setIsSettingsOpen(false)}>
          <div className="settings-modal" onClick={e => e.stopPropagation()}>
            <div className="settings-close" onClick={() => setIsSettingsOpen(false)}>✕</div>

            <div className="settings-sidebar">
              <div className="sidebar-section">
                <div className="sidebar-section-title">Settings</div>
                <div className={`sidebar-item ${activeSettingsTab === 'General' ? 'active' : ''}`} onClick={() => setActiveSettingsTab('General')}>
                  <span style={{ fontSize: '16px', marginRight: '6px' }}>⚙️</span> General
                </div>
                <div className={`sidebar-item ${activeSettingsTab === 'Flashcards' ? 'active' : ''}`} onClick={() => setActiveSettingsTab('Flashcards')}>
                  <span style={{ fontSize: '16px', marginRight: '6px' }}>⚡</span> Flashcards
                </div>
                <div className={`sidebar-item ${activeSettingsTab === 'Database' ? 'active' : ''}`} onClick={() => setActiveSettingsTab('Database')}>
                  <span style={{ fontSize: '16px', marginRight: '6px' }}>🗄️</span> Database
                </div>
              </div>
            </div>

            <div className="settings-content">
              <h2>{activeSettingsTab} Settings</h2>

              {activeSettingsTab === 'Flashcards' && (
                <div className="settings-form">
                  <div className="form-group">
                    <label>Flashcard Display Mode</label>
                    <select value={displayMode} onChange={(e) => setDisplayMode(e.target.value)} className="claude-select">
                      <option value="Comparison">Interactive Comparison</option>
                      <option value="Static">Static Expression</option>
                      <option value="Timed">Timed Exposure (Flash)</option>
                    </select>
                  </div>

                  {displayMode === 'Timed' && (
                    <div className="form-group stacked">
                      <div className="flex-row-between">
                        <label>Flash Duration (ms)</label>
                        <span className="slider-value-display">{flashDuration}ms</span>
                      </div>
                      <input type="range" className="claude-slider" min="50" max="2000" step="50" value={flashDuration} onChange={(e) => setFlashDuration(Number(e.target.value))} />
                    </div>
                  )}

                  <div className="form-group stacked">
                    <div className="flex-row-between">
                      <label>Expression Intensity Range (1-10)</label>
                      <span className="slider-value-display">{intensityMin} - {intensityMax}</span>
                    </div>
                    <div className="dual-range-container">
                      <div className="dual-range-track" style={{
                        left: `${(intensityMin - 1) * 11.11}%`,
                        right: `${100 - (intensityMax - 1) * 11.11}%`
                      }}></div>
                      <input 
                        type="range" 
                        min="1" 
                        max="10" 
                        value={intensityMin} 
                        onChange={(e) => {
                          const val = Math.min(Number(e.target.value), intensityMax);
                          setIntensityMin(val);
                        }} 
                        className="dual-range-input"
                        style={{ zIndex: intensityMin > 5 ? 5 : 3 }}
                      />
                      <input 
                        type="range" 
                        min="1" 
                        max="10" 
                        value={intensityMax} 
                        onChange={(e) => {
                          const val = Math.max(Number(e.target.value), intensityMin);
                          setIntensityMax(val);
                        }} 
                        className="dual-range-input"
                        style={{ zIndex: intensityMin > 5 ? 3 : 5 }}
                      />
                    </div>
                  </div>



                  <div className="form-group">
                    <label>Curriculum Difficulty Override</label>
                    <select value={difficulty} onChange={(e) => handleDifficultyChange(e.target.value)} className="claude-select">
                      <option value="Very Easy">Very Easy</option>
                      <option value="Easy">Easy</option>
                      <option value="Novice">Novice</option>
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                      <option value="Expert">Expert</option>
                      <option value="Master">Master</option>
                      <option value="Grandmaster">Grandmaster</option>
                    </select>
                  </div>

                  <div className="form-group stacked" style={{ marginTop: '12px' }}>
                    <div className="flex-row-between">
                      <label>Auto-Reveal Expression</label>
                      <input type="checkbox" checked={autoFlashEnabled} onChange={(e) => setAutoFlashEnabled(e.target.checked)} style={{ transform: 'scale(1.2)' }} />
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Automatically switch from Neutral to Expression during the guessing phase.</p>
                  </div>

                  {autoFlashEnabled && (
                    <div className="form-group stacked">
                      <div className="flex-row-between">
                        <label>Auto-Reveal Delay (Seconds)</label>
                        <span className="slider-value-display">{parseFloat(autoFlashDelay).toFixed(1)}s</span>
                      </div>
                      <input type="range" className="claude-slider" min="0.1" max="5.0" step="0.1" value={autoFlashDelay} onChange={(e) => setAutoFlashDelay(e.target.value)} />
                    </div>
                  )}

                  <div className="form-group" style={{ borderTop: '1px solid var(--settings-border)', paddingTop: '20px', display: 'flex', justifyContent: 'center' }}>
                    <button className="submit-btn" style={{ width: '100%', padding: '10px' }} onClick={handleReshuffleFromSettings}>
                      RESHUFFLE DECK NOW
                    </button>
                  </div>
                </div>
              )}

              {activeSettingsTab === 'General' && (
                <div className="settings-form">
                  <div className="form-group">
                    <label>Application Theme</label>
                    <select value={theme} onChange={(e) => setTheme(e.target.value)} className="claude-select">
                      <option value="Dark">Dark Mode</option>
                      <option value="Light">Light Mode</option>
                    </select>
                  </div>
                </div>
              )}
              {activeSettingsTab === 'Database' && (
                <div className="settings-form">
                  <div style={{ marginBottom: '24px', padding: '16px', borderRadius: '8px', background: 'rgba(35, 137, 212, 0.1)', border: '1px solid var(--accent-blue)' }}>
                    <h3 style={{ fontSize: '14px', color: 'var(--accent-blue)', marginBottom: '8px', marginTop: '0' }}>BATCH DATASET GENERATOR</h3>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', marginBottom: '16px' }}>Lock up Unreal Engine to automatically render thousands of combinations. This bridges the dynamic environment out to a completely static database.</p>

                    <div style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 'bold', marginBottom: '8px', letterSpacing: '1px' }}>DATASET COMPOSITION ({datasetCache.length} TOTAL FRAMES)</div>
                      {datasetCache.length === 0 ? (
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>Database is currently empty. Generated frames will appear here.</div>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {Object.entries(datasetCache.reduce((acc, entry) => {
                            const e = (entry.emotions && entry.emotions.length > 0) ? entry.emotions[0] : "NEUTRAL";
                            acc[e] = (acc[e] || 0) + 1; return acc;
                          }, {})).sort((a, b) => b[1] - a[1]).map(([emotion, count]) => {
                            const pct = ((count / datasetCache.length) * 100);
                            return (
                              <div key={emotion} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-main)', letterSpacing: '0.5px' }}>
                                  <span style={{ fontWeight: '500' }}>{emotion}</span>
                                  <span style={{ opacity: 0.8 }}>{count} ({pct.toFixed(1)}%)</span>
                                </div>
                                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                                  <div style={{ height: '100%', width: `${pct}%`, background: emotion === 'NEUTRAL' ? '#666' : 'var(--accent-blue)', borderRadius: '3px' }}></div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="form-group stacked">
                    <div className="flex-row-between">
                      <label>Batch Size (1 - 100,000 frames)</label>
                    </div>
                    <input type="number" className="claude-slider" min="1" max="100000" value={batchSize} onChange={e => setBatchSize(e.target.value)} style={{ padding: '8px', background: 'var(--bg-input)', border: '1px solid var(--border-color)', borderRadius: '6px', color: 'var(--text-main)', fontSize: '14px' }} />
                  </div>

                  <div className="form-group stacked">
                    <div className="flex-row-between">
                      <label>Expression Intensity Range (1-10)</label>
                      <span className="slider-value-display">{batchIntensityMin} - {batchIntensityMax}</span>
                    </div>
                    <div className="dual-range-container">
                      <div className="dual-range-track" style={{
                        left: `${(batchIntensityMin - 1) * 11.11}%`,
                        right: `${100 - (batchIntensityMax - 1) * 11.11}%`
                      }}></div>
                      <input 
                        type="range" 
                        min="1" 
                        max="10" 
                        value={batchIntensityMin} 
                        onChange={(e) => {
                          const val = Math.min(Number(e.target.value), batchIntensityMax);
                          setBatchIntensityMin(val);
                        }} 
                        className="dual-range-input"
                        style={{ zIndex: batchIntensityMin > 5 ? 5 : 3 }}
                      />
                      <input 
                        type="range" 
                        min="1" 
                        max="10" 
                        value={batchIntensityMax} 
                        onChange={(e) => {
                          const val = Math.max(Number(e.target.value), batchIntensityMin);
                          setBatchIntensityMax(val);
                        }} 
                        className="dual-range-input"
                        style={{ zIndex: batchIntensityMin > 5 ? 3 : 5 }}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Maximum Render Quality (MRQ)</label>
                    <select className="claude-select" value={batchQuality} onChange={e => setBatchQuality(e.target.value)}>
                      <option value="720p">High-Speed (720x960)</option>
                      <option value="1080p">Production (1080x1440)</option>
                      <option value="4K">Lossless 4K (2160x2880)</option>
                    </select>
                  </div>

                  <div className="form-group stacked" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
                    <div className="flex-row-between" style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold' }}>Emotion Distribution Weights</label>
                      <button 
                        type="button"
                        className="toggle-btn" 
                        style={{ fontSize: '11px', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: 'var(--text-main)', cursor: 'pointer', borderRadius: '4px' }}
                        onClick={() => setEmotionWeights({ ANGER: 10, CONTEMPT: 10, DISGUST: 10, FEAR: 10, HAPPINESS: 10, SADNESS: 10, SURPRISE: 10 })}
                      >
                        Reset Equal
                      </button>
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: '1.4' }}>
                      Drag sliders to change the frequency of each expression in the generated batch.
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'var(--bg-input)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      {Object.keys(emotionWeights).map(emo => {
                        const sum = Object.values(emotionWeights).reduce((a, b) => a + b, 0);
                        const percent = sum > 0 ? (emotionWeights[emo] / sum) * 100 : 0;
                        return (
                          <div key={emo} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-main)' }}>
                              <span style={{ fontWeight: '500' }}>{emo}</span>
                              <span style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>{percent.toFixed(0)}%</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                              <input 
                                type="range" 
                                className="claude-slider" 
                                min="0" 
                                max="100" 
                                value={emotionWeights[emo]} 
                                onChange={(e) => {
                                  const val = Number(e.target.value);
                                  setEmotionWeights(prev => ({ ...prev, [emo]: val }));
                                }} 
                                style={{ flex: 1, margin: 0 }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {isBatching ? (
                    <div style={{ marginTop: '32px', padding: '16px', background: 'var(--bg-input)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-blue)', fontWeight: 'bold', fontSize: '13px' }}>
                        <span>GENERATING BATCH...</span>
                        <span>{batchProgress ? `${batchProgress.current} / ${batchProgress.total}` : 'Initiating...'}</span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', background: 'var(--accent-blue)', width: `${batchProgress ? (batchProgress.current / batchProgress.total) * 100 : 0}%`, transition: 'width 0.3s' }}></div>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px' }}>
                        <span>Elapsed: {batchProgress ? Math.floor(batchProgress.elapsed) : 0}s</span>
                        <span>ETA: {batchProgress ? Math.floor(batchProgress.eta) : '?'}s</span>
                      </div>
                      <button className="submit-btn" style={{ background: '#d32f2f', marginTop: '8px', padding: '8px' }} onClick={async () => {
                        try { await fetch("http://localhost:8123/api/cancel_batch", { method: 'POST' }); setIsBatching(false); loadDataset(); } catch (e) { }
                      }}>CANCEL GENERATION</button>
                    </div>
                  ) : (
                    <button className="submit-btn" style={{ marginTop: '32px', alignSelf: 'center', width: '100%' }} onClick={async () => {
                      setIsBatching(true);
                      setBatchProgress(null);
                      try {
                        const payload = { 
                          num_images: parseInt(batchSize), 
                          intensity_min: batchIntensityMin / 10.0, 
                          intensity_max: batchIntensityMax / 10.0, 
                          quality: batchQuality,
                          emotion_weights: emotionWeights
                        };
                        const res = await fetch("http://localhost:8123/api/generate_batch", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
                        if (!res.ok && res.status === 503) { throw new Error("503"); }
                        const data = await res.json();
                        alert(data.status === 'success' ? `Dataset Generated successfully mapped!` : 'Generation Failed');
                        loadDataset();
                      } catch (e) {
                        setShowConnectModal(true);
                      } finally {
                        setIsBatching(false);
                      }
                    }}>COMMENCE UNREAL BATCH GENERATION</button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="header" style={{ height: '50px' }}>
        <div className="header-left">
          <svg className="brain-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style={{ width: 24, height: 24 }}>
            <path d="M12,2C6.48,2 2,6.48 2,12C2,17.52 6.48,22 12,22C17.52,22 22,17.52 22,12C22,6.48 17.52,2 12,2M11,19.93C7.06,19.43 4,16.05 4,12C4,7.95 7.06,4.57 11,4.07V19.93M13,4.07C16.94,4.57 20,7.95 20,12C20,16.05 16.94,19.43 13,19.93V4.07Z" />
          </svg>
          <span style={{ fontSize: '14px' }}>MICRO-EXPRESSION TRAINING APP</span>
        </div>
        <div className="header-tabs">
          <div className={`tab ${activeTab === 'TUTORIAL' ? 'active' : ''}`} onClick={() => setActiveTab('TUTORIAL')}>TUTORIAL</div>
          <div className={`tab ${activeTab === 'FLASHCARDS' ? 'active' : ''}`} onClick={() => setActiveTab('FLASHCARDS')}>FLASHCARDS</div>
          <div className={`tab ${activeTab === 'ABOUT' ? 'active' : ''}`} onClick={() => setActiveTab('ABOUT')}>ABOUT</div>
        </div>
        <div className="header-right" style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div className="icon">👤</div>
          <div className="icon" onClick={() => setIsSettingsOpen(true)}>⚙️</div>
        </div>
      </header>

      <main className="main-content">
        {activeTab === 'TUTORIAL' && (
          <div className="tutorial-placeholder">
            <h2>Welcome to the Tutorial</h2>
            <p>Interactive lessons on Action Units and basic emotions will be available here soon.</p>
          </div>
        )}

        {activeTab === 'ABOUT' && (
          <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
            <ConnectionInstructions />
          </div>
        )}

        {activeTab === 'FLASHCARDS' && (
          <div className="flashcard-workspace">
            {datasetCache.length === 0 ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'var(--text-muted)', background: 'var(--bg-panel)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '16px', opacity: 0.5 }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <h2 style={{ color: 'var(--text-main)', margin: '0 0 8px 0', letterSpacing: '2px' }}>DATASET EMPTY</h2>
                <p style={{ fontSize: '13px' }}>Open the Settings menu ⚙️ in the top right to generate a new offline batch database.</p>
              </div>
            ) : isRangeEmpty ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'var(--text-muted)', background: 'var(--bg-panel)', borderRadius: '12px', border: '1px solid var(--border-color)', padding: '40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚖️</div>
                <h2 style={{ color: 'var(--text-main)', margin: '0 0 8px 0', letterSpacing: '2px', textTransform: 'uppercase' }}>NO IMAGES IN RANGE</h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '24px', textAlign: 'center', maxWidth: '400px', lineHeight: '1.5' }}>
                  No active expressions found in the intensity range ({intensityMin} - {intensityMax}). Adjust the range sliders in the Settings panel ⚙️ or generate a new batch with the corresponding range.
                </p>
                <button className="submit-btn" style={{ padding: '12px 32px', fontSize: '14px' }} onClick={() => setIsSettingsOpen(true)}>
                  OPEN SETTINGS
                </button>
              </div>
            ) : isDeckCompleted ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'var(--text-main)', background: 'var(--bg-panel)', borderRadius: '12px', border: '1px solid var(--border-color)', padding: '40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎉</div>
                <h2 style={{ margin: '0 0 8px 0', letterSpacing: '1px', textTransform: 'uppercase' }}>DECK COMPLETED!</h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '24px', textAlign: 'center', maxWidth: '300px', lineHeight: '1.5' }}>
                  Excellent! You have successfully reviewed all {datasetCache.length} cards in this flashcard deck.
                </p>
                <button className="submit-btn" style={{ padding: '12px 32px', fontSize: '14px' }} onClick={handleReshuffleDeck}>
                  RESHUFFLE & START OVER
                </button>
              </div>
            ) : !hasSubmitted ? (
              // ================= PRE-SUBMIT PHASE =================
              <div className="pre-submit-flow">
                <div className="massive-image-arena">
                  <div className="image-title">{displayMode === 'Static' ? 'EXPRESSION' : viewingImage}</div>
                  <div className="massive-image-wrapper" onWheel={(e) => handleWheel(e, setZoomMain)}>
                    {isLoading ? (
                      <div className="loading-overlay">RENDERING ENGINE FRAME...</div>
                    ) : !currentFlashcard.imgExpression ? (
                      <div className="loading-overlay">NO IMAGE DATA</div>
                    ) : (
                      <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        {/* Neutral Baseline Image */}
                        <img 
                          src={currentFlashcard.imgNeutral} 
                          alt="Neutral" 
                          className="full-height-img" 
                          style={{ 
                            transform: `scale(${zoomMain})`, 
                            position: 'absolute', 
                            opacity: (displayMode !== 'Static' && viewingImage === 'NEUTRAL') ? 1 : 0, 
                            visibility: (displayMode !== 'Static' && viewingImage === 'NEUTRAL') ? 'visible' : 'hidden',
                            zIndex: (displayMode !== 'Static' && viewingImage === 'NEUTRAL') ? 2 : 1
                          }} 
                        />
                        {/* Expression Active Image */}
                        <img 
                          src={currentFlashcard.imgExpression} 
                          alt="Expression" 
                          className="full-height-img" 
                          style={{ 
                            transform: `scale(${zoomMain})`, 
                            position: 'absolute', 
                            opacity: (displayMode === 'Static' || viewingImage === 'EXPRESSION') ? 1 : 0, 
                            visibility: (displayMode === 'Static' || viewingImage === 'EXPRESSION') ? 'visible' : 'hidden',
                            zIndex: (displayMode === 'Static' || viewingImage === 'EXPRESSION') ? 2 : 1
                          }} 
                        />
                      </div>
                    )}
                  </div>
                  {displayMode === 'Comparison' && (
                    <div className="image-toggles">
                      <button className={`toggle-btn ${viewingImage === 'NEUTRAL' ? 'active' : ''}`} onClick={() => setViewingImage('NEUTRAL')}>NEUTRAL</button>
                      <button className={`toggle-btn ${viewingImage === 'EXPRESSION' ? 'active' : ''}`} onClick={() => setViewingImage('EXPRESSION')}>EXPRESSION</button>
                    </div>
                  )}
                  {displayMode === 'Timed' && (
                    <div className="image-toggles">
                      <button className={`toggle-btn flash-btn ${isFlashing ? 'flashing' : ''}`} onClick={triggerFlash} disabled={isFlashing} style={{ padding: '12px 28px', background: 'var(--accent-blue)', color: 'white', borderRadius: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', border: 'none', cursor: 'pointer', fontSize: '13px', letterSpacing: '0.5px' }}>
                        <span>⚡</span> {isFlashing ? 'EXPOSING...' : 'FLASH EXPRESSION'}
                      </button>
                    </div>
                  )}
                </div>

                <div className="guessing-sidebar">
                  <div className="selection-group">
                    <div className="selection-title">SELECT EMOTION (blends supported)</div>
                    <div className="button-row">
                      {emotions.map(emo => (
                        <button key={emo} className={`emotion-btn ${selectedEmotions.includes(emo) ? 'selected' : ''}`} onClick={() => toggleEmotion(emo)}>{emo}</button>
                      ))}
                    </div>
                  </div>

                  <div className="selection-group flex-fill">
                    <div className="selection-title">SELECT ACTION UNITS (AUs)</div>
                    <div className="au-grid">
                      {allAUs.map(au => (
                        <button key={au.id} className={`emotion-btn ${selectedAUs.includes(au.id) ? 'selected' : ''}`} onClick={() => toggleAU(au.id)} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '12px', fontWeight: '900', fontSize: '14px' }}>
                          {au.id}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="sidebar-footer">
                    <div className="progress-bar">
                      <span>Card {reviewedCount} (Pool: {poolSize || datasetCache.length})</span>
                    </div>
                    <button className="submit-btn large-submit" onClick={handleCheckAnswer}>CHECK ANSWER</button>
                  </div>
                </div>
              </div>
            ) : (
              // ================= POST-SUBMIT PHASE =================
              <div className="post-submit-flow">
                <div className="post-submit-top">
                  <div className="massive-image-arena duo">
                    <div className="image-title">
                      {displayMode !== 'Static' ? 'INTERACTIVE COMPARISON (NEUTRAL vs EXPRESSION)' : 'YOUR EXPRESSION'}
                    </div>
                    <div className="massive-image-wrapper" onWheel={(e) => handleWheel(e, setZoomMain)}>
                      {!currentFlashcard.imgExpression ? (
                        <div className="loading-overlay">NO IMAGE DATA</div>
                      ) : displayMode !== 'Static' ? (
                        <div className="comparison-slider" style={{ transform: `scale(${zoomMain})`, transformOrigin: 'center center' }}>
                          <img src={currentFlashcard.imgExpression} alt="Expression" className="slider-bg-img" />
                          <div className="slider-clip" style={{ width: `${sliderValue}%` }}>
                            <img src={currentFlashcard.imgNeutral} alt="Neutral" className="slider-fg-img" />
                          </div>
                          <input type="range" min="0" max="100" value={sliderValue} onChange={(e) => setSliderValue(e.target.value)} className="slider-input" />
                          <div className="slider-divider" style={{ left: `${sliderValue}%` }}></div>
                          <div className="slider-label slider-label-left" style={{ transform: `scale(${1/zoomMain})`, transformOrigin: 'bottom left' }}>NEUTRAL</div>
                          <div className="slider-label slider-label-right" style={{ transform: `scale(${1/zoomMain})`, transformOrigin: 'bottom right' }}>EXPRESSION</div>
                        </div>
                      ) : (
                        <img src={currentFlashcard.imgExpression} alt="Expression" className="full-height-img" style={{ transform: `scale(${zoomMain})` }} />
                      )}
                    </div>
                    {displayMode !== 'Static' && (
                      <div className="slider-legend" style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px 0', fontSize: '11px', fontWeight: 'bold', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        <span>← Left of divider: NEUTRAL</span>
                        <span>Right of divider: EXPRESSION →</span>
                      </div>
                    )}
                  </div>

                  <div className="massive-image-arena duo">
                    <div className="image-title" style={{ color: 'var(--accent-blue)' }}>
                      VISUAL GUIDE: {currentFlashcard.correctEmotions.join(' + ')}
                    </div>
                    <div className="massive-image-wrapper visual-guide-wrapper" onWheel={(e) => handleWheel(e, setZoomGuide)}>
                      {!currentFlashcard.imgExpression ? (
                        <div className="loading-overlay">NO IMAGE DATA</div>
                      ) : (
                        <>
                          <img src={currentFlashcard.imgExpression} alt="Visual Guide" className="full-height-img" style={{ transform: `scale(${zoomGuide})` }} />
                          <div className="guide-arrow" style={{ top: '25%', left: '35%', transform: 'scaleY(-1)' }}>↑</div>
                          <div className="guide-highlight" style={{ top: '20%', left: '25%', width: '50%', height: '15%' }}></div>
                          <div className="guide-text-overlay" style={{ top: '15%', left: '48%' }}>AU4</div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="post-submit-bottom">
                  <div className="results-strip">
                    <div className="res-block">
                      <div className="res-header">YOUR EMOTION</div>
                      <div className="res-val-row">
                        <span>{selectedEmotions.length ? selectedEmotions.join(' + ') : 'None'}</span>
                        <span className={`res-badge ${isEmotionCorrect ? 'correct' : 'incorrect'}`}>{isEmotionCorrect ? 'CORRECT' : 'INCORRECT'}</span>
                      </div>
                      {!isEmotionCorrect && <div className="res-correction">Should be: {currentFlashcard.correctEmotions.join(' + ')}</div>}
                    </div>
                    <div className="res-block">
                      <div className="res-header">YOUR ACTION UNITS</div>
                      <div className="res-val-row">
                        <span>{selectedAUs.length ? selectedAUs.join(' + ') : 'None'}</span>
                        <span className={`res-badge ${isAUsCorrect ? 'correct' : 'incorrect'}`}>{isAUsCorrect ? 'CORRECT' : 'INCORRECT'}</span>
                      </div>
                      {!isAUsCorrect && <div className="res-correction">Should be: {currentFlashcard.correctAUs.join(' + ')}</div>}
                    </div>
                  </div>

                  <div className="bottom-nav">
                    <button className="nav-btn" onClick={handlePrevImage} disabled={drawnIndices.length === 0} style={{ opacity: drawnIndices.length === 0 ? 0.5 : 1 }}>PREVIOUS</button>
                    <button className="nav-btn primary" onClick={handleNextImage}>NEXT IMAGE</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {showConnectModal && (
        <div className="connect-modal-overlay">
          <div className="connect-modal-content">
            <button className="close-modal-btn" onClick={() => setShowConnectModal(false)}>×</button>
            <ConnectionInstructions />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
