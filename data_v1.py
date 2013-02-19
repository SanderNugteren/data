class Agent(object):
    
    NAME = "data_v1"
    SHARED_KNOWLEDGE = None # call with Agent.shared_knowledge not self.shared...!
    PRIOR_KNOWLEDGE = None
    AMMOLOCS = {}
    #TODO
    AGENTS = []
    STATE = None
    GOALS = []
    AGENT_SIZE = 12 #TODO get this from the Tank object
    
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
        
        
        # Read the binary blob
        if blob is not None:
            print "Agent %s received binary blob of %s" % (
               self.callsign, type(pickle.loads(blob.read())))
            blob.seek(0)
            Agent.PRIOR_KNOWLEDGE = pickle.load(blob)
            print Agent.PRIOR_KNOWLEDGE
            blob.seek(0) 
        
        # Recommended way to share variables between agents. 
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)
    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        
        self.observation = observation
        self.selected = observation.selected

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
            
        # Drive to where the user clicked
        # Clicked is a list of tuples of (x, y, shift_down, is_selected)
        if self.selected and self.observation.clicked:
            self.goal = self.observation.clicked[0][0:2]

        # Walk to random CP
        if self.goal is None:
            print 'cp:', obs.cps[0]
            self.goal = obs.cps[random.randint(0,len(obs.cps)-1)][0:2]
        
        shoot = False
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
        
        return (turn,speed,shoot)

    #TODO make a function that refreshes only every 4 secs or something
    #See if this helps/increases performance
    def refreshActions(self):
        '''
        Generates a dictionary of the form:
        actions[action] = list of x,y distances relative to the agent
        So for example:
        actions['get_ammo'] = [(0,1),(3,-6)]
        '''
        actions = {}
        actions['get_ammo'] = []
        actions['defend_cp'] = []
        actions['capture_cp'] = []
        actions['shoot'] = []
        obs = self.observation
        loc = obs.loc
        #ammo
        ammopacks = filter(lambda x: x[2] == "Ammo", obs.objects)
        if ammopacks:
            #self.goal = ammopacks[0][0:2]
            # Register visible ammo
            for ammopack in ammopacks:
                ammo_loc = ammopack[0:2]
                #available = Agent.AMMOLOCS.get(loc, _)
                Agent.AMMOLOCS[loc] = 1
                actions['get_ammo'].append(ammo_loc[0] - loc[0], ammo_loc[1] - loc[1])
            
        # Register missing ammo (ammo appears to bee seen even at max_see + 14 ?)
        max_see = self.settings.max_see
        visibleSpawnPoint = []
        for k in Agent.AMMOLOCS.keys():
            if abs(k[0]-obs.loc[0]) <= max_see and (abs(k[1]-obs.loc[1]) <= max_see): #if agent sees ammo spawn point
                visibleSpawnPoint.append(k)
            visibleAmmo = [loc[0:2] for loc in ammopacks]
            emptySpawnPoints = set(visibleSpawnPoint).difference(visibleAmmo)
            for esp in emptySpawnPoints:
                Agent.AMMOLOCS[esp] = 0

        #control points
        for cp in obs.cp:
            if cp[2] == self.team:
                actions['defend_cp'].append(cp[0] - loc[0], cp[1] - loc[1])
            else:
                actions['capture_cp'].append(cp[0] - loc[0], cp[1] - loc[1])
        #enemies
        if (obs.ammo > 0 and obs.foes):
            for foe in obs.foes:
                friendly_fire = False
                #check for range and colisions
                if (point_dist(foe[0:2], loc) < self.settings.max_range and
                not line_intersects_grid(loc, foe[0:2], self.grid, self.settings.tilesize)):
                    for friend in obs.friends:
                        #check for friendly fire
                        if line_intersects_circ(loc, foe[0:2], friend[0:2], AGENT_SIZE):
                            friendly_fire = True
                            break
                if not friendly_fire:
                    actions['shoot'].append(foe[0] - loc[0], foe[1] - loc[1])

        return actions

        
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
        Agent.PRIOR_KNOWLEDGE += 1 #just for testing
        blob = open("domination/agentB_blob" , "wb") #TODO: make path dynamical!!
        pickle.dump(Agent.PRIOR_KNOWLEDGE, blob)
        pass
       
'''
class State:

    def __init__():
        pass

    def getCPsControlled(self):
        pass
    
    def getAmmoTeam(self):
        pass

    def getEnemies(self):
        pass
'''

#This computes the optimal set of actions for all agents in a certain state
def compJointValue(agents, state):
    '''
    This function takes a list of agents, and the current state of the game.
    It computes the best joint action recursively
    '''
    #If there are no more agents left, stop
    if len(agents) is 0:
        #small alteration of my original code:
        #instead of returning 0, compute the actual state value here
        #and for the rest only compute costs
        return {}, computeValue(state)
    best_value = 0
    best_map = {}
    #find an agent in agents
    agent = agents[0]
    #remove it
    del agents[agent]
    #for each action, find the best map and its cost
    #combine this with the value of the action of this agent
    for a in agent.getActions():
        #TODO update the state as if this action was taken
        new_state = state.copy().execute(a)
        #done with copies to prevent stuff being changed during
        #recursion
        new_map, value = compJointValue(agents.copy(), new_state)
        if value + a.getCost() > best_value:
            best_map = new_map
            best_map[agent] = a
            best_value = value + a.getCost()
    return best_map, best_value

#TODO value function for state
def computeValue(state):
    #parameters (to learn)
    c = 1 #control point modifier
    a = 1 #ammo modifier
    e = 1 #enemy amount modifier
    return c * state.getCPsControlled() + a*state.getAmmoTeam() + e * state.getEnemies()

if __name__ == '__main__':
    #This code will execute when the file is run directly
    pass
