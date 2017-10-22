
## Problem statement

A computation circuit operating over GF(2^n) is given (example AES S-Box)
as a computation flowgraph: a directed acyclic graph (DAG) where vertices represent
operations (gates), and edges represent data.

The goal is to prove that a circuit is (S)NI, if the NI/SNI proporty is given for each gate,
or to modify the flowgraph and add required properties on gates to make the circuit (S)NI
(optimizing some cost criterion).

## Graph description

The computation flowgraph (it is a directed acyclic graph, DAG). It is
made of 5 kinds of vertices:
+ A: Represents a basic arithmetic operation (typically: multiplication or addition).
It is assumed that it can be instantiated in NI and SNI versions.
Can have any number of inputs, always has one output.
+ S: 1 input, n outputs. This "split" vertex is used to model the use of a
value as an input for different vertices. (The values of the outputs are
the same as the input.)
+ I: 0 input, 1 output. This vertex represents an input of the circuit.
+ O: 1 input, 0 output. This vertex represents an output of the circuit.

A refresh is an identity SNI arithmetic vertex.

## Reduction from NI to graph theory

The goal is to prove that circuit is NI, by computing properties of the graph.

For each wire $i$, we can compute an upper bound $S_i$ on the number of known
shares required to simulate the circuit for a given set of adversarial probes.
Let $I_i$ the number of adversarial probes in gate $i$.
This bound depends on the gate $j$ at the input of which the wire $i$ is
connected:
+ O: $S_i = 0$.
+ R: $S_i = I_j$
+ S: $S_i = S_k + S_l$, with $k$ and $l$ the ouput wires of the gate. We assume
that the adversary cannot put probes in S gates.
+ A1/A2: $S_i = I_j + S_k$, where $k$ is the output wire.

Let $i$ a wire. We want $S_i \leq d$.  By developping the expression os $S_i$,
we can write it as $S_i = \sum_j \alpha_j I_j$, $\alpha_j \in N$. Since the
adversary can make arbitrary choices for $I_j$ and $\sum_j I_j \leq d$. Our
goal is fullfilled iff $\alpha_j \leq 1$ for all $j$.

If we ignore Refresh gates, we can see that the values of $S_i$ propagates
backwards in the graph, being added together at Split gates, and increased by
$I_j$ at other gates.  Hence, a necessary and sufficient condition for NI is
that there is no pair of vertices $(i_1, i_2)$ such that there are two distinct
paths from $i_1$ to $i_2$, since it would imply that at the start of the path,
a wire would have a coefficient $\alpha_{i_2} > 1$.

A Refresh gate stops this propagation, and instead sets $S_i = I_j$, it thus
acts like it has no output wire. If the graph is modified in such a way, the
previous condition becomes equivalent to NI.

To get SNI, the additionnal requirement is that there is no path between any
input vertex and any output vertex.

These properties can be efficiently tested, since the algorithm for computing number of
paths in a DAG has $O(m+n)$ complexity, where $m$ and $n$ are the number of
vertices and edges.

## Deciding where to put NI, SNI and refresh gates

We reformulate the problem as an integer linear optimization problem.

For each edge i, $c_i = 1$ if the edge is cut, $c_i = 0$ otherwise.

For each pair of nodes $(i, j)$, the set of paths $P_{i, j, k}, k = 1, ..., n$
is computed, and $p_{i, j, k} = 1$ if the path is cut, 0 otherwise.
At least $n-1$ paths must be cut: $\sum{k=1}^n p_{i,j,k} \geq n-1$.
A path is cut if any of the edges in the wire is cut (hence
$p_{i, j, k} \leq \sum_{l in p_{i,j,k}} c_l$).

To get SNI, for input and output nodes, all the paths must be cut.

### Handling split with more than two outputs

To get maximum efficiency, the problem should be studied with a network of split-2 in place of each split-n.
The exact topology of the network impacts the result, hence each different topology should be studied (each topology corresponds to a
set partition of n).
This can be handled in one instance of the problem. (to be analyzed.)

### Cost function

The cost is associated to cutting edges. A simple metric is the number of cut edges, which is realistic
if each cut edge corresponds to a SNI refresh insertion.
It can be less costly, for example, to change a multiplication into a SNI multiplication (this corresponds to cutting
its output edge), and this can be represented by taking a weighted sum of cut edges as cost function.

