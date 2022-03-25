import json

from multiprogram import MultiProgram, Source
from custom_functions import prototypes

DEBUG = True


def main():
    yarn_files = ["YarnCollection.json"]

    scenes = {}
    for yarn_file in yarn_files:
        file_scenes = _yarn_scenes(yarn_file)
        for title, source in file_scenes.items():
            assert title not in scenes, \
                "Duplicated scene {}".format(title)

            scenes[title] = source

    mp = MultiProgram(scenes, prototypes)
    mp.compile("./binaries")


def _yarn_scenes(path):
    file_scenes = {}
    with open(path, "r") as fd:
        payload = fd.read()
        json_collection = json.loads(payload)
        for scene in json_collection:
            title = scene["title"]
            source = scene["body"]

            if len(source) != 0:
                file_scenes[title] = Source(title, source)

    return file_scenes


if __name__ == "__main__":
    main()
