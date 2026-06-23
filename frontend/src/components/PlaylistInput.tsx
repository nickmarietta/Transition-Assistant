"use client";

import { useState } from "react";

interface Props {
  onLoad: (url: string) => void;
  loading: boolean;
}

export default function PlaylistInput({ onLoad, loading }: Props) {
  const [url, setUrl] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (url.trim()) onLoad(url.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Paste a Spotify playlist URL…"
        className="flex-1 rounded-lg bg-zinc-800 px-4 py-2 text-sm outline-none ring-1 ring-zinc-700 focus:ring-green-500"
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="rounded-lg bg-green-500 px-4 py-2 text-sm font-medium text-black hover:bg-green-400 disabled:opacity-50"
      >
        {loading ? "Loading…" : "Load"}
      </button>
    </form>
  );
}
