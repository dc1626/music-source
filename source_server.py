#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LX Music Source Server - 音乐源服务器
对接: 咪咕音乐 (api.migu.cn)

支持的接口:
1. /search?keyword=关键词  - 搜索歌曲
2. /song?id=xxx            - 获取歌曲详情
3. /url?id=xxx             - 获取播放链接
4. /lyric?id=xxx           - 获取歌词

启动服务: python source_server.py
端口: 6000
"""

from flask import Flask, request, jsonify, redirect
import json
import hashlib
import time
import requests

app = Flask(__name__)

# 缓存，用于存储搜索结果中的详细信息
SEARCH_CACHE = {}

# 咪咕音乐 API 配置
MIGU_BASE = "https://migu.music.kspkg.cn"
MIGUReferer = "https://m.music.migu.cn"


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


def sign_params(params):
    """咪咕签名算法"""
    """参考: https://github.com/moshuqi/ksmigu/blob/master/ksmigu/ksmigu.go#L88"""
    # 咪咕的签名算法比较复杂，这里使用简化版本
    # 实际使用时可能需要更完整的签名实现
    return params


def search_migu(keyword, page=1, limit=20):
    """搜索咪咕音乐"""
    global SEARCH_CACHE
    
    offset = (page - 1) * limit
    
    url = f"{MIGU_BASE}/search"
    params = {
        "keyword": keyword,
        "type": 2,  # 歌曲
        "limit": limit,
        "offset": offset,
        "raw": 1
    }
    
    headers = {
        "Referer": MIGUReferer,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("returnCode") != "000000":
            return []
        
        results = []
        songs = data.get("data", {}).get("result", []).get("songs", [])
        
        for song in songs:
            # 构建缓存
            song_id = str(song.get("id", ""))
            artist = song.get("artist", [{}])[0].get("name", "未知艺术家") if song.get("artist") else "未知艺术家"
            album = song.get("album", {})
            album_name = album.get("name", "未知专辑") if album else "未知专辑"
            duration = song.get("duration", 0)
            pic = song.get("pic", "")
            lyrics = song.get("lyrics", [])
            
            # 保存到缓存
            SEARCH_CACHE[song_id] = {
                "id": song_id,
                "title": song.get("name", ""),
                "artist": artist,
                "album": album_name,
                "duration": duration,
                "pic": pic,
                "lyrics": lyrics,
                "url": "",  # 需要单独获取
                "copyrightId": song.get("copyrightId", ""),
                "source": "migu"
            }
            
            results.append({
                "id": song_id,
                "title": song.get("name", ""),
                "artist": artist,
                "album": album_name,
                "duration": duration,
                "pic": pic,
                "source": "migu"
            })
        
        return results
    except Exception as e:
        print(f"搜索失败: {e}")
        return []


def get_url_migu(song_id):
    """获取咪咕音乐播放链接"""
    if song_id not in SEARCH_CACHE:
        return None, 0
    
    song = SEARCH_CACHE[song_id]
    copyright_id = song.get("copyrightId", "")
    
    if not copyright_id:
        return None, 0
    
    url = f"{MIGU_BASE}/songdetail"
    params = {
        "copyrightId": copyright_id,
        "raw": 1
    }
    
    headers = {
        "Referer": MIGUReferer,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("returnCode") != "000000":
            return None, 0
        
        play_url = data.get("data", {}).get("playUrl", "")
        
        # 替换为 https
        if play_url.startswith("http:"):
            play_url = "https:" + play_url[5:]
        
        # 咪咕返回的是试听链接，可能需要验证
        return play_url, 320
    except Exception as e:
        print(f"获取播放链接失败: {e}")
        return None, 0


def get_lyric_migu(song_id):
    """获取咪咕音乐歌词"""
    if song_id not in SEARCH_CACHE:
        return ""
    
    song = SEARCH_CACHE[song_id]
    lyrics = song.get("lyrics", [])
    
    # 合并所有歌词
    full_lyric = ""
    for lrc in lyrics:
        full_lyric += lrc.get("content", "") + "\n"
    
    return full_lyric


@app.route('/')
def index():
    """源信息"""
    return jsonify({
        "name": "咪咕音乐源",
        "author": "dc1626",
        "version": "1.0.0",
        "protocol": "2.0.0",
        "description": "对接咪咕音乐 - api.migu.cn",
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
    """
    global SEARCH_CACHE
    
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    if not keyword:
        return error_response("缺少关键词")
    
    results = search_migu(keyword, page, limit)
    
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
    """
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SEARCH_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    song = SEARCH_CACHE[song_id]
    
    return success_response({
        "id": song['id'],
        "title": song['title'],
        "artist": song['artist'],
        "album": song['album'],
        "duration": song['duration'],
        "pic": song['pic'],
        "lyric": song.get('lyrics', []),
        "tlyric": "",
        "url": "",
        "source": "migu"
    })


@app.route('/url')
def get_url():
    """
    获取播放链接
    GET /url?id=歌曲ID
    """
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SEARCH_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    url, br = get_url_migu(song_id)
    
    if not url:
        return error_response("获取播放链接失败，可能是版权限制")
    
    return success_response({
        "id": song_id,
        "url": url,
        "br": br
    })


@app.route('/lyric')
def get_lyric():
    """
    获取歌词
    GET /lyric?id=歌曲ID
    """
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SEARCH_CACHE:
        return error_response("歌曲不存在，请先搜索")
    
    lyric = get_lyric_migu(song_id)
    
    return success_response({
        "id": song_id,
        "lyric": lyric,
        "tlyric": ""
    })


@app.route('/pic')
def get_pic():
    """获取封面图片"""
    song_id = request.args.get('id', '')
    
    if not song_id:
        return error_response("缺少歌曲ID")
    
    if song_id not in SEARCH_CACHE:
        return error_response("歌曲不存在")
    
    pic_url = SEARCH_CACHE[song_id].get('pic', '')
    
    if pic_url:
        if pic_url.startswith("http:"):
            pic_url = "https:" + pic_url[5:]
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
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         LX Music 咪咕音乐源服务器 v1.0.0 - 启动中...    ║
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
