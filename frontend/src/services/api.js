import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL, timeout: 120000 });

export async function searchByVibe({ vibe, inventory = [], vibesFilter = null, diet = "any", limit = 10 }) {
  const { data } = await client.post("/recipes/by-vibe", {
    vibe,
    inventory,
    vibes_filter: vibesFilter,
    diet,
    limit,
  });
  return data;
}

export async function getRecipe(id) {
  const { data } = await client.get(`/recipes/${id}`);
  return data;
}

export async function listVibes() {
  const { data } = await client.get("/recipes/vibes");
  return data.vibes;
}
