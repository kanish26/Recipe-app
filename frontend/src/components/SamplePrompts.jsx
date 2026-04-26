const SAMPLES = [
  "cozy comfort food for a rainy night",
  "quick weeknight dinner in 20 minutes",
  "spicy bold indian curry",
  "fresh light summer salad",
  "romantic date night pasta",
  "sweet treat for a birthday",
  "post-workout protein bowl",
  "hearty winter stew",
];

export default function SamplePrompts({ onPick }) {
  return (
    <aside className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Try these</h3>
      <ul className="space-y-2">
        {SAMPLES.map((s) => (
          <li key={s}>
            <button
              onClick={() => onPick(s)}
              className="w-full text-left text-sm rounded-lg border border-gray-200 px-3 py-2 text-gray-700 hover:border-orange-300 hover:bg-orange-50 transition"
            >
              {s}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
