
import React from 'react';

interface SummaryCardProps {
  title: string;
  value: React.ReactNode;
  subtitle?: string;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, value, subtitle, icon, footer, className = '' }) => {
  return (
    <div className={`bg-white p-7 rounded-[2rem] border border-emerald-50 shadow-[0_8px_30px_rgb(0,0,0,0.02)] flex flex-col justify-between transition-all hover:shadow-lg hover:translate-y-[-2px] ${className}`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-[10px] font-black text-emerald-900/30 uppercase tracking-[0.2em] mb-1">{title}</h3>
          <div className="text-2xl font-black text-emerald-950 tracking-tight">{value}</div>
        </div>
        {icon && <div className="p-3 bg-emerald-50/50 rounded-2xl text-emerald-600 border border-emerald-100/20">{icon}</div>}
      </div>
      {subtitle && <p className="text-[11px] text-slate-600 font-bold uppercase tracking-tight">{subtitle}</p>}
      {footer && <div className="mt-5 pt-5 border-t border-slate-50">{footer}</div>}
    </div>
  );
};

export default SummaryCard;
