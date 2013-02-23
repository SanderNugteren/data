import random

class Agent(object):
    
    NAME = "agent_T1"
    SHARED_KNOWLEDGE = None 
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

        ammoloc1 = (152, 136)
        ammoloc2 = (312, 136)
        
        if self.goal == None:
            if obs.step < 10:
                if self.id == 0:
                    self.goal = ammoloc1
                if self.id == 1:
                    self.goal = ammoloc2
                if self.id == 2: 
                    self.goal = obs.cps[0][0:2]
            else:
                if obs.ammo == 0:
                    if random.randint(0,1):
                        self.goal = ammoloc1
                    else:
                        self.goal = ammoloc2
                else:
                    if random.randint(0,1):
                        self.goal = obs.cps[0]
                    else:
                        self.goal = obs.cps[1]

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


        # Shoot enemies
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
        if self.id == 0 and self.blobpath is not None:
            try:
                # We simply write the same content back into the blob.
                # in a real situation, the new blob would include updates to
                # your learned data.
                print self.blobpath
                blobfile = open(self.blobpath, 'wb')
                pickle.dump(self.blobcontent, blobfile, pickle.HIGHEST_PROTOCOL)
            except:
                # We can't write to the blob, this is normal on AppEngine since
                # we don't have filesystem access there.        
                print "Agent %s can't write blob." % self.callsign

