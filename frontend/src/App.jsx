import { useState, useEffect, createContext, useContext, useCallback } from "react";

// ─── API ──────────────────────────────────────────────
const API = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.reload();
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Xatolik yuz berdi");
  }
  return res.json();
}

// ─── Auth Context ─────────────────────────────────────
const AuthContext = createContext(null);
function useAuth() { return useContext(AuthContext); }

function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(() => {
    try { return JSON.parse(localStorage.getItem("admin") || "null"); } catch { return null; }
  });

  const login = async (username, password) => {
    const form = new URLSearchParams({ username, password });
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("admin", JSON.stringify(data.admin));
    setAdmin(data.admin);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("admin");
    setAdmin(null);
  };

  return <AuthContext.Provider value={{ admin, login, logout }}>{children}</AuthContext.Provider>;
}

// ─── Icons ────────────────────────────────────────────
const Icon = ({ d, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);
const Icons = {
  grid:    "M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 0h7v7h-7z",
  users:   "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm14 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75",
  msg:     "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
  send:    "M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z",
  bar:     "M18 20V10M12 20V4M6 20v-6",
  gear:    "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 0v3m0-12V3m9 9h-3M6 12H3m15.364-6.364l-2.121 2.121M8.757 15.243l-2.121 2.121M18.364 18.364l-2.121-2.121M8.757 8.757 6.636 6.636",
  logout:  "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9",
  plus:    "M12 5v14M5 12h14",
  check:   "M20 6L9 17l-5-5",
  x:       "M18 6 6 18M6 6l12 12",
  refresh: "M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15",
  eye:     "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zm11 3a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
  tg:      "M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z",
};

// ─── Reusable Components ──────────────────────────────
function StatCard({ label, value, sub, color = "#1D9E75" }) {
  return (
    <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, padding: "14px 18px", flex: 1, minWidth: 140 }}>
      <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 600, color, lineHeight: 1.2 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function Badge({ children, type = "ok" }) {
  const colors = {
    ok:   { bg: "#d1fae5", color: "#065f46" },
    warn: { bg: "#fef3c7", color: "#92400e" },
    info: { bg: "#dbeafe", color: "#1e40af" },
    err:  { bg: "#fee2e2", color: "#991b1b" },
  };
  const c = colors[type] || colors.ok;
  return (
    <span style={{ background: c.bg, color: c.color, fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 4 }}>
      {children}
    </span>
  );
}

function MiniBar({ data = [], color = "#1D9E75" }) {
  const max = Math.max(...data.map(d => d.count), 1);
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 56 }}>
      {data.map((d, i) => (
        <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
          <div style={{ width: "100%", background: color, borderRadius: 3, height: Math.max(4, (d.count / max) * 48), opacity: 0.85 }} />
          <span style={{ fontSize: 10, color: "var(--muted)" }}>{d.date}</span>
        </div>
      ))}
    </div>
  );
}

