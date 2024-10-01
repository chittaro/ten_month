<!-- ---
layout: spec
title: Test Case Legend
sitemapOrder: 10
--- -->

# Test Case Legend
{: .primer-spec-toc-ignore }

Some of the test cases on the autograder follow a pattern and others do
not. The test files that do not fit this pattern you can think of as
handwritten cases which test a particular aspect of your program, though
some can be very large.

- `INV*`: Invalid test cases, derived from the
  [TL Input Errors](https://eecs281staff.github.io/p2-stocks/#tl-input-errors).

- `st*`: The example from the project specification, in TL mode.

- `sp*`: The example from the project specification, in PR mode.

- `P*`: PR mode files, of a varying number of orders.

- `K*`: TL mode files, which contain a large number of orders.

- `M*`: TL mode files, which tend to be small-medium number of orders.

- `F*`: TL or PR mode files, which tend to have a small-medium number of
trades.

`*A*`: Runs with all options: `-i -m -t -v`.

`*i*`, `*m*`, `*t*`, `*v*`: Run with just one of the options (`-i` *or* `-m`
*or* `-t` *or* `-v`).
