class Agent(object):
    #This agent is a dummy that doesn't do anything, for testing purposes.
    NAME = "dummy" # Replay filenames and console output will contain this name.
        
    def __init__(self, id, team, settings=None,
        field_rects=None, field_grid=None,
        nav_mesh=None, **kwargs):
        pass
            
    def observe(self, observation):
        pass
                    
    def action(self):
        return (0,0,False)
                        
    def debug(self, surface):
        pass
                        
    def finalize(self, interrupted=False):
        pass