function Table({ columns, data, emptyText = "Ma'lumot yo'q" }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "0.5px solid var(--border)" }}>
            {columns.map(c => (
              <th key={c.key} style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500, color: "var(--muted)", whiteSpace: "nowrap" }}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={columns.length} style={{ padding: "24px 12px", textAlign: "center", color: "var(--muted)" }}>{emptyText}</td></tr>
          ) : data.map((row, i) => (
            <tr key={i} style={{ borderBottom: "0.5px solid var(--border)" }}>
              {columns.map(c => (
                <td key={c.key} style={{ padding: "10px 12px", whiteSpace: "nowrap" }}>
                  {c.render ? c.render(row[c.key], row) : row[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Modal({ open, onClose, title, children }) {
  if (!open) return null;
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center" }}
      onClick={onClose}>
      <div style={{ background: "var(--bg)", border: "0.5px solid var(--border)", borderRadius: 12, padding: 24, minWidth: 380, maxWidth: "90vw" }}
        onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
          <div style={{ fontWeight: 600, fontSize: 15 }}>{title}</div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", padding: 4 }}>
            <Icon d={Icons.x} size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function Input({ label, ...props }) {
  return (
    <div style={{ marginBottom: 14 }}>
      {label && <label style={{ display: "block", fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>{label}</label>}
      <input {...props} style={{ width: "100%", boxSizing: "border-box", padding: "9px 12px", borderRadius: 8, border: "0.5px solid var(--border)", background: "var(--bg)", color: "var(--fg)", fontSize: 14, outline: "none", ...props.style }} />
    </div>
  );
}

function Textarea({ label, ...props }) {
  return (
    <div style={{ marginBottom: 14 }}>
      {label && <label style={{ display: "block", fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>{label}</label>}
      <textarea {...props} style={{ width: "100%", boxSizing: "border-box", padding: "9px 12px", borderRadius: 8, border: "0.5px solid var(--border)", background: "var(--bg)", color: "var(--fg)", fontSize: 14, outline: "none", resize: "vertical", ...props.style }} />
    </div>
  );
}

// ─── Pages ────────────────────────────────────────────

function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/stats/dashboard").then(d => { setStats(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ color: "var(--muted)", padding: 32 }}>Yuklanmoqda...</div>;
  if (!stats) return <div style={{ color: "var(--muted)", padding: 32 }}>Ma'lumot olishda xatolik</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <StatCard label="Jami foydalanuvchilar" value={stats.users.total.toLocaleString()} sub={`+${stats.users.new_month} bu oy`} color="#1D9E75" />
        <StatCard label="Faol foydalanuvchilar" value={stats.users.active.toLocaleString()} color="#378ADD" />
        <StatCard label="Jami xabarlar" value={stats.messages.total.toLocaleString()} sub={`Bugun: ${stats.messages.today}`} color="#7F77DD" />
        <StatCard label="Broadcastlar" value={stats.broadcasts.total.toLocaleString()} color="#EF9F27" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, padding: 18 }}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Oxirgi 7 kun — Xabarlar</div>
          <MiniBar data={stats.charts.daily_messages} color="#1D9E75" />
        </div>
        <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, padding: 18 }}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Oxirgi 7 kun — Yangi foydalanuvchilar</div>
          <MiniBar data={stats.charts.daily_users} color="#7F77DD" />
        </div>
      </div>
    </div>
  );
}

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (q = "") => {
    setLoading(true);
    try {
      const d = await apiFetch(`/users/?limit=50&search=${encodeURIComponent(q)}`);
      setUsers(d.items);
      setTotal(d.total);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const t = setTimeout(() => load(search), 400);
    return () => clearTimeout(t);
  }, [search, load]);

  const changeStatus = async (id, status) => {
    await apiFetch(`/users/${id}/status?status=${status}`, { method: "PATCH" });
    load(search);
  };

  const statusBadge = (s) => {
    if (s === "active") return <Badge type="ok">Faol</Badge>;
    if (s === "blocked") return <Badge type="err">Bloklangan</Badge>;
    return <Badge type="warn">Kutmoqda</Badge>;
  };

  const cols = [
    { key: "telegram_id", label: "Telegram ID" },
    { key: "first_name",  label: "Ism" },
    { key: "username",    label: "Username", render: v => v ? `@${v}` : "—" },
    { key: "language_code", label: "Til" },
    { key: "status",      label: "Status", render: v => statusBadge(v) },
    { key: "created_at",  label: "Qo'shilgan", render: v => v ? v.substring(0, 10) : "—" },
    { key: "id", label: "Amal", render: (id, row) => (
      <div style={{ display: "flex", gap: 6 }}>
        {row.status !== "active"  && <button onClick={() => changeStatus(id, "active")}  style={{ fontSize: 11, padding: "3px 8px", borderRadius: 4, border: "0.5px solid var(--border)", background: "none", cursor: "pointer", color: "#1D9E75" }}>Faollashtirish</button>}
        {row.status !== "blocked" && <button onClick={() => changeStatus(id, "blocked")} style={{ fontSize: 11, padding: "3px 8px", borderRadius: 4, border: "0.5px solid var(--border)", background: "none", cursor: "pointer", color: "#D85A30" }}>Bloklash</button>}
      </div>
    )},
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <input
          placeholder="Qidirish: ism, username..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, padding: "9px 14px", borderRadius: 8, border: "0.5px solid var(--border)", background: "var(--bg)", color: "var(--fg)", fontSize: 14, outline: "none" }}
        />
        <span style={{ fontSize: 13, color: "var(--muted)" }}>Jami: {total}</span>
        <button onClick={() => load(search)} style={{ padding: "9px 12px", borderRadius: 8, border: "0.5px solid var(--border)", background: "none", cursor: "pointer", color: "var(--fg)" }}>
          <Icon d={Icons.refresh} size={16} />
        </button>
      </div>
      <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, overflow: "hidden" }}>
        {loading ? <div style={{ padding: 32, color: "var(--muted)", textAlign: "center" }}>Yuklanmoqda...</div>
          : <Table columns={cols} data={users} emptyText="Foydalanuvchilar topilmadi" />}
      </div>
    </div>
  );
}

function MessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/messages/?limit=100").then(d => { setMessages(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const cols = [
    { key: "user_id",   label: "Foydalanuvchi ID" },
    { key: "direction", label: "Yo'nalish", render: v => v === "in" ? <Badge type="info">Kiruvchi</Badge> : <Badge type="ok">Chiquvchi</Badge> },
    { key: "text",      label: "Matn", render: v => v ? (v.length > 60 ? v.substring(0, 60) + "…" : v) : <span style={{ color: "var(--muted)" }}>—</span> },
    { key: "media_type", label: "Media", render: v => v || "—" },
    { key: "is_read",   label: "O'qildi", render: v => v ? <Badge type="ok">Ha</Badge> : <Badge type="warn">Yo'q</Badge> },
    { key: "created_at", label: "Vaqt", render: v => v ? v.substring(0, 16).replace("T", " ") : "—" },
  ];

  return (
    <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, overflow: "hidden" }}>
      {loading ? <div style={{ padding: 32, color: "var(--muted)", textAlign: "center" }}>Yuklanmoqda...</div>
        : <Table columns={cols} data={messages} emptyText="Xabarlar yo'q" />}
    </div>
  );
}

function BroadcastsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ title: "", text: "" });
  const [sending, setSending] = useState(false);
  const [toast, setToast] = useState("");

  const load = async () => {
    setLoading(true);
    try { const d = await apiFetch("/broadcasts/"); setItems(d); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(""), 3000); };

  const submit = async () => {
    if (!form.title || !form.text) return;
    setSending(true);
    try {
      await apiFetch("/broadcasts/", { method: "POST", body: JSON.stringify(form) });
      setModal(false);
      setForm({ title: "", text: "" });
      showToast("Broadcast yaratildi va yuborilmoqda!");
      load();
    } catch (e) {
      showToast("Xatolik: " + e.message);
    } finally { setSending(false); }
  };

  const sendNow = async (id) => {
    await apiFetch(`/broadcasts/${id}/send`, { method: "POST" });
    showToast("Yuborish boshlandi!");
    load();
  };

  const statusBadge = (s) => {
    if (s === "sent") return <Badge type="ok">Yuborildi</Badge>;
    if (s === "scheduled") return <Badge type="info">Yuborilmoqda</Badge>;
    if (s === "failed") return <Badge type="err">Xatolik</Badge>;
    return <Badge type="warn">Qoralama</Badge>;
  };

  const cols = [
    { key: "title", label: "Sarlavha" },
    { key: "text",  label: "Matn", render: v => v.length > 50 ? v.substring(0, 50) + "…" : v },
    { key: "status", label: "Status", render: v => statusBadge(v) },
    { key: "sent_count", label: "Yuborildi", render: v => v || 0 },
    { key: "fail_count", label: "Xatolik", render: v => v || 0 },
    { key: "created_at", label: "Yaratilgan", render: v => v ? v.substring(0, 10) : "—" },
    { key: "id", label: "Amal", render: (id, row) => row.status === "draft" && (
      <button onClick={() => sendNow(id)} style={{ fontSize: 11, padding: "3px 10px", borderRadius: 4, border: "0.5px solid var(--border)", background: "none", cursor: "pointer", color: "#1D9E75" }}>
        Yuborish
      </button>
    )},
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {toast && (
        <div style={{ position: "fixed", top: 20, right: 20, background: "#1D9E75", color: "#fff", padding: "10px 20px", borderRadius: 8, zIndex: 200, fontSize: 14 }}>
          {toast}
        </div>
      )}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>Jami: {items.length}</span>
        <button onClick={() => setModal(true)}
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 16px", borderRadius: 8, border: "0.5px solid var(--border)", background: "#1D9E75", color: "#fff", cursor: "pointer", fontSize: 13, fontWeight: 500 }}>
          <Icon d={Icons.plus} size={16} /> Yangi broadcast
        </button>
      </div>
      <div style={{ background: "var(--bg2)", border: "0.5px solid var(--border)", borderRadius: 10, overflow: "hidden" }}>
        {loading ? <div style={{ padding: 32, color: "var(--muted)", textAlign: "center" }}>Yuklanmoqda...</div>
          : <Table columns={cols} data={items} emptyText="Broadcastlar yo'q" />}
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title="Yangi broadcast">
        <Input label="Sarlavha" placeholder="Broadcast sarlavhasi" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
        <Textarea label="Xabar matni (HTML qo'llab-quvvatlanadi)" placeholder="<b>Yangilik!</b> Matn kiriting..." value={form.text} onChange={e => setForm(f => ({ ...f, text: e.target.value }))} rows={6} />
        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 8 }}>
          <button onClick={() => setModal(false)} style={{ padding: "9px 18px", borderRadius: 8, border: "0.5px solid var(--border)", background: "none", cursor: "pointer", fontSize: 13 }}>Bekor</button>
          <button onClick={submit} disabled={sending || !form.title || !form.text}
            style={{ padding: "9px 18px", borderRadius: 8, border: "none", background: form.title && form.text ? "#1D9E75" : "#ccc", color: "#fff", cursor: "pointer", fontSize: 13, fontWeight: 500 }}>
            {sending ? "Yuborilmoqda…" : "Yuborish"}
          </button>
        </div>
      </Modal>
    </div>
  );
}

