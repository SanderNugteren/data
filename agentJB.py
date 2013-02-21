import math

class Agent(object):
    
    NAME = "AgentB"
    SHARED_KNOWLEDGE = [] # call with Agent.shared_knowledge not self.shared...!
    PRIOR_KNOWLEDGE = None
    AMMOLOCS = {}

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None, **kwargs):
        """ Each agent is initialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.goal = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.blobpath = None   

        if self.id == 0:
            pois = [(152, 136), (312, 136)]
            distances = {}
            for i in range(len(field_grid)):
                for j in range(len(field_grid[i])):
                    if field_grid[i][j] == 0:
                        loc = (j*16 + 8, i*16 + 8)
                        dist = []
                        for poi in pois:
                            path = find_path(loc, poi, self.mesh, self.grid, self.settings.tilesize)
                            prevSg = loc
                            steps = 0
                            for sg in path:
                                dx = sg[0] - prevSg[0]
                                dy = sg[1] - prevSg[1]
                                steps += math.ceil(math.hypot(abs(dx), abs(dy))/self.settings.max_speed)
                                prevSg = sg

                                # turn = angle_fix(math.atan2(dy, dx) - obs.angle)
                                # if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                                #     steps += 1

                            dist.append((steps, "hoek"))
                        distances[(j, i)] = dist
            print distances

        print self.settings.max_speed

    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        
        self.observation = observation
        self.selected = observation.selected

        Agent.SHARED_KNOWLEDGE.append(observation)

        if observation.selected:
            print observation 

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        # Check if agent reached goal.
        if self.goal is not None and point_dist(self.goal, obs.loc) < self.settings.tilesize:
            self.goal = None 
            
        # #determine goals
        # goals = []
        # for cp in obs.cps:
        #     if cp


        
#        print "Agent %s ammo: %s" %(self.id ,obs.ammo)
            
        # # Walk to ammo
        # ammopacks = filter(lambda x: x[2] == "Ammo", obs.objects)
        # if ammopacks:
        #     self.goal = ammopacks[0][0:2]
        #     # Register visible ammo
        #     for ammopack in ammopacks:
        #         loc = ammopack[0:2]
        #         #available = Agent.AMMOLOCS.get(loc, _)
        #         Agent.AMMOLOCS[loc] = 1
            
        # # Register missing ammo (ammo appears to bee seen even at max_see + 14 ?)
        # max_see = self.settings.max_see
        # visibleSpawnPoint = []
        # for k in Agent.AMMOLOCS.keys():
        #     if abs(k[0]-obs.loc[0]) <= max_see and (abs(k[1]-obs.loc[1]) <= max_see): #if agent sees ammo spawn point
        #         visibleSpawnPoint.append(k)
        #     visibleAmmo = [loc[0:2] for loc in ammopacks]
        #     emptySpawnPoints = set(visibleSpawnPoint).difference(visibleAmmo)
        #     for esp in emptySpawnPoints:
        #         Agent.AMMOLOCS[esp] = 0
    
        # # Drive to where the user clicked
        # # Clicked is a list of tuples of (x, y, shift_down, is_selected)
        # if self.selected and self.observation.clicked:
        #     self.goal = self.observation.clicked[0][0:2]

        # # Walk to random CP
        # if self.goal is None:
        #     for cp in obs.cps:
        #         self.goal = cp[0:2] #TODO: change is something usefull!!
        
        ammoloc1 = (152, 136)
        ammoloc2 = (312, 136)

        if self.id == 0:
            self.goal = (152, 136)

        if self.id == 1:
            self.goal = (312, 136)

        if self.id == 2: 
            self.goal = obs.loc
            pathLength = float('inf')
            for cp in obs.cps:
                if cp[2] != self.team: 
                    path = find_path(obs.loc, cp[0:2], self.mesh, self.grid, self.settings.tilesize)
                    if len(path) < pathLength:
                        pathLength = len(path)
                        self.goal = cp[0:2]

        if self.id == 0:
            self.goal = (24, 250)

        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            speed = (dx**2 + dy**2)**0.5
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
                speed = 0
        else:
            turn = 0
            speed = 0

        # # Shoot enemies
        shoot = False
        if obs.ammo > 0 and obs.foes:
            for foe in obs.foes: 
                if point_dist(foe[0:2], obs.loc) < self.settings.max_range and not line_intersects_grid(obs.loc, foe[0:2], self.grid, self.settings.tilesize):
                    dx = foe[0] - obs.loc[0]
                    dy = foe[1] - obs.loc[1]
                    turn = angle_fix(math.atan2(dy, dx) - obs.angle)
                    if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                        shoot = False
                    else:
                        shoot = True


        # #make steps last a little longer (for debugging only!)
        # import time
        # time.sleep(0.59) 

        return (turn,speed,shoot)
        
    def debug(self, surface):
        """ Allows the agents to draw on the game UI,
            Refer to the pygame reference to see how you can
            draw on a pygame.surface. The given surface is
            not cleared automatically. Additionally, this
            function will only be called when the renderer is
            active, and it will only be called for the active team.
        """
        import pygame
        # First agent clears the screen
        if self.id == 0:
            surface.fill((0,0,0,0))
        # Selected agents draw their info
        if self.selected:
            if self.goal is not None:
                pygame.draw.line(surface,(0,0,0),self.observation.loc, self.goal)
        

    def finalize(self, interrupted=False):
        """ This function is called after the game ends,
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        pass   

