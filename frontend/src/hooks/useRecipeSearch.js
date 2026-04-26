import { useCallback, useEffect, useState } from "react";
import { searchByVibe } from "../services/api";

const STORAGE_KEY = "recipeSearchState_v1";

function loadPersisted() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const EMPTY = {
  vibe: "",
  inventory: [],
  vibesFilter: [],
  diet: "any",
  result: null,
};

export function useRecipeSearch() {
  const persisted = loadPersisted();
  const [vibe, setVibe] = useState(persisted?.vibe ?? EMPTY.vibe);
  const [inventory, setInventory] = useState(persisted?.inventory ?? EMPTY.inventory);
  const [vibesFilter, setVibesFilter] = useState(persisted?.vibesFilter ?? EMPTY.vibesFilter);
  const [diet, setDiet] = useState(persisted?.diet ?? EMPTY.diet);
  const [result, setResult] = useState(persisted?.result ?? EMPTY.result);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const snapshot = { vibe, inventory, vibesFilter, diet, result };
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot)); } catch {}
  }, [vibe, inventory, vibesFilter, diet, result]);

  const search = useCallback(async () => {
    if (!vibe.trim()) {
      setError("Please describe a vibe first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await searchByVibe({
        vibe,
        inventory,
        vibesFilter: vibesFilter.length ? vibesFilter : null,
        diet,
        limit: 12,
      });
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Search failed");
    } finally {
      setLoading(false);
    }
  }, [vibe, inventory, vibesFilter, diet]);

  const reset = useCallback(() => {
    setVibe(EMPTY.vibe);
    setInventory(EMPTY.inventory);
    setVibesFilter(EMPTY.vibesFilter);
    setDiet(EMPTY.diet);
    setResult(EMPTY.result);
    setError(null);
    try { sessionStorage.removeItem(STORAGE_KEY); } catch {}
  }, []);

  return {
    vibe, setVibe,
    inventory, setInventory,
    vibesFilter, setVibesFilter,
    diet, setDiet,
    loading, error, result,
    search, reset,
  };
}