// ─── Login Page ───────────────────────────────────────
function LoginPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try { await login(form.username, form.password); }
    catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg3)" }}>
      <div style={{ background: "var(--bg)", border: "0.5px solid var(--border)", borderRadius: 14, padding: 36, width: 360 }}>
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: "#1D9E75", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 14px", color: "#fff" }}>
            <Icon d={Icons.tg} size={24} />
          </div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>InfoSys</div>
          <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>Admin panel</div>
        </div>
        <form onSubmit={submit}>
          <Input label="Login" type="text" placeholder="admin" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} />
          <Input label="Parol" type="password" placeholder="••••••••" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
          {error && <div style={{ color: "#D85A30", fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button type="submit" disabled={loading}
            style={{ width: "100%", padding: "11px", borderRadius: 8, border: "none", background: "#1D9E75", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer", marginTop: 4 }}>
            {loading ? "Kirish…" : "Kirish"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ─── Main Layout ──────────────────────────────────────
const PAGES = [
  { id: "dashboard",   label: "Boshqaruv",       icon: Icons.grid },
  { id: "users",       label: "Foydalanuvchilar", icon: Icons.users },
  { id: "messages",    label: "Xabarlar",         icon: Icons.msg },
  { id: "broadcasts",  label: "Bildirishnomalar", icon: Icons.send },
];

function AppLayout() {
  const { admin, logout } = useAuth();
  const [page, setPage] = useState("dashboard");

  const renderPage = () => {
    if (page === "dashboard")  return <DashboardPage />;
    if (page === "users")      return <UsersPage />;
    if (page === "messages")   return <MessagesPage />;
    if (page === "broadcasts") return <BroadcastsPage />;
    return null;
  };

  const pageTitle = PAGES.find(p => p.id === page)?.label || "";

  return (
    <div style={{ display: "flex", height: "100vh", background: "var(--bg3)", fontFamily: "system-ui, sans-serif", color: "var(--fg)" }}>
      {/* Sidebar */}
      <div style={{ width: 220, background: "var(--bg)", borderRight: "0.5px solid var(--border)", display: "flex", flexDirection: "column", flexShrink: 0 }}>
        <div style={{ padding: "20px 18px 16px", borderBottom: "0.5px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: "#1D9E75", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", flexShrink: 0 }}>
              <Icon d={Icons.tg} size={18} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>InfoSys</div>
              <div style={{ fontSize: 11, color: "var(--muted)" }}>Admin panel</div>
            </div>
          </div>
        </div>

        <nav style={{ flex: 1, padding: "10px 8px" }}>
          {PAGES.map(p => (
            <button key={p.id} onClick={() => setPage(p.id)}
              style={{
                display: "flex", alignItems: "center", gap: 10, width: "100%",
                padding: "9px 12px", borderRadius: 8, border: "none", cursor: "pointer",
                background: page === p.id ? "var(--bg3)" : "transparent",
                color: page === p.id ? "var(--fg)" : "var(--muted)",
                fontWeight: page === p.id ? 500 : 400,
                fontSize: 13, marginBottom: 2, textAlign: "left",
              }}>
              <Icon d={p.icon} size={16} />
              {p.label}
            </button>
          ))}
        </nav>

        <div style={{ padding: "12px 8px", borderTop: "0.5px solid var(--border)" }}>
          <div style={{ padding: "8px 12px", fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>
            <div style={{ fontWeight: 500, color: "var(--fg)", fontSize: 13 }}>{admin?.full_name || admin?.username}</div>
            <div>{admin?.is_superuser ? "Superadmin" : "Admin"}</div>
          </div>
          <button onClick={logout}
            style={{ display: "flex", alignItems: "center", gap: 10, width: "100%", padding: "9px 12px", borderRadius: 8, border: "none", background: "transparent", cursor: "pointer", color: "var(--muted)", fontSize: 13 }}>
            <Icon d={Icons.logout} size={16} /> Chiqish
          </button>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ padding: "16px 24px", borderBottom: "0.5px solid var(--border)", background: "var(--bg)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ fontSize: 16, fontWeight: 600 }}>{pageTitle}</div>
          <div style={{ fontSize: 12, color: "var(--muted)" }}>
            {new Date().toLocaleDateString("uz-UZ", { day: "numeric", month: "long", year: "numeric" })}
          </div>
        </div>
        <div style={{ flex: 1, overflow: "auto", padding: 24 }}>
          {renderPage()}
        </div>
      </div>
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────
export default function App() {
  const { admin } = useAuth();
  return admin ? <AppLayout /> : <LoginPage />;
}

export function Root() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
