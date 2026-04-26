import { useEffect, useState } from "react";
import { listVibes } from "../services/api";

export default function MoodSelector({ value, onChange }) {
  const [vibes, setVibes] = useState([]);

  useEffect(() => {
    listVibes().then(setVibes).catch(() => setVibes([]));
  }, []);

  function append(tag) {
    const current = (value || "").trim();
    // Avoid duplicate insertions.
    if (current.toLowerCase().includes(tag.toLowerCase())) return;
    const next = current ? `${current}, ${tag}` : tag;
    onChange(next);
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">What's the vibe?</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. cozy comfort food for a rainy night"
        className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none"
      />
      {vibes.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wide text-gray-500 mb-2">
            Tap a tag to add it to your query
          </div>
          <div className="flex flex-wrap gap-2">
            {vibes.map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => append(v)}
                className="text-xs rounded-full border border-gray-300 bg-white px-3 py-1 hover:border-indigo-400 hover:text-indigo-600 transition"
              >
                + {v}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
