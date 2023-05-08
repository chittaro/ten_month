# EECS 281: Project 2 Part A - Star Wars Episode XI: A New Heap

**This README is for staff only.**

The spec is publicly available at https://eecs281staff.github.io/p2-a-new-heap

There are three major sections in the repo:

- [The Spec](#the-spec) (`docs/`): files used by GitHub Pages to generate the
  public version of the spec that is given to students
- [The Solution](#the-solution) (`solution/`): this is instructor reference
  solution as it is submitted to the AG to verify that is online
- [The Autograder](#the-autograder) (`ag/`): files needed for the automated
  deploy to course autograder (AG) hardware


## Quickstart

To review the instructor reference solution, enter The Solution and look
around: (there may be multiple solutions in subdirectories of solution/)

    $ cd solution
    $ ls
    $ less somefile.cpp

To build and run the instructor reference solution, enter The Solution and
use `make`:

    $ cd solution
    $ make release
    $ ./ship ...

To view the test cases used on the AG, enter The Autograder tests directory.
These files will most likely be compressed and unreadable as-is. Look at the
contents of `test-case-inputs.info` for size and mode info for each test
case. To view an individual test case, decompress it and have a look:

    $ cd ag/tests
    $ less test-case-inputs.info
    $ xz --decompress --keep compressed/sometestcase.xz
    $ mv compressed/sometestcase.txt .
    $ less sometestcase.txt

To make changes to the instructor reference solution or use another solution
and compare outputs to the AG with its test cases there is a bash script that
will compile the AG solution (executable named `correct`), decompress the
test case inputs (`ag/tests`) and run all test cases configured on the AG
(from project.ini), and put the outputs in a `testing/` directory. Also
included there will be a file with the test case invocations
`testing/integration-tests.ini`.

    $ ./testing.sh
    $ cd testing
    $ ls
    $ cat integration-tests.ini
    $ less sometest-out.txt
    $ ./correct [some opts/args] < someinput.txt

**`correct` is the AG solution against which all student outputs are
measured. Don't mess around in `ag/` unless you are making approved changes
to the AG itself.**


## Project Overview

These are the skills and concepts in this project:


## The Spec

You can find the spec in the [docs/](docs/) folder. The spec is publicly
available at
[https://eecs281staff.github.io/p2-a-new-heap/](https://eecs281staff.github.io/p2-a-new-heap/)

When the project is inactive (not being used in a given semester), the
abbreviated spec from the [inactive/](inactive/) folder should be used. In
the Inactive directory, a truncated version of the spec README.md that lives
in that directory will be displayed.

***TODO***: Add info about how to switch between active and inactive versions
of the spec here....


## The Solution


This is the instructor reference solution that you will usually find as the
first submit of the project. It can be found in `solution/`. The instructor
responsible for deploying will submit this version to verify the AG is up and
running and grading. There may be better ways to do things, but this is the
"average" version that is suitable for comparison to student-based solutions.


## The Autograder

This is where everything lives that make the g281 machines autograde. It can
be found in `ag/`. This is for faculty or AG staff only. To deploy a version
in a new semester, have a look in/edit `project.ini` at the top level of the
repo. After that, hands off everything in here unless you **know** what
you're doing!


## Contributing

See the [contributing guide](CONTRIBUTING.md) for help with spec preview,
project release, autograder setup, and more.
