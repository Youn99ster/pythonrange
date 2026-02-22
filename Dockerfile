# ============================================================
# HackShop Web 服务 Docker 镜像
# 基础镜像: Python 3.11 slim（体积小，适合生产部署）
# 构建步骤:
#   1. 先复制 requirements.txt 并安装依赖（利用 Docker 层缓存）
#   2. 再复制应用代码
#   3. 创建非 root 用户 hackshop 运行服务
# 入口: start.sh（等待 MySQL → 迁移/建表 → 可选播种 → Gunicorn）
# ============================================================

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 先安装依赖，代码变更时不会重新安装（利用层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户，降低容器逃逸风险
RUN groupadd -r hackshop && useradd -r -g hackshop -d /app hackshop \
    && mkdir -p /app/logs /app/app/uploads \
    && chown -R hackshop:hackshop /app

USER hackshop
EXPOSE 8000
CMD ["sh", "start.sh"]
