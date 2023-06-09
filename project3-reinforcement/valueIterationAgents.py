# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        iterations= self.iterations
        #get our iterations 
        for i in range(iterations):
          current = util.Counter()
          states = self.mdp.getStates()
          for state in states:
            #if terminal state we want to set to zero
            if self.mdp.isTerminal(state):
              current[state] = 0
              continue
            else:
              actions = self.mdp.getPossibleActions(state) 
              #initializing our largest to be a super small number
              largest = -100000000
              
              for action in actions:
                finalSum = 0
                #looking through the utilities and probabilities in our trans states
                transitionStates= self.mdp.getTransitionStatesAndProbs(state,action)
                for conseq, chance in transitionStates:
                  reward = self.mdp.getReward(state,action,conseq) 
                  finalSum += chance*reward
                  finalSum += chance*self.discount*self.values[conseq]
                if (finalSum>largest): 
                    largest = finalSum
                current[state] = largest
        #reset our iteration at the end
          self.values = current


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        qVal = 0
        transitions =self.mdp.getTransitionStatesAndProbs(state,action) 
        for conseq, chance in transitions:
          reward = self.mdp.getReward(state,action,conseq) 
          qVal += chance * reward
          qVal += chance* (self.discount*self.values[conseq])
        return qVal
        

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        else:
            val = float("-inf")
            actions = self.mdp.getPossibleActions(state)
            optimal = actions[0]
            for a in actions:
                if self.computeQValueFromValues(state, a) <= val:
                    continue
                else:
                    optimal = a
                    val = self.computeQValueFromValues(state, a)
                    
            return optimal

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        
        iterations = self.iterations
        for iteration in range(iterations):
            state = self.mdp.getStates()[iteration % len(self.mdp.getStates())]
            #if not a terminal state
            if self.mdp.isTerminal(state) ==False:
              curr = util.Counter()
              #iterate through the actions and get the q value for each state
              actions = self.mdp.getPossibleActions(state)
              for a in actions:
                  curr[a] = self.computeQValueFromValues(state, a)
              #set the value as the max out of all vals
              self.values[state] = max(curr.values())

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        #Initializing empty priority queue
        myQueue = util.PriorityQueue()

        #Dictionary to keep track of the sets of predecessors for each state, using the state as the key
        predecessors = {}

        #Iterate over all states to get predecessors and Q-values for each state
        for state in self.mdp.getStates():
          if not self.mdp.isTerminal(state):
            q_values = []
            #Compute predecessor states
            for action in self.mdp.getPossibleActions(state):
              for (nextState, prob) in self.mdp.getTransitionStatesAndProbs(state, action):
                if not nextState in predecessors.keys():
                  predecessors[nextState] = set()
                if prob > 0:
                  predecessors[nextState].add(state)
                  q_values.append(self.computeQValueFromValues(state, action))
            #Find difference between the current value of the state and the highest Q-value
            diff = abs(self.values[state] - max(q_values))
            #update the state in the priority queue
            myQueue.update(state, -1*diff)

        #iterate over all of the iterations
        for i in range(self.iterations):
          #terminate if priority queue is empty
          if myQueue.isEmpty():
            return
          #pop a state off the priority queue
          currState = myQueue.pop()

          #if the current state is not a terminal state, update it in self.values
          if not self.mdp.isTerminal(currState):
            q_values = []
            for action in self.mdp.getPossibleActions(currState):
              for (nextState, prob) in self.mdp.getTransitionStatesAndProbs(currState, action):                  
                if prob > 0:
                  q_values.append(self.computeQValueFromValues(currState, action))
          self.values[currState] = max(q_values)

          #Find difference between the current value of all the predecessors for the current state and their highest Q-value
          for predecessor in predecessors[currState]:
            q_values_predecessor = []
            #Compute q values for predecessor states
            for action in self.mdp.getPossibleActions(predecessor):
              q_values_predecessor.append(self.computeQValueFromValues(predecessor, action))
            diff = abs(self.values[predecessor] - max(q_values_predecessor))

            #check if diff is greater than theta and update the predecessor on the priority queue
            if diff > self.theta:
              myQueue.update(predecessor, -1*diff)