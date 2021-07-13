import os
import subprocess
import time
import signal
import random
import logging
import faulthandler
from multiprocessing import set_start_method

from droidlet import dashboard

if __name__ == "__main__":
    # this line has to go before any imports that contain @sio.on functions
    # or else, those @sio.on calls become no-ops
    dashboard.start()

from droidlet.dialog.dialogue_manager import DialogueManager
from droidlet.dialog.map_to_dialogue_object import DialogueObjectMapper
from droidlet.base_util import to_player_struct, Pos, Look, Player
from droidlet.memory.memory_nodes import PlayerNode
from droidlet.perception.semantic_parsing.nsp_querier import NSPQuerier
from agents.loco_mc_agent import LocoMCAgent
from agents.argument_parser import ArgumentParser
from droidlet.memory.robot.loco_memory import LocoAgentMemory, DetectedObjectNode
from droidlet.perception.robot import Perception
from self_perception import SelfPerception
from droidlet.interpreter.robot import (
    dance, 
    default_behaviors,
    LocoGetMemoryHandler, 
    PutMemoryHandler, 
    LocoInterpreter,
)
from droidlet.dialog.robot import LocoBotCapabilities
import droidlet.lowlevel.rotation as rotation
from droidlet.lowlevel.locobot.locobot_mover import LoCoBotMover
from droidlet.lowlevel.hello_robot.hello_robot_mover import HelloRobotMover
from droidlet.event import sio

faulthandler.register(signal.SIGUSR1)

random.seed(0)
log_formatter = logging.Formatter(
    "%(asctime)s [%(filename)s:%(lineno)s - %(funcName)s() %(levelname)s]: %(message)s"
)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().handlers.clear()


mover = None

@sio.on("movement command")
def test_command(sid, commands):
    global mover
    if mover == None:
        return
    movement = [0.0, 0.0, 0.0]
    for command in commands:
        if command == "MOVE_FORWARD":
            movement[0] += 0.1
            print("action: FORWARD")
        elif command == "MOVE_BACKWARD":
            movement[0] -= 0.1
            print("action: BACKWARD")
        elif command == "MOVE_LEFT":
            movement[2] += 0.3
            print("action: LEFT")
        elif command == "MOVE_RIGHT":
            movement[2] -= 0.3
            print("action: RIGHT")
        elif command == "PAN_LEFT":
            mover.bot.set_pan(mover.bot.get_pan() + 0.08)
        elif command == "PAN_RIGHT":
            mover.bot.set_pan(mover.bot.get_pan() - 0.08)
        elif command == "TILT_UP":
            mover.bot.set_tilt(mover.bot.get_tilt() - 0.08)
        elif command == "TILT_DOWN":
            mover.bot.set_tilt(mover.bot.get_tilt() + 0.08)
        print(command, movement)
        mover.move_relative([movement])


if __name__ == "__main__":
    ip = os.getenv("LOCOBOT_IP")
    print("Connecting to robot at ip: ", ip)
    mover = HelloRobotMover(ip=ip)
    print("Mover is ready to be operated")
    while True:
        print("base_state: ", mover.get_base_pos_in_canonical_coords())
        # print("rgb_depth: ", mover.get_rgb_depth())
        time.sleep(0.3)
