// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#pragma once

#include <queue>
#include <functional>


// Needs a numeric type (such as int) for which less<T> and greater<T> exist
template <typename T>
class RunningMedian {
private:
    std::priority_queue<T, std::vector<T>, std::less<T>> low;
    std::priority_queue<T, std::vector<T>, std::greater<T>> high;

public:
    void push(T difficulty) {
        if (high.empty() || difficulty >= high.top())
            high.push(difficulty);
        else
            low.push(difficulty);

        if (high.size() - low.size() == 2) {
            low.push(high.top());
            high.pop();
        } // if
        else if (low.size() - high.size() == 2) {
            high.push(low.top());
            low.pop();
        } // else if
    } // push()

    bool hasMedian() {
        return ((high.size() + low.size()) > 0);
    } // hasMedian()

    T median() {
        if (high.size() == low.size())
#ifdef BUG3 // Median doesn't average when even number
            return high.top();
#else
            return (high.top() + low.top()) / 2;
#endif

        else if (high.size() > low.size())
            return high.top();
        else
            return low.top();
    } // median()
};
