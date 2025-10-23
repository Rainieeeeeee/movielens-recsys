# backend/recommender.py
import os
import pandas as pd
import joblib
from surprise import Dataset, Reader

class Recommender:
    def __init__(self,
                 data_dir="../data/ml-1m",
                 model_path="../models/svd_model.pkl",
                 pop_path="../models/pop_fallback.csv"):
        # 路径
        ratings_path = f"{data_dir}/ratings.dat"
        movies_path  = f"{data_dir}/movies.dat"

        # 读取原始数据（注意 movies 用 latin-1）
        self.ratings = pd.read_csv(
            ratings_path, sep="::",
            names=["userId","movieId","rating","timestamp"],
            engine="python"
        )
        self.movies = pd.read_csv(
            movies_path, sep="::",
            names=["movieId","title","genres"],
            engine="python",
            encoding="latin-1"
        )

        # Surprise 用于 ID 映射（predict 也支持原始 id）
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(self.ratings[["userId","movieId","rating"]], reader)
        self.trainset = data.build_full_trainset()

        # 载入 SVD 模型
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"请确保已在 notebook 中保存模型到 ../models/svd_model.pkl"
            )
        self.algo = joblib.load(model_path)

        # 冷启动兜底（贝叶斯平均文件）
        self.pop_fallback = None
        if os.path.exists(pop_path):
            self.pop_fallback = pd.read_csv(pop_path)

    def topn_for_user(self, user_id: int, N: int = 10) -> pd.DataFrame:
        """给定 user_id，返回 Top-N 推荐（排除已看过）"""
        seen = set(self.ratings[self.ratings["userId"] == user_id]["movieId"].tolist())
        all_items = set(self.ratings["movieId"].unique().tolist())
        candidates = list(all_items - seen)
        if not candidates:
            return pd.DataFrame(columns=["title","genres","movieId","est"])

        preds = []
        for mid in candidates:
            est = self.algo.predict(user_id, mid).est
            preds.append((mid, est))

        preds.sort(key=lambda x: x[1], reverse=True)
        topn = preds[:N]
        out = (
            pd.DataFrame(topn, columns=["movieId","est"])
            .merge(self.movies[["movieId","title","genres"]], on="movieId", how="left")
            .sort_values("est", ascending=False)
            .reset_index(drop=True)
        )
        return out

    def cold_start_topn(self, N: int = 10) -> pd.DataFrame:
        """冷启动：返回热门/贝叶斯平均 Top-N"""
        if self.pop_fallback is not None:
            # 统一列名返回
            cols = [c for c in ["title","genres","movieId","bayes"] if c in self.pop_fallback.columns]
            return self.pop_fallback.head(N)[cols]

        # 兜底：按出现次数排序
        pop = (
            self.ratings.groupby("movieId")["rating"].size().reset_index(name="pop")
            .merge(self.movies[["movieId","title","genres"]], on="movieId", how="left")
            .sort_values("pop", ascending=False)
        )
        return pop.head(N)[["title","genres","movieId","pop"]]