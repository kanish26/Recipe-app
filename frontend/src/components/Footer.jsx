export default function Footer() {
  const mailto = "mailto:feedback@example.com?subject=Recipe%20Vibes%20Feedback";
  return (
    <footer id="disclaimer" className="mt-10 sm:mt-16 border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-8 grid gap-6 sm:grid-cols-2">
        <div>
          <h3 className="font-semibold text-gray-900">Disclaimer</h3>
          <p className="mt-2 text-sm text-gray-600 leading-relaxed">
            Recipe Vibes is a demo app. Recipes are sourced from public datasets
            (Food.com, RecipeNLG, Indian Food 101) and may contain inaccuracies.
            Always verify ingredients for allergens and dietary restrictions.
            Vibe and dietary filters are heuristic — review each recipe before cooking.
          </p>
        </div>
        <div className="flex flex-col items-start sm:items-end">
          <h3 className="font-semibold text-gray-900">Feedback</h3>
          <p className="mt-2 text-sm text-gray-600">Spotted a bug or have ideas?</p>
          <a
            href={mailto}
            className="mt-3 inline-flex items-center rounded-lg bg-orange-500 px-4 py-2 text-white text-sm font-medium hover:bg-orange-600 transition"
          >
            Send feedback
          </a>
        </div>
      </div>
      <div className="text-center text-xs text-gray-500 py-4 border-t border-gray-100">
        © {new Date().getFullYear()} Recipe Vibes · Built by Kanish Godani with FastAPI, Supabase, and Ollama
      </div>
    </footer>
  );
}
