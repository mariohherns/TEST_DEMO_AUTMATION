import { useEffect, useState } from "react";
import { getAnalytics } from "../lib/api";
import { goTo } from "../lib/nav";

export default function Analytics() {
  const [data, setData] = useState(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    if (!token) {
      goTo("/login");
      return;
    }

    (async () => {
      const a = await getAnalytics(token);
      setData(a);
    })();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Analytics</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
      <p><a href="/jobs">Back to Jobs</a></p>
    </div>
  );
}

