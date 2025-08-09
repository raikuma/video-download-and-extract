import argparse
import glob
import json
import os
import shutil
from urllib import request

from tqdm import tqdm
from pytubefix import YouTube
from pytubefix.cli import on_progress

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def download(url, url_type, download_folder):
    if url_type == 'youtube':
        yt = YouTube(url, on_progress_callback=on_progress)
        stream_1 = yt.streams.get_highest_resolution() # mp4 only
        stream_2 = yt.streams.order_by("resolution").last() # include webm
        stream = max(stream_1, stream_2, key=lambda x: int(x.resolution[:-1]))
        video_path = stream.download(download_folder)
    
    if url_type == 'url':
        pbar = tqdm(unit='B', unit_scale=True, unit_divisor=1024)
        def download_hook(count, block_size, total_size):
            pbar.total = total_size
            pbar.update(block_size)
        video_path = os.path.join(download_folder, os.path.basename(url))
        opener = request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36')
        opener.retrieve(url, video_path, reporthook=download_hook)
        pbar.close()
        
    # remove whitespace of filename
    new_video_path = video_path.replace(' ', '_')
    shutil.move(video_path, new_video_path)
    video_path = new_video_path
    
    return video_path

def extract(video_path, start_sec, end_sec, save_folder=None, save_video=False, verbose=False):
    if save_folder is None:
        image_folder = os.path.join(os.path.dirname(video_path), 'images')
    else:
        image_folder = os.path.join(os.path.join(save_folder, 'images'))
    if os.path.exists(image_folder):
        print("remove exists folder")
        shutil.rmtree(image_folder)
    os.makedirs(image_folder, exist_ok=False)

    img_path = os.path.join(image_folder, '%04d.png')
    cmd = f'ffmpeg -i "{video_path}" -ss {start_sec} -to {end_sec} "{img_path}"'
    if not verbose:
        cmd += f' -hide_banner -loglevel error'
    print(cmd)
    os.system(cmd)

    if save_video:
        cut_path = os.path.join(save_folder, 'cut.mp4')
        cmd = f'ffmpeg -i "{video_path}" -ss {start_sec} -to {end_sec} -c:v copy -c:a copy "{cut_path}" -y'
        if not verbose:
            cmd += f' -hide_banner -loglevel error'
        print(cmd)
        os.system(cmd)
        print(f"save cutted video at {cut_path}")

    return image_folder

def parseTarget(ex):
    if ex == 'all':
        return ex
    res = []
    for a in ex.split(','):
        if '-' in a:
            s, e = a.split('-')
            res += [str(x) for x in range(int(s), int(e)+1)]
        else:
            res += [a]
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VDE: Video download and frame extrat tool')
    parser.add_argument('-l', '--list', type=str, default='list.json',
        help='json file path of video list (default: ./list.json)')
    parser.add_argument('-o', '--output', type=str, default='data',
        help='root path of outputs (default: ./data)')
    parser.add_argument('-d', '--download_only', action='store_true',
        help='just download video')
    parser.add_argument('-e', '--extract_only', action='store_true',
        help='just extract downloaded video')
    parser.add_argument('-f', '--force', action='store_true',
        help='re-work already existed results')
    parser.add_argument('-s', '--save_video', action='store_true',
        help='save cutted video together')
    parser.add_argument('-t', '--target', type=str, default='all',
        help='specify target video ex) "0" "0,1" "0-2"')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='show ffmpeg stdout, stderr')
    args = parser.parse_args()

    output_path = args.output
    list_json_path = args.list
    do_download = not args.extract_only
    do_extract = not args.download_only
    force = args.force
    save_video = args.save_video
    target = parseTarget(args.target)
    verbose = args.verbose

    video_list = json.loads(open(list_json_path).read())
    print(f"load {len(video_list)} video info")

    os.makedirs(output_path, exist_ok=True)

    for video in video_list:
        if target != 'all' and not video['id'] in target:
            continue

        print(f"[{video['id']}]")
        data_path = os.path.join(output_path, str(video['id']))
        os.makedirs(data_path, exist_ok=True)

        video_exists = False
        video_paths = glob.glob(os.path.join(data_path, '*.mp4'))
        video_paths += glob.glob(os.path.join(data_path, '*.webm'))
        if len(video_paths) > 0:
            video_exists = True
            video_path = video_paths[0]

        if do_download:
            if not video_exists or force:
                print(f"downloading from {video['url']}")
                video_path = download(
                    url=video['url'],
                    url_type=video['type'],
                    download_folder=data_path
                )
                video_exists = True
                print(f"save video at {video_path}")
            else:
                print("pass already downloaded video")

        image_exists = False
        image_paths = glob.glob(os.path.join(data_path, 'images'))
        if len(image_paths) > 0:
            image_exists = True
            image_path = image_paths[0]

        if do_extract:
            if not image_exists or force:
                if video_exists:
                    print(f'extracting from {video_path}')
                    image_path = extract(
                        video_path=video_path,
                        start_sec=video['start'],
                        end_sec=video['end'],
                        save_folder=data_path,
                        save_video=save_video,
                        verbose=verbose
                    )
                    print(f"save images at {image_path}")
                else:
                    print("could not find video file")
            else:
                print("pass already extracted video")
