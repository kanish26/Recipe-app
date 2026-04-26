import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="fixed top-0 inset-x-0 z-40 backdrop-blur bg-white/80 border-b border-gray-200">
      <div className="mx-auto max-w-6xl px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center text-white font-bold shadow-sm">
            RV
          </div>
          <span className="font-semibold text-gray-900">Recipe Vibes</span>
        </Link>
        <div className="hidden sm:flex items-center gap-5 text-sm text-gray-600">
          <Link to="/" className="hover:text-orange-600">Home</Link>
          <a href="#disclaimer" className="hover:text-orange-600">About</a>
        </div>
      </div>
    </nav>
  );
}
