import requests
import re
import json
import subprocess
import os
import shutil

cookie = input("输入您在bilibili的Cookie：\n（输入正确Cookie后下载视频时可达较高清晰度，若不输入回车跳过即可，但下载视频的清晰度为默认480P，就像您需要登录bilibili后才能解锁较高清晰度）\n")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36", "Referer": "https://www.bilibili.com/",
           "Cookie": cookie}


def send_request(url):
    response = requests.get(url=url, headers=headers)
    return response


def get_data(html_data):
    title = re.findall('<title data-vue-meta="true">(.*?)</title>',
                       html_data)[0].replace("_哔哩哔哩_bilibili", "")
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    file_name = re.sub(rstr, "_", title)
    json_data = re.findall(
        r'<script>window.__playinfo__=(.*?)</script>', html_data)[0]
    json_data = json.loads(json_data)
    audio_url = json_data["data"]["dash"]["audio"][0]["backupUrl"][0]
    video_url = json_data["data"]["dash"]["video"][0]["backupUrl"][0]
    data = [file_name, audio_url, video_url]
    return data


def get_audio_only(file_name, audio_url):
    print('正在下载 "' + file_name + '"的音频...')
    audio_data = send_request(audio_url).content
    print('完成下载 "' + file_name + '"的音频！')
    with open(file_name + ".mp3", "wb") as f:
        f.write(audio_data)


def get_video_only(file_name, video_url):
    print('正在下载 "' + file_name + '"的视频...')
    video_data = send_request(video_url).content
    print('完成下载 "' + file_name + '"的视频！')
    with open(file_name + ".m4s", "wb") as f:
        f.write(video_data)


def get_complete_video(file_name, audio_url, video_url):
    get_audio_only(file_name, audio_url)
    get_video_only(file_name, video_url)
    os.rename(file_name + ".mp3", "0.mp3")
    os.rename(file_name + ".m4s", "0.mp4")
    print('正在合并 "' + file_name + '"的音频和视频...')
    subprocess.call(
        "ffmpeg -i 0.mp4 -i 0.mp3 -c:v copy -c:a aac -strict experimental output.mp4", shell=True)
    os.rename("output.mp4", file_name + ".mp4")
    os.remove("0.mp3")
    os.remove("0.mp4")
    print('完成合并 "' + file_name + '"的音频和视频！')
    print("视频下载已完成！")


def main():
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    url = input("输入视频对应的网站链接即可进入下载：\n")
    html_data = send_request(url).text
    data = get_data(html_data)
    while (1):
        choose = input(
            "下载选项：\n[1]仅下载音频\n[2]仅下载视频（无声音）\n[3]下载完整视频\n请输入下载选项前的数字进行下载...\n")
        if choose == "1":
            get_audio_only(data[0], data[1])
            break
        elif choose == "2":
            get_video_only(data[0], data[2])
            break
        elif choose == "3":
            get_complete_video(data[0], data[1], data[2])
            break
        else:
            print('输入错误,仅支持输入"1"或"2"或"3",请重新输入')
            continue


if __name__ == "__main__":
    main()
