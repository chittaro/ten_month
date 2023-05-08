#!/usr/bin/env python2
"""
Usage:
    python projkit.py test <project-ini> <submit-file>
    python projkit.py compile-genoutput <project-ini>
    python projkit.py compile-grade <project-ini>
    python projkit.py compile-solutions <project-ini>
    python projkit.py compile-register <project-ini>
"""
#from sortedcontainers import SortedDict
import ConfigParser as cp
import collections
import contextlib
import logging
import glob
import tempfile
import os
import re
import shutil
import subprocess
import sys


def die(message):
    """Print the given message and exit(1)."""
    print(message)
    sys.exit(1)


def print_usage():
    """Print the usage message and exit(1)."""
    print(__doc__.strip())
    sys.exit(1)


class ScriptCompiler(object):
    GENOUTPUT_TEMPLATE = r"""
#!/usr/bin/perl
require "../../common/projkit/genoutput.pl";

my %project_data = (
    "solution_exe" => "{solution_exe}",
    "solution_dir" => "{solution_dir}",
    "output_dir"   => "{output_dir}",
    "tests_dir"    => "{tests_dir}",
);

my @tests = (
{test_cases}
);

genoutput(\%project_data, \@tests);
""".strip()

    def __init__(self, config):
        self._config = config

    def get_genoutput(self):
        """Returns the contents of 'genoutput.pl', which generates the test
        cases and benchmarks for the autograder.

        """
        test_cases = ""
        #for k, v in self._config.integration_tests.iteritems():
        for k in sorted(self._config.integration_tests):
            test_input, flags = self._config.integration_tests[k]
            if not self._config.tests_to_stdin:
                test_input = "/dev/null"
            test_cases += "    '{test_id}', '{test_input}', '{flags}',\n".format(
                test_id=k,
                test_input=test_input,
                flags=flags
            )

        return self.GENOUTPUT_TEMPLATE.format(
            test_cases=test_cases,
            solution_exe=self._config.staff_solution_exe,
            solution_dir=self._config.staff_solution_dir,
            tests_dir=self._config.integration_tests_dir,
            output_dir=OutputGenerator.OUTPUT_DIR
        )

    # Note the double-braces for Python's str.format function.
    GRADE_TEMPLATE = r"""
#!/usr/bin/perl
our $project_info = {{
    "project_id"        => "{project_id}",
    "hints_file"        => "{hints_file}",
    "identifier"        => "{identifier}",
    "total_points"      => {total_points},
    "submission_exe"    => "{submission_exe}",
    "has_test_suite"    => {has_test_suite},
    "solution_dir"      => "{solution_dir}",
    "judge_dir"         => "{judge_dir}",
    "judge_exes"        => {judge_exes},
    "tests_to_stdin"    => {tests_to_stdin},
    "valid_cerr_output" => {valid_cerr_output},
    "has_scoreboard"    => {has_scoreboard},
}};

our $jail_info = {{
    "time_limit"           => {time_limit},
    "disk_limit"           => {disk_limit},
    "memory_limit"         => {memory_limit},
    "student_files"        => {student_files},
    "grader_files"         => {grader_files},
    "prohibited_libraries" => {prohibited_libraries},
}};

our $test_info = {{
    "test_dir"            => "{integration_tests_dir}",
    "invalid_test_prefix" => "{invalid_test_prefix}",
    "integration_points"  => {integration_points},
    "memory_leak_points"  => {memory_leak_points},
    "memory_leak_percent" => {memory_leak_percent},
    "runtime_scoring"     => "{runtime_scoring}",
    "memory_scoring"      => "{memory_scoring}",
}};

our %leak_check_cases = {leak_check_cases};

our $suite_info = {{
    "points"                 => {test_suite_points},
    "flags_command"          => "{flags_command}",
    "min_bugs_for_points"    => {min_bugs_for_points},
    "bugs_for_full_points"   => {bugs_for_full_points},
    "bugs_for_extra_submit"  => {bugs_for_extra_submit},
    "buggy_solutions"        => {buggy_solutions},
    "test_suite_exe"         => "{test_suite_exe}",
    "max_student_test_files" => {max_student_test_files},
}};

require "common/projkit/grade.pl";

""".strip()

    def get_grade(self):
        """Return the contents of `grade.pl`, which actually runs the grading
        process on the autograder.

        """
        def to_perl_array(array):
            """Converts a Python list into a Perl array reference of strings.

            """
            # Assume that Python is better at escaping things than us.
            return str(array)

        judges_exe_str = "{\n"
        for i in self._config.judge_regexes:
            judges_exe_str += "        '{regex}' => '{exe}',\n".format(
                regex=i[1].pattern,
                exe=i[0]
            )
        judges_exe_str += "    }"

        leak_check_cases_str = "(\n"
        for i in self._config.leak_check_cases:
            test_file, flags = self._config.integration_tests[i]
            test_file_str = "'test_file' => '{test_file}'".format(
                test_file=test_file
            )
            flags_str = "'flags' => '{flags}'".format(
                flags=flags
            )
            value = "{{{test_file_str}, {flags_str}}}".format(
                test_file_str=test_file_str,
                flags_str=flags_str
            )
            leak_check_cases_str += "\t'{name}' => {value},\n".format(
                name=i,
                value=value
            )
        leak_check_cases_str += ")"

        strings = {
            "project_id": self._config.project_id,
            "hints_file": self._config.hints_file,
            "identifier": self._config.identifier,
            "total_points": self._config.total_points,
            "submission_exe": self._config.submission_exe,
            "has_test_suite": int(self._config.has_test_suite),
            "solution_dir": self._config.staff_solution_dir,
            "judge_dir": self._config.judge_dir,
            "judge_exes": judges_exe_str,
            "tests_to_stdin": int(self._config.tests_to_stdin),
            "valid_cerr_output": to_perl_array(self._config.valid_cerr_output),
            "has_scoreboard": int(self._config.has_scoreboard),

            "time_limit": self._config.jail_time_limit,
            "disk_limit": self._config.jail_disk_limit,
            "memory_limit": self._config.jail_memory_limit,
            "student_files": to_perl_array(self._config.student_files),
            "grader_files": to_perl_array(self._config.grader_files),
            "prohibited_libraries": to_perl_array(
                self._config.prohibited_libraries
            ),

            "integration_tests_dir": self._config.integration_tests_dir,
            "invalid_test_prefix": self._config.invalid_test_prefix,
            "integration_points": self._config.integration_points,
            "memory_leak_points": self._config.memory_leak_points,
            "memory_leak_percent": self._config.memory_leak_percent,
            "runtime_scoring": self._config.runtime_scoring,
            "memory_scoring": self._config.memory_scoring,

            "leak_check_cases": leak_check_cases_str,

            "test_suite_points": 0,
            "flags_command": "",
            "min_bugs_for_points": 0,
            "bugs_for_full_points": 0,
            "bugs_for_extra_submit": 9999, 
            "buggy_solutions": to_perl_array([]),
            "test_suite_exe": "",
            "max_student_test_files": 10,
        }

        if self._config.has_test_suite:
            strings.update({
                "test_suite_points": self._config.test_suite_points,
                "flags_command": self._config.flags_command,
                "min_bugs_for_points": self._config.min_bugs_for_points,
                "bugs_for_full_points": self._config.bugs_for_full_points,
                "bugs_for_extra_submit": self._config.bugs_for_extra_submit,
                "buggy_solutions": to_perl_array(self._config.bugs),
                "test_suite_exe": self._config.test_suite_exe,
                "max_student_test_files": self._config.max_student_test_files,
            })

        return self.GRADE_TEMPLATE.format(**strings)

    REGISTER_TEMPLATE = r"""
#!/usr/bin/perl
require "../../common/projkit/register_project.pl";

register_project(
    "{project_id}",
    "{project_description}",
    "{closing_time}",
    "{daily_submissions}",
    "{bugs_for_extra_submit}",
    "{has_scoreboard}"
);
""".strip()

    def get_register(self):
        closing_date = self._config.closing_date
        closing_time = "{closing_date} 23:59:59".format(
            closing_date=closing_date
        )

        return self.REGISTER_TEMPLATE.format(
            project_id=self._config.project_id,
            project_description=self._config.project_description,
            closing_time=closing_time,
            daily_submissions=self._config.daily_submissions,
            bugs_for_extra_submit=self._config.bugs_for_extra_submit,
            has_scoreboard=self._config.has_scoreboard
        )


