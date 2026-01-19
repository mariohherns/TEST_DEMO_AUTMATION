import { useEffect, useState } from "react";
import { createJob, listJobs, getResult, getJob } from "../lib/api";
import { goTo } from "../lib/nav";

export default function Jobs() {
  const [input, setInput] = useState("");
  const [jobs, setJobs] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [result, setResult] = useState(null);
  const [msg, setMsg] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  async function refresh() {
    if (!token) return;
    const data = await listJobs(token);
    setJobs(data);
  }

  useEffect(() => {
    if (!token) {
      goTo("/login");
      return; 
    }
    refresh();
    const t = setInterval(refresh, 2000);
    return () => clearInterval(t);
  }, []);

  async function submit() {
    setMsg("");
    try {
      await createJob(token, input);
      setInput("");
      await refresh();
    } catch (e) {
      setMsg("Failed to submit job");
    }
  }

  async function inspect(jobId) {
    setSelectedId(jobId);
    setDetail(null);
    setResult(null);

    const j = await getJob(token, jobId);
    setDetail(j);

    try {
      const r = await getResult(token, jobId);
      setResult(r);
    } catch {
      setResult({ message: "Result not ready (expected if status not DONE)" });
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Jobs</h2>

      <div>
        <input data-testid="job-input" style={{ width: 420 }} value={input} onChange={e => setInput(e.target.value)} />
        <button data-testid="submit-job" onClick={submit} style={{ marginLeft: 8 }}>Submit</button>
        <button onClick={refresh} style={{ marginLeft: 8 }}>Refresh</button>
      </div>

      <p style={{ marginTop: 10 }}>
      </p>

      {msg && <p>{msg}</p>}

      <table data-testid="jobs-table" border="1" cellPadding="8" style={{ marginTop: 12 }}>
        <thead>
          <tr>
            <th>ID</th><th>Status</th><th>User</th><th>Created</th><th>Action</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map(j => (
            <tr key={j.id}>
              <td>{j.id}</td>
              <td>{j.status}</td>
              <td>{j.submitted_by}</td>
              <td>{j.created_at}</td>
              <td><button onClick={() => inspect(j.id)}>Inspect</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedId && (
        <div style={{ marginTop: 16 }}>
          <h3>Job #{selectedId}</h3>
          <h4>Job detail</h4>
          <pre>{JSON.stringify(detail, null, 2)}</pre>
          <h4>Result</h4>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
