import MoodSelector from "../components/MoodSelector";
import InventoryInput from "../components/InventoryInput";
import DietSelector from "../components/DietSelector";
import RecipeList from "../components/RecipeList";
import LoadingState from "../components/LoadingState";
import SamplePrompts from "../components/SamplePrompts";
import { useRecipeSearch } from "../hooks/useRecipeSearch";

export default function Home() {
  const s = useRecipeSearch();

  function handleSubmit(e) {
    e.preventDefault();
    s.search();
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Recipe Vibes</h1>
        <p className="mt-2 text-gray-600">Tell us the mood — get recipes that match it.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div>
          <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <MoodSelector value={s.vibe} onChange={s.setVibe} />
            <DietSelector value={s.diet} onChange={s.setDiet} />
            <InventoryInput items={s.inventory} onChange={s.setInventory} />

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={s.loading}
                className="flex-1 rounded-lg bg-indigo-600 px-4 py-3 text-white font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {s.loading ? "Searching..." : "Find recipes"}
              </button>
              <button
                type="button"
                onClick={s.reset}
                className="rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
                title="Clear all and start over"
              >
                Reset
              </button>
            </div>
            {s.error && <p className="text-sm text-red-600">{s.error}</p>}
          </form>

          <section className="mt-8">
            {s.loading && <LoadingState />}
            {s.result && !s.loading && (
              <>
                {s.result.narrative && (
                  <div className="mb-6 rounded-xl bg-amber-50 border border-amber-200 p-4 text-amber-900 text-sm leading-relaxed">
                    {s.result.narrative}
                  </div>
                )}
                <RecipeList recipes={s.result.recipes} />
              </>
            )}
          </section>
        </div>

        <div className="lg:sticky lg:top-20 lg:self-start">
          <SamplePrompts onPick={s.setVibe} />
        </div>
      </div>
    </div>
  );
}