def shellquote(s):
    """Quote an argument to a shell command.

    From http://stackoverflow.com/a/35857/344643

    """
    return "'" + s.replace("'", "'\\'") + "'"


class Jail(object):
    """Simulates the autograder jail."""
    def __init__(self, directory, time_limit, disk_limit, memory_limit):
        """Constructor."""
        self.directory = directory
        self.time_limit = time_limit
        self.disk_limit = disk_limit
        self.memory_limit = memory_limit

    def run(
        self,
        command,
        accept_failure=False,
        limited=False
    ):
        """Runs the given command in the jail, without limiting resources. It's
        assumed that the script has pre-sanitized the command.

        """
        if limited:
            command = (
                "ulimit -f {disk} && "
                "ulimit -t {time} && "
                "ulimit -m {memory} && "
                "{command}".format(
                    disk=self.disk_limit,
                    time=self.time_limit,
                    memory=self.memory_limit,
                    command=command
                )
            )

        logging.info("Running command '{command}'".format(command=command))
        return_code = subprocess.call(command, shell=True)

        if return_code != 0 and not accept_failure:
            die("Command failed: '{command}'".format(command=command))

        return return_code

    @contextlib.contextmanager
    def cd(self, new_dir):
        old_dir = os.getcwd()
        try:
            os.chdir(new_dir)
            yield
        finally:
            os.chdir(old_dir)


@contextlib.contextmanager
def make_jail(time_limit, disk_limit, memory_limit):
    """Construct a new jail, which will be cleaned up afterward."""
    jail_dir = tempfile.mkdtemp()
    logging.info("Jail dir is {jail_dir}".format(jail_dir=jail_dir))
    jail = Jail(jail_dir, time_limit, disk_limit, memory_limit)
    try:
        with jail.cd(jail_dir):
            yield jail
    finally:
        shutil.rmtree(jail_dir)


