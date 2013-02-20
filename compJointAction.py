import math
import time

#This computes the optimal set of actions for all agents in a certain state
#TODO value function for state
def compJointValue(agents, state):
    '''
    This function takes a dict of the current positions of each agent,
    and a list of goal positions. It returns a dictionary of positions for
    each agent to move to, and the total distance for all agents.
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
    agent = agents.keys()[0]
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

if __name__ == '__main__':
    #This code will execute when the file is run directly
    pass
