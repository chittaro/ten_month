PATH := /usr/um/gcc-6.2.0/bin:$(PATH)
LD_LIBRARY_PATH := /usr/um/gcc-6.2.0/lib64
LD_RUN_PATH := /usr/um/gcc-6.2.0/lib64


CXX = g++
CXX_FLAGS = -Wall -Werror -Wextra -pedantic -Wconversion -std=c++11

HEADERS = common.h
SOURCES = edit_distance_judge.cpp
JUDGE = edit_distance_judge

.PHONY: all
all: $(JUDGE)

.PHONY: clean
clean:
	rm -f $(JUDGE)

$(JUDGE): $(HEADERS) $(SOURCES)
	$(CXX) $(CXX_FLAGS) $(SOURCES) -o $(JUDGE)