def parse_arguments(arguments):
    """Parse the command-line arguments.

    We don't want to have any dependencies, so we can't use a library like
    `docopt`.

    """
    if not arguments:
        raise ValueError("No command given.")

    compile_commands = ["genoutput", "grade", "solutions", "register"]
    compile_commands = ["compile-" + i for i in compile_commands]

    command = arguments[0]

    if command == "test":
        try:
            return (command_test, {
                "config_file": arguments[1],
                "submit_file": arguments[2],
            })
        except IndexError:
            raise ValueError("Invalid parameters to 'test'.")
    elif command in compile_commands:
        func_name = "command_{func_name}".format(
            func_name=command.replace("-", "_")
        )
        # Should not throw an error -- we registered this function in
        # `compile_commands` above, so it should exist.
        func = globals()[func_name]

        try:
            return (func, {"config_file": arguments[1]})
        except IndexError:
            raise ValueError("Invalid parameters to '{command}'.".format(
                command=command
            ))

    raise ValueError("Not a command: {command}".format(
        command=command
    ))


class OutputGenerator(object):
    """Generates output and benchmarking information for a given test."""
    OUTPUT_DIR = "output"
    """The directory to put all the output in."""

    OUTPUT_EXTENSION = "output"
    """The extension for output files."""

    BENCHMARK_EXTENSION = "benchmark"
    """The extension for benchmarking information."""

    MIN_BENCHMARK_TIME = 0.003
    """The minimum time to benchmark a test case at, since minor variability
    will otherwise cause tests to fail.

    """

    BENCHMARK_FACTOR = 1.5
    """The time multiplier to allow for student submissions."""

    def __init__(self, config, test_runner):
        self._config = config
        self._exe_path = os.path.join(
            ".",
            config.staff_solution_dir,
            config.staff_solution_exe
        )
        self._test_runner = test_runner

    def _make_output_dir(self):
        """Make the output directory if it doesn't exist."""
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

    def generate_output(self, test_id, test_info):
        """Generate output for a given test and write it to the appropriate
        files in `OUTPUT_DIR`.

        """
        self._make_output_dir()

        output_path = self.get_output_path(test_id)
        benchmark_path = self.get_benchmark_path(test_id)

        should_remake = self._should_remake(
            test_id,
            test_info,
            output_path,
            benchmark_path
        )
        if not should_remake:
            logging.info("Skipped output generation for test {test_id}".format(
                test_id=test_id
            ))
            return
        else:
            logging.info("Generating output for test {test_id}".format(
                test_id=test_id
            ))

        input_file, flags = test_info
        input_path = os.path.join(
            self._config.integration_tests_dir,
            input_file
        )

        _, total_time = self._test_runner.run_with_flags_timed(
            self._exe_path,
            input_path,
            flags,
            output_path,
            accept_failure=False
        )

        total_time *= self.BENCHMARK_FACTOR
        total_time = max(self.MIN_BENCHMARK_TIME, total_time)
        logging.info("Got benchmark time {time} for test {test_id}".format(
            time=total_time,
            test_id=test_id
        ))
        self._save_benchmark_data(test_id, test_info, total_time)

    def _should_remake(self, test_id, test_info, output_path, benchmark_path):
        """Determines whether or not the output and benchmarking data should be
        remade.

        """
        if self._config.is_invalid_test_case(test_id):
            return False

        exists = os.path.exists
        if not exists(output_path) or not exists(benchmark_path):
            return True

        mtime = os.path.getmtime
        exe_mtime = mtime(self._exe_path)
        output_mtime = mtime(output_path)
        benchmark_mtime = mtime(benchmark_path)

        if exe_mtime > output_mtime or exe_mtime > benchmark_mtime:
            return True

        benchmark_data = self.get_benchmark_data(test_id)
        if benchmark_data["flags"] != test_info[1]:
            return True

        return False

    @classmethod
    def get_output_path(cls, test_id):
        """Get the path to the output file for a given test."""
        output_filename = "{test_id}.{output_ext}".format(
            test_id=test_id,
            output_ext=cls.OUTPUT_EXTENSION
        )
        return os.path.join(cls.OUTPUT_DIR, output_filename)

    @classmethod
    def get_benchmark_path(cls, test_id):
        """Get the path to the benchmark file for a given test."""
        benchmark_filename = "{test_id}.{benchmark_ext}".format(
            test_id=test_id,
            benchmark_ext=cls.BENCHMARK_EXTENSION
        )
        return os.path.join(cls.OUTPUT_DIR, benchmark_filename)

    @classmethod
    def get_benchmark_data(cls, test_id):
        """Returns a dict with keys: "input", the input file; "flags", the flags
        to pass to the program (as a string); and "time", the benchmark time.

        """
        ret = {}
        with open(cls.get_benchmark_path(test_id)) as f:
            lines = f.readlines()
            ret["input"] = lines[0].strip()
            ret["flags"] = lines[1].strip()
            ret["time"] = float(lines[2].strip())
        return ret

    def _save_benchmark_data(self, test_id, test_info, time):
        """Save the given benchmark data for a test.

        test_id: The test ID.
        test_info: A list with the input file as the first element and the
            flags as the remainder.
        time: The benchmarked time, as a float.

        """
        data = "{input}\n{flags}\n{time}\n".format(
            input=test_info[0],
            flags=test_info[1],
            time=time
        )
        with open(self.get_benchmark_path(test_id), "w") as f:
            f.write(data)


