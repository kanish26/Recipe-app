export default function LoadingState({ label = "Finding recipes..." }) {
  return (
    <div className="flex items-center gap-3 text-gray-600">
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
