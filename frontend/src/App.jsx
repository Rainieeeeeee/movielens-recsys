import { useState } from "react";
import Recommend from "./components/Recommend";

function App() {
  const [userId, setUserId] = useState("");
  const [topN, setTopN] = useState(10);

  const handleSubmit = (e) => {
    e.preventDefault();
    // 这里可触发 Recommend 组件更新
    setUserId(userId);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>MovieLens Recommender</h1>
      <form onSubmit={handleSubmit}>
        <label>User ID: </label>
        <input
          type="number"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          required
        />
        <label> Top-N: </label>
        <input
          type="number"
          value={topN}
          onChange={(e) => setTopN(e.target.value)}
          min="1"
        />
        <button type="submit">Get Recommendations</button>
      </form>

      {userId && <Recommend userId={parseInt(userId, 10)} topN={parseInt(topN, 10)} />}
    </div>
  );
}

export default App;
