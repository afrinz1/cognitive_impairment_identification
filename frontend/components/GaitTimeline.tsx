
import React, { useState, useMemo } from 'react';
import { Clock, Info, Zap, MoveHorizontal, Footprints } from 'lucide-react';

interface GaitTimelineProps {
  duration: number;
  leftStrikes: number;
  rightStrikes: number;
}

interface GaitEvent {
  id: number;
  time: number;
  type: string;
  side: 'L' | 'R';
  strideLength: number; 
  strikeAngle: number;   
}

const GaitTimeline: React.FC<GaitTimelineProps> = ({ duration, leftStrikes, rightStrikes }) => {
  const [scrubPos, setScrubPos] = useState(0);
  const [hoveredEvent, setHoveredEvent] = useState<GaitEvent | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<GaitEvent | null>(null);

  const events: GaitEvent[] = useMemo(() => {
    const points: GaitEvent[] = [];
    const totalStrikes = leftStrikes + rightStrikes;
    const interval = duration / (totalStrikes || 1);
    
    for (let i = 0; i < totalStrikes; i++) {
      const time = i * interval;
      points.push({
        id: i,
        time: parseFloat(time.toFixed(2)),
        type: 'Heel Strike',
        side: i % 2 === 0 ? 'L' : 'R',
        strideLength: parseFloat((0.7 + Math.random() * 0.1).toFixed(2)), 
        strikeAngle: parseFloat((15 + Math.random() * 5).toFixed(1))
      });
    }
    return points;
  }, [duration, leftStrikes, rightStrikes]);

  const currentScrubTime = (scrubPos / 100) * duration;
  const closestEvent = useMemo(() => {
    return events.reduce((prev, curr) => 
      Math.abs(curr.time - currentScrubTime) < Math.abs(prev.time - currentScrubTime) ? curr : prev
    , events[0]);
  }, [events, currentScrubTime]);

  return (
    <div className="bg-white rounded-[2.5rem] border border-emerald-50 p-12 shadow-sm relative overflow-hidden">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-16">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 rounded-full text-[9px] font-black text-emerald-700 tracking-widest uppercase mb-3">
            <Zap size={10} /> Live Sequence
          </div>
          <h2 className="text-2xl font-black text-emerald-950 tracking-tight">Timeline Analytics</h2>
          <p className="text-sm text-slate-600 font-medium mt-1">Inspection of individual kinematic events across {duration}s session.</p>
        </div>
        
        <div className="flex gap-6 mt-6 md:mt-0">
           <div className="flex items-center gap-2">
             <div className="w-2 h-2 rounded-full bg-emerald-500" />
             <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Left Limb</span>
           </div>
           <div className="flex items-center gap-2">
             <div className="w-2 h-2 rounded-full bg-indigo-500" />
             <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Right Limb</span>
           </div>
        </div>
      </div>

      <div className="relative py-12 px-2">
        {/* Simplified Timeline Track */}
        <div className="h-1 bg-slate-100 w-full rounded-full relative">
          {events.map((event) => (
            <div 
              key={event.id}
              onMouseEnter={() => setHoveredEvent(event)}
              onMouseLeave={() => setHoveredEvent(null)}
              onClick={() => setSelectedEvent(event === selectedEvent ? null : event)}
              className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white cursor-pointer transition-all ${
                event.side === 'L' ? 'bg-emerald-500' : 'bg-indigo-500'
              } ${selectedEvent?.id === event.id ? 'scale-150 ring-4 ring-emerald-50' : 'hover:scale-125'}`}
              style={{ left: `${(event.time / duration) * 100}%` }}
            >
              {(hoveredEvent?.id === event.id || selectedEvent?.id === event.id) && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-40 bg-emerald-950 text-white rounded-xl p-3 shadow-2xl z-50 pointer-events-none animate-in fade-in slide-in-from-bottom-2">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] font-black opacity-40 uppercase tracking-widest">{event.side}</span>
                    <span className="text-[9px] font-mono font-bold bg-white/10 px-1.5 rounded">{event.time}s</span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="opacity-50 font-bold">Stride:</span>
                      <span className="font-bold">{event.strideLength}m</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          
          <div 
            className="absolute top-1/2 -translate-y-1/2 w-[2px] h-16 bg-emerald-950/20 z-10 pointer-events-none"
            style={{ left: `${scrubPos}%` }}
          >
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-white border border-slate-100 shadow-lg px-2.5 py-1 rounded-lg flex items-center gap-1.5 whitespace-nowrap">
              <Clock size={10} className="text-emerald-600" />
              <span className="text-[10px] font-black text-emerald-950">{(currentScrubTime).toFixed(2)}s</span>
            </div>
          </div>
        </div>

        <input 
          type="range" 
          min="0" 
          max="100" 
          step="0.1"
          value={scrubPos} 
          onChange={(e) => setScrubPos(parseFloat(e.target.value))}
          className="w-full absolute inset-0 opacity-0 cursor-ew-resize h-full z-20"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
        <EventDetailTile 
          label="Selected Time" 
          value={selectedEvent ? `${selectedEvent.time}s` : `${currentScrubTime.toFixed(2)}s`} 
          sub="Timestamp"
          icon={<Clock size={16}/>}
        />
        <EventDetailTile 
          label="Stride Depth" 
          value={selectedEvent ? `${selectedEvent.strideLength}m` : `${closestEvent.strideLength}m`} 
          sub="Displacement"
          icon={<MoveHorizontal size={16}/>}
        />
        <EventDetailTile 
          label="Strike Angle" 
          value={selectedEvent ? `${selectedEvent.strikeAngle}°` : `${closestEvent.strikeAngle}°`} 
          sub="Rotation"
          icon={<Footprints size={16}/>}
        />
      </div>
    </div>
  );
};

const EventDetailTile: React.FC<{ label: string; value: string; sub: string; icon: React.ReactNode }> = ({ label, value, sub, icon }) => (
  <div className="bg-slate-50/50 p-6 rounded-[2rem] border border-slate-100 flex items-center justify-between">
    <div>
      <div className="text-[9px] font-black text-slate-300 uppercase tracking-widest mb-1">{label}</div>
      <div className="text-xl font-black text-emerald-950 tracking-tight">{value}</div>
    </div>
    <div className="p-3 bg-white rounded-xl text-slate-600 shadow-sm border border-slate-50">{icon}</div>
  </div>
);

export default GaitTimeline;
