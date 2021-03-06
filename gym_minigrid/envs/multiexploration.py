#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gym_minigrid.minigrid import *
from gym_minigrid.register import register
import matplotlib.pyplot as plt
import time
import pyastar


class MultiExplorationEnv(MiniGridEnv):
    """
    Classic 4 rooms gridworld environment.
    Can specify agent and goal position, if not it set at random.
    """

    def __init__(self, agent_pos=None, goal_pos=None, agent_num=2):
        self._agent_default_pos = agent_pos
        self._goal_default_pos = goal_pos
        self.door_size = 3
        super().__init__(grid_size=19, max_steps=100, agent_num=agent_num)


    def _gen_grid(self, width, height):
        # Create the grid
        self.grid = Grid(width, height)
        
        # Generate the surrounding walls
        self.grid.horz_wall(0, 0)
        self.grid.horz_wall(0, height - 1)
        self.grid.vert_wall(0, 0)
        self.grid.vert_wall(width - 1, 0)
        room_w = width // 2
        room_h = height // 2

        # For each row of rooms
        for j in range(0, 2):

            # For each column
            for i in range(0, 2):
                xL = i * room_w
                yT = j * room_h
                xR = xL + room_w
                yB = yT + room_h

                # Bottom wall and door
                if i + 1 < 2:

                    self.grid.vert_wall(xR, yT, room_h)
                    #pos = (xR, self._rand_int(yT + 1, yB))
                    pos = (xR, self._rand_int(yT + 1, yB - 2))
                    for s in range(self.door_size):
                        self.grid.set(*pos, None)
                        pos = (pos[0], pos[1] + 1)

                # Bottom wall and door
                if j + 1 < 2:
                    self.grid.horz_wall(xL, yB, room_w)
                    pos = (self._rand_int(xL + 1, xR), yB)
                    self.grid.set(*pos, None)
        # Randomize the player start position and orientation
        if self._agent_default_pos is not None:
            self.agent_pos = self._agent_default_pos
            for i in range(self.agent_num):
                if self.agent_num == 1:
                    self.grid.set(*self._agent_default_pos, None)
                else:    
                    self.grid.set(*self._agent_default_pos[i], None)
            if self.agent_num == 1:
                self.agent_dir = self._rand_int(0, 4)
            else:
                self.agent_dir = [self._rand_int(0, 4) for i in range(self.agent_num)]  # assuming random start direction
        else:
            self.place_agent()
        '''
        if self._goal_default_pos is not None:
            goal = Goal()
            self.put_obj(goal, *self._goal_default_pos)
            goal.init_pos, goal.cur_pos = self._goal_default_pos
        else:
            self.place_obj(Goal())
        '''
        self.mission = 'Reach the goal'

    def reset(self):
        obs = MiniGridEnv.reset(self)
        self.gt_map = self.grid.encode()[:,:,0].T
        self.pad_gt_map = np.pad(self.gt_map,((self.agent_view_size, self.agent_view_size), (self.agent_view_size,self.agent_view_size)) , constant_values=(0,0))
        # init local map
        self.explored_each_map = []
        self.obstacle_each_map = []
        for i in range(self.agent_num):
            self.explored_each_map.append(np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size)))
            self.obstacle_each_map.append(np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size)))
        '''
        for i in range(self.agent_num):
            local_map = np.rot90(obs[i]['image'][:,:,0].T,3)
            pos = [self.agent_pos[i][1], self.agent_pos[i][0]]
            direction = self.agent_dir[i]
            if direction == 0:
                topx = max(0, pos[0]-self.agent_view_size // 2)
                topy = pos[1] 
                botx = min(self.width - 1, pos[0] + self.agent_view_size // 2 + 1)
                boty = min(self.height - 1, pos[1] + self.agent_view_size  + 1)
            if direction == 1:
                topx = pos[0]
                topy = max(0, pos[1] - self.agent_view_size // 2) 
                botx = min(self.width - 1, pos[0] + self.agent_view_size  + 1)
                boty = min(self.height - 1, pos[1] + self.agent_view_size // 2  + 1)
            if direction == 2:
                topx = max(0, pos[0] - self.agent_view_size // 1)
                topy = max(0, pos[1] - self.agent_view_size) 
                botx = min(self.width - 1, pos[0] + self.agent_view_size // 2 + 1)
                boty = pos[1]
            if direction == 3:
                topx = max(0, pos[0] - self.agent_view_size)
                topy = max(0, pos[1] - self.agent_view_size // 2) 
                botx = pos[0]
                boty = min(self.height - 1, pos[1] + self.agent_view_size // 2  + 1)
        import pdb; pdb.set_trace()
        '''
        for i in range(self.agent_num):
            local_map = np.rot90(obs[i]['image'][:,:,0].T,3)
            pos = [self.agent_pos[i][1] + self.agent_view_size, self.agent_pos[i][0] + self.agent_view_size]
            direction = self.agent_dir[i]
            ### adjust angle
            local_map = np.rot90(local_map, 4-direction)
            if direction == 0:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map[i][x+pos[0]-self.agent_view_size//2][y+pos[1]] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map[i][x+pos[0]-self.agent_view_size//2][y+pos[1]] = 1
            if direction == 1:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map[i][x+pos[0]][y+pos[1]-self.agent_view_size//2] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map[i][x+pos[0]][y+pos[1]-self.agent_view_size//2] = 1
            if direction == 2:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map[i][x+pos[0]-self.agent_view_size//2][y+pos[1]-self.agent_view_size+1] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map[i][x+pos[0]-self.agent_view_size//2][y+pos[1]-self.agent_view_size+1] = 1
            if direction == 3:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map[i][x+pos[0]-self.agent_view_size+1][y+pos[1]-self.agent_view_size//2] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map[i][x+pos[0]-self.agent_view_size+1][y+pos[1]-self.agent_view_size//2] = 1
        self.explored_all_map = np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size))
        self.obstacle_all_map = np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size))
        for i in range(self.agent_num):
            self.explored_all_map = np.logical_or(self.explored_all_map, self.explored_each_map[i])
            self.obstacle_all_map = np.logical_or(self.obstacle_all_map, self.obstacle_each_map[i])
        return obs

    def step(self, action):
        obs, reward, done, info = MiniGridEnv.step(self, action)
        self.explored_each_map_t = []
        self.obstacle_each_map_t = []
        for i in range(self.agent_num):
            self.explored_each_map_t.append(np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size)))
            self.obstacle_each_map_t.append(np.zeros((self.width + 2*self.agent_view_size, self.height + 2*self.agent_view_size)))
        for i in range(self.agent_num):
            local_map = np.rot90(obs[i]['image'][:,:,0].T,3)
            pos = [self.agent_pos[i][1] + self.agent_view_size, self.agent_pos[i][0] + self.agent_view_size]
            direction = self.agent_dir[i]
            ### adjust angle
            local_map = np.rot90(local_map, 4-direction)
            if direction == 0:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map_t[i][x+pos[0]-self.agent_view_size//2][y+pos[1]] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map_t[i][x+pos[0]-self.agent_view_size//2][y+pos[1]] = 1
            if direction == 1:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map_t[i][x+pos[0]][y+pos[1]-self.agent_view_size//2] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map_t[i][x+pos[0]][y+pos[1]-self.agent_view_size//2] = 1
            if direction == 2:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map_t[i][x+pos[0]-self.agent_view_size//2][y+pos[1]-self.agent_view_size+1] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map_t[i][x+pos[0]-self.agent_view_size//2][y+pos[1]-self.agent_view_size+1] = 1
            if direction == 3:
                for x in range(self.agent_view_size):
                    for y in range(self.agent_view_size):
                        if local_map[x][y] == 0:
                            continue
                        else:
                            self.explored_each_map_t[i][x+pos[0]-self.agent_view_size+1][y+pos[1]-self.agent_view_size//2] = 1
                            if local_map[x][y] != 1:
                                self.obstacle_each_map_t[i][x+pos[0]-self.agent_view_size+1][y+pos[1]-self.agent_view_size//2] = 1
        for i in range(self.agent_num):
            self.explored_each_map[i] = np.logical_or(self.explored_each_map[i], self.explored_each_map_t[i])
            self.obstacle_each_map[i] = np.logical_or(self.obstacle_each_map[i], self.obstacle_each_map_t[i])
        for i in range(self.agent_num):
            self.explored_all_map = np.logical_or(self.explored_all_map, self.explored_each_map[i])
            self.obstacle_all_map = np.logical_or(self.obstacle_all_map, self.obstacle_each_map[i])
        ## self.explored_all_map[7:-7,7:-7].astype(np.int8)
        #cv2.imshow(self.explored_all_map.astype(np.int8))
        #import pdb; pdb.set_trace()
        return obs, reward, done, info

    def get_short_term_action(self,inputs):
        actions = []
        temp_map = self.gt_map.astype(np.float32)
        temp_map[temp_map == 2] = np.inf
        for i in range(self.agent_num):
            goal = [inputs[i][1], inputs[i][0]]
            agent_pos = [self.agent_pos[i][1], self.agent_pos[i][0]]
            agent_dir = self.agent_dir[i]
            path = pyastar.astar_path(temp_map, agent_pos, goal, allow_diagonal=False)
            if len(path) == 1:
                actions.append(1)
                continue
            relative_pos = np.array(path[1]) - np.array(agent_pos)
            # first quadrant
            if relative_pos[0] < 0 and relative_pos[1] > 0:
                if agent_dir == 0 or agent_dir == 3:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 1:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 2:
                    actions.append(1)  # turn right
                    continue
            # second quadrant
            if relative_pos[0] > 0 and relative_pos[1] > 0:
                if agent_dir == 0 or agent_dir == 1:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 2:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 3:
                    actions.append(1)  # turn right
                    continue
            # third quadrant
            if relative_pos[0] > 0 and relative_pos[1] < 0:
                if agent_dir == 1 or agent_dir == 2:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 3:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 0:
                    actions.append(1)  # turn right
                    continue
            # fourth quadrant
            if relative_pos[0] < 0 and relative_pos[1] < 0:
                if agent_dir == 2 or agent_dir == 3:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 0:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 1:
                    actions.append(1)  # turn right
                    continue
            if relative_pos[0] == 0 and relative_pos[1] ==0:
                # turn around
                actions.append(1)
                continue
            if relative_pos[0] == 0 and relative_pos[1] > 0:
                if agent_dir == 0:
                    actions.append(2)
                    continue
                if agent_dir == 1:
                    actions.append(0)
                    continue
                else:
                    actions.append(1)
                    continue
            if relative_pos[0] == 0 and relative_pos[1] < 0:
                if agent_dir == 2:
                    actions.append(2)
                    continue
                if agent_dir == 1:
                    actions.append(1)
                    continue
                else:
                    actions.append(0)
                    continue
            if relative_pos[0] > 0 and relative_pos[1] == 0:
                if agent_dir == 1:
                    actions.append(2)
                    continue
                if agent_dir == 0:
                    actions.append(1)
                    continue
                else:
                    actions.append(0)
                    continue
            if relative_pos[0] < 0 and relative_pos[1] == 0:
                if agent_dir == 3:
                    actions.append(2)
                    continue
                if agent_dir == 0:
                    actions.append(0)
                    continue
                else:
                    actions.append(1)
                    continue
        '''
        for i in range(self.agent_num):
            goal = inputs[i]
            agent_pos = self.agent_pos[i]
            agent_dir = self.agent_dir[i]
            relative_pos = np.array(goal) - np.array(agent_pos)
            # first quadrant
            if relative_pos[0] >= 0 and relative_pos[1] <= 0:
                if agent_dir == 0 or agent_dir == 3:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 1:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 2:
                    actions.append(1)  # turn right
                    continue
            # second quadrant
            if relative_pos[0] >= 0 and relative_pos[1] >= 0:
                if agent_dir == 0 or agent_dir == 1:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 2:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 3:
                    actions.append(1)  # turn right
                    continue
            # third quadrant
            if relative_pos[0] <= 0 and relative_pos[1] >= 0:
                if agent_dir == 1 or agent_dir == 2:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 3:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 0:
                    actions.append(1)  # turn right
                    continue
            # fourth quadrant
            if relative_pos[0] <= 0 and relative_pos[1] <= 0:
                if agent_dir == 2 or agent_dir == 3:
                    actions.append(2)  # forward
                    continue
                if  agent_dir == 0:
                    actions.append(0)  # turn left
                    continue
                if  agent_dir == 1:
                    actions.append(1)  # turn right
                    continue
        '''
        return actions
            


register(
    id='MiniGrid-MultiExploration-v0',
    entry_point='gym_minigrid.envs:MultiExplorationEnv'
)
