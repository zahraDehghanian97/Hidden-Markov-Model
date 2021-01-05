import json
import os


class MyHmm(object):  # base class for different HMM models
    def __init__(self, model_name):
        # model is (A, B, pi) where A = Transition probs, B = Emission Probs, pi = initial distribution
        self.model = json.loads(open(model_name).read())["hmm"]
        self.A = self.model["A"]
        self.states = self.A.keys()  # get the list of states
        self.N = len(self.states)  # number of states of the model
        self.B = self.model["B"]
        s = []
        for k, v in self.B.items():
            s.extend(v.keys())
        s = set(s)
        self.symbols = s  # get the list of symbols, assume that all symbols are listed in the B matrix
        self.M = len(self.symbols)  # number of states of the model
        self.pi = self.model["pi"]
        return

    def backward(self, obs):
        self.bwk = [{} for t in range(len(obs))]
        T = len(obs)
        # Initialize base cases (t == T)
        for y in self.states: self.bwk[T - 1][y] = 1  # self.A[y]["Final"] #self.pi[y] * self.B[y][obs[0]]
        for t in reversed(range(T - 1)):
            for y in self.states:
                self.bwk[t][y] = sum(
                    (self.bwk[t + 1][y1] * self.A[y][y1] * self.B[y1][obs[t + 1]]) for y1 in self.states)
        prob = sum((self.pi[y] * self.B[y][obs[0]] * self.bwk[0][y]) for y in self.states)
        return prob

    def forward(self, obs):
        self.fwd = [{}]
        # Initialize base cases (t == 0)
        for y in self.states:
            self.fwd[0][y] = self.pi[y] * self.B[y][obs[0]]
        # Run Forward algorithm for t > 0
        for t in range(1, len(obs)):
            self.fwd.append({})
            for y in self.states:
                self.fwd[t][y] = sum((self.fwd[t - 1][y0] * self.A[y0][y] * self.B[y][obs[t]]) for y0 in self.states)
        prob = sum((self.fwd[len(obs) - 1][s]) for s in self.states)
        return prob

    def forward_backward(self, obs, iteration):  # returns model given the initial model and observations
        for d in range(iteration):
            landa = [{} for t in range(len(obs))]
            phi = [{} for t in range(len(obs) - 1)]
            # Expectation step : compute landa and phi
            p_obs = self.forward(obs)
            self.backward(obs)
            for t in range(len(obs)):
                for y in self.states:
                    landa[t][y] = (self.fwd[t][y] * self.bwk[t][y]) / p_obs
                    if t == 0: self.pi[y] = landa[t][y]
                    if t == len(obs) - 1:continue
                    phi[t][y] = {}
                    for y1 in self.states:
                        phi[t][y][y1] = round(self.fwd[t][y] * self.A[y][y1] * self.B[y1][obs[t + 1]] * self.bwk[t + 1][y1] / p_obs , 4)
            # Maximization step : compute A and B
            for y in self.states:
                # compute A
                for y1 in self.states:
                    val = sum([phi[t][y][y1] for t in range(len(obs) - 1)])  #
                    val /= sum([landa[t][y] for t in range(len(obs) - 1)])
                    self.A[y][y1] = round(val,4)
                # compute B
                for k in self.symbols:
                    val = 0.0
                    for t in range(len(obs)):
                        if obs[t] == k: val += landa[t][y]
                    val /= sum([landa[t][y] for t in range(len(obs))])
                    self.B[y][k] = round(val,4)
        return

    def viterbi(self, obs):
        vit = [{}]
        path = {}
        # Initialize base cases (t == 0)
        for y in self.states:
            vit[0][y] = self.pi[y] * self.B[y][obs[0]]
            path[y] = [y]
        # Run Viterbi for t > 0
        for t in range(1, len(obs)):
            vit.append({})
            newpath = {}
            for y in self.states:
                (prob, state) = max((vit[t - 1][y0] * self.A[y0][y] * self.B[y][obs[t]], y0) for y0 in self.states)
                vit[t][y] = prob
                newpath[y] = path[state] + [y]
                # Don't need to remember the old paths
            path = newpath
        n = 0  # if only one element is observed max is sought in the initialization values
        if len(obs) != 1:
            n = t
        (prob, state) = max((vit[n][y], y) for y in self.states)
        return (prob, path[state])


seq0 = ('Heads', 'Heads', 'Heads')
seq1 = ('Heads', 'Heads', 'Tails')
seq2 = ('Heads', 'Tails', 'Heads')
seq3 = ('Heads', 'Tails', 'Tails')
seq4 = ('Tails', 'Heads', 'Heads')
seq5 = ('Tails', 'Heads', 'Tails')
seq6 = ('Tails', 'Tails', 'Heads')
seq7 = ('Tails', 'Tails', 'Tails')
observation_list = [seq0, seq1, seq2, seq3, seq4, seq5, seq6, seq7]
observations = seq6 + seq0 + seq7 + seq1  # you can set this variable to any arbitrary length of observations
print("Learning the model through Forward-Backward Algorithm for the observations", observations)
models_dir = os.path.join('.', 'models')
model_file = os.path.join(models_dir,"coins1.json")
hmm = MyHmm(os.path.join('.', model_file))

iteration = [1,5,10]
for iter in iteration:
    hmm.forward_backward(observations , iter)
    print("The new model parameters after "+str(iter)+" iteration are: ")
    print("A = ", hmm.A)
    print("B = ", hmm.B)
    print("pi = ", hmm.pi)
