#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LX Music Source Server - 音乐源服务器
对接: 网易云音乐 (music.163.com)
"""

from flask import Flask, request, jsonify, redirect
import json
import time
import requests

app = Flask(__name__)

# 缓存
SONG_CACHE = {}

# 网易云 API
NETEASE_API = "https://music.163.com/api"


def success_response(data):
    return jsonify({
        "success": True,
        "data": data
    })


def error_response(message, code=-1):
    return jsonify({
        "success": False,
        "message": message,
        "code": code
    })


def search_netease(keyword, page=1, limit=20):
    """搜索网易云音乐"""
    global SONG_CACHE
    
    url = f"{NETEASE_API}/search/get"
    params = {
        "s": keyword,
        "type": 1,  # 歌曲
        "limit": limit,
        "offset": (page - 1) * limit
    }
    
    headers = {
        "Referer": "https://music.163.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("code") != 200:
            return [], 0
        
        result = data.get("result", {})
        songs = result.get("songs", [])
        total = result.get("songCount", 0)
        
        results = []
        for song in songs:
            song_id = str(song.get("id", ""))
            name = song.get("name", "")
            artists = song.get("ar", [])
            artist = artists[0].get("name", "未知艺术家") if artists else "未知艺术家"
            album = song.get("al", {})
            album_name = album.get("name", "未知专辑") if album else "未知专辑"
            album_pic = album.get("picUrl", "")
            duration = song.get("dt", 0) // 1000  # 毫秒转秒
            
            # 保存到缓存
            SONG_CACHE[song_id] = {
                "id": song_id,
                "title": name,
                "artist": artist,
                "album": album_name,
                "duration": duration,
                "pic": album_pic,
                "source": "netease"
            }
            
            results.append({
                "id": song_id,
                "title": name,
                "artist": artist,
                "album": album_name,
                "duration": duration,
                "pic": album_pic,
                "source": "netease"
            })
        
        return results, total
    except Exception as e:
        print(f"搜索失败: {e}")
        return [], 0


def get_url_netease(song_id):
    """获取网易云播放链接"""
    if song_id not in SONG_CACHE:
        return None, 0
    
    url = f"{NETEASE_API}/song/url"
    params = {
        "id": song_id,
        "br": 320000  # 320kbps
    }
    
    headers = {
        "Referer": "https://music.163.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("code") != 200:
            return None, 0
        
        urls = data.get("data", [])
        if urls:
            return urls[0].get("url", None), urls[0].get("br", 0) // 1000
        
        return None, 0
    except Exception as e:
        print(f"获取播放链接失败: {e}")
        return None, 0


def get_lyric_netease(song_id):
    """获取网易云歌词"""
    if song_id not in SONG_CACHE:
        return "", ""
    
    url = f"{NETEASE_API}/lyric"
    params = {
        "id": song_id
    }
    
    headers = {
        "Referer": "https://music.163.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("code") != 200:
            return "", ""
        
        lrc = data.get("lrc", {}).get("lyric", "")
        tlrc = data.get("tlyric", {}).get("lyric", "")
        
        return lrc, tlrc
    except Exception as e:
        print(f"获取歌词失败: {e}")
        return "", ""


@app.route('/')
def index():
    """源信息"""
    return jsonify({
        "name": "网易云音乐源",
        "author": "dc1626",
        "version": "1.0.0",
        "protocol": "2.0.0",
        "description": "对接网易云音乐 - music.163.com",
        "endpoints": {
            "search": "/search?keyword=关键词",
            "song": "/song?id=歌曲ID",
            "url": "/url?id=歌曲ID",
            "lyric": "/lyric?id=歌曲ID"
        }
    })


@app.route('/search')
def search():
    """搜索歌曲"""
    global SONG_CACHE
    
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    if not keyword:
        return error_response("缺少关键词")
    
    results, total = search_netease(keyword, page, limit)
    
    return success_response({
        "list": results,
        "total": total,
        "page": page,
        "limit": limit
    })


@app.route('/song')
def song_info():
    """获取歌曲详情"""
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SONG_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    song = SONG_CACHE[song_id]
    
    return success_response({
        "id": song['id'],
        "title": song['title'],
        "artist": song['artist'],
        "album": song['album'],
        "duration": song['duration'],
        "pic": song['pic'],
        "lyric": "",
        "tlyric": "",
        "url": "",
        "source": "netease"
    })


@app.route('/url')
def get_url():
    """获取播放链接"""
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SONG_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    url, br = get_url_netease(song_id)
    
    if not url:
        return error_response("获取播放链接失败，可能需要付费")
    
    return success_response({
        "id": song_id,
        "url": url,
        "br": br
    })


@app.route('/lyric')
def get_lyric():
    """获取歌词"""
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SONG_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    lyric, tlyric = get_lyric_netease(song_id)
    
    return success_response({
        "id": song_id,
        "lyric": lyric,
        "tlyric": tlyric
    })


@app.route('/pic')
def get_pic():
    """获取封面"""
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SONG_CACHE:
        return error_response("歌曲不存在")
    
    pic_url = SONG_CACHE[song_id].get('pic', '')
    
    if pic_url:
        return redirect(pic_url, code=302)
    
    return error_response("封面不存在")


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
    # Flask 配置，支持中文显示
    app.config['JSON_AS_ASCII'] = False
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║         LX Music 网易云音乐源服务器 v1.0.0 - 启动中...       ║
╠══════════════════════════════════════════════════════════════════════════╣
║  端口: 6000                                                          ║
║  地址: http://localhost:6000                                         ║
╠══════════════════════════════════════════════════════════════════════════╣
║  API 接口:                                                           ║
║    GET /search?keyword=关键词  - 搜索歌曲                             ║
║    GET /song?id=xxx             - 获取歌曲详情                        ║
║    GET /url?id=xxx              - 获取播放链接                        ║
║    GET /lyric?id=xxx            - 获取歌词                            ║
║    GET /pic?id=xxx              - 获取封面                            ║
║    GET /                        - 源信息                              ║
╠══════════════════════════════════════════════════════════════════════════╣
║  LX Music 配置:                                                       ║
║    设置 → 自定义源 → 输入: http://你的IP:6000                         ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    
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
