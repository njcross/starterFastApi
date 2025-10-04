// frontend/src/pages/Login.tsx
import React, { useState } from "react";
import "./Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function sendLink(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      const res = await fetch("/api/auth/request-link", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      setMsg("If that email exists, we’ve sent a sign-in link.");
    } catch (err: any) {
      setMsg(err?.message ?? "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 420, margin: "48px auto", fontFamily: "system-ui, sans-serif" }}>
      <h1>Sign in</h1>
      <p>Enter your email and we’ll send you a one-time sign-in link.</p>
      <form onSubmit={sendLink} style={{ display: "grid", gap: 12 }}>
        <input
          type="email"
          placeholder="you@example.com"
          value={email}
          required
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: 10, fontSize: 16 }}
        />
        <button disabled={busy} type="submit" style={{ padding: 10, fontSize: 16 }}>
          {busy ? "Sending…" : "Send magic link"}
        </button>
      </form>
      {msg && <p style={{ marginTop: 12 }}>{msg}</p>}
    </main>
  );
}