class JudgeResult(object):
    """The result of a judge run. Either the judge rejected the student
    result, or it accepted it with some 'ratio', denoting the percentage of
    points awarded to that student. (Usually that ratio is 1.00, but this
    changes for things like TSP optimization.)

    """
    def __init__(self, status, ratio=None):
        """Constructor.

        status: The return code of the judge. 0 means that the student
            passed, 2 means that the student failed, and 1 means that an
            internal error occurred.
        ratio: The percentage of points to award to the student. If not
            provided, defaults to 1.0. This is ignored and the student is
            awarded no points if they did not pass the test case.

        """
        self._status = status
        if ratio is None:
            self._ratio = 1.0
        else:
            self._ratio = ratio

    @property
    def passed(self):
        """Whether or not the student passed this test case."""
        return (self._status == 0)

    @property
    def status(self):
        return self._status

    @property
    def ratio(self):
        """The percentage of points to award to the student for the test case.
        If the student did not pass, returns 0.0; otherwise, usually returns
        1.0 (unless the judge did something to specify the ratio of awarded
        points).

        """
        if self.passed:
            return self._ratio
        else:
            return 0


class TestRunner(object):
    """Runs all sorts of tests in the jail. Doesn't actually carry out the
    grading process, but returns the test results.

    """
    SUBMIT_DIR = "submission"
    """The directory to unzip the student's submission into."""

    SUBMIT_FILE = "submit.tar.gz"
    """The name of the submit archive."""

    def __init__(self, config, jail, project_dir):
        self._config = config
        self._jail = jail
        self._project_dir = project_dir

    def prepare_jail(self):
        """Move all of the project files into place."""
        self._jail.run("cp -r {project_dir}/* {jail_dir}".format(
            project_dir=shellquote(self._project_dir),
            jail_dir=shellquote(self._jail.directory)
        ))

    def compile_solutions(self):
        """Compile the staff solution, buggy solutions, and judges."""
        def make(target):
            self._jail.run("make --no-print-directory {target}".format(
                target=target
            ))

        # Solution exe.
        with self._jail.cd(self._config.get("project-info", "solution-dir")):
            make(self._config.staff_solution_exe)

            if self._config.has_test_suite:
                make(self._config.test_suite_exe)
                make(self._config.flags_command)
                for i in self._config.bugs:
                    make(i)

        # Judges.
        with self._jail.cd(self._config.get("project-info", "judge-dir")):
            for i in self._config.judges:
                make(i)

    def unzip_submission(self):
        self._jail.run("mkdir {submit_dir}".format(
            submit_dir=shellquote(self.SUBMIT_DIR)
        ))
        self._jail.run("mv {submit_file} {submit_dir}".format(
            submit_file=shellquote(self.SUBMIT_FILE),
            submit_dir=shellquote(self.SUBMIT_DIR)
        ))
        with self._jail.cd(self.SUBMIT_DIR):
            self._jail.run("tar -xf {submit_archive}".format(
                submit_archive=shellquote(self.SUBMIT_FILE)
            ))

            # Copy over any grader files. Overwrite student files.
            grader_files = [
                shellquote(os.path.join(self._project_dir, i))
                for i
                in self._config.grader_files
            ]
            if grader_files:
                self._jail.run("cp -r {files} .".format(
                    files=" ".join(grader_files)
                ))

            # Make the student executable.
            self._jail.run("make --no-print-directory")

    def get_student_file(self, student_filename):
        """Return the path to one of the student's files, assuming that it's in
        the student submit directory.

        """
        return os.path.join(self.SUBMIT_DIR, student_filename)

    @contextlib.contextmanager
    def cd_to_submission_dir(self):
        """Change to the submission directory."""
        with self._jail.cd(self.SUBMIT_DIR):
            yield

    def judge(
        self,
        test_id,
        expected_file,
        student_file,
        input_file,
        print_output=True
    ):
        """Invoke the judge for a given test ID. Returns a JudgeResult.

        print_output: Whether or not to print the judge output to standard
            output. Useful for integration testing but not for the test suite.

        """
        judge = self._config.get_judge_for_test(test_id)
        judge_path = os.path.join(
            self._jail.directory,
            self._config.judge_dir,
            judge
        )

        with tempfile.NamedTemporaryFile() as f:
            command = \
                "{judge_path} {expected} {student} {input} >{output}".format(
                    judge_path=judge_path,
                    judge=shellquote(judge),
                    expected=shellquote(expected_file),
                    student=shellquote(student_file),
                    input=shellquote(input_file),
                    output=shellquote(f.name)
                )
            judge_status = self._jail.run(
                command,
                accept_failure=True
            )

            if judge_status not in [0, 2]:
                die("Judge crashed when running command {command}".format(
                    command=command
                ))

            # Determine "real" output. If they passed, check to see if they
            # printed anything. If they did, assume the first line is a ratio
            # of points to award and remove it from the output. (If they
            # failed, leave the output as is.)
            real_output = f.read()
            did_print_output = (len(real_output.strip()) > 0)
            ratio = None
            if judge_status == 0 and did_print_output:
                lines = real_output.split("\n")
                real_output = "\n".join(lines[1:])
                try:
                    ratio = float(lines[0])
                    logging.info("Got ratio {ratio} for judge.".format(
                        ratio=ratio
                    ))
                except ValueError:
                    die("""
Configuration error: Judge returned success and printed output, but the first
line was not a ratio. Fix your judge executable! (See project.ini's comments on
`judge-dir`.)
""".strip())
                if ratio < 0 or ratio > 1:
                    die("Ratio {ratio} was not between 0 and 1.".format(
                        ratio=ratio
                    ))

        # If the user requested that output be printed, print the "real"
        # output generated above.
        if print_output and did_print_output:
            # The output might end with a newline, but `print` also prints a
            # newline.
            print(real_output.strip())

        return JudgeResult(judge_status, ratio)

    def determine_multiplier(self, scale, ratio):
        """Returns the multiplier to apply to a score.

        scale: The string scale given in `project.ini`, like
            "0.00-1.00:1.00  1.00-2.00:0.95".
        ratio: The ratio of student time/memory to budgeted time/memory.

        """
        for i in scale.split():
            interval, multiplier = i.split(":")
            begin, end = interval.split("-")

            begin = float(begin)
            end = float(end)
            multiplier = float(multiplier)

            if begin <= ratio < end:
                return multiplier
        return 0.0

    def _get_command_with_flags(
        self,
        executable,
        input_file,
        flags,
        output_file
    ):
        """Returns a list of elements in the command to run for `run_with_flags`.

        """
        command_parts = [shellquote(executable)]

        if self._config.tests_to_stdin:
            command_parts.append("<")
        command_parts.append(shellquote(input_file))

        # If we got the flags output from the flags command, it will have a
        # trailing newline. Regardless of how we got it, the flags shouldn't
        # have trailing whitespace.
        flags = flags.strip()
        command_parts.append(flags)

        command_parts.append(">")
        command_parts.append(shellquote(output_file))

        # Rather than write it to the terminal.
        command_parts.append('2>/dev/null')

        return command_parts

    def run_with_flags(
        self,
        *args,
        **kwargs
    ):
        """Run the given student or staff executable with the given flags and
        input file.

        """
        command = " ".join(self._get_command_with_flags(*args))
        return self._jail.run(command, **kwargs)

    def run_with_flags_timed(
        self,
        *args,
        **kwargs
    ):
        """Same as `run_with_flags`, but measures the time spent by the program
        using `/usr/bin/time`.

        """
        def get_seconds(f):
            """Get the number of seconds from bash's time output.

            There can be a great deal of variability from incorporating 'sys'
            time into the result when simulating; the solution here is just to
            use 'user' and hope that there's less variability on the
            autograder.

            """
            try:
                output = f.read().strip().split("\n")
                user_time = output[-2].split()[1]
                minutes, seconds = user_time.split("m")

                # Remove the trailing 's'.
                seconds = seconds[:-1]
                return float(seconds) + (60.0 * int(minutes))
            except ValueError:
                logging.info("Failed to read time.")
                return 999.0

        with tempfile.NamedTemporaryFile() as f:
            command_parts = self._get_command_with_flags(*args)

            # Make sure to use bash's built-in time, since that gives us three
            # decimal places of precision.
            command = "2>{filename} bash -c \"time {old_command}\"".format(
                filename=f.name,
                old_command=" ".join(command_parts)
            )

            status = self._jail.run(command, **kwargs)
            return status, get_seconds(f)


