import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Pokemon from "./pages/Pokemon";
import Move from "./pages/Move";
import Ability from "./pages/Ability";
import Search from "./pages/Search";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/search" replace />} />
        <Route path="/pokemon" element={<Pokemon />} />
        <Route path="/move" element={<Move />} />
        <Route path="/ability" element={<Ability />} />
        <Route path="/search" element={<Search />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;