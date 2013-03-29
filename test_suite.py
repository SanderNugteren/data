#This module is used to test agents
#Place it in the Domination-Game dir, otherwise the import will not work
from domination import core
import math

# Make it a short game
settings = core.Settings(max_steps=300,
                              max_score=100,
                              spawn_time=11,
                              ammo_amount=1,  
                              ammo_rate=9,
                              max_range=60,
                              max_see=80,
                              max_turn=math.pi/4,
                              think_time=0.06,
                              capture_mode=core.CAPTURE_MODE_MAJORITY)

FIELD2 = """
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ C _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ w w w w w w w w w w w w w w w _ _ _ _ _ _ _ w
w _ _ _ w _ _ _ w _ _ _ _ _ _ _ _ _ _ a _ _ _ _ _ _ w _ _ _ w
w R _ _ w _ _ _ w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w _ _ B w
w R _ _ w _ _ _ w _ _ _ _ w w w w w _ _ _ _ w _ _ _ w _ _ B w
w R _ _ w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w _ _ _ w _ _ B w
w _ _ _ w _ _ _ _ _ _ a _ _ _ _ _ _ _ _ _ _ w _ _ _ w _ _ _ w
w _ _ _ _ _ _ _ w w w w w w w w w w w w w w w _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ C _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
"""
FIELD = core.Field.from_string(FIELD2)

runs = 1000 #maybe make this into convergence
#opponents we will be playing (hope the ordering is from easy to difficult here)
opponents = ['agent',
    #'Vasili_IIv8',
    #'KillerQueen_v5',
    #'HardCoded_v2'
    ]

for op in opponents:
    avg = 0
    avgR = 0
    f = open('../data/results/results'+op,'wb')
    path = '../data/adversaries/'+op+'.py'
    for i in xrange(runs):
        print op + ' ' + str(i)
        #test
        r_init = {}
        #r_init["beta"] = 10
        # Initialize a game
        game = core.Game('../data/scotty.py', path,
            record=False, rendered=False, settings=settings, field=FIELD, red_init=r_init, verbose=False)
        # Will run the entire game.
        game.run()
        stats = game.stats
        #print "score red: " + str(stats.score_red)
        #print "score red/total: " + str(stats.score)
        avg = (i*avg + stats.score)/(i+1)
        avgR = (i*avgR + stats.score_red)/(i+1)
        f.write(str(stats.score) + ',' + str(avg) + '\n')
