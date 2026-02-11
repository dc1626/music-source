#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LX Music Source Server - 音乐源服务器
协议格式参考: https://github.com/lxmusics/lx-music-api-server

支持的接口:
1. /search?keyword=关键词  - 搜索歌曲
2. /song?id=xxx            - 获取歌曲详情
3. /url?id=xxx             - 获取播放链接
4. /lyric?id=xxx           - 获取歌词

启动服务: python source_server.py
端口: 6000
"""

from flask import Flask, request, jsonify
import json
import hashlib
import time

app = Flask(__name__)

# 模拟数据（替换为真实API调用）
MOCK_SONGS = {
    "1": {
        "id": "1",
        "title": "晴天",
        "artist": "周杰伦",
        "album": "叶惠美",
        "duration": 267,
        "pic": "https://example.com/cover/qingtian.jpg",
        "url": "https://example.com/music/qingtian.mp3",
        "lyric": "[00:00.00]词: 方文山 曲: 周杰伦\n[00:05.00]故事的小黄花"
    },
    "2": {
        "id": "2",
        "title": "夜曲",
        "artist": "周杰伦",
        "album": "十一月的萧邦",
        "duration": 285,
        "pic": "https://example.com/cover/yequ.jpg",
        "url": "https://example.com/music/yequ.mp3",
        "lyric": "[00:00.00]词: 方文山 曲: 周杰伦\n[00:05.00]一群嗜血的蚂蚁"
    },
    "3": {
        "id": "3",
        "title": "稻香",
        "artist": "周杰伦",
        "album": "稻香",
        "duration": 235,
        "pic": "https://example.com/cover/daoxiang.jpg",
        "url": "https://example.com/music/daoxiang.mp3",
        "lyric": "[00:00.00]词: 周杰伦 曲: 周杰伦\n[00:05.00]稻花香里说丰年"
    }
}


def success_response(data):
    """成功响应格式"""
    return jsonify({
        "success": True,
        "data": data
    })


def error_response(message, code=-1):
    """错误响应格式"""
    return jsonify({
        "success": False,
        "message": message,
        "code": code
    })


@app.route('/')
def index():
    """源信息"""
    return jsonify({
        "name": "我的音乐源",
        "author": "dc1626",
        "version": "1.0.0",
        "protocol": "2.0.0",
        "description": "自定义音乐源服务器",
        "endpoints": {
            "search": "/search?keyword=关键词",
            "song": "/song?id=歌曲ID",
            "url": "/url?id=歌曲ID",
            "lyric": "/lyric?id=歌曲ID"
        }
    })


@app.route('/search')
def search():
    """
    搜索歌曲
    GET /search?keyword=关键词&page=1&limit=20
    
    返回格式（LX Music协议）:
    {
      "success": true,
      "data": [
        {
          "id": "歌曲ID",
          "title": "歌名",
          "artist": "艺术家",
          "album": "专辑名",
          "duration": 时长(秒),
          "pic": "封面URL",
          "source": "源标识"
        }
      ]
    }
    """
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    # TODO: 这里调用真实音乐平台的搜索API
    # 示例：调用网易云音乐API
    # response = requests.get(
    #     "https://music.163.com/api/search/get",
    #     params={"s": keyword, "type": 1, "limit": limit, "offset": (page-1)*limit}
    # )
    
    # 模拟搜索结果
    results = []
    for song_id, song in MOCK_SONGS.items():
        if keyword.lower() in song['title'].lower() or keyword.lower() in song['artist'].lower():
            results.append({
                "id": song['id'],
                "title": song['title'],
                "artist": song['artist'],
                "album": song['album'],
                "duration": song['duration'],
                "pic": song['pic'],
                "source": "custom"
            })
    
    return success_response({
        "list": results,
        "total": len(results),
        "page": page,
        "limit": limit
    })


@app.route('/song')
def song_info():
    """
    获取歌曲详情
    GET /song?id=歌曲ID
    
    返回格式:
    {
      "success": true,
      "data": {
        "id": "歌曲ID",
        "title": "歌名",
        "artist": "艺术家",
        "album": "专辑名",
        "duration": 时长,
        "pic": "封面URL",
        "lyric": "歌词",
        "tlyric": "翻译歌词",
        "url": "播放链接"
      }
    }
    """
    song_id = request.args.get('id', '')
    
    if song_id not in MOCK_SONGS:
        return error_response("歌曲不存在")
    
    song = MOCK_SONGS[song_id]
    
    # TODO: 调用真实平台的歌曲详情API
    
    return success_response({
        "id": song['id'],
        "title": song['title'],
        "artist": song['artist'],
        "album": song['album'],
        "duration": song['duration'],
        "pic": song['pic'],
        "lyric": song.get('lyric', ''),
        "tlyric": "",
        "url": song.get('url', ''),
        "source": "custom"
    })


@app.route('/url')
def get_url():
    """
    获取播放链接
    GET /url?id=歌曲ID
    
    返回格式:
    {
      "success": true,
      "data": {
        "id": "歌曲ID",
        "url": "音频URL",
        "br": 比特率(kbps)
      }
    }
    """
    song_id = request.args.get('id', '')
    
    if song_id not in MOCK_SONGS:
        return error_response("歌曲不存在")
    
    song = MOCK_SONGS[song_id]
    
    # TODO: 调用真实平台的播放链接API
    # 例如：https://music.163.com/api/song/url?id={song_id}
    
    return success_response({
        "id": song['id'],
        "url": song['url'],
        "br": 320  # 比特率: 128/192/320
    })


@app.route('/lyric')
def get_lyric():
    """
    获取歌词
    GET /lyric?id=歌曲ID
    
    返回格式:
    {
      "success": true,
      "data": {
        "id": "歌曲ID",
        "lyric": "原歌词",
        "tlyric": "翻译歌词"
      }
    }
    """
    song_id = request.args.get('id', '')
    
    if song_id not in MOCK_SONGS:
        return error_response("歌曲不存在")
    
    song = MOCK_SONGS[song_id]
    
    # TODO: 调用真实平台的歌词API
    
    return success_response({
        "id": song_id,
        "lyric": song.get('lyric', ''),
        "tlyric": ""
    })


@app.route('/pic')
def get_pic():
    """
    获取封面图片
    GET /pic?id=歌曲ID
    """
    song_id = request.args.get('id', '')
    
    if song_id not in MOCK_SONGS:
        return error_response("歌曲不存在")
    
    song = MOCK_SONGS[song_id]
    
    # 返回重定向到图片URL
    from flask import redirect
    return redirect(song['pic'], code=302)


@app.route('/check')
def check_update():
    """检查更新"""
    return success_response({
        "version": "1.0.0",
        "last_check": int(time.time()),
        "update_url": "",
        "changelog": ""
    })


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         LX Music 源服务器 v1.0.0 - 启动中...              ║
╠══════════════════════════════════════════════════════════════════╣
║  端口: 6000                                                  ║
║  地址: http://localhost:6000                                ║
╠══════════════════════════════════════════════════════════════════╣
║  API 接口:                                                   ║
║    GET /search?keyword=关键词  - 搜索歌曲                    ║
║    GET /song?id=xxx             - 获取歌曲详情               ║
║    GET /url?id=xxx              - 获取播放链接               ║
║    GET /lyric?id=xxx            - 获取歌词                   ║
║    GET /pic?id=xxx              - 获取封面                   ║
║    GET /                        - 源信息                     ║
╠══════════════════════════════════════════════════════════════════╣
║  LX Music 配置:                                               ║
║    设置 → 自定义源 → 输入: http://你的IP:6000                ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # 从配置文件读取设置
    import os
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    port = 6000
    debug = False
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                port = config.get('port', 6000)
                debug = config.get('debug', False)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