TestResult = collections.namedtuple("TestResult", [
    "passed",
    "percent",
    "runtime",
    "runtime_budget",
])
"""The results of a test run."""


class IntegrationTestGrader(object):
    """Grades the student solutions using the integration tests."""
    def __init__(self, config, test_runner):
        self._config = config
        self._test_runner = test_runner

    def _grade_test(self, test_id, test_info):
        """Grade a test. Returns a `TestResult`."""
        student_output_path = "__correct.out"
        correct_output_path = OutputGenerator.get_output_path(test_id)

        exe_path = os.path.join(
            ".",
            TestRunner.SUBMIT_DIR,
            self._config.submission_exe
        )

        input_filename, flags = test_info
        input_path = os.path.join(
            self._config.integration_tests_dir,
            input_filename
        )

        status, total_time = self._test_runner.run_with_flags_timed(
            exe_path,
            input_path,
            flags,
            student_output_path,
            accept_failure=True,
            limited=True
        )

        passed = False
        percent = 0.0
        runtime = 0.0
        runtime_budget = 1.0

        if self._config.is_invalid_test_case(test_id):
            passed = (status != 0)
            if passed:
                percent = 1.0
            else:
                logging.info("INV case returned zero when it shouldn't have.")
                percent = 0.0
        elif status == 0:
            judge_result = self._test_runner.judge(
                test_id,
                correct_output_path,
                student_output_path,
                input_path
            )
            passed = judge_result.passed
            logging.info("Judge returned {status}".format(
                status=judge_result.status
            ))

            runtime = total_time
            benchmark_data = OutputGenerator.get_benchmark_data(test_id)
            runtime_budget = benchmark_data["time"]

            ratio = judge_result.ratio
            percent = ratio * self._test_runner.determine_multiplier(
                self._config.runtime_scoring,
                float(runtime) / runtime_budget
            )

        return TestResult(
            passed=passed,
            percent=percent,
            runtime=runtime,
            runtime_budget=runtime_budget
        )

    def grade_integration_tests(self):
        """Grade integration tests. Yields a sequence of tuples of
        `(test_id, TestResult)`.

        """
        tests = self._config.integration_tests
        for test_id in sorted(tests.keys()):
            result = self._grade_test(test_id, tests[test_id])
            yield test_id, result

    def run_and_print(self):
        results = {}
        for test_id, result in self.grade_integration_tests():
            results[test_id] = result

            output = "Test {test_id} ".format(test_id=test_id)
            if result.passed:
                output += "passed "
            else:
                output += "failed "

            output += (
                "({percent:0.2f}%, "
                "runtime {runtime:0.3f}, "
                "budget {budget:0.3f})".format(
                    percent=result.percent * 100,
                    runtime=result.runtime,
                    budget=result.runtime_budget
                )
            )
            print(output)
        return results

    def grade(self, results):
        score = 0
        for i in results.values():
            if i.passed:
                score += i.percent
        total_cases = len(results)
        if not total_cases:
            die("No integration tests were found.")
        percentage = float(score) / total_cases
        return self._config.integration_points * percentage

    @staticmethod
    def generate_output(config, test_runner):
        """Generate output for integration tests."""
        generator = OutputGenerator(config, test_runner)
        for test_id, test_info in config.integration_tests.iteritems():
            generator.generate_output(test_id, test_info)


