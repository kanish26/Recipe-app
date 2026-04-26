import { useState } from "react";

export default function InventoryInput({ items, onChange }) {
  const [draft, setDraft] = useState("");

  function add() {
    const next = draft.split(",").map((s) => s.trim()).filter(Boolean);
    if (!next.length) return;
    onChange([...new Set([...items, ...next])]);
    setDraft("");
  }

  function remove(item) {
    onChange(items.filter((x) => x !== item));
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        What's in your kitchen? (optional)
      </label>
      <div className="flex gap-2">
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())}
          placeholder="chicken, rice, onion..."
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-base shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none"
        />
        <button
          type="button"
          onClick={add}
          className="rounded-lg bg-gray-900 px-4 py-2 text-white text-sm hover:bg-gray-700"
        >
          Add
        </button>
      </div>
      {items.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {items.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 rounded-full bg-indigo-50 text-indigo-700 px-3 py-1 text-sm"
            >
              {item}
              <button
                onClick={() => remove(item)}
                className="text-indigo-400 hover:text-indigo-700"
                aria-label={`remove ${item}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
