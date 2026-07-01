import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList
} from 'recharts';

interface GaitChartProps {
  data: { name: string; value: number }[];
  color?: string;
}

const GaitChart: React.FC<GaitChartProps> = ({
  data,
  color = '#059669'
}) => {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 10, right: 60, left: 60, bottom: 10 }}
        >
          {/* DARKER GRID LINES */}
          <CartesianGrid
            strokeDasharray="3 3"
            horizontal={false}
            stroke="#0f172a"   // slate-900 (near black)
            strokeOpacity={1}
          />

          <XAxis type="number" hide />

          {/* Y-AXIS LABELS */}
          <YAxis
            dataKey="name"
            type="category"
            width={120}
            axisLine={false}
            tickLine={false}
            tick={{
              fill: '#0f172a',
              fontSize: 11,
              fontWeight: 700
            }}
          />

          <Tooltip
            cursor={{ fill: '#e5e7eb', radius: 8 }}
            contentStyle={{
              borderRadius: '16px',
              border: 'none',
              boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
              padding: '12px'
            }}
            itemStyle={{
              fontSize: '12px',
              fontWeight: 'bold'
            }}
          />

          <Bar
            dataKey="value"
            radius={[0, 12, 12, 0]}
            barSize={32}
          >
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={color}
                fillOpacity={0.85}
              />
            ))}

            {/* VALUE LABELS */}
            <LabelList
              dataKey="value"
              position="right"
              offset={10}
              style={{
                fill: '#020617',
                fontSize: 12,
                fontWeight: 800,
                fontFamily: 'Inter'
              }}
              formatter={(v: number) => `${v}ms`}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default GaitChart;
