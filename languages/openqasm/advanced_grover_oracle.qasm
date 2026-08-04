OPENQASM 3.0;
include "stdgates.inc";

// Advanced Exhibit: 3-Qubit Grover Search Oracle & Diffuser
qubit[3] q;
bit[3] c;

// Superposition
h q[0];
h q[1];
h q[2];

// Oracle for target |111>
cz q[0], q[2];

// Diffuser
h q[0]; h q[1]; h q[2];
x q[0]; x q[1]; x q[2];
h q[2];
cz q[0], q[2];
h q[2];
x q[0]; x q[1]; x q[2];
h q[0]; h q[1]; h q[2];

c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
