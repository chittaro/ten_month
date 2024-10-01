<!-- ---
layout: spec
title: Hints and Advice
sitemapOrder: 1
--- -->

# Hints and Advice
{: .primer-spec-toc-ignore }

The project is specified so that the various pieces of output are all
independent. We strongly recommend working on them separately, implementing
one command-line option at a time. The autograder has *some* test cases which
are named so that you can get a sense of where your bugs might be.

We place a strong emphasis on time budgets in this project. This means that
you may find that you need to rewrite sections of your code that are
performing too slowly or consider using different data structures. Pay
attention to the Big-O complexities of your implementation and examine the
tradeoffs of using different possible solutions. Using `perf` on this project
will be incredibly helpful in finding which parts of your code are taking up
the most amount of time, and remember that `perf` is most effective when your
code is well modularized (i.e. broken up into functions).

Running your code locally in valgrind can help you find and remove
undefined (buggy) behavior and memory leaks from your code. This can save
you from losing points in the final run when you mistakenly believe your
code to be correct.

It is extremely helpful to compile your code with the following gcc
options: `-Wall -Wextra -Werror -Wconversion -pedantic`. This way the
compiler can warn you about parts of your code that may result in
unintended/undefined behavior. Compiling with the provided Makefile does
this for you.

Don’t spend all your time getting Part A working before thinking about Part
B. Start reading the Fredman paper to prepare for Pairing Heaps, study and
understand the [Unordered Priority Queue](https://eecs281staff.github.io/p2b-priority-queues/p2b-priority-queues/UnorderedPQ.hpp), and start
working on the [Sorted Priority Queue](https://eecs281staff.github.io/p2b-priority-queues/p2b-priority-queues/SortedPQ.hpp); this one is
mostly about using the STL, there’s very little actual code to write (the
best solution is on the order of 5 lines of code added). Lecture 8 (on Heaps)
is what you need to understand and implement the
[Binary Priority Queue](https://eecs281staff.github.io/p2b-priority-queues/p2b-priority-queues/BinaryPQ.hpp).
