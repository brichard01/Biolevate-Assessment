import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Pokemon from "./pages/Pokemon";
import Move from "./pages/Move";
import Ability from "./pages/Ability";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/pokemon?id=25" replace />} />
        <Route path="/pokemon" element={<Pokemon />} />
        <Route path="/move" element={<Move />} />
        <Route path="/ability" element={<Ability />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;