class TestSuiteGrader(object):
    """Grades the student test suite."""
    def __init__(self, config, jail, test_runner):
        self._config = config
        self._jail = jail
        self._test_runner = test_runner

    def _get_student_tests(self):
        """Return a dict of test_id => test_file_name for each student test.

        For example, if the student has test-1.txt and test-2.txt, returns
        {"1": "test-1.txt", "2": "test-2.txt"}.

        """
        ret = {}
        prefix = "test-"
        suffix = ".txt"
        with self._test_runner.cd_to_submission_dir():
            for i in glob.glob(prefix + "*" + suffix):
                test_id = i[len(prefix):][:-len(suffix)]
                ret[test_id] = i
        return ret

    def _get_test_flags(self, test_path):
        """Get the test flags for a given test case.

        Returns a string containing the command-line flags on success, or
        `None` if the test case did not have a valid name.

        Do not check for truthiness of the returned value, as it may be the
        empty string. Instead check for `flags is None`.

        """
        with tempfile.NamedTemporaryFile() as f:
            flags_command = "{flags_command} {test_path} >{output}".format(
                flags_command=shellquote(self._config.flags_command_path),
                test_path=shellquote(test_path),
                output=shellquote(f.name)
            )
            return_code = self._jail.run(flags_command, accept_failure=True)
            flags = f.read().strip()

        if return_code == 0:
            return flags
        elif return_code == 2:
            return None
        else:
            die("Flags command crashed (status {ret}): {flags_command}".format(
                flags_command=flags_command,
                ret=return_code
            ))

    def _grade_student_test(self, test_filename, test_flags):
        """Grade a single student test, yielding the bugs that it caught."""
        correct_output_path = "__correct.out"
        buggy_output_path = "__buggy.out"

        def get_staff_exe(filename):
            return os.path.join(
                self._jail.directory,
                self._config.staff_solution_dir,
                filename
            )

        caught_bugs = set()

        # Generate correct solution output.
        status = self._test_runner.run_with_flags(
            get_staff_exe(self._config.test_suite_exe),
            test_filename,
            test_flags,
            correct_output_path,
            accept_failure=True
        )
        if status == 2:
            logging.info("Illegal test case {test_filename}".format(
                test_filename=test_filename
            ))
            # Skip this test case.
            return caught_bugs
        elif status != 0:
            die("Test suite solution crashed ({ret}): "
                "{test_filename}".format(
                    test_filename=test_filename,
                    ret=status
                ))

        for i in self._config.bugs:
            # Generate buggy solution output. This might cause the program to
            # exit with error, so don't catch that.
            self._test_runner.run_with_flags(
                get_staff_exe(i),
                test_filename,
                test_flags,
                buggy_output_path
            )

            # Judge the two and determine if they differ.
            judge_result = self._test_runner.judge(
                test_filename,
                correct_output_path,
                buggy_output_path,
                test_filename,
                print_output=False
            )
            if not judge_result.passed:
                caught_bugs.add(i)

        return caught_bugs

    def grade_test_suite(self):
        """Grade the test suite. Returns the set of caught bugs"""
        bugs = set()

        if not self._config.has_test_suite:
            logging.info("Test suite not enabled.")
            return bugs

        student_tests = self._get_student_tests()
        if not student_tests:
            logging.info("No test suite provided by student.")
            return bugs

        for k, v in student_tests.iteritems():
            test_flags = self._get_test_flags(v)
            if test_flags is None:
                logging.info("Invalid test filename: {test_filename}".format(
                    test_filename=v
                ))
                continue

            submission_dir = os.path.join(
                self._jail.directory,
                self._test_runner.SUBMIT_DIR
            )
            with self._jail.cd(submission_dir):
                caught_bugs = self._grade_student_test(v, test_flags)
                logging.info("Student test {test} caught bugs: {bugs}".format(
                    test=k,
                    bugs=" ".join(sorted(list(caught_bugs)))
                ))

            bugs |= caught_bugs
        return bugs

    def run_and_print(self):
        caught_bugs = self.grade_test_suite()
        print("Caught bugs: {bugs}".format(
            bugs=" ".join(sorted(list(caught_bugs)))
        ))
        return caught_bugs

    def grade(self, caught_bugs):
        min_bugs = self._config.min_bugs_for_points
        full_bugs = self._config.bugs_for_full_points
        num_bugs = len(caught_bugs)

        percentage = float(num_bugs - min_bugs) / (full_bugs - min_bugs)
        percentage = max(percentage, 0)
        percentage = min(percentage, 1)

        return percentage * self._config.test_suite_points


