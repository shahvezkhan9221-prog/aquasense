"use client"

import { useEffect, useMemo, useState } from "react"
import { useTheme } from "next-themes"
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Activity, AlertTriangle, BarChart3, Bell, ChevronDown, ChevronsLeft, ChevronsRight, CircleHelp, Droplets, Gauge, LayoutDashboard, LogOut, MapPin, Menu, Moon, Radio, Search, Settings2, ShieldCheck, SlidersHorizontal, Sparkles, Sun, User, Waves, X, Zap } from "lucide-react"
import { baseMetrics, locations, thresholds, trend, type Metrics } from "@/lib/aquasense-data"
import { ChatWidget } from "@/components/chat-widget"

function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  const isLight = mounted && resolvedTheme === "light"
  return (
    <button
      className="theme-toggle"
      onClick={() => setTheme(isLight ? "dark" : "light")}
      aria-label={isLight ? "Switch to dark theme" : "Switch to light theme"}
    >
      {isLight ? <Moon /> : <Sun />}
    </button>
  )
}

function ProfileMenu({ align = "end" }: { align?: "start" | "end" }) {
  const [open, setOpen] = useState(false)
  useEffect(() => {
    if (!open) return
    const close = () => setOpen(false)
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false) }
    window.addEventListener("click", close)
    window.addEventListener("keydown", onKey)
    return () => { window.removeEventListener("click", close); window.removeEventListener("keydown", onKey) }
  }, [open])
  return <div className="profile-menu" onClick={(e) => e.stopPropagation()}>
    <button className="avatar profile-trigger" onClick={() => setOpen((v) => !v)} aria-haspopup="true" aria-expanded={open} aria-label="Open profile menu">TO</button>
    {open && <div className={`profile-dropdown ${align === "start" ? "align-start" : "align-end"}`} role="menu">
      <div className="profile-dropdown-header"><div className="avatar">TO</div><div className="min-w-0"><div className="truncate text-xs font-medium">Tarun Oli</div><div className="truncate text-[10px] text-muted-foreground">Network administrator</div></div></div>
      <div className="profile-dropdown-divider" />
      <button className="profile-dropdown-item" role="menuitem"><User /> View profile</button>
      <button className="profile-dropdown-item" role="menuitem"><Settings2 /> Account settings</button>
      <div className="profile-dropdown-divider" />
      <button className="profile-dropdown-item danger" role="menuitem"><LogOut /> Sign out</button>
    </div>}
  </div>
}

function StateDropdown({ value, onChange, states }: { value: string; onChange: (v: string) => void; states: string[] }) {
  const [open, setOpen] = useState(false)
  useEffect(() => {
    if (!open) return
    const close = () => setOpen(false)
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false) }
    window.addEventListener("click", close)
    window.addEventListener("keydown", onKey)
    return () => { window.removeEventListener("click", close); window.removeEventListener("keydown", onKey) }
  }, [open])
  return <div className="state-dropdown" onClick={(e) => e.stopPropagation()}>
    <button className="state-dropdown-trigger" onClick={() => setOpen((v) => !v)} aria-haspopup="true" aria-expanded={open}>
      <MapPin className="size-3.5 text-primary" />{value === "All" ? "All states" : value}<ChevronDown className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
    </button>
    {open && <div className="state-dropdown-menu" role="menu">
      {states.map((s) => <button key={s} role="menuitem" onClick={() => { onChange(s); setOpen(false) }} className={`state-dropdown-item ${value === s ? "selected" : ""}`}>{s === "All" ? "All states" : s}{value === s && <span className="size-1.5 rounded-full bg-primary shadow-[0_0_10px_#63e6e2]" />}</button>)}
    </div>}
  </div>
}

function useChartTheme() {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  const isLight = mounted && resolvedTheme === "light"
  return {
    grid: isLight ? "rgba(16,23,34,.08)" : "rgba(255,255,255,.06)",
    tick: isLight ? "#55677a" : "#8193a7",
    tooltipBg: isLight ? "#ffffff" : "#101722",
    tooltipBorder: isLight ? "rgba(16,23,34,.12)" : "rgba(255,255,255,.12)",
  }
}

