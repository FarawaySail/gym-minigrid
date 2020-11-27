#!/usr/bin/env python3

import time
import argparse
import numpy as np
import gym
import gym_minigrid
from gym_minigrid.wrappers import *
from gym_minigrid.window import Window

def redraw(img):
    if not args.agent_view:
        img = env.render_multi_agent('rgb_array', tile_size=args.tile_size)
    window.show_img(img)
    window_explored.show_img(env.explored_all_map[7:-7,7:-7].astype(np.uint8))
    window_obstacle.show_img(env.obstacle_all_map[7:-7,7:-7].astype(np.uint8))
    time.sleep(2)

def reset():
    if args.seed != -1:
        env.seed(args.seed)

    obs = env.reset()
    #import pdb; pdb.set_trace()
    #env.render_multi_agent()
    #import pdb; pdb.set_trace()
    #obs, reward, done, info = env.step([0,1])
    #env.render_multi_agent()
    #import pdb; pdb.set_trace()
    #import pdb; pdb.set_trace()
    if hasattr(env, 'mission'):
        print('Mission: %s' % env.mission)
        window.set_caption(env.mission)

    redraw(obs)

def step(action):
    obs, reward, done, info = env.step(action)
    print('step=%s, reward=%.2f' % (env.step_count, reward))

    if done:
        print('done!')
        reset()
    else:
        redraw(obs)

def key_handler(event):
    print('pressed', event.key)

    if event.key == 'escape':
        window.close()
        return

    if event.key == 'backspace':
        reset()
        return

    if event.key == 'left':
        step(env.actions.left)
        return
    if event.key == 'right':
        step(env.actions.right)
        return
    if event.key == 'up':
        step(env.actions.forward)
        return

    # Spacebar
    if event.key == ' ':
        step(env.actions.toggle)
        return
    if event.key == 'pageup':
        step(env.actions.pickup)
        return
    if event.key == 'pagedown':
        step(env.actions.drop)
        return

    if event.key == 'enter':
        step(env.actions.done)
        return

parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    help="gym environment to load",
    default='MiniGrid-MultiRoom-N6-v0'
)
parser.add_argument(
    "--seed",
    type=int,
    help="random seed to generate the environment with",
    default=-1
)
parser.add_argument(
    "--tile_size",
    type=int,
    help="size at which to render tiles",
    default=32
)
parser.add_argument(
    '--agent_view',
    default=False,
    help="draw the agent sees (partially observable view)",
    action='store_true'
)
parser.add_argument(
    '--agent_num',
    type=int,
    help="number of agents",
    default=2
)

args = parser.parse_args()

env = gym.make(args.env, agent_pos=[(1,1),(17,1)])

if args.agent_view:
    env = RGBImgPartialObsWrapper(env)
    env = ImgObsWrapper(env)

window = Window('gym_minigrid - ' + args.env)
window_explored = Window('explored_area')
window_obstacle = Window('obstacle_area')
#window.reg_key_handler(key_handler)

reset()

while(1):
    actions = env.get_short_term_action([[1,17],[17,17]])
    step(actions)
# Blocking event loop
# window.show(block=True)
