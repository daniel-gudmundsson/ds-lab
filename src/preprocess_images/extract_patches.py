OPENSLIDE_PATH = r'C:\\Users\\dantg\\openslide-win64-20220811\\openslide-win64-20220811\\bin'

import os
import matplotlib.pyplot as plt
import json
from matplotlib import path
import numpy as np
# Opening JSON file
import itertools
if hasattr(os, 'add_dll_directory'):
    # Python >= 3.8 on Windows
    with os.add_dll_directory(OPENSLIDE_PATH):
        import openslide
        from openslide.deepzoom import DeepZoomGenerator
else:
    import openslide
    from openslide.deepzoom import DeepZoomGenerator
from PIL import Image
from pathlib import Path
import sys

type = sys.argv[1]
i = int(sys.argv[2])
datapath = sys.argv[3]
outputFolder = sys.argv[4]
# datapath = '../../../WSS1-v1/'
files = zip(['train', 'test'], range(1,6))
tileSize = 224
minAmountOfVotes = 0.75*tileSize**2
slideName = f'0{i}.svs'
anno = f'0{i}_anno.json'
f = open(f'{datapath}/{type}/{anno}')
annos = json.load(f)
slide = openslide.OpenSlide(f'{datapath}/{type}/{slideName}')
width, height = slide.dimensions
print('Slide name:', type, slideName)
print('Slide height: ', height)
print('Slide width: ', width)
print('Slide level count: ', slide.properties)

tiles=DeepZoomGenerator(slide, tile_size=tileSize, overlap=0, limit_bounds=False)
print(tiles.tile_count)
print(tiles.level_count)
print(len(tiles.level_tiles))
print(tiles.level_dimensions)
maxZoomLevel = len(tiles.level_tiles)-1
offset = int((int(slide.properties['openslide.objective-power']) / 20) / 2)
level = maxZoomLevel - offset
print('level: ', level)
col, rows= tiles.level_tiles[level]
arr = np.zeros((rows, col))
print('level tiles: ', tiles.level_tiles[level])
print('num rows: ', rows)
print('num cols: ', col)
print('num poly', len(annos))
for poly in annos:
    poly['poly'] = path.Path(poly['vertices'])

for c in range(col):
    for r in range(rows):
        # print('(c,r)=', c, r)
        vote = {}
        tile=tiles.get_tile(level,(c, r))
        coords = list(tiles.get_tile_coordinates(level,(c, r)))[0]

        points = list(itertools.product(range(coords[0], coords[0]+tileSize), range(coords[1], coords[1]+tileSize)))
        for poly in annos:
            count = sum(poly['poly'].contains_points(points))
            vote[poly['class']] = vote.get(poly['class'], 0) + count

        if all(value == 0 for value in vote.values()):
            Path(f'{outputFolder}/dataset/unknown').mkdir(parents=True, exist_ok=True)
            tile.save(f'{outputFolder}/dataset/unknown/{type}_0{i}_row_{r}_col_{c}_x_{coords[0]}_y_{coords[1]}.tif')
            continue
        
        topClass = max(vote, key=vote.get)
        if vote[topClass] > minAmountOfVotes: 
            Path(f'{outputFolder}/dataset/{topClass}').mkdir(parents=True, exist_ok=True)
            tile.save(f'{outputFolder}/dataset/{topClass}/{type}_0{i}_row_{r}_col_{c}_x_{coords[0]}_y_{coords[1]}.tif')