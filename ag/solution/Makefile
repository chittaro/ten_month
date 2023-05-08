# enables c++17 on CAEN
PATH := /usr/um/gcc-6.2.0/bin:$(PATH)
LD_LIBRARY_PATH := /usr/um/gcc-6.2.0/lib64
LD_RUN_PATH := /usr/um/gcc-6.2.0/lib64

# designate which compiler to use
CXX			= g++
# list of sources used in project
SOURCES 	= $(wildcard *.cpp)
# list of objects used in project
OBJECTS		= $(SOURCES:%.cpp=%.o)
# name of the executable produced by the top level
EXECUTABLE 	= market
# name of the tar ball created for submission
SUBMIT_FILE = submit.tar.gz
# names of all output files
OUTS = $(wildcard *.out)

#Default Flags
CXXFLAGS = -std=c++17 -Wall -Werror -Wextra -pedantic -Wconversion

# make release - will compile "all" with $(CXXFLAGS) and the -O3 flag
#				 also defines NDEBUG so that asserts will not check
release: CXXFLAGS += -O3 -DNDEBUG
release: all

test-diff:
	./market -v -m < test-1-PR.txt > PR.out
	./market -v -m < test-1-TL.txt > TL.out
	diff -q PR.out TL.out
	rm PR.out TL.out

PR_orders: debug
	./market < test-1-PR.txt > test-1-TL.txt

test: 
	./market -v -m -c -t < test-1-PR.txt
	
test1: 
	./market -v -m < test-10-i-GE.txt

# make debug - will compile "all" with $(CXXFLAGS) and the -g flag
#              also defines DEBUG so that "#ifdef DEBUG /*...*/ #endif" works
debug: CXXFLAGS += -g3 -DDEBUG
debug: clean all

# make profile - will compile "all" with $(CXXFLAGS) and the -pg flag
profile: CXXFLAGS += -pg
profile: clean all

# highest target; sews together all objects into executable
all: $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(EXECUTABLE)

# individual dependencies for objects
market.o: market.cpp stocks.h
stocks.o: stocks.cpp stocks.h orders.h RunningMedian.h TimeTraveler.h

# rule for creating objects
%.o:
	$(CXX) $(CXXFLAGS) -c $*.cpp

# make clean - remove .o files, executable, tarball
clean:
	rm -vf $(OBJECTS) $(EXECUTABLE) $(SUBMIT_FILE) $(OUTS) correct bug*

# make submit.tar.gz - cleans, runs dos2unix, creates tarball
MY_FILES=$(wildcard Makefile *.h *.cpp test*.txt)
submit.tar.gz: $(MY_FILES)
	dos2unix $(MY_FILES)
	tar -vvczf $(SUBMIT_FILE) $(MY_FILES)

# shortcut for make submit.tar.gz (make submit)
submit: submit.tar.gz

# Creating "correct" and buggy solutions
correct: market.cpp stocks.h stocks.cpp
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DCORRECT -o correct

bugs: market.cpp stocks.h stocks.cpp
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG1  -o bug1
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG2  -o bug2
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG3  -o bug3
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG4  -o bug4
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG5  -o bug5
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG6  -o bug6
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG7  -o bug7
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG8  -o bug8
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG9  -o bug9
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG10 -o bug10
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG11 -o bug11
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG12 -o bug12
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG13 -o bug13
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG14 -o bug14
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG15 -o bug15
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(SOURCES) -DBUG16 -o bug16

# these targets do not create any files
.PHONY: all release debug profile clean submit
# disable built-in rules
.SUFFIXES:

