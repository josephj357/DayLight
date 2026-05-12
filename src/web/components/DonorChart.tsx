"use client";

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Donor, IndustryBreakdown } from "@/lib/api";
import { formatUSD, formatUSDCompact } from "@/lib/utils";

interface DonorBarChartProps {
  donors: Donor[];
  height?: number;
}

const BAR_PALETTE = [
  "#f59e0b", // daylight-500
  "#d97706", // daylight-600
  "#b45309",
  "#92400e",
  "#78350f",
];

const PIE_PALETTE = [
  "#f59e0b",
  "#d97706",
  "#b45309",
  "#92400e",
  "#78350f",
  "#a8a29e",
  "#57534e",
];

/** Top donors as a horizontal bar chart. */
export function DonorBarChart({ donors, height = 240 }: DonorBarChartProps) {
  const data = donors
    .slice(0, 5)
    .map((d) => ({ name: d.name, amount: d.amount }));

  if (data.length === 0) {
    return (
      <p className="text-sm text-ink-500" role="status">
        No disclosed donor data available for this candidate yet.
      </p>
    );
  }

  return (
    <div
      role="img"
      aria-label={`Top ${data.length} donors by amount: ${data
        .map((d) => `${d.name} ${formatUSD(d.amount)}`)
        .join("; ")}`}
      style={{ width: "100%", height }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 8, right: 16, bottom: 8, left: 8 }}
        >
          <XAxis
            type="number"
            tickFormatter={(v: number) => formatUSDCompact(v)}
            stroke="#a8a29e"
            tick={{ fill: "#57534e", fontSize: 12 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            stroke="#a8a29e"
            tick={{ fill: "#1c1917", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "rgba(245,158,11,0.08)" }}
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e7e5e4",
              borderRadius: 8,
              fontSize: 12,
              color: "#1c1917",
            }}
            formatter={(value: number) => [formatUSD(value), "Amount"]}
          />
          <Bar dataKey="amount" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={BAR_PALETTE[i % BAR_PALETTE.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

interface IndustryDonutProps {
  breakdown: IndustryBreakdown[];
  height?: number;
}

/** Industry concentration as a donut chart. */
export function IndustryDonut({ breakdown, height = 260 }: IndustryDonutProps) {
  const data = breakdown.map((b) => ({
    name: b.industry,
    value: b.amount,
    share: b.share,
  }));

  if (data.length === 0) {
    return (
      <p className="text-sm text-ink-500" role="status">
        No industry breakdown available yet.
      </p>
    );
  }

  return (
    <div
      role="img"
      aria-label={`Industry breakdown of donations: ${data
        .map((d) => `${d.name} ${(d.share * 100).toFixed(1)}%`)
        .join("; ")}`}
      style={{ width: "100%", height }}
      className="flex"
    >
      <ResponsiveContainer width="60%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius="55%"
            outerRadius="85%"
            paddingAngle={2}
            stroke="#fffdf6"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={PIE_PALETTE[i % PIE_PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e7e5e4",
              borderRadius: 8,
              fontSize: 12,
              color: "#1c1917",
            }}
            formatter={(value: number, _name: string, entry: { payload?: { share?: number } }) => [
              `${formatUSD(value)} (${((entry?.payload?.share ?? 0) * 100).toFixed(1)}%)`,
              "Amount",
            ]}
          />
        </PieChart>
      </ResponsiveContainer>
      <ul className="w-2/5 pl-2 self-center space-y-1 text-xs">
        {data.map((d, i) => (
          <li key={d.name} className="flex items-center gap-2 text-ink-700">
            <span
              className="inline-block h-2.5 w-2.5 rounded-sm shrink-0"
              style={{ backgroundColor: PIE_PALETTE[i % PIE_PALETTE.length] }}
              aria-hidden="true"
            />
            <span className="truncate">{d.name}</span>
            <span className="ml-auto tabular-nums text-ink-500">
              {(d.share * 100).toFixed(1)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
