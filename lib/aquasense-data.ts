export type Metrics = { ph: number; turbidity: number; tds: number; temperature: number; risk: "LOW" | "MEDIUM" | "HIGH" }
export type Location = { id: string; village: string; district: string; state: string; lat: number; lng: number; status: "Operational" | "Attention" }

export const locations: Location[] = [
  { id: "AS-001", village: "Kampur", district: "Nagaon", state: "Assam", lat: 26.32, lng: 92.68, status: "Operational" },
  { id: "AS-002", village: "Borkhola", district: "Cachar", state: "Assam", lat: 24.83, lng: 92.78, status: "Operational" },
  { id: "AS-003", village: "Sonapur", district: "Kamrup", state: "Assam", lat: 26.17, lng: 91.88, status: "Attention" },
  { id: "AS-004", village: "Rangia", district: "Kamrup", state: "Assam", lat: 26.45, lng: 91.62, status: "Operational" },
  { id: "AS-005", village: "Diphu", district: "Karbi Anglong", state: "Assam", lat: 25.84, lng: 93.43, status: "Operational" },
  { id: "AS-006", village: "Jorhat East", district: "Jorhat", state: "Assam", lat: 26.75, lng: 94.20, status: "Operational" },
  { id: "AS-007", village: "Tura Hills", district: "West Garo Hills", state: "Meghalaya", lat: 25.52, lng: 90.22, status: "Operational" },
  { id: "AS-008", village: "Aizawl North", district: "Aizawl", state: "Mizoram", lat: 23.75, lng: 92.72, status: "Attention" },
]

export const baseMetrics: Record<string, Metrics> = {
  "AS-001": { ph: 7.24, turbidity: 1.82, tds: 218, temperature: 24.6, risk: "LOW" },
  "AS-002": { ph: 7.08, turbidity: 2.14, tds: 242, temperature: 25.1, risk: "LOW" },
  "AS-003": { ph: 6.81, turbidity: 4.92, tds: 386, temperature: 27.3, risk: "MEDIUM" },
  "AS-004": { ph: 7.32, turbidity: 1.24, tds: 186, temperature: 23.8, risk: "LOW" },
  "AS-005": { ph: 6.94, turbidity: 2.76, tds: 274, temperature: 24.2, risk: "LOW" },
  "AS-006": { ph: 7.18, turbidity: 1.56, tds: 198, temperature: 23.4, risk: "LOW" },
  "AS-007": { ph: 7.42, turbidity: 0.92, tds: 164, temperature: 21.8, risk: "LOW" },
  "AS-008": { ph: 6.66, turbidity: 5.44, tds: 420, temperature: 26.9, risk: "HIGH" },
}

export const trend = Array.from({ length: 24 }, (_, i) => ({
  hour: `${String((i + 1) % 24).padStart(2, "0")}:00`,
  ph: Number((7.08 + Math.sin(i / 3.2) * 0.16 + (i % 5) * 0.012).toFixed(2)),
  turbidity: Number((2.1 + Math.cos(i / 2.8) * 0.65 + (i % 4) * 0.08).toFixed(2)),
  tds: Math.round(218 + Math.sin(i / 4) * 24 + (i % 3) * 5),
  temperature: Number((24.2 + Math.sin(i / 5) * 2.1).toFixed(1)),
}))

export const thresholds = { ph: "6.5 – 8.5", turbidity: "< 5 NTU", tds: "< 500 mg/L", temperature: "18 – 32 °C" }
