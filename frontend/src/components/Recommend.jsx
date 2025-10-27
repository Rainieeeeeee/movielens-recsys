import React, { useEffect, useState } from "react";

function Recommend({ userId, topN }) {
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    console.log("📤 Fetching for userId:", userId, "topN:", topN);
    if (!userId) return;

    fetch("http://127.0.0.1:8000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: parseInt(userId, 10),
        topn: parseInt(topN, 10),
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Server responded with status ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // 取 items 字段，如果没有就空数组
        setRecs(data.items || []);
      })
      .catch((err) => {
        console.error("Error fetching recommendations:", err);
        setRecs([]);  // 出错时清空推荐
      });
  }, [userId, topN]);

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Top {topN} Recommendations for User {userId}</h2>
      <ul>
        {recs.map((item) => (
          <li key={item.movieId}>
            {item.title} — Predicted Rating: {item.est?.toFixed(2) ?? "N/A"}
          </li>
        ))}
      </ul>
      {recs.length === 0 && <p>No recommendations found.</p>}
    </div>
  );
}

export default Recommend;
