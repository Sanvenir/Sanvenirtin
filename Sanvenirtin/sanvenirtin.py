#!usr/bin/python3
# -*-coding: utf-8 -*-

""""""
import sys
import scene
import interface
import graphics
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
import os
import re

from configure import TILE_WIDTH, TILE_HEIGHT


def find_files(directory, suffix, name_list):
    for file in os.listdir(directory):
        if re.search(".%s$" % suffix, file):
            name_list.append(os.path.join(directory, file))
        elif os.path.isdir(os.path.join(directory, file)):
            find_files(os.path.join(directory, file), suffix, name_list)


def convert_resource():
    name_list = []
    find_files("res", "png", name_list)
    for name in name_list:
        print(name)
        res = QImage(name)
        res.save(name)


def load_resources():
    if not os.path.exists("sav"):
        os.mkdir("sav")
    graphics.Resources.ground_image = graphics.CombinePixmap("res//tiles//map//ground.png", 48, 48, 11)
    graphics.Resources.obstacle_image = graphics.CombinePixmap("res//tiles//map//obstacle//obstacle_1.png", 48, 48, 6)
    graphics.Resources.obstacle_images = {"forest_small": graphics.CombinePixmap(
        "res//tiles//map//obstacle//forest_small.png", 48, 48, 6),
        "forest_large": graphics.CombinePixmap(
            "res//tiles//map//obstacle//forest_large.png", 192, 192, 4, line_count=2)}

    graphics.Resources.character_images["male"] = []
    image_list = []
    find_files("res//tiles//character//male", "gif", image_list)
    for image in image_list:
        graphics.Resources.character_images["male"].append(graphics.CombinePixmap(image, 48, 48, 1, 1))
    graphics.Resources.character_images["female"] = []
    image_list = []
    find_files("res//tiles//character//female", "gif", image_list)
    for image in image_list:
        graphics.Resources.character_images["female"].append(graphics.CombinePixmap(image, 48, 48, 1, 1))
    graphics.Resources.character_images["others"] = []
    image_list = []
    find_files("res//tiles//character//others", "gif", image_list)
    for image in image_list:
        graphics.Resources.character_images["others"].append(graphics.CombinePixmap(image, 48, 48, 1, 1))


def sanvenirtin():
    # #convert_resource()
    app = QApplication(sys.argv)
    load_resources()
    game_scene = scene.Scene()
    window = interface.GameSceneInterface(game_scene)
    window.show()
    app.exec_()

if __name__ == "__main__":
    sanvenirtin()
