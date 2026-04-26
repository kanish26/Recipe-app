import { Link } from "react-router-dom";

export default function RecipeCard({ recipe }) {
  const pct = recipe.similarity != null ? Math.round(recipe.similarity * 100) : null;
  return (
    <Link
      to={`/recipe/${recipe.id}`}
      state={{ similarity: recipe.similarity }}
      className="block rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-gray-900 capitalize">{recipe.title}</h3>
        {pct != null && <span className="text-xs text-gray-500 shrink-0">{pct}% match</span>}
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {(recipe.vibes || []).map((v) => (
          <span key={v} className="text-xs rounded-full bg-amber-50 text-amber-700 px-2 py-0.5">
            {v}
          </span>
        ))}
      </div>
      <p className="mt-3 text-sm text-gray-600 line-clamp-2">
        {(recipe.ingredients || []).slice(0, 6).join(", ")}
        {recipe.ingredients?.length > 6 ? "…" : ""}
      </p>
    </Link>
  );
}
