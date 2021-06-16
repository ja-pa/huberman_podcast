#!/usr/bin/python3

import urllib.parse as urlparse
from urllib.parse import parse_qs

from youtube_dl import YoutubeDL
import os

from urllib.request import urlopen
import json

import argparse


class YI:
    def __init__(self, video_code):
        self._url_template = "http://www.youtube.com/watch?v=%s"
        self._video_code = video_code
        self._video_url = self._url_template % self._video_code
        self._info_dict = self.get_info_dict()

    def get_info_dict(self):
        video_url = self._url_template % self._video_code
        with YoutubeDL({}) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            return info_dict

    def get_subtitle_url(self):
        en_sub = self._info_dict.get('subtitles', None).get("en-US", None)
        if not en_sub:
            en_sub = self._info_dict.get('automatic_captions', None).get("en", None)
        if en_sub:
            for sub in en_sub:
                ext = sub.get("ext")
                if ext == "vtt":
                    return sub.get("url")
        return None

    def get_title(self):
        return self._info_dict.get("title", None)

    def get_description(self):
        return self._info_dict.get("description", None)

    def get_url(self):
        return self._video_url

    def get_code(self):
        return self._video_code

    def get_subtitles(self):
        subtitle_url = self.get_subtitle_url()
        if subtitle_url:
            page = urlopen(subtitle_url).read().decode('utf-8')
        else:
            page = None
        return page


def get_video_code(url):
    parsed = urlparse.urlparse(url)
    code_list = parse_qs(parsed.query)
    video_code_list = code_list.get("v", None)

    if video_code_list:
        video_code = video_code_list[0]
        return video_code
    return None


def write_video_info(yt_obj):
    info_file = yt_obj.get_code() + ".json"
    json_info = {
        "desc": yt_obj.get_description(),
        "title": yt_obj.get_title(),
        "url": yt_obj.get_url(),
        "code": yt_obj.get_code(),
        "subtitles": yt_obj.get_subtitles()
    }
    for key, val in json_info.items():
        if val == None:
            print("Error. Empty value for key \"%s\"" % key)
            return False

    if not os.path.isfile(info_file):
        with open(info_file, 'w') as fp:
            json.dump(json_info, fp)
        print("Info file %s created." % info_file)
        return False
    else:
        print("Info file %s already exists. Skipping download." % info_file)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--get-info', help='Download subtitles from video')
    args = parser.parse_args()
    if args.get_info:
        video_code = get_video_code(args.get_info)
        if video_code:
            yd_obj = YI(video_code)
            write_video_info(yd_obj)
        else:
            print("Error. Video code wasn't detected.")
