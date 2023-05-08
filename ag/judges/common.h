#include <string>
#include <algorithm>
using namespace std;


const int EXIT_STUDENT_PASSED = 0;
const int EXIT_STUDENT_FAILED = 2;


template <typename T>
T min(T x, T y, T z) {
    return min(min(x, y), z);
} // min()


// Outdated, use std::to_string() instead.
//template<class A, class B>
//A convert(const B & x) {
//    stringstream s;
//    s << x;
//    A ret;
//    s >> ret;
//    return ret;
//} // convert()


string getline(ifstream & f) {
    string ret;
    int ch = f.get();
    while (ch != -1 && ch != '\n' && ch != '\r') {
        ret += char(ch);
        ch = f.get();
    } // while
    if (ch == '\r') {
        ch = f.get();
        if (ch != -1 && ch != '\n')
            f.unget();
    } // if
    return ret;
} // getline()


string formatOutput(const string & s, size_t left, size_t right) {
    right = min(s.size(), max(static_cast<size_t>(0), right));
    left = min(max(static_cast<size_t>(0), left), right);
    string ret;
    if (left)
        ret += "...";
    ret += '\"';
    ret += s.substr(left, right - left);
    ret += '\"';
    if (right < s.size())
        ret += "...";
    if (left)
        ret += " truncated at position " + to_string(left);
    return ret;
} // formatOutput()


string trim(const string & s) {
    size_t a = 0;
    size_t b = s.size();
    while (a < b && (s[a] == ' ' || s[a] == '\t' || !s[a]))
        a++;
    while (a < b && (s[b - 1] == ' ' || s[b - 1] == '\t' || !s[b - 1]))
        b--;
    return s.substr(a, b - a);
} // trim()