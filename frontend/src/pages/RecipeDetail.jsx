import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { getRecipe } from "../services/api";
import LoadingState from "../components/LoadingState";

export default function RecipeDetail() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const similarity = location.state?.similarity;
  const pct = typeof similarity === "number" ? Math.round(similarity * 100) : null;

  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getRecipe(id).then(setRecipe).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <p className="p-10 text-red-600">{error}</p>;
  if (!recipe) return <div className="p-10"><LoadingState label="Loading recipe..." /></div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-indigo-600 hover:underline"
      >
        &larr; Back to results
      </button>

      <div className="mt-4 flex items-start justify-between gap-4">
        <h1 className="text-3xl font-bold text-gray-900 capitalize">{recipe.title}</h1>
        {pct != null && (
          <span className="shrink-0 rounded-full bg-indigo-50 text-indigo-700 px-3 py-1 text-sm font-medium">
            {pct}% match
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {(recipe.vibes || []).map((v) => (
          <span key={v} className="text-xs rounded-full bg-amber-50 text-amber-700 px-2 py-0.5">
            {v}
          </span>
        ))}
      </div>

      {recipe.cuisine && (
        <div className="mt-2 text-sm text-gray-500">Cuisine: {recipe.cuisine}</div>
      )}

      <section className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900">Ingredients</h2>
        <ul className="mt-3 list-disc list-inside space-y-1 text-gray-700">
          {(recipe.ingredients || []).map((ing, i) => (
            <li key={i}>{ing}</li>
          ))}
        </ul>
      </section>

      <section className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900">Instructions</h2>
        <pre className="mt-3 whitespace-pre-wrap text-gray-700 font-sans text-base leading-relaxed">
{recipe.instructions}
        </pre>
      </section>

      <div className="mt-10">
        <Link to="/" className="text-sm text-gray-500 hover:text-indigo-600">
          Back to home
        </Link>
      </div>
    </div>
  );
}
