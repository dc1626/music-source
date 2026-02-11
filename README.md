# LX Music 源服务器

搭建自己的音乐源，对接 LX Music 桌面软件。

## 快速开始

### 1. 安装依赖

```bash
pip install flask requests
```

### 2. 启动服务

```bash
python source_server.py
```

### 3. 配置到 LX Music

1. 打开 LX Music
2. 设置 → 自定义源
3. 输入源地址：`http://你的IP:6000`

## API 接口文档

### 搜索歌曲

```http
GET /search?keyword=歌名&page=1&limit=20
```

**响应:**

```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "1",
        "title": "晴天",
        "artist": "周杰伦",
        "album": "叶惠美",
        "duration": 267,
        "pic": "https://example.com/cover.jpg",
        "source": "custom"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20
  }
}
```

### 获取歌曲详情

```http
GET /song?id=歌曲ID
```

**响应:**

```json
{
  "success": true,
  "data": {
    "id": "1",
    "title": "晴天",
    "artist": "周杰伦",
    "album": "叶惠美",
    "duration": 267,
    "pic": "https://example.com/cover.jpg",
    "lyric": "[00:00.00]歌词内容",
    "tlyric": "",
    "url": "https://example.com/music.mp3",
    "source": "custom"
  }
}
```

### 获取播放链接

```http
GET /url?id=歌曲ID
```

**响应:**

```json
{
  "success": true,
  "data": {
    "id": "1",
    "url": "https://example.com/music.mp3",
    "br": 320
  }
}
```

### 获取歌词

```http
GET /lyric?id=歌曲ID
```

**响应:**

```json
{
  "success": true,
  "data": {
    "id": "1",
    "lyric": "[00:00.00]原歌词",
    "tlyric": "[00:00.00]翻译歌词"
  }
}
```

## 对接真实音乐平台

编辑 `source_server.py`，替换 TODO 部分：

### 网易云音乐 示例

```python
import requests

def search_netease(keyword, page=1, limit=20):
    """搜索网易云音乐"""
    response = requests.get(
        "https://music.163.com/api/search/get",
        params={
            "s": keyword,
            "type": 1,
            "limit": limit,
            "offset": (page-1) * limit
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    data = response.json()
    
    results = []
    for item in data['result']['songs']:
        results.append({
            "id": str(item['id']),
            "title": item['name'],
            "artist": item['ar'][0]['name'] if item['ar'] else "",
            "album": item['al']['name'],
            "duration": item['dt'] // 1000,
            "pic": item['al']['picUrl'],
            "source": "netease"
        })
    
    return results

def get_url_netease(song_id):
    """获取网易云播放链接"""
    response = requests.get(
        f"https://music.163.com/api/song/url?id={song_id}",
        params={"br": 320000}
    )
    data = response.json()
    
    return {
        "url": data['data'][0]['url'],
        "br": 320
    }
```

### 酷狗音乐 示例

```python
def search_kugou(keyword):
    """搜索酷狗音乐"""
    response = requests.get(
        "https://search Recommendapi.kugou.com",
        params={
            "keyword": keyword,
            "page": 1,
            "limit": 20
        }
    )
    # 处理返回数据...
```

## 目录结构

```
music-source/
├── source_server.py   # 主服务
├── config.json       # 配置文件
├── README.md        # 说明文档
└── .github/
    └── workflows/
        └── deploy.yml  # 自动部署
```

## 部署

### Linux systemd

```ini
[Unit]
Description=LX Music Source Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/music-source
ExecStart=/usr/bin/python3 /path/to/music-source/source_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install flask requests

EXPOSE 6000

CMD ["python", "source_server.py"]
```

## License

MIT
