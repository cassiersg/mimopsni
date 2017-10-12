
## Graph description

Compute the computation flowgraph (it is a directed acyclic graph, DAG). It is
made of 5 kinds of vertices:
+ A2: 2 inputs, 1 output. This vertex represents any arithmetic operation over
two values (typically multiplication).
+ A1: 1 inputs, 1 output. This vertex represents any arithmetic operation over
one value (typically squaring).
+ S: 1 input, 2 outputs. This "split" vertex is used to model the use of a
value as an input for two different vertices. (The values of the outputs are
the same as the input.)
+ I: 0 input, 1 output. This vertex represents an input of the circuit.
+ O: 1 input, 0 output. This vertex represents an output of the circuit.
+ R: 1 input, 1 output. This vertex represents a SNI refresh.

All the wires in the circuit are represented as directed edges.
We assume that all the implementations of the gates are NI.

NB: Any SNI gate can be modelled as a NI gate followed by a SNI refresh.

## Reduction from NI to graph theory

The goal is to prove that circuit is NI, by computing properties of the graph.
(SNI is handled by adding a SNI refresh at the output.)

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

This property can be easily tested, since the algorithm for computing number of
paths in a DAG has $O(m+n)$ complexity, where $m$ and $n$ are the number of
vertices and edges.

## Deciding where to put NI, SNI and refresh gates

The problem know is to optimally build the circuit, not only to prove that it
is NI.  As a simplification, we consider only inserting refresh gates.
(Possible simplification to SNI gates can be done easily after this step.) The
goal is to minimize the number of refresh gates.

Remark: inserting a refresh gate on a wire is equivalent to removing the corresponding edge.
Furthermore, the graph can be simplified by removing A1 gates (and merging their input and output wires).

### Proposed heuristic algorithm

Count the number of "multipaths", i.e. $\sum_{(i_1, i_2), P(i_1, i_2)>1} P(i_1,i_2)$, where $P(i_1, i_2)$ is the number of paths between $i_1$ and $i_2$.
Iteratively, remove the edge whose removal would give the lowest number of multipaths.

Intuition: do not use "multipaths", but "minimal multipaths" could give better results.


