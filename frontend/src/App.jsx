import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Pokemon from "./pages/Pokemon";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/pokemon?id=25" replace />} />
        <Route path="/pokemon" element={<Pokemon />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;