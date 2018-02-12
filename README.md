# Randomness requirements optimization tool for masked S-Boxes implementation

This tool was built to generate results of the paper
[Improved Bitslice Masking: from Optimized Non-Interference to Probe Isolation].
It is likely necessary to read this paper to effectively use and understand
this tool.

## Usage

The are 3 main tools:
* GF(256) AES S-Box optimization: [aes_gf256.py](aes_gf256.py)
* Bitslice implementation optimization: [aes_bitslice.py](aes_bitslice.py),
  [ft_bitslice.py](ft_bitslice.py) (and
  [aes_bitslice_export.py](aes_bitslice_export.py) to format results in LaTeX)
* Computations of the cost of various implementation strategies:
  [gadget_cost_com.py](gadget_cost_com.py)

## Dependencies

The scripts have been tested only with Python 3.6, with the following package
versions:
* `networkx == 2.1`
* `pulp == 1.6.8` (tested with integrated CBC solver and IBM CPLEX 12.8)
* `matplotlib == 2.1.2`

## License

Distributed under the terms of the Apache License (Version 2.0).
See [LICENSE](LICENSE) for details.
