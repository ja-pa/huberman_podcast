import webvtt
from datetime import datetime
from jinja2 import Template
import json
import pprint
import os
import re
import argparse


def parse_subtitle(subtitle_file):
    tmp_list = []
    for caption in webvtt.read(subtitle_file):
        txt = caption.text.replace("\n", " ")
        pt = datetime.strptime(caption.start, '%H:%M:%S.%f')
        sec = pt.second + pt.minute*60 + pt.hour*3600
        tmp_list.append({
            "time": caption.start,
            "sec": sec,
            "text": txt
            })
    return tmp_list


def parse_yt_json(json_file):
    if os.path.isfile(json_file):
        with open(json_file) as json_file:
            data = json.load(json_file)
            tmp_sub_file = "tmp_subtitles.txt"
            with open(tmp_sub_file, "w") as fp:
                fp.write(data["subtitles"])
            subtitles_list = parse_subtitle(tmp_sub_file)
            data["subtitles_list"] = subtitles_list
            return data
    return None


def format_video_time(desc, video_code):
    m1 = re.findall(r'^\d{1,2}:\d{1,2}:\d{1,2}', desc)
    m2 = re.findall(r'^\d{2}:\d{1,2}', desc)
    ma = m1 + m2
    for item in ma:
        desc = desc.replace(item, "<a href=%s >%s</a>" % (video_code, item))
        print(item)


def format_description(desc):
    return desc.replace("\n", "<br>")


def generate_page(yt_obj, template_file):
    with open(template_file) as fp:
        temp_text = fp.read()
        t = Template(temp_text)
        # format_video_time(yt_obj["desc"], "aaaaaaauuuuuuuuuu")
        return t.render(
                    subtitles_list=yt_obj["subtitles_list"],
                    code=yt_obj["code"],
                    description=format_description(yt_obj["desc"]),
                    title=yt_obj["title"],
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-input', help='Generated json file')
    parser.add_argument('--page-template', help='Jinja2 template', default="podcast_template.j2")
    parser.add_argument('--output', help='Output file', default="page.html")

    args = parser.parse_args()

    if args.json_input:
        with open(args.output, "w") as fp:
            dd = parse_yt_json(args.json_input)
            page = generate_page(dd, args.page_template)
            fp.write(page)
            print("Page generated %s " % args.output)