const nav = [{ label: "Overview", icon: LayoutDashboard }, { label: "Analytics", icon: BarChart3 }, { label: "Risk Simulator", icon: SlidersHorizontal }, { label: "About JalSetu", icon: CircleHelp }]
const riskClass = { LOW: "text-emerald-300", MEDIUM: "text-amber-300", HIGH: "text-rose-300" }
const riskBg = { LOW: "bg-emerald-400/10 border-emerald-300/20", MEDIUM: "bg-amber-400/10 border-amber-300/20", HIGH: "bg-rose-400/10 border-rose-300/20" }
const rippleTone = { LOW: "emerald", MEDIUM: "amber", HIGH: "rose" }
const pathogenPositions = [{ top: "22%", left: "58%" }, { top: "48%", left: "78%" }, { top: "68%", left: "52%" }, { top: "34%", left: "88%" }, { top: "58%", left: "68%" }]

function DropletField() {
  const drops = useMemo(() => Array.from({ length: 22 }, (_, i) => ({ left: (i * 4.4 + (i % 3) * 7) % 100, duration: 7 + (i % 6) * 1.8, delay: -(i * 1.7) % 12, scale: .6 + (i % 4) * .18 })), [])
  return <div className="droplet-field" aria-hidden="true">{drops.map((d, i) => <span key={i} className="droplet" style={{ left: `${d.left}%`, animationDuration: `${d.duration}s`, animationDelay: `${d.delay}s`, transform: `scale(${d.scale})` }} />)}</div>
}

const guardianLines: Record<"LOW" | "MEDIUM" | "HIGH", string[]> = {
  LOW: ["This source looks clean — great work keeping cholera and typhoid at bay!", "Readings are steady. I'll keep watch so your village stays safe.", "All clear! Safe water means fewer sick days for everyone."],
  MEDIUM: ["Turbidity is creeping up — that's a warning sign for pathogens like giardia. Worth a field check.", "I'm sensing early trouble here. Let's flag this source before it becomes a health risk.", "Something's shifting in the water. Early warnings save lives — don't ignore this one."],
  HIGH: ["Danger! Conditions favor cholera, dysentery and typhoid bacteria. Isolate this source now.", "This is a red alert — unsafe for drinking until it's inspected. I'm sounding the warning.", "High contamination risk detected. Please advise the community to boil water immediately."],
}

const tricks = ["cartwheel", "jump", "flip", "flex"] as const
type Trick = "idle" | (typeof tricks)[number]

function Guardian({ risk, page }: { risk: "LOW" | "MEDIUM" | "HIGH"; page: string }) {
  const [dismissed, setDismissed] = useState(false)
  const [lineIndex, setLineIndex] = useState(0)
  const [trick, setTrick] = useState<Trick>("idle")
  const tone = risk === "HIGH" ? "rose" : risk === "MEDIUM" ? "amber" : "emerald"
  useEffect(() => { setLineIndex(0) }, [risk])
  useEffect(() => { const id = setInterval(() => setLineIndex((i) => (i + 1) % guardianLines[risk].length), 9000); return () => clearInterval(id) }, [risk])
  const doTrick = () => { const next = tricks[Math.floor(Math.random() * tricks.length)]; setTrick(next); window.setTimeout(() => setTrick("idle"), 1100) }
  useEffect(() => { const id = setInterval(doTrick, 6500); return () => clearInterval(id) }, [])
  useEffect(() => { doTrick() }, [page])
  if (dismissed) return <button className="guardian-avatar-btn guardian-inline-avatar" onClick={() => setDismissed(false)} aria-label="Show Neer, the water guardian"><img src="/images/neer-guardian.png" alt="Neer, the JalSetu water guardian mascot" /></button>
  return <div className={`guardian-widget guardian-inline tone-${tone}`}>
    <div className={`guardian-inline-avatar trick-${trick}`}>
      <img src="/images/neer-guardian.png" alt="Neer, the JalSetu water guardian mascot, a cartoon warrior fighting water-borne pathogens" onClick={doTrick} />
      <button className="guardian-close" onClick={() => setDismissed(true)} aria-label="Dismiss Neer, the water guardian"><X /></button>
    </div>
    <div className="guardian-bubble guardian-bubble-inline" role="status"><div className="g-name"><span className="dot" /> Neer • Water Guardian</div><p>{guardianLines[risk][lineIndex]}</p></div>
  </div>
}

