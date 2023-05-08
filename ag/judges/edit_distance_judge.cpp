// Checks each line individually for correctness.  It will trim whitespace from
// each line of the expected and actual files before comparison.
//
// Returns 0 on success and 2 if the files are different.  If output incorrect
// will also output a hint to the student to give an idea of what went wrong.
// If the lines are "close enough", they can see the entire line (ours and theirs).
//
// Usage
// ./edit_distance_judge expected_output_file student_output_file

#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <stdlib.h>
#include "common.h"
using namespace std;


// The radius around the error to expose the student's output.
// The exposed output will never wrap lines.
#define OUTPUT_RADIUS 2

// Different constant costs for insertions, deletions, and replacements
// Insertion is expected + char -> student
// Deletion is expected - char -> student
#define INS_COST 5
#define DEL_COST 3
#define REP_COST 1


// Replacement cost is cheaper for same types
unsigned repCost(char c1, char c2) {
    int isc1dig = isdigit(c1);
    int isc2dig = isdigit(c2);
    if (isc1dig && isc2dig)
        return 1;

    int isc1alp = isalpha(c1);
    int isc2alp = isalpha(c2);
    if (isc1alp && isc2alp)
        return 1;
    if ((isc1dig && isc2alp) || (isc1alp && isc2dig))
        return 3;

    int isc1pnc = ispunct(c1);
    int isc2pnc = ispunct(c2);
    if (isc1pnc && isc2pnc)
        return 1;
    if ((isc1alp && isc2pnc) || (isc1pnc && isc2alp))
        return 2;
    return 3;
} // repCost()


// Edit distance which assigns different weights to different operations.
// We want to make adding characters expensive, so that students can't just
// add parts of the input to the output to determine the input.
unsigned weightedEditDistance(const string &str1, const string &str2) {
    size_t m = str1.length(), n = str2.length();
    vector<vector<unsigned>> dp(m + 1, vector<unsigned>(n + 1, 0));

    for (unsigned i = 0; i <= m; ++i) {
        for (unsigned j = 0; j <= n; ++j) {
            if (i == 0)
                // First string is empty, insert all characters of second string
                dp[i][j] = INS_COST * j;

            else if (j == 0)
                // Second string is empty, remove all characters of first string
                dp[i][j] = DEL_COST * i;

            else if (str1[i - 1] == str2[j - 1])
                // Current characters are same, use old cost for shorter string
                dp[i][j] = dp[i - 1][j - 1];

            // Last char diff, min of possibilities
            else
                dp[i][j] = min(INS_COST + dp[i][j - 1],      // Insert
                               DEL_COST + dp[i - 1][j],      // Remove
                               repCost(str1[i - 1], str2[j - 1]) + dp[i - 1][j - 1]); // Replace
        } // for j
    } // for i

    return dp[m][n];
} // weightedEditDistance()


// Longest common sequence, non-consecutive.  This could also be used
// to determine if the input and output strings are "close enough".
unsigned lcs(const string &str1, const string &str2) {
    size_t m = str1.length(), n = str2.length();
    vector<vector<unsigned>> dp(m + 1, vector<unsigned>(n + 1, 0));

    for (unsigned i = 0; i <= m; ++i) {
        for (unsigned j = 0; j <= n; ++j) {
            if (i == 0 || j == 0)
                dp[i][j] = 0;
            else if (str1[i - 1] == str2[j - 1])
                dp[i][j] = dp[i - 1][j - 1] + 1;
            else
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]);
        } // for j
    } // for i

    return dp[m][n];
} // lcs()


#define BASE_LIMIT 3        // Regardless of line length, edit distance can be at least this
#define DIVISOR 7           // One additional edit distance is added every DIVISOR characters
#define MAX_LINE_LENGTH 125 // Lines longer than this must use the old method


void compare_lines(const string &exp, const string &act, unsigned line) {
    string lnexp = trim(exp);
    string lnact = trim(act);
    if (lnexp != lnact) {
        size_t diff;
        for (diff = 0; diff < lnexp.size() && diff < lnact.size(); diff++)
            if (lnexp[diff] != lnact[diff])
                break;

        unsigned dist = weightedEditDistance(lnexp, lnact);
        size_t limit = BASE_LIMIT + lnexp.length() / DIVISOR;
        //unsigned similar = lcs(lnexp, lnact);
        //double percent = 1.0 * similar / lnexp.length();

        cout << "Line: " << line << endl;

        // If the edit distance is too large, or the line is too long, show old output
        if (dist > limit || lnexp.length() > MAX_LINE_LENGTH) {
            size_t left = (diff <= OUTPUT_RADIUS ? 0 : diff - OUTPUT_RADIUS);
            size_t right = left + 2 * OUTPUT_RADIUS;

            cout << "Correct output: " << formatOutput(lnexp, left, right) << endl;
            cout << "Student output: " << formatOutput(lnact, left, right) << endl;
        } // if
        else {
            // Edit distance within limits, show them the full lines
            cout << "Correct output: " << lnexp << endl;
            cout << "Student output: " << lnact << endl;
        } // else

        exit(EXIT_STUDENT_FAILED);
    } // if
} // compare_lines()


int main(int argc, char * argv[]) {
    if (argc < 3) {
        cout << "Usage: edit_distance_judge expected_file actual_file" << endl;
        return EXIT_STUDENT_FAILED;
    } // if

    ifstream fexp(argv[1]);
    ifstream fact(argv[2]);

    if (!fexp.good()) {
        cout << "Error: Could not find expected output" << endl;
        return EXIT_STUDENT_FAILED;
    } // if

    if (!fact.good()) {
        cout << "Error: Could not find actual output" << endl;
        return EXIT_STUDENT_FAILED;
    } // if

    unsigned line = 1;
    while (!fexp.eof() && !fact.eof()) {
        compare_lines(getline(fexp), getline(fact), line++);
    } // while

    if (fact.eof() && fexp.eof()) {
        return EXIT_STUDENT_PASSED;
    } // if

    if (fexp.eof()) {
        if (getline(fact).empty() && fact.eof()) return EXIT_STUDENT_PASSED;
        cout << "Your file had too many lines." << endl;
    } // if
    else {
        if (getline(fexp).empty() && fexp.eof()) {
            cout << "To avoid this message, add a newline character at the end-of-file (it's good style)." << endl;
            return EXIT_STUDENT_PASSED;
        } // if
        cout << "Your file had too few lines." << endl;
    } // else

    return EXIT_STUDENT_FAILED;
} // main()
