import RecipeCard from "./RecipeCard";

export default function RecipeList({ recipes }) {
  if (!recipes?.length) {
    return <p className="text-gray-500 text-sm">No recipes found. Try a different vibe.</p>;
  }
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {recipes.map((r) => (
        <RecipeCard key={r.id} recipe={r} />
      ))}
    </div>
  );
}
