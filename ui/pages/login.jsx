import { useState } from "react";
import { login } from "../lib/api";

export default function Login() {
  const [username, setU] = useState("viewer");
  const [password, setP] = useState("viewer123");
  const [err, setErr] = useState("");

  async function onLogin() {
    setErr("");
    try {
      const data = await login(username, password);
      localStorage.setItem("token", data.access_token);
      window.location.href = "/jobs";
    } catch {
      setErr("Login failed");
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>QA Lab</h2>
      <p>Login (OAuth2 password flow)</p>

      <div>
        <input data-testid="username" placeholder="username" value={username} onChange={e => setU(e.target.value)} />
      </div>
      <div style={{ marginTop: 8 }}>
        <input  data-testid="password" placeholder="password" type="password" value={password} onChange={e => setP(e.target.value)} />
      </div>

      <button data-testid="login-btn" style={{ marginTop: 12 }} onClick={onLogin}>Login</button>
      {err && <p style={{ marginTop: 12 }}>{err}</p>}
    </div>
  );
}
