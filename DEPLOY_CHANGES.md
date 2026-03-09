# 文件变更清单

## 需要同步到服务器的文件更新

由于 Milvus 端口配置从 19530 变更为 19532，以下文件需要更新：

### 1. Backend 配置文件

**文件**: `backend/app/core/config.py`

变更内容:
```python
# Milvus 端口从 19530 改为 19532
milvus_port: int = Field(default=19532, alias="MILVUS_PORT")  # 原: 19530
```

### 2. 环境变量文件

**文件**: `.env`

变更内容:
```bash
# Milvus 端口配置更新
MILVUS_PORT=19532  # 原: 19530
```

### 3. Docker 配置文件

**文件**: `docker/docker-compose.yml`

变更内容:
```yaml
containers:
  - milvus-etcd → cc-rag-etcd
  - milvus-minio → cc-rag-minio
  - milvus-standalone → cc-rag-milvus
  - milvus-attu → cc-rag-attu

ports:
  milvus:
    - "19532:19530"  # 原: "19530:19530"
    - "19093:9091"   # 新增

  attu:
    - "13002:3000"   # 原: "3000:3000"

networks:
  cc-rag-network    # 原: milvus-network
```

### 4. README 更新

**文件**: `README.md`

- 更新 Attu 访问地址
- 添加端口配置说明

## 服务器操作步骤

### 方式 1: 传输新文件

```bash
# 在本地执行，传输更新后的文件到服务器
scp backend/app/core/config.py chenxuhao@服务器IP:~/project/cc_dev_RAG/backend/app/core/config.py
scp .env chenxuhao@服务器IP:~/project/cc_dev_RAG/.env
```

然后在服务器上执行：
```bash
# 更新 Docker 配置文件
cd ~/project/cc_dev_RAG/docker
cat > docker-compose.yml << 'EOF'
[上面给出的docker-compose.yml完整内容]
EOF

# 重启 Docker 容器
docker-compose down
docker-compose up -d

# 重启后端（如果在运行）
cd ~/project/cc_dev_RAG/backend
# 停止旧的后端进程，然后用新配置启动
```

### 方式 2: 在服务器上直接修改

```bash
cd ~/project/cc_dev_RAG

# 1. 修改 config.py 中的 Milvus 端口
sed -i 's/milvus_port: int = Field(default=19530/milvus_port: int = Field(default=19532/' backend/app/core/config.py

# 2. 修改 .env 中的 Milvus 端口
sed -i 's/MILVUS_PORT=19530/MILVUS_PORT=19532/' .env

# 3. 更新 Docker 配置
cd docker
# 使用之前提供的 cat 命令创建新配置
```

## 验证更新

更新完成后，验证配置是否正确：

```bash
# 1. 检查 Docker 容器状态
docker-compose ps

# 应该看到以下容器运行：
# - cc-rag-etcd
# - cc-rag-minio
# - cc-rag-milvus
# - cc-rag-attu

# 2. 检查端口监听
sudo netstat -tulpn | grep 19532

# 3. 测试 Attu 访问
# 在浏览器打开: http://服务器IP:13002

# 4. 启动后端后测试连接
cd ~/project/cc_dev_RAG/backend
python -c "from app.core.config import settings; print(settings.milvus_port)"
# 应该输出: 19532
```

## 工作端口总结

| 服务 | 端口 | 说明 |
|------|------|------|
| Milvus API | **19532** | 后端连接使用 |
| Milvus 监控 | 19093 | 内部监控端口 |
| Attu 管理界面 | **13002** | Web UI 访问 |
| 后端 API | **8000** | FastAPI 服务 |
| 前端 | **5173** | Vue 开发服务器 |

注意 `MILVUS_PORT` 环境变量应设置为 `19532`，这样后端才能正确连接 Milvus。