class Config(object):
    def __init__(self, parser):
        self._parser = parser
        self.get = parser.get
        self.judge_regexes = self._compile_judge_regexes()

    def _compile_judge_regexes(self):
        """Compile the judge test-matching regexes."""
        judges = self._parser.get("project-info", "judge-exes").strip()
        if not judges:
            die("No judges provided.")

        judge_regexes = []
        for i in judges.split():
            i = i.split(":")
            exe = i.pop(0)
            regex = re.compile(":".join(i))
            judge_regexes.append((exe, regex))
        return judge_regexes

    @property
    def project_id(self):
        return self._parser.get("project-info", "project-id")

    @property
    def hints_file(self):
        # This new option might not exist in older project.ini files,
        # and we don't want the old file to crash with a new projkit.py
        if self._parser.has_option("project-info", "hints-file"):
            return self._parser.get("project-info", "hints-file")
        else:
            return "none"

    @property
    def identifier(self):
        return self._parser.get("project-info", "identifier")

    @property
    def project_description(self):
        return self._parser.get("project-info", "project-description")

    @property
    def closing_date(self):
        return self._parser.get("project-info", "closing-date")

    @property
    def daily_submissions(self):
        return self._parser.get("project-info", "daily-submissions")

    @property
    def submission_exe(self):
        """The expected submission executable filename."""
        return self._parser.get("project-info", "submission-exe")

    @property
    def staff_solution_dir(self):
        """The directory where the staff solution executable is available."""
        return self._parser.get("project-info", "solution-dir")

    @property
    def staff_solution_exe(self):
        """The staff solution executable name."""
        return self._parser.get("project-info", "staff-solution-exe")

    @property
    def judge_dir(self):
        """The directory where the judges are available."""
        return self._parser.get("project-info", "judge-dir")

    @property
    def judges(self):
        return [i for i, j in self.judge_regexes]

    def get_judge_for_test(self, test_id):
        """Get the judge corresponding to a given test."""
        matches = [
            exe
            for exe, regex
            in self.judge_regexes
            if regex.search(test_id)
        ]

        if len(matches) == 0:
            die("No judge found for test {test_id}".format(test_id=test_id))
        elif len(matches) > 1:
            die("Multiple judges found for test {test_id}: {matches}".format(
                test_id=test_id,
                matches=matches
            ))
        return matches[0]

    @property
    def total_points(self):
        return self._parser.getfloat("project-info", "total-points")

    @property
    def tests_to_stdin(self):
        """Whether or not tests are passed directly into standard input."""
        value = self._parser.getint("project-info", "tests-to-stdin")
        if value not in [0, 1]:
            die("Unknown tests-to-stdin value {value}".format(
                value=value
            ))
        return bool(value)
    
    @property
    def valid_cerr_output(self):
        # This new option might not exist in older project.ini files,
        # and we don't want the old file to crash with a new projkit.py
        if self._parser.has_option("project-info", "valid-cerr-output"):
            entire_config_line = self._parser.get("project-info", "valid-cerr-output")
            config_array = entire_config_line.split(",")
            for i in range(len(config_array)):
                config_array[i] = config_array[i].strip()
            return config_array
        else:
            return []

    @property
    def has_scoreboard(self):
        """Whether or not the project has a scoreboard, leaderboard, statistics, etc."""
        if self._parser.has_option("project-info", "has-scoreboard"):
            value = self._parser.getint("project-info", "has-scoreboard")
            if value not in [0, 1]:
                die("Unknown has-scoreboard value {value}".format(
                    value=value
                ))
            return value
        else:
            # TODO: update this value to 1 if we decide to default to scoreboard on
            return 0
    
    @property
    def jail_time_limit(self):
        """The time limit for the jail, in seconds."""
        return self._parser.getint("jail-info", "time-limit")

    @property
    def jail_disk_limit(self):
        """The disk limit for the jail, in bytes."""
        return self._parser.getint("jail-info", "disk-limit")

    @property
    def jail_memory_limit(self):
        """The memory limit for the jail, in megabytes."""
        return self._parser.getint("jail-info", "memory-limit")

    @property
    def student_files(self):
        """Returns a list of student files to copy to the submission directory.

        """
        return self._parser.get("jail-info", "student-files").split()

    @property
    def grader_files(self):
        """Returns a list of grader files to copy to the submission directory.

        """
        return self._parser.get("jail-info", "grader-files").split()

    @property
    def prohibited_libraries(self):
        """Returns the list of prohibited libraries for this project."""
        return self._parser.get("jail-info", "prohibited-libraries").split()

    @property
    def integration_tests_dir(self):
        """The directory in which the integration tests are located."""
        return self._parser.get("integration-info", "test-dir")

    @property
    def invalid_test_prefix(self):
        return self._parser.get("integration-info", "invalid-test-prefix")

    def is_invalid_test_case(self, test_id):
        return test_id.startswith(self.invalid_test_prefix)

    @property
    def integration_points(self):
        return self._parser.getint("integration-info", "points")

    @property
    def memory_leak_points(self):
        return self._parser.getint("integration-info", "memory-leak-points")

    @property
    def memory_leak_percent(self):
        return self._parser.getint("integration-info", "memory-leak-percent")

    @property
    def leak_check_cases(self):
        cases = self._parser.get("integration-info", "leak-check-cases")
        return cases.split()

    @property
    def runtime_scoring(self):
        return self._parser.get("integration-info", "runtime-scoring")

    @property
    def memory_scoring(self):
        return self._parser.get("integration-info", "memory-scoring")

    @property
    def integration_tests(self):
        """A dict of `{test_id: (input_file, flags)}`, where `test_id` and
        `input_file` are strings and `flags` is a list of strings.

        """
        ret = {}
        for test_id, data in self._parser.items("integration-tests"):
            if test_id in ret:
                die("Duplicate integration test '{test_id}'".format(
                    test_id=test_id
                ))

            data = data.split()
            input_file = data.pop(0)
            flags = " ".join(data)
            ret[test_id] = (input_file, flags)
        return ret

    @property
    def has_test_suite(self):
        return self._parser.has_section("suite-info")

    @property
    def test_suite_points(self):
        return self._parser.getint("suite-info", "points")

    @property
    def min_bugs_for_points(self):
        return self._parser.getint("suite-info", "min-bugs-for-points")

    @property
    def bugs_for_full_points(self):
        return self._parser.getint("suite-info", "bugs-for-full-points")

    @property
    def bugs_for_extra_submit(self):
        # This new option might not exist in older project.ini files,
        # and we don't want the old file to crash with a new projkit.py
        if self._parser.has_option("suite-info", "bugs-for-extra-submit"):
            return self._parser.getint("suite-info", "bugs-for-extra-submit")
        else:
            return 9999

    @property
    def max_student_test_files(self):
        return self._parser.getint("suite-info", "max-student-test-files")

    @property
    def flags_command(self):
        """The command to run to get the command-line flags from a given student
        test file.

        """
        return self._parser.get("suite-info", "flags-command")

    @property
    def flags_command_path(self):
        """Return the path to the flags command executable."""
        return os.path.join(self.staff_solution_dir, self.flags_command)

    @property
    def bugs(self):
        solutions_str = self._parser.get("suite-info", "buggy-solutions")
        return solutions_str.strip().split()

    @property
    def test_suite_exe(self):
        return self._parser.get("suite-info", "test-suite-exe")


