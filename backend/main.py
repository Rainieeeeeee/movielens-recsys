# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommender import Recommender

# 创建 FastAPI 实例
app = FastAPI(title="MovieLens Recommender API", version="1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 如果你还可能从其它端口或地址访问前端，也可加上
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- CORS 结束 ---

# 初始化推荐系统（只加载一次，避免重复加载模型）
rec = Recommender()

# 定义请求体
class RecommendRequest(BaseModel):
    user_id: int
    topn: int = 10


@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok"}


@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    给指定用户推荐 Top-N 电影
    如果用户是冷启动（未在模型中出现），则返回热门推荐
    """
    df = rec.topn_for_user(req.user_id, req.topn)

    if df.empty:
        cold = rec.cold_start_topn(req.topn)
        return {
            "user_id": req.user_id,
            "cold_start": True,
            "items": cold.to_dict(orient="records")
        }

    return {
        "user_id": req.user_id,
        "cold_start": False,
        "items": df[["title", "genres", "movieId", "est"]].to_dict(orient="records")
    }


@app.get("/coldstart")
def coldstart(topn: int = 10):
    """返回冷启动推荐结果"""
    df = rec.cold_start_topn(topn)
    return {"items": df.to_dict(orient="records")}