function Spark({ data, tone = "cyan" }: { data: number[]; tone?: "cyan" | "violet" | "amber" | "rose" }) {
  const colors = { cyan: "#63e6e2", violet: "#a78bfa", amber: "#fbbf24", rose: "#fb7185" }
  return <svg viewBox="0 0 120 32" className="h-9 w-28" aria-hidden="true"><defs><linearGradient id={`spark-${tone}`} x1="0" x2="1"><stop stopColor={colors[tone]} stopOpacity=".8" /><stop offset="1" stopColor={colors[tone]} stopOpacity=".1" /></linearGradient></defs><polyline fill="none" stroke={`url(#spark-${tone})`} strokeWidth="2.5" strokeLinecap="round" points={data.map((v, i) => `${i * 120 / (data.length - 1)},${30 - v * 25}`).join(" ")} /></svg>
}

function MetricCard({ label, value, unit, status, tone, data, icon: Icon }: { label: string; value: string; unit: string; status: string; tone: "cyan" | "violet" | "amber" | "rose"; data: number[]; icon: typeof Gauge }) {
  return <article className="metric-card group"><div className="flex items-start justify-between"><div className="icon-tile"><Icon /></div><span className="status-chip">{status}</span></div><div className="mt-7 flex items-end justify-between"><div><p className="eyebrow">{label}</p><div className="mt-2"><span className="metric-value">{value}</span><span className="ml-2 text-sm text-muted-foreground">{unit}</span></div></div><Spark tone={tone} data={data} /></div><div className="mt-5 h-px divider-line" /><div className="mt-3 flex items-center gap-2 text-[11px] text-muted-foreground"><span className="size-1.5 rounded-full bg-emerald-300" /> Stable in the last 24 hours <span className="ml-auto font-mono text-emerald-300">+2.4%</span></div></article>
}