def get_config(arguments):
    parser = cp.RawConfigParser()
    parser.optionxform = str
    parser.readfp(open(arguments["config_file"]))
    return Config(parser)


def compile_solutions(arguments):
    config = get_config(arguments)
    project_dir = os.getcwd()

    # This isn't actually used for jailing; it's just for convenience to run
    # commands in the project directory.
    project_jail = Jail(project_dir, None, None, None)
    project_test_runner = TestRunner(config, project_jail, project_dir)
    project_test_runner.compile_solutions()

    return config, project_dir, project_test_runner


def command_test(arguments):
    config, project_dir, project_test_runner = compile_solutions(arguments)
    submit_file_path = os.path.abspath(arguments["submit_file"])

    IntegrationTestGrader.generate_output(config, project_test_runner)

    with make_jail(
        time_limit=config.jail_time_limit,
        disk_limit=config.jail_disk_limit,
        memory_limit=config.jail_memory_limit
    ) as jail:
        jail.run("cp {submit} {submit_archive}".format(
            submit=shellquote(submit_file_path),
            submit_archive=shellquote(TestRunner.SUBMIT_FILE)
        ))

        test_runner = TestRunner(config, jail, project_dir)
        test_runner.prepare_jail()
        test_runner.unzip_submission()

        score = 0.0

        integration_grader = IntegrationTestGrader(config, test_runner)
        results = integration_grader.run_and_print()
        integration_score = integration_grader.grade(results)
        score += integration_score
        print("Integration tests score: {score:0.2f}".format(
            score=integration_score
        ))
        print("---")

        if config.has_test_suite:
            test_suite_grader = TestSuiteGrader(config, jail, test_runner)
            caught_bugs = test_suite_grader.run_and_print()
            test_suite_score = test_suite_grader.grade(caught_bugs)
            score += test_suite_score
            print("Test suite score: {score:0.2f}".format(
                score=test_suite_score
            ))
            print("---")

        print("Score: {score:0.2f}/{total_points:0.2f}".format(
            score=score,
            total_points=config.total_points
        ))

    return 0


def command_compile_genoutput(arguments):
    config = get_config(arguments)
    compiler = ScriptCompiler(config)
    print(compiler.get_genoutput())
    return 0


def command_compile_grade(arguments):
    config = get_config(arguments) 
    compiler = ScriptCompiler(config)
    print (compiler.get_grade())
    return 0


def command_compile_register(arguments):
    config = get_config(arguments)
    compiler = ScriptCompiler(config)
    print (compiler.get_register())
    return 0


def command_compile_solutions(arguments):
    compile_solutions(arguments)
    return 0


def main(arguments):
    log_level = os.environ.get("LOGLEVEL", "WARNING")
    logging.basicConfig(level=getattr(logging, log_level))

    try:
        command, arguments = parse_arguments(arguments)
    except ValueError as e:
        print("Error: {message}".format(message=str(e)))
        print_usage()

    return command(arguments)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

