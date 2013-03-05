import math
import copy

class Agent(object):
    
    NAME = "mayweather"
    SHARED_KNOWLEDGE = [] # call with Agent.shared_knowledge not self.shared...!
    PRIOR_KNOWLEDGE = None
    STATE = None
    AMMOLOCS = []
    CPS = []

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
        # Read the binary blob
        if blob is not None and self.id == 0:
            self.blobpath = blob.name
            Agent.PRIOR_KNOWLEDGE = pickle.load(blob)
        elif self.id == 0: #create a distance dict   
            pois = [(184, 168), (312, 104), (232, 56), (264, 216)]
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
                            initAngle = 0
                            angle = 0
                            for k in range(len(path)):
                                dx = path[k][0] - prevSg[0]
                                dy = path[k][1] - prevSg[1]
                                #calc no steps towards subGoal
                                steps += math.ceil(math.hypot(abs(dx), abs(dy))/self.settings.max_speed)
                                #calc initial angle
                                if k == 0:
                                    initAngle = angle_fix(math.atan2(dy, dx))
                                    angle = initAngle
                                #calc no steps to turn 
                                angle = angle_fix(math.atan2(dy, dx) - angle)
                                if angle > self.settings.max_turn or angle < -self.settings.max_turn:
                                    steps += math.floor(abs(angle)/float(self.settings.max_turn))
                                prevSg = path[k]
                            dist.append((steps, initAngle))
                        distances[(j, i)] = dist
            Agent.PRIOR_KNOWLEDGE = distances
            try:
                blobfile = open('domination/' + Agent.NAME + '_blob', 'wb')
                pickle.dump(Agent.PRIOR_KNOWLEDGE, blobfile, pickle.HIGHEST_PROTOCOL)
            except:
                print "Agent %s can't write blob." % self.callsign
        Agent.SHARED_KNOWLEDGE.append(self)


    def observe(self, observation):
        self.observation = observation
        self.selected = observation.selected
        if observation.selected:
            print observation 


    def action(self):

        obs = self.observation

        if self.id == 0:
            self.getState()

        # Check if agent reached goal.
        if self.goal is not None and point_dist(self.goal, obs.loc) < self.settings.tilesize:
            self.goal = None 
                        
        # # Walk to ammo
        # ammopacks = filter(lambda x: x[2] == "Ammo", obs.objects)
        # if ammopacks:
        #     self.goal = ammopacks[0][0:2]
        #     # Register visible ammo
        #     for ammopack in ammopacks:
        #         loc = ammopack[0:2]
        #         #available = Agent.AMMOLOCS.get(loc, _)
        #         Agent.AMMOLOCS[loc] = 1
            

        # # Walk to random CP
        # if self.goal is None:
        #     for cp in obs.cps:
        #         self.goal = cp[0:2] #TODO: change is something usefull!!
        
        ammoloc1 = (184, 168)
        ammoloc2 = (312, 104)

        if self.id == 0:
            self.goal = ammoloc1

        if self.id == 1:
            self.goal = ammoloc2

        if self.id == 2: 
            self.goal = obs.loc
            pathLength = float('inf')
            for cp in obs.cps:
                if cp[2] != self.team: 
                    path = find_path(obs.loc, cp[0:2], self.mesh, self.grid, self.settings.tilesize)
                    if len(path) < pathLength:
                        pathLength = len(path)
                        self.goal = cp[0:2]

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
        

    #distance augments the intial needed turn to begin the path in pathlength
    def distance(self, loc, angle):
        x = loc[0]/16
        y = loc[1]/16
        distances = []
        for d in Agent.PRIOR_KNOWLEDGE[(x, y)]:
            steps = d[0]
            turn = angle_fix(d[1] - angle)
            steps += math.floor(abs(turn)/float(self.settings.max_turn))
            distances.append(steps)
        return distances

    def getState(self):
        # State = [[distances A0], ammo A0, ...An, [CP control]]
        # What about ammo spawn time, current score?
        state = []
        for agent in Agent.SHARED_KNOWLEDGE:
            state.append(self.distance(agent.observation.loc, agent.observation.angle))
            state.append(agent.observation.ammo > 0)
        state.append([x[2] for x in Agent.SHARED_KNOWLEDGE[0].observation.cps])
        print state
        return state


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




















