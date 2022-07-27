# video-download-and-extract
 VDE: Video download and frame extract tool

## Requirements

- ffmpeg

## Usage

1. Install packages with `pip install -r requirements.txt`
1. Prepare list.json
1. run with `python vde.py`

- list.json supports youtube url and http file url

## Options

```bash
usage: vde.py [-h] [-l LIST] [-o OUTPUT] [-d] [-e] [-f] [-s] [-t TARGET]

VDE: Video download and frame extrat tool

options:
  -h, --help            show this help message and exit
  -l LIST, --list LIST  json file path of video list (default: ./list.json)
  -o OUTPUT, --output OUTPUT
                        root path of outputs (default: ./data)
  -d, --download_only   just download video
  -e, --extract_only    just extract downloaded video
  -f, --force           re-work already existed results
  -s, --save_video      save cutted video together
  -t TARGET, --target TARGET
                        specify target video ex) "0" "0,1" "0-2"
```