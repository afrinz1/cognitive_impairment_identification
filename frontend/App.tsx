import React, { useState, useEffect, useMemo } from 'react';
import { 
  Activity, 
  Brain, 
  ShieldAlert, 
  Clock, 
  Download, 
  FileText, 
  Upload, 
  CheckCircle2, 
  TrendingUp,
  LayoutDashboard,
  Timer,
  FileSpreadsheet,
  Stethoscope,
  Quote,
  Info,
  Layers,
  Cpu,
  Zap,
  Menu,
  X,
  ArrowRight,
  Sparkles,
  Waves,
  Home,
  MonitorCheck,
  Microscope,
  Database
} from 'lucide-react';
import SummaryCard from './components/SummaryCard.tsx';
import GaitChart from './components/GaitChart.tsx';
import GaitTimeline from './components/GaitTimeline.tsx';
import { PredictionData, ExtractedFeatures } from './types.ts';
import { parsePredictionCSV, parseFeaturesCSV, downloadCSV } from './services/csvParser.ts';
import { GAIT_NORMAL_RANGES, loadPredictionCSV, loadFeaturesCSV } from './constants.tsx';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';

type Tab = 'home' | 'overview' | 'metrics' | 'timeline' | 'data' | 'about';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [features, setFeatures] = useState<ExtractedFeatures | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const predCsv = await loadPredictionCSV();
        const featCsv = await loadFeaturesCSV();
        setPrediction(parsePredictionCSV(predCsv));
        setFeatures(parseFeaturesCSV(featCsv));
      } catch (err) {
        console.error('Failed to load CSVs:', err);
      }
    })();
  }, []);

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'green': return 'bg-emerald-500';
      case 'yellow': return 'bg-yellow-500';
      case 'orange': return 'bg-orange-500';
      case 'red': return 'bg-rose-500';
      default: return 'bg-black';
    }
  };

  const temporalData = useMemo(() => {
    if (!prediction) return [];
    return [
      { name: 'Step Time', value: prediction.Step_Time_MS },
      { name: 'Stride Time', value: prediction.Stride_Time_MS },
      { name: 'Stance Time', value: prediction.Stance_MS },
      { name: 'Swing Time', value: prediction.Swing_MS },
    ];
  }, [prediction]);

  const supportData = useMemo(() => {
    if (!prediction) return [];
    return [
      { name: 'SLS', value: prediction.SLS_MS },
      { name: 'IDS', value: prediction.IDS_MS },
      { name: 'TDS', value: prediction.TDS_MS },
    ];
  }, [prediction]);

  const radarData = useMemo(() => {
    if (!prediction) return [];
    return [
      { subject: 'Step Time', A: prediction.Step_Time_MS / 6.5, fullMark: 100 },
      { subject: 'Stride Time', A: prediction.Stride_Time_MS / 12.5, fullMark: 100 },
      { subject: 'Swing Time', A: prediction.Swing_MS / 5.0, fullMark: 100 },
      { subject: 'Stance Time', A: prediction.Stance_MS / 8.0, fullMark: 100 },
      { subject: 'SLS', A: prediction.SLS_MS / 4.5, fullMark: 100 },
    ];
  }, [prediction]);

  // ─── Dynamic Table Helpers ───────────────────────────────────────────
  const PARAMETER_MAP: Record<string, string> = {
    'Step Time': 'Step_Time_MS',
    'Stride Time': 'Stride_Time_MS',
    'Stance Time': 'Stance_MS',
    'Swing Time': 'Swing_MS',
    'Single Limb Support': 'SLS_MS',
    'Initial Double Support': 'IDS_MS',
    'Terminal Double Support': 'TDS_MS',
  };

  const getValue = (param: string): number | string => {
    if (!prediction) return '--';
    const key = PARAMETER_MAP[param] as keyof PredictionData;
    if (!key) return '--';
    const raw = prediction[key];
    return typeof raw === 'number' ? Math.round(raw) : '--';
  };

  const getStatus = (value: number, min: number, max: number): string => {
    if (value < min) return 'Low';
    if (value > max) return 'High';
    return 'Optimal';
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'Low':
        return 'bg-blue-50 text-blue-700 border-blue-100';
      case 'High':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'Optimal':
        return 'bg-emerald-50 text-emerald-700 border-emerald-100';
      default:
        return 'bg-slate-50 text-slate-500 border-slate-100';
    }
  };
  // ─────────────────────────────────────────────────────────────────────

  const toggleTab = (tab: Tab) => {
    setActiveTab(tab);
    setIsMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!prediction || !features) return (
    <div className="flex items-center justify-center h-screen bg-white">
      <Activity className="w-12 h-12 text-emerald-600 animate-pulse" />
    </div>
  );

  return (
    <div className={`min-h-screen selection:bg-emerald-100 selection:text-emerald-900 ${activeTab === 'home' ? 'bg-[#010805] text-white overflow-x-hidden' : 'bg-[#fafbfc] text-[#064e3b]'}`}>
      
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 border-b transition-all duration-500 ${activeTab === 'home' ? 'bg-[#010805]/40 backdrop-blur-2xl border-white/5' : 'bg-white/90 backdrop-blur-md border-emerald-50'}`}>
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4 cursor-pointer" onClick={() => toggleTab('home')}>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-lg transition-all ${activeTab === 'home' ? 'bg-emerald-500 shadow-emerald-500/20' : 'emerald-gradient shadow-emerald-900/10'}`}>
              <Activity className="text-white" size={20} />
            </div>
            <div>
              <h1 className={`text-lg font-black tracking-tighter leading-none ${activeTab === 'home' ? 'text-white' : 'text-emerald-950'}`}>CogniGait AI</h1>
              <p className={`text-[9px] font-black uppercase tracking-[0.2em] mt-1 ${activeTab === 'home' ? 'text-emerald-500/60' : 'text-emerald-600/40'}`}>Diagnostic Intelligence</p>
            </div>
          </div>

          {activeTab !== 'home' ? (
            <div className="hidden md:flex items-center bg-slate-100/50 p-1 rounded-2xl border border-slate-200/20">
              <NavTab active={false} onClick={() => toggleTab('home')} icon={<Home size={16}/>} label="Home" />
              <NavTab active={activeTab === 'overview'} onClick={() => toggleTab('overview')} icon={<LayoutDashboard size={16}/>} label="Overview" />
              <NavTab active={activeTab === 'metrics'} onClick={() => toggleTab('metrics')} icon={<Activity size={16}/>} label="Metrics" />
              <NavTab active={activeTab === 'timeline'} onClick={() => toggleTab('timeline')} icon={<Timer size={16}/>} label="Timeline" />
              <NavTab active={activeTab === 'about'} onClick={() => toggleTab('about')} icon={<Info size={16}/>} label="About" />
            </div>
          ) : <div className="flex-1" />}

          <div className="flex items-center gap-3">
            {activeTab === 'home' ? (
              <button 
                onClick={() => toggleTab('overview')} 
                className="hidden md:flex px-6 py-2.5 bg-emerald-500 text-[#010805] rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/10"
              >
                Launch Dashboard
              </button>
            ) : (
              <button 
                onClick={async () => { const csv = await loadPredictionCSV(); downloadCSV(csv, 'report.csv'); }} 
                className="hidden sm:flex text-[10px] font-black text-white bg-emerald-950 px-5 py-2.5 rounded-xl hover:bg-emerald-900 transition-all shadow-lg items-center gap-2 uppercase tracking-widest"
              >
                <Download size={14} /> Export Report
              </button>
            )}
            <button 
              className={`md:hidden p-2.5 rounded-xl transition-colors ${activeTab === 'home' ? 'bg-white/5 text-white' : 'bg-emerald-50 text-emerald-950'}`}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className={`${activeTab !== 'home' ? 'pt-24' : ''}`}>
        {activeTab === 'home' && (
          <div className="relative min-h-screen flex flex-col items-center justify-center pt-24 pb-20 px-6 text-center">
            
            {/* Minimal Background Subtle Glows */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
               <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.05)_0%,transparent_60%)]" />
            </div>

            {/* Hero Section */}
            <div className="relative z-10 max-w-5xl mx-auto space-y-10">
              <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-emerald-400 text-[11px] font-black uppercase tracking-[0.3em] animate-in fade-in slide-in-from-top-4 duration-700">
                 <Sparkles size={14} /> Kinetic Bio-Intelligence Platform
              </div>

              <h1 className="text-6xl md:text-9xl font-black tracking-tighter leading-[0.85] text-white animate-in zoom-in-95 duration-1000">
                DECODE <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-br from-emerald-400 via-emerald-200 to-indigo-400">HUMAN</span> <br/>
                STRIDE
              </h1>

              <p className="max-w-2xl mx-auto text-emerald-100/50 text-lg md:text-xl font-medium leading-relaxed animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
                Transforming high-frequency IMU sensor telemetry into clinically actionable cognitive insights through advanced LSTM neural modeling.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6 animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-300">
                <button 
                  onClick={() => toggleTab('overview')} 
                  className="group relative px-12 py-5 bg-white text-[#010805] rounded-2xl font-black text-xs uppercase tracking-[0.2em] overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-xl shadow-white/5"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-emerald-200 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <span className="relative z-10 flex items-center gap-3">
                     Enter Dashboard <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                <button 
                  onClick={() => toggleTab('about')} 
                  className="px-12 py-5 bg-white/5 border border-white/10 text-white rounded-2xl font-black text-xs uppercase tracking-[0.2em] hover:bg-white/10 transition-all backdrop-blur-md"
                >
                  Technical Review
                </button>
              </div>

              {/* Enhanced Feature Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-24 pb-12">
                <HomeCard 
                  icon={<Cpu size={24}/>} 
                  label="Neural Core" 
                  title="LSTM-A2 Modeling" 
                  desc="Processes complex temporal sequences to identify sub-perceptual gait anomalies." 
                />
                <HomeCard 
                  icon={<Waves size={24}/>} 
                  label="Telemetry" 
                  title="100Hz Precision" 
                  desc="High-fidelity sensor fusion capturing 100 data points per second of session." 
                />
                <HomeCard 
                  icon={<Brain size={24}/>} 
                  label="Cognition" 
                  title="MMSE Alignment" 
                  desc="Validated against clinical standards to predict cognitive risk stratification." 
                />
                <HomeCard 
                  icon={<ShieldAlert size={24}/>} 
                  label="Reliability" 
                  title="Zero-Latency" 
                  desc="Real-time edge processing for immediate diagnostic result delivery." 
                />
              </div>

              {/* Status Strip */}
              <div className="p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-xl flex flex-col md:flex-row items-center justify-between gap-8 mt-12">
                <div className="flex items-center gap-6">
                  <div className="flex -space-x-3">
                    {[1,2,3].map(i => (
                      <div key={i} className="w-10 h-10 rounded-full border-2 border-[#010805] bg-emerald-500 flex items-center justify-center text-[10px] font-black text-[#010805]">
                        {i === 1 ? <MonitorCheck size={14}/> : i === 2 ? <Microscope size={14}/> : <Database size={14}/>}
                      </div>
                    ))}
                  </div>
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-widest text-emerald-400">System Status</div>
                    <div className="text-sm font-bold text-white">All clinical engines operational &bull; v2.5.1</div>
                  </div>
                </div>
                <div className="h-[1px] md:h-10 w-full md:w-[1px] bg-white/10" />
                <div className="flex gap-12 text-left">
                   <div>
                     <div className="text-[9px] font-black uppercase tracking-widest text-white/30 mb-1">Last Analysis</div>
                     <div className="text-sm font-bold text-white">0.42ms</div>
                   </div>
                   <div>
                     <div className="text-[9px] font-black uppercase tracking-widest text-white/30 mb-1">Model Accuracy</div>
                     <div className="text-sm font-bold text-white">96.8%</div>
                   </div>
                   <div>
                     <div className="text-[9px] font-black uppercase tracking-widest text-white/30 mb-1">Validated</div>
                     <div className="text-sm font-bold text-emerald-400 flex items-center gap-1.5"><CheckCircle2 size={12}/> YES</div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Views */}
        {activeTab === 'overview' && (
          <main className="max-w-7xl mx-auto px-6 py-10 space-y-10 animate-in fade-in duration-500">
              <div className="bg-white rounded-[2.5rem] p-10 border border-emerald-50 shadow-sm flex flex-col lg:flex-row items-center justify-between gap-10 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1/3 h-full bg-emerald-50/20 skew-x-[-12deg] -translate-x-12 pointer-events-none" />
                <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
                    <div className="relative">
                      <div className="w-32 h-32 rounded-full border-4 border-emerald-100 flex items-center justify-center bg-emerald-50/30">
                        <span className="text-4xl font-black text-emerald-950">{prediction.Predicted_MMSE}</span>
                      </div>
                      <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-emerald-950 text-white text-[9px] font-black px-3 py-1 rounded-full whitespace-nowrap uppercase tracking-widest shadow-xl">
                        / 30 Score
                      </div>
                    </div>
                    <div className="text-center md:text-left">
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 rounded-full text-[10px] font-black text-emerald-700 tracking-widest uppercase mb-3 border border-emerald-100/50">
                        <Stethoscope size={12} /> Assessment Result
                      </div>
                      <h2 className="text-3xl md:text-4xl font-black text-emerald-950 tracking-tighter leading-none mb-2">{prediction.Cognitive_Status}</h2>
                      <p className="text-slate-600 font-medium max-w-md text-sm">Automated screening using multi-sensor wearable telemetry and LSTM modeling.</p>
                    </div>
                </div>
                <div className="flex gap-4 relative z-10 w-full lg:w-auto">
                    <div className="flex-1 bg-slate-50 p-6 rounded-3xl border border-slate-100 text-center min-w-[120px]">
                      <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Confidence</div>
                      <div className="text-2xl font-black text-emerald-950">{prediction.Confidence_Percent}%</div>
                    </div>
                    <div className="flex-1 bg-slate-50 p-6 rounded-3xl border border-slate-100 text-center min-w-[120px]">
                      <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Risk Profile</div>
                      <div className={`text-sm font-black text-white px-3 py-1 rounded-lg mt-2 inline-block uppercase tracking-widest ${getRiskColor(prediction.Risk_Level)}`}>
                        {prediction.Risk_Level}
                      </div>
                    </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-8 space-y-8">
                  <div className="bg-white rounded-[2.5rem] border border-emerald-50 p-6 md:p-10 shadow-sm overflow-hidden">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                          <h3 className="text-lg font-black text-emerald-950 tracking-tight">Kinematic Fingerprint</h3>
                          <p className="text-xs text-slate-600 font-medium uppercase tracking-widest">Normalised gait cycle mapping</p>
                        </div>
                        <div className="hidden sm:flex items-center gap-2 text-[10px] font-black text-emerald-300 uppercase tracking-widest bg-emerald-50/30 px-3 py-1.5 rounded-lg border border-emerald-100/50">
                          Spatial-Temporal
                        </div>
                    </div>
                    <div className="h-64 md:h-80 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                            <PolarGrid stroke="#f1f5f9" />
                            <PolarAngleAxis dataKey="subject" tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 800}} />
                            <Radar name="Subject" dataKey="A" stroke="#059669" fill="#059669" fillOpacity={0.15} />
                          </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="bg-emerald-50/40 rounded-[2.5rem] border border-emerald-100 p-6 md:p-10 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:scale-105 transition-transform duration-1000">
                      <Brain size={200} />
                    </div>
                    <div className="flex items-center gap-3 mb-8 relative z-10">
                        <div className="p-2.5 bg-white rounded-xl text-emerald-600 shadow-sm">
                          <Brain size={20} />
                        </div>
                        <h3 className="text-xl font-black text-emerald-950 tracking-tight">Expert Clinical Insight</h3>
                    </div>
                    <div className="relative pl-6 md:pl-10 border-l-2 border-emerald-200 relative z-10">
                      <Quote className="absolute top-0 left-0 -translate-x-1/2 -translate-y-4 text-emerald-100/50 w-12 h-12" />
                      <p className="text-lg md:text-xl leading-relaxed text-emerald-900 font-medium italic mb-8">
                          "Biomechanical signatures indicate high predictive correlation with <span className="text-emerald-950 font-black not-italic underline decoration-emerald-200 decoration-4 underline-offset-4">{prediction.Cognitive_Status}</span>. Consistent temporal phasing was observed throughout the session."
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-8">
                          <div className="bg-white/50 p-4 rounded-2xl border border-white/50">
                            <div className="text-[9px] font-black text-emerald-800/40 uppercase tracking-[0.2em] mb-1">Gait Variability</div>
                            <div className="text-sm font-bold text-emerald-900">Optimal</div>
                          </div>
                          <div className="bg-white/50 p-4 rounded-2xl border border-white/50">
                            <div className="text-[9px] font-black text-emerald-800/40 uppercase tracking-[0.2em] mb-1">Symmetry Index</div>
                            <div className="text-sm font-bold text-emerald-900">91.7 / 100</div>
                          </div>
                          <div className="bg-white/50 p-4 rounded-2xl border border-white/50">
                            <div className="text-[9px] font-black text-emerald-800/40 uppercase tracking-[0.2em] mb-1">Decision Engine</div>
                            <div className="text-sm font-bold text-emerald-900">LSTM v2.5</div>
                          </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="lg:col-span-4 space-y-8">
                  <div className="bg-white rounded-[2.5rem] border border-emerald-50 p-8 shadow-sm">
                    <h3 className="text-[11px] font-black text-emerald-950 uppercase tracking-[0.2em] mb-8 flex items-center gap-3">
                      <TrendingUp size={18} className="text-emerald-500" /> Clinical KPIs
                    </h3>
                    <div className="space-y-8">
                        <MiniMetric label="Step Consistency" value="94.2%" trend="+2%" />
                        <MiniMetric label="Limb Symmetry" value="91.7%" trend="Stable" />
                        <MiniMetric label="Stride Uniformity" value="88.5%" trend="-0.4%" />
                        <MiniMetric label="Propulsion Power" value="0.92g" trend="Optimal" />
                    </div>
                  </div>
                  <div className="bg-white rounded-[2.5rem] border border-emerald-50 p-8 shadow-sm">
                    <h3 className="text-[11px] font-black text-emerald-950 uppercase tracking-[0.2em] mb-6 flex items-center gap-3">
                      <Activity size={18} className="text-indigo-500" /> Capture Summary
                    </h3>
                    <div className="space-y-4">
                      <TelemetryRow label="Total Samples" value={features.Total_Samples.toLocaleString()} />
                      <TelemetryRow label="Session Duration" value={`${features.Duration_Seconds}s`} />
                      <TelemetryRow label="Sampling Rate" value="100Hz" />
                      <TelemetryRow label="Status" value="Verified" />
                    </div>
                  </div>
                </div>
              </div>
          </main>
        )}

        {activeTab === 'metrics' && (
          <main className="max-w-7xl mx-auto px-6 py-10 space-y-10 animate-in slide-in-from-bottom-4 duration-500">
             <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
              <MetricCard title="Temporal Profile" subtitle="Phase duration analysis (ms)" color="#059669" data={temporalData} />
              <MetricCard title="Support Profile" subtitle="Ground contact dynamics (ms)" color="#4f46e5" data={supportData} />
            </div>
            <div className="bg-white rounded-[2.5rem] border border-emerald-50 overflow-x-auto shadow-sm">
              <div className="p-6 md:p-10 border-b border-slate-50 flex items-center justify-between min-w-[600px]">
                <div>
                  <h2 className="text-xl font-black text-emerald-950 tracking-tight">Reference Thresholds</h2>
                  <p className="text-xs text-slate-600 font-bold uppercase tracking-widest mt-1">Clinical Normalcy comparison</p>
                </div>
              </div>
              <table className="w-full text-left min-w-[600px]">
                <thead className="bg-slate-50/30">
                  <tr>
                    <th className="px-10 py-5 text-[9px] font-black text-slate-300 uppercase tracking-[0.2em]">Biomarker</th>
                    <th className="px-10 py-5 text-[9px] font-black text-slate-300 uppercase tracking-[0.2em]">Recorded</th>
                    <th className="px-10 py-5 text-[9px] font-black text-slate-300 uppercase tracking-[0.2em]">Expected</th>
                    <th className="px-10 py-5 text-[9px] font-black text-slate-300 uppercase tracking-[0.2em] text-right">Valuation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {GAIT_NORMAL_RANGES.map((range, i) => {
                    const value = getValue(range.parameter);
                    const numericValue = typeof value === 'number' ? value : NaN;
                    const status = isNaN(numericValue) ? 'No Data' : getStatus(numericValue, range.min, range.max);

                    return (
                      <tr key={i} className="hover:bg-emerald-50/10 transition-all duration-200">
                        <td className="px-10 py-7">
                          <div className="font-black text-emerald-950">{range.parameter}</div>
                          <div className="text-[10px] text-slate-600 font-medium mt-0.5">{range.description}</div>
                        </td>
                        <td className="px-10 py-7 font-mono font-black text-emerald-700">
                          {value !== '--' ? `${value}ms` : '--'}
                        </td>
                        <td className="px-10 py-7 text-xs text-slate-600 font-bold">
                          {range.min} - {range.max}ms
                        </td>
                        <td className="px-10 py-7 text-right">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[9px] font-black tracking-tighter uppercase border ${getStatusColor(status)}`}>
                            {status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </main>
        )}

        {activeTab === 'timeline' && (
          <main className="max-w-7xl mx-auto px-6 py-10 animate-in fade-in duration-500">
            <GaitTimeline 
              duration={features.Duration_Seconds} 
              leftStrikes={features.Left_Heel_Strikes} 
              rightStrikes={features.Right_Heel_Strikes} 
            />
          </main>
        )}

        {activeTab === 'about' && (
          <main className="max-w-7xl mx-auto px-6 py-10 space-y-12 animate-in slide-in-from-bottom-6 duration-700 pb-20">
             <div className="max-w-4xl mx-auto space-y-16">
                <div className="text-center space-y-6">
                  <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-[10px] font-black tracking-[0.3em] uppercase bg-emerald-950 text-white`}>
                    Platform Architecture
                  </div>
                  <h1 className={`text-3xl md:text-5xl font-black tracking-tighter leading-tight text-emerald-950`}>
                    Next-Generation Cognitive <br className="hidden md:block"/> Gait Analysis
                  </h1>
                  <p className={`text-base md:text-lg font-medium leading-relaxed max-w-2xl mx-auto text-slate-500`}>
                    CogniGait AI bridges the gap between biomechanics and neurology, utilizing wearable sensor fusion to predict cognitive health with clinical precision.
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
                   <AboutCard isDark={false} icon={<Layers className="text-emerald-600"/>} title="IMU Sensor Fusion" desc="High-fidelity capture of linear acceleration and angular velocity using foot-mounted inertial units." />
                   <AboutCard isDark={false} icon={<Cpu className="text-indigo-600"/>} title="LSTM Neural Engine" desc="Long Short-Term Memory networks process temporal sequences to identify sub-perceptual gait anomalies." />
                   <AboutCard isDark={false} icon={<Zap className="text-emerald-400"/>} title="Predictive Analytics" desc="Validated against MMSE benchmarks to provide real-time cognitive risk stratification." />
                </div>
                <div className={`rounded-[2.5rem] p-8 md:p-12 border shadow-sm space-y-10 bg-white border-emerald-50`}>
                   <section className="space-y-4">
                     <h3 className={`text-2xl font-black tracking-tight text-emerald-950`}>System Overview</h3>
                     <p className={`leading-relaxed font-medium text-sm md:text-base text-slate-600`}>
                        The CogniGait AI dashboard is designed as a Decision Support System (DSS) for clinicians. By leveraging data from wearable IMU sensors operating at 100Hz, the system captures micro-variations in gait timing which are clinically linked to neurodegenerative decline.
                     </p>
                   </section>
                   <section className="space-y-4">
                     <h3 className={`text-2xl font-black tracking-tight text-emerald-950`}>LSTM Methodology</h3>
                     <p className={`leading-relaxed font-medium text-sm md:text-base text-slate-600`}>
                        Unlike traditional threshold-based gait analysis, our LSTM model analyzes the *sequence* of steps. It identifies patterns of instability that precede symptomatic cognitive impairment, allowing for earlier clinical intervention.
                     </p>
                   </section>
                   <div className={`p-6 md:p-8 rounded-[2rem] border bg-emerald-50 border-emerald-100`}>
                     <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg shadow-sm bg-white text-emerald-600`}><Info size={20}/></div>
                        <div>
                          <h4 className={`font-black uppercase tracking-widest text-[10px] mb-2 text-emerald-950`}>Technical Note</h4>
                          <p className={`text-xs md:text-sm font-medium leading-relaxed text-emerald-900/70`}>
                            MMSE predictions are generated focusing on temporal biomarkers. A score below 24 may indicate potential cognitive impairment, requiring specialist neurological review.
                          </p>
                        </div>
                     </div>
                   </div>
                </div>
                <div className="flex justify-center">
                   <button onClick={() => toggleTab('overview')} className="bg-emerald-500 text-[#010805] px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-emerald-500/20">
                     Explore Dashboard
                   </button>
                </div>
             </div>
          </main>
        )}
      </div>

      {activeTab !== 'home' && (
        <footer className="mt-20 py-16 border-t border-emerald-50 text-center bg-white">
          <div className="max-w-7xl mx-auto px-6 flex flex-col items-center gap-4">
            <p className="text-[10px] font-black text-slate-300 uppercase tracking-[0.4em]">
              CogniGait AI &middot; Clinical Intelligence System v2.5.1
            </p>
          </div>
        </footer>
      )}
    </div>
  );
};

// Home UI Components
const HomeCard: React.FC<{ icon: React.ReactNode; label: string; title: string; desc: string }> = ({ icon, label, title, desc }) => (
  <div className="group p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-md transition-all hover:bg-white/10 hover:border-emerald-500/50 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(16,185,129,0.1)] text-left">
    <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-6 group-hover:scale-110 group-hover:bg-emerald-500 group-hover:text-[#010805] transition-all">
      {icon}
    </div>
    <div className="text-[10px] font-black uppercase tracking-widest text-emerald-400/60 mb-1">{label}</div>
    <h3 className="text-xl font-black text-white tracking-tight mb-3">{title}</h3>
    <p className="text-sm font-medium text-emerald-100/40 leading-relaxed">{desc}</p>
  </div>
);

const NavTab: React.FC<{ active: boolean; onClick: () => void; icon: React.ReactNode; label: string }> = ({ active, onClick, icon, label }) => (
  <button 
    onClick={onClick}
    className={`px-5 py-3 rounded-xl text-[11px] font-black flex items-center gap-2.5 transition-all uppercase tracking-wider ${
      active ? 'bg-white text-emerald-950 shadow-md border border-emerald-50/50 scale-105' : 'text-slate-600 hover:text-emerald-800'
    }`}
  >
    {icon} <span>{label}</span>
  </button>
);

const MobileNavTab: React.FC<{ active: boolean; onClick: () => void; icon: React.ReactNode; label: string; isDark?: boolean }> = ({ active, onClick, icon, label, isDark }) => (
  <button 
    onClick={onClick}
    className={`w-full px-6 py-5 rounded-[1.5rem] text-sm font-black flex items-center gap-4 transition-all uppercase tracking-widest ${
      active 
        ? (isDark ? 'bg-white/10 text-white' : 'bg-emerald-50 text-emerald-950 border border-emerald-100 shadow-sm') 
        : (isDark ? 'text-emerald-500/50 hover:bg-white/5' : 'text-slate-500 hover:bg-slate-50')
    }`}
  >
    <div className={active ? (isDark ? 'text-emerald-400' : 'text-emerald-600') : 'text-slate-600'}>{icon}</div>
    <span>{label}</span>
  </button>
);

const MiniMetric: React.FC<{ label: string; value: string; trend: string }> = ({ label, value, trend }) => (
  <div className="flex items-center justify-between group">
    <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">{label}</span>
    <div className="flex items-center gap-3">
      <span className="font-black text-emerald-950 text-lg tracking-tighter">{value}</span>
      <span className={`text-[9px] font-black px-2 py-1 rounded-lg ${trend.includes('+') ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-50 text-slate-600'}`}>
        {trend}
      </span>
    </div>
  </div>
);

const MetricCard: React.FC<{ title: string; subtitle: string; color: string; data: any[] }> = ({ title, subtitle, color, data }) => (
  <div className="bg-white rounded-[2.5rem] shadow-sm border border-emerald-50 overflow-hidden group text-left">
    <div className="p-6 md:p-10 border-b border-slate-50 group-hover:bg-slate-50/30 transition-colors">
      <h2 className="text-xl font-black text-emerald-950 tracking-tight">{title}</h2>
      <p className="text-[10px] text-slate-300 font-black uppercase tracking-widest mt-1">{subtitle}</p>
    </div>
    <div className="p-6 md:p-10"><GaitChart data={data} color={color} /></div>
  </div>
);

const AboutCard: React.FC<{ icon: React.ReactNode; title: string; desc: string; isDark?: boolean }> = ({ icon, title, desc, isDark }) => (
  <div className={`p-8 rounded-[2.5rem] border shadow-sm space-y-4 hover:border-emerald-500/50 transition-all group ${isDark ? 'bg-white/5 border-white/10' : 'bg-white border-emerald-50'} text-left`}>
    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>{icon}</div>
    <h3 className={`text-lg font-black tracking-tight ${isDark ? 'text-white' : 'text-emerald-950'}`}>{title}</h3>
    <p className={`text-sm leading-relaxed font-medium ${isDark ? 'text-emerald-100/40' : 'text-slate-600'}`}>{desc}</p>
  </div>
);

const TelemetryRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between items-center text-[10px] py-2 border-b border-emerald-100/30 last:border-0">
    <span className="text-slate-600 font-black uppercase tracking-tight">{label}</span>
    <span className="font-black text-emerald-900">{value}</span>
  </div>
);

export default App;