# Note Summary Linux 部署指南

## 一、服务器要求

| 项目 | 最低要求 |
|------|----------|
| 系统 | Ubuntu 20.04+ / CentOS 7+ / Debian 10+ |
| CPU | 1 核 |
| 内存 | 1 GB |
| 磁盘 | 10 GB |
| 网络 | 需访问 `dashscope.aliyuncs.com`（AI 接口） |

## 二、安装依赖

### 2.1 Python 3.9+

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# CentOS
sudo yum install -y python3 python3-pip
```

验证：

```bash
python3 --version   # 需要 >= 3.9
```

### 2.2 Node.js 18+

```bash
# 使用 NodeSource 安装
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 或用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 18
```

验证：

```bash
node --version   # >= 18.0.0
npm --version
```

### 2.3 PostgreSQL（如使用 PostgreSQL）

```bash
# Ubuntu
sudo apt install -y postgresql postgresql-contrib

# 启动
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

创建数据库和用户：

```bash
sudo -u postgres psql

# 在 psql 中执行
CREATE USER notes_user WITH PASSWORD 'your_password';
CREATE DATABASE knowledge_db OWNER notes_user;
\q
```

安装 pgvector 扩展：

```bash
# Ubuntu
sudo apt install -y postgresql-14-pgvector   # 版本号对应你的 PG 版本

# 在数据库中启用
sudo -u postgres psql -d knowledge_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2.4 Nginx（反向代理）

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

## 三、上传项目

将项目上传到服务器（例如 `/opt/note-summary`）：

```bash
# 方式一：git clone（如果项目在 Git 仓库）
cd /opt
sudo git clone <your-repo-url> note-summary

# 方式二：scp 上传
# 本地执行：
scp -r ./note-summary user@server-ip:/opt/note-summary
```

## 四、配置环境变量

```bash
cd /opt/note-summary

# 创建 .env 文件
cat > .env << 'EOF'
OPENAI_API_KEY=your-dashscope-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3.5-27b

OPENAI_EMBEDDING_API_KEY=your-dashscope-api-key
OPENAI_EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_EMBEDDING_MODEL=qwen-vl-embedding

DATABASE_URL=postgresql://notes_user:your_password@127.0.0.1:5432/knowledge_db

SECRET_KEY=$(openssl rand -hex 32)
EOF

# 生成随机 SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

## 五、构建后端

```bash
cd /opt/note-summary/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 验证
python -c "from app.main import app; print('OK')"
```

## 六、构建前端

```bash
cd /opt/note-summary/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建产物在 dist/ 目录，后端会自动托管
```

## 七、启动服务

### 方式一：直接启动（测试用）

```bash
cd /opt/note-summary

# 启动后端（后台运行）
cd backend
source venv/bin/activate
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
cd ..

# 验证
sleep 3
curl http://127.0.0.1:8000/docs -o /dev/null -w "%{http_code}"
# 应输出 200
```

### 方式二：Systemd 服务（推荐生产使用）

创建后端服务文件：

```bash
sudo tee /etc/systemd/system/note-summary.service << 'EOF'
[Unit]
Description=Note Summary Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/note-summary/backend
ExecStart=/opt/note-summary/backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/opt/note-summary/backend/venv/bin

[Install]
WantedBy=multi-user.target
EOF
```

启动并设置开机自启：

```bash
sudo systemctl daemon-reload
sudo systemctl start note-summary
sudo systemctl enable note-summary

# 查看状态
sudo systemctl status note-summary

# 查看日志
sudo journalctl -u note-summary -f
```

## 八、配置 Nginx 反向代理

```bash
sudo tee /etc/nginx/sites-available/note-summary << 'EOF'
server {
    listen 80;
    server_name your-domain.com;   # 改为你的域名或 IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # AI 接口可能较慢，增大超时
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/note-summary /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 检查配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## 九、配置 HTTPS（可选，推荐）

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com

# 自动续期已内置，验证：
sudo certbot renew --dry-run
```

## 十、验证部署

```bash
# 1. 检查后端
curl http://127.0.0.1:8000/docs -o /dev/null -w "%{http_code}\n"

# 2. 检查 Nginx
curl http://your-domain.com/ -o /dev/null -w "%{http_code}\n"

# 3. 检查注册接口
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123456","confirm_password":"test123456"}'
```

## 十一、常用运维命令

```bash
# 查看后端状态
sudo systemctl status note-summary

# 重启后端
sudo systemctl restart note-summary

# 查看实时日志
sudo journalctl -u note-summary -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 重新加载 Nginx 配置
sudo nginx -s reload

# 更新代码后重新部署
cd /opt/note-summary
sudo systemctl stop note-summary

# 更新后端
cd backend && source venv/bin/activate && pip install -r requirements.txt

# 重新构建前端
cd ../frontend && npm install && npm run build

# 启动
sudo systemctl start note-summary
```

## 十二、文件权限

```bash
# 设置项目目录所有者
sudo chown -R www-data:www-data /opt/note-summary

# 确保虚拟环境可执行
chmod +x /opt/note-summary/backend/venv/bin/python

# .env 文件仅 owner 可读
chmod 600 /opt/note-summary/.env
```

## 十三、防火墙配置

```bash
# 只开放 80 和 443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 十四、目录结构总览

```
/opt/note-summary/
├── .env                    # 环境变量（敏感信息）
├── start.sh                # 开发启动脚本
├── backend/
│   ├── venv/               # Python 虚拟环境
│   ├── requirements.txt    # Python 依赖
│   └── app/                # 后端代码
├── frontend/
│   ├── dist/               # 前端构建产物（后端托管）
│   ├── package.json
│   └── src/                # 前端源码
└── backend.log             # 日志文件（直接启动方式）
```