export default function Dashboard() {
  const [active, setActive] = useState("Overview")
  const [selectedId, setSelectedId] = useState("AS-001")
  const [selectedState, setSelectedState] = useState("All")
  const [range, setRange] = useState("24H")
  const [query, setQuery] = useState("")
  const [live, setLive] = useState(true)
  const [metrics, setMetrics] = useState<Metrics>(baseMetrics[selectedId])
  const [mobileOpen, setMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const location = locations.find((item) => item.id === selectedId) ?? locations[0]
  const states = useMemo(() => ["All", ...Array.from(new Set(locations.map((l) => l.state))).sort()], [])
  const villagesInState = useMemo(() => locations.filter((l) => selectedState === "All" || l.state === selectedState), [selectedState])

  useEffect(() => { setMetrics(baseMetrics[selectedId]) }, [selectedId])
  useEffect(() => { if (!villagesInState.some((l) => l.id === selectedId)) setSelectedId(villagesInState[0]?.id ?? locations[0].id) }, [selectedState])
  useEffect(() => { if (!live) return; const id = setInterval(() => setMetrics((m) => ({ ...m, ph: Number((m.ph + (Math.random() - .5) * .02).toFixed(2)), turbidity: Number(Math.max(.2, m.turbidity + (Math.random() - .5) * .12).toFixed(2)), tds: Math.round(m.tds + (Math.random() - .5) * 4), temperature: Number((m.temperature + (Math.random() - .5) * .08).toFixed(1)) })), 3500); return () => clearInterval(id) }, [live])
  const filtered = locations.filter((l) => `${l.village} ${l.district} ${l.state}`.toLowerCase().includes(query.toLowerCase()))
  const chartData = useMemo(() => range === "7D" ? trend.map((x, i) => ({ ...x, hour: `D${i + 1}` })).slice(0, 7) : range === "30D" ? trend.filter((_, i) => i % 3 === 0) : trend, [range])
  const changeView = (label: string) => { setActive(label); setMobileOpen(false) }

  return <div className="relative z-[1] min-h-screen bg-background text-foreground">
    <DropletField />
    <ChatWidget />
    <aside className={`sidebar ${collapsed ? "collapsed" : ""} ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>
      <div className="flex items-center gap-3"><div className="brand-mark shrink-0"><Waves /></div>{!collapsed && <div className="min-w-0"><div className="truncate text-[15px] font-semibold tracking-tight">Jal<span className="text-primary">Setu</span></div><div className="eyebrow mt-0.5">Water intelligence</div></div>}<button className="ml-auto text-muted-foreground lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X /></button></div>
      {!collapsed && <div className="mt-12 flex items-center justify-between"><span className="eyebrow">Workspace</span><span className="rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 font-mono text-[9px] text-primary">PRO</span></div>}
      <nav className={`flex flex-col gap-1 ${collapsed ? "mt-10" : "mt-4"}`}>{nav.map(({ label, icon: Icon }) => <button key={label} onClick={() => changeView(label)} title={collapsed ? label : undefined} className={`nav-item ${active === label ? "active" : ""}`}><Icon />{!collapsed && <>{label}{active === label && <span className="ml-auto size-1.5 rounded-full bg-primary shadow-[0_0_10px_#63e6e2]" />}</>}</button>)}</nav>
      {!collapsed && <div className="mt-auto rounded-2xl status-box p-4"><div className="flex items-center gap-2 text-xs font-medium"><span className="status-dot" /> Network status <span className="ml-auto text-[10px] text-emerald-300">LIVE</span></div><div className="mt-4 flex items-end justify-between"><span className="text-xs text-muted-foreground">Sensors online</span><span className="font-mono text-sm text-primary">46 <span className="text-muted-foreground">/ 48</span></span></div><div className="mt-2 h-1 overflow-hidden rounded-full progress-track"><div className="h-full w-[96%] rounded-full bg-gradient-to-r from-primary to-violet-400" /></div><div className="mt-3 text-[10px] text-muted-foreground">Last sync 12 seconds ago</div></div>}
      {collapsed && <div className="mt-auto flex justify-center"><span className="status-dot" title="46 / 48 sensors online" /></div>}
      <div className={`flex items-center border-top-soft pt-5 ${collapsed ? "mt-5 justify-center" : "mt-5 gap-3"}`}><ProfileMenu align="start" />{!collapsed && <><div className="min-w-0"><div className="truncate text-xs font-medium">Tarun Oli</div><div className="truncate text-[10px] text-muted-foreground">Network administrator</div></div><Settings2 className="ml-auto size-4 text-muted-foreground" /></>}</div>
      <button className="sidebar-collapse-btn hidden lg:flex" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} title={collapsed ? "Expand sidebar" : "Collapse sidebar"}>{collapsed ? <ChevronsRight /> : <ChevronsLeft />}</button>
    </aside>
    {mobileOpen && <button className="fixed inset-0 z-10 bg-background/80 backdrop-blur-sm lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation" />}
    <main className={`relative z-[1] transition-[padding] duration-300 ${collapsed ? "lg:pl-[84px]" : "lg:pl-[280px]"}`}><header className="topbar"><div className="flex items-center gap-3"><button className="text-muted-foreground lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu /></button><div className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex"><span>Operations</span><span className="text-separator">/</span><span className="text-foreground">{active}</span></div></div><div className="flex items-center gap-3"><button onClick={() => setLive(!live)} className={`live-toggle ${live ? "on" : ""}`}><span className="status-dot" />{live ? "Live telemetry" : "Paused"}</button><button className="icon-button" aria-label="Notifications"><Bell /><span /></button><ThemeToggle /><ProfileMenu /></div></header>
      <div className="page-wrap"><div className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><div className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-[.18em] text-primary"><Sparkles className="size-3.5" /> Northeast India <span className="text-separator">•</span> 7 states monitored</div><div className="flex flex-wrap items-center gap-4"><h1 className="hero-title">{active === "Overview" ? "Water, made visible." : active}</h1><Guardian risk={metrics.risk} page={active} /></div><p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{active === "Overview" ? "One calm command center for the health of every community water source." : "Explore your network and make better decisions with JalSetu."}</p></div><div className="flex items-center gap-2"><button onClick={() => setLive(!live)} className="action-button"><Activity className={live ? "text-primary" : ""} />{live ? "Streaming" : "Resume stream"}</button><button className="icon-button" aria-label="Settings"><Settings2 /></button></div></div>
      {active === "Overview" && <><section className="overview-grid"><section className="glass-panel location-panel"><div className="flex items-start justify-between gap-4"><div><div className="eyebrow flex items-center gap-2"><MapPin className="size-3.5 text-primary" /> Selected location</div><div className="mt-3 flex flex-wrap items-center gap-3"><h2 className="text-xl font-semibold tracking-tight">{location.village}</h2><span className="status-chip border-emerald-300/20 bg-emerald-300/10 text-emerald-300">{location.status}</span></div><p className="mt-1.5 text-xs text-muted-foreground">{location.district}, {location.state} <span className="mx-2 text-separator">•</span> Sensor {location.id}</p></div><div className="relative"><Search className="absolute left-3 top-2.5 size-4 text-muted-foreground" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Find a village" className="search-input" />{query && <div className="search-results">{filtered.slice(0, 4).map((l) => <button key={l.id} onClick={() => { setSelectedId(l.id); setQuery(""); setSelectedState("All") }} className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs"><MapPin className="size-3.5 text-primary" />{l.village}<span className="ml-auto text-muted-foreground">{l.district}</span></button>)}</div>}</div></div><div className="mt-6 flex flex-wrap items-center gap-3"><StateDropdown value={selectedState} onChange={setSelectedState} states={states} /><span className="text-[11px] text-muted-foreground">{villagesInState.length} village{villagesInState.length === 1 ? "" : "s"}</span></div><div className="mt-4 flex flex-wrap gap-2">{villagesInState.map((l) => <button key={l.id} onClick={() => setSelectedId(l.id)} className={`location-pill ${selectedId === l.id ? "selected" : ""}`} title={l.state}>{l.village}</button>)}</div></section><section className={`glass-panel risk-panel ${riskBg[metrics.risk]}`}><div className={`ripple-rings tone-${rippleTone[metrics.risk]}`} aria-hidden="true"><span /><span /><span /></div>{metrics.risk !== "LOW" && <div className={`microbe-cluster ${riskClass[metrics.risk]}`} aria-hidden="true">{pathogenPositions.map((p, i) => <span key={i} className="pathogen-dot" style={{ top: p.top, left: p.left, animationDelay: `${i * -1.1}s`, animationDuration: `${5 + (i % 3)}s` }} />)}</div>}<div className="flex items-start justify-between"><div><div className="eyebrow flex items-center gap-2"><ShieldCheck className="size-3.5" /> Safety classification</div><div className={`mt-4 font-mono text-4xl font-semibold tracking-tight ${riskClass[metrics.risk]}`}>{metrics.risk}</div><p className="mt-2 max-w-xs text-xs leading-5 text-muted-foreground">{metrics.risk === "LOW" ? "All indicators are within recommended community thresholds." : metrics.risk === "MEDIUM" ? "Elevated turbidity may support pathogen growth — field review recommended." : "Contamination risk detected — likely conditions for water-borne pathogens."}</p></div><div className="risk-orbit"><ShieldCheck /></div></div><div className="mt-7 flex items-end justify-between"><div><div className="eyebrow">Confidence score</div><div className="mt-2 font-mono text-lg">94.8<span className="text-xs text-muted-foreground"> / 100</span></div></div><div className="mini-bars">{[35, 55, 42, 72, 62, 88, 76, 94].map((h, i) => <i key={i} style={{ height: `${h}%` }} />)}</div></div></section></section><div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="pH level" value={metrics.ph.toFixed(2)} unit="pH" status="Optimal" tone="cyan" data={trend.map(x => x.ph / 8)} icon={Droplets} /><MetricCard label="Turbidity" value={metrics.turbidity.toFixed(2)} unit="NTU" status={metrics.turbidity < 5 ? "Within range" : "Review"} tone="violet" data={trend.map(x => x.turbidity / 6)} icon={Waves} /><MetricCard label="Total dissolved solids" value={`${metrics.tds}`} unit="mg/L" status="Within range" tone="amber" data={trend.map(x => x.tds / 500)} icon={Gauge} /><MetricCard label="Temperature" value={metrics.temperature.toFixed(1)} unit="°C" status="Normal" tone="rose" data={trend.map(x => x.temperature / 32)} icon={Zap} /></div><section className="glass-panel mt-5 p-5 sm:p-6"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><h2 className="text-base font-semibold">Telemetry history</h2><p className="mt-1 text-xs text-muted-foreground">Live readings for {location.village}</p></div><div className="range-toggle">{["24H", "7D", "30D"].map((r) => <button key={r} onClick={() => setRange(r)} className={range === r ? "selected" : ""}>{r}</button>)}</div></div><div className="mt-7 grid gap-8 lg:grid-cols-2"><ChartBox title="pH level" dataKey="ph" color="#63e6e2" data={chartData} domain={[6, 8.5]} /><ChartBox title="Turbidity" dataKey="turbidity" color="#a78bfa" data={chartData} domain={[0, 6]} /><ChartBox title="TDS concentration" dataKey="tds" color="#fbbf24" data={chartData} domain={[100, 500]} /><ChartBox title="Temperature" dataKey="temperature" color="#fb7185" data={chartData} domain={[16, 34]} /></div></section></>}
      {active === "Analytics" && <Analytics />}{active === "Risk Simulator" && <Simulator metrics={metrics} />}{active === "About JalSetu" && <About />}</div></main></div>
}

function ChartBox({ title, dataKey, color, data, domain }: { title: string; dataKey: string; color: string; data: object[]; domain: [number, number] }) { const ct = useChartTheme(); return <div className="min-w-0"><div className="mb-3 flex items-center justify-between"><span className="text-xs font-medium text-muted-foreground">{title}</span><span className="font-mono text-[10px] text-primary/80">{thresholds[dataKey as keyof typeof thresholds]}</span></div><div className="h-48"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><defs><linearGradient id={`fill-${dataKey}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={color} stopOpacity={.22} /><stop offset="100%" stopColor={color} stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke={ct.grid} vertical={false} /><XAxis dataKey="hour" tick={{ fill: ct.tick, fontSize: 9 }} tickLine={false} axisLine={false} interval="preserveStartEnd" /><YAxis domain={domain} tick={{ fill: ct.tick, fontSize: 9 }} tickLine={false} axisLine={false} width={30} /><Tooltip contentStyle={{ background: ct.tooltipBg, border: `1px solid ${ct.tooltipBorder}`, borderRadius: 10, fontSize: 11 }} /><Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#fill-${dataKey})`} strokeWidth={2} dot={false} /></AreaChart></ResponsiveContainer></div></div> }
function Analytics() { const ct = useChartTheme(); const bars = locations.map((l, i) => ({ name: l.village.split(" ")[0], score: 92 - i * 4 + (i % 3) * 3 })); return <div className="grid gap-5 lg:grid-cols-[1.3fr_1fr]"><section className="glass-panel p-5 sm:p-6"><div className="flex items-center justify-between"><div><h2 className="text-base font-semibold">Network health score</h2><p className="mt-1 text-xs text-muted-foreground">Comparative confidence across active locations.</p></div><span className="status-chip border-primary/20 bg-primary/10 text-primary">94.8 avg</span></div><div className="mt-7 h-80"><ResponsiveContainer width="100%" height="100%"><BarChart data={bars}><CartesianGrid stroke={ct.grid} vertical={false} /><XAxis dataKey="name" tick={{ fill: ct.tick, fontSize: 10 }} axisLine={false} tickLine={false} /><YAxis domain={[0, 100]} tick={{ fill: ct.tick, fontSize: 10 }} axisLine={false} tickLine={false} /><Tooltip contentStyle={{ background: ct.tooltipBg, border: `1px solid ${ct.tooltipBorder}`, borderRadius: 10, fontSize: 11 }} /><Bar dataKey="score" fill="#63e6e2" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer></div></section><section className="glass-panel p-5 sm:p-6"><div className="eyebrow">Reference system</div><h2 className="mt-3 text-lg font-semibold">Safe water thresholds</h2><div className="mt-6 flex flex-col gap-4">{Object.entries(thresholds).map(([key, value]) => <div key={key} className="flex items-center justify-between border-bottom-soft pb-4 text-sm"><span className="capitalize text-muted-foreground">{key}</span><span className="font-mono text-primary">{value}</span></div>)}</div></section></div> }
function Simulator({ metrics }: { metrics: Metrics }) { const [turbidity, setTurbidity] = useState(metrics.turbidity); const risk = turbidity > 5 ? "HIGH" : turbidity > 3.5 ? "MEDIUM" : "LOW"; return <section className="glass-panel max-w-3xl p-6 sm:p-8"><div className="flex items-start justify-between"><div><div className="eyebrow flex items-center gap-2"><SlidersHorizontal className="size-3.5 text-primary" /> Scenario lab</div><h2 className="mt-4 text-2xl font-semibold tracking-tight">Risk simulator</h2><p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">Adjust a sensor variable and see how the water safety classification responds in real time.</p></div><div className="icon-tile"><AlertTriangle className={riskClass[risk]} /></div></div><div className="mt-10"><div className="flex justify-between text-sm"><span>Turbidity</span><span className="font-mono text-primary">{turbidity.toFixed(1)} NTU</span></div><input type="range" min="0" max="10" step="0.1" value={turbidity} onChange={(e) => setTurbidity(Number(e.target.value))} className="mt-5 w-full accent-[#63e6e2]" /><div className="mt-2 flex justify-between text-[10px] text-muted-foreground"><span>Clear</span><span>Threshold: 5 NTU</span><span>Critical</span></div></div><div className={`mt-10 rounded-2xl border p-6 ${riskBg[risk]}`}><div className="eyebrow">Projected classification</div><div className={`mt-3 font-mono text-5xl font-semibold ${riskClass[risk]}`}>{risk}</div><p className="mt-3 text-xs leading-5 text-muted-foreground">{risk === "LOW" ? "Water remains within the recommended turbidity threshold." : risk === "MEDIUM" ? "An alert would be raised for field review." : "Immediate inspection and source isolation recommended."}</p></div></section> }
function About() { return <section className="glass-panel max-w-3xl p-6 sm:p-8"><div className="flex items-center gap-4"><div className="brand-mark size-12"><Droplets /></div><div><h2 className="text-2xl font-semibold">JalSetu</h2><p className="text-xs text-muted-foreground">Community-first water intelligence</p></div></div><p className="mt-8 text-sm leading-7 text-muted-foreground">JalSetu turns distributed water sensors into a calm, actionable view of the communities they serve. This console monitors 48 locations across Northeast India, combining live telemetry, threshold checks, and explainable risk scoring.</p><div className="mt-8 grid gap-3 sm:grid-cols-3">{[["48", "Locations monitored"], ["96%", "Sensors online"], ["24/7", "Telemetry coverage"]].map(([v, l]) => <div key={l} className="rounded-xl stat-card p-4"><div className="font-mono text-2xl text-primary">{v}</div><div className="mt-1 text-xs text-muted-foreground">{l}</div></div>)}</div></section> }
