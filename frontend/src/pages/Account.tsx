import React, { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/SimpleAuthContext";
import authService from "@/services/authService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API_CONFIG } from "@/config/api";

const Account: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [keys, setKeys] = useState<Array<{ id: string; name: string; prefix: string; created_at: string }>>([]);
  const [name, setName] = useState("production");
  const [freshKey, setFreshKey] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const data = await authService.listApiKeys();
      setKeys(data.keys || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load keys");
    }
  };

  useEffect(() => {
    if (isAuthenticated) load();
  }, [isAuthenticated]);

  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/signin" replace />;

  const createKey = async () => {
    setError("");
    setFreshKey("");
    try {
      const created = await authService.createApiKey(name);
      setFreshKey(created.api_key);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create key");
    }
  };

  const revoke = async (id: string) => {
    await authService.deleteApiKey(id);
    await load();
  };

  return (
    <div className="container max-w-2xl mx-auto px-4 py-12 space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Account</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {user?.fullName || user?.username} · {user?.email}
        </p>
      </div>

      <section className="rounded-xl border p-6 space-y-4">
        <h2 className="font-semibold">API keys</h2>
        <p className="text-sm text-muted-foreground">
          Use these to call the detector without a browser session:
          <code className="block mt-2 text-xs bg-muted p-2 rounded">
            curl -X POST {API_CONFIG.BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000')}/v1/detect -H "X-API-Key: ifk_…" -F file=@video.mp4
          </code>
        </p>
        <div className="flex gap-2">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Key name" />
          <Button onClick={createKey}>Create key</Button>
        </div>
        {freshKey && (
          <p className="text-sm bg-amber-50 dark:bg-amber-950/40 border border-amber-200 rounded p-3 break-all">
            Copy now — it will not be shown again:<br />
            <strong>{freshKey}</strong>
          </p>
        )}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <ul className="divide-y text-sm">
          {keys.map((k) => (
            <li key={k.id} className="py-3 flex items-center justify-between gap-3">
              <span>
                {k.name} · <code>{k.prefix}…</code>
              </span>
              <Button variant="outline" size="sm" onClick={() => revoke(k.id)}>
                Revoke
              </Button>
            </li>
          ))}
          {keys.length === 0 && <li className="py-3 text-muted-foreground">No keys yet.</li>}
        </ul>
      </section>

      <Link className="text-sm underline" to="/try">
        Back to Try It
      </Link>
    </div>
  );
};

export default Account;
