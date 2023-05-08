// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#include <iostream>
#include <getopt.h>
#include <map>
#include "stocks.h"
#include <random>
#include <set>
#include <vector>
#include "P2random.h"
using namespace std;


void convertPRtoTL(stringstream &ss, ostream &os, const string &comment, unsigned numTraders, unsigned numEquities);
void printHelp();


int main(int argc, char * argv[]) {
    std::ios_base::sync_with_stdio(false);
    Command commandLineFlags;
    stringstream ss;
    string type;
    string comment, garbage;
    unsigned int numEquities;
    unsigned int numTraders;
    unsigned int randomSeed;
    unsigned int numOrders;
    unsigned int arrivalRate;

    struct option longOpts[] = {
        {"help",           no_argument, nullptr, 'h'},
        {"verbose",        no_argument, nullptr, 'v'},
        {"median",         no_argument, nullptr, 'm'},
        {"trader_info",    no_argument, nullptr, 'i'},
        {"time_travelers", no_argument, nullptr, 't'},
        {"pr_to_tl",       no_argument, nullptr, 'p'},
        {nullptr,          0,           nullptr, '\0' }
    };

    opterr = 1;
    int opt = 0, index = 0;
    while ((opt = getopt_long(argc, argv, "hvmitp", longOpts, &index)) != -1) {
        switch (opt) {
        case 'h':
            printHelp();
            return 0;
        case 'v':
            commandLineFlags.verbose = true;
            break;
        case 'm':
            commandLineFlags.median = true;
            break;
        case 'i':
            commandLineFlags.traderInfo = true;
            break;
        case 't':
            commandLineFlags.travelers = true;
            break;
        case 'p':
            commandLineFlags.convertPRtoTL = true;
            break;
        case '?':
        default:
            printHelp();
            exit(1);
        } // switch
    } // while

    getline(cin, comment);
    cin >> garbage >> type;
    cin >> garbage >> numTraders;
    cin >> garbage >> numEquities;

    if (!cin) {
        cerr << "Your input file is invalid: missing space, text where there should be a number, etc." << endl;
        cerr << "Encountered while trying to read the header (first four lines)." << endl;
        exit(1);
    } // if

    if (type == "TL")
        runMarket(commandLineFlags, numEquities, numTraders, cin);
    else if (type == "PR") {
#ifdef CORRECT // Must be TL mode
        cerr << "ERROR: Expected TL mode." << endl;
        exit(1);
#endif
        cin >> garbage >> randomSeed;
        cin >> garbage >> numOrders;
        cin >> garbage >> arrivalRate;

        if (!cin) {
            cerr << "Your input file is invalid: missing space, text where there should be a number, etc." << endl;
            cerr << "Encountered while trying to read the PR lines." << endl;
            exit(1);
        } // if

        P2random::PR_init(ss, randomSeed, numTraders, numEquities, numOrders, arrivalRate);
        if (commandLineFlags.convertPRtoTL)
            convertPRtoTL(ss, cout, comment, numTraders, numEquities);
        else
            runMarket(commandLineFlags, numEquities, numTraders, ss);
    } // else if
    else {
        cerr << "ERROR: Mode must be PR or TL." << endl;
        exit(1);
    } // else

    return 0;
} // main()


void convertPRtoTL(stringstream &ss, ostream &os, const string &comment, unsigned numTraders, unsigned numEquities) {
    os << comment << '\n';
    os << "MODE: TL\n";
    os << "NUM_TRADERS: " << numTraders << '\n';
    os << "NUM_STOCKS: " << numEquities << '\n';

    os << ss.str();
} // convertPRtoTL()


static const char helpText[] = "NAME\n\
\tmarket - an electronic stock exchange market\n\n\
SYNOPSIS\n\
\tmarket [OPTION]\n\n\
DESCRIPTION\n\
\tMarket is an electronic stock exchange market simulator. The market offers\n\
\ta variety of equities. Any market trader can place a buy or sell order on\n\
\t stock to request that a transaction be executed when matching sellers\n\
\tor buyers become available. The simulator takes in buy and sell orders for\n\
\ta variety of equities as they arrive and matches buyers with sellers to\n\
\texecute trades as quickly as possible. In addition, it has the ability to\n\
\tcreate an insider trader, allowing for instantaneous trades and for the\n\
\tstock exchange to make even more money on the side.\n\n\
\t-p, --pr_to_tl\n\
\t\tAn optional flag that converts a PR mode file into a TL mode file.\n\
\t\tThis is only used for development, and overrides all other flags.\n\n\
\t-i, --trader__info\n\
\t\tAn optional flag that indicates the program should print information about\n\
\t\teach trader at the end of the day.\n\n\
\t-v, --verbose\n\
\t\tAn optional flag that indicates the program should print additional\n\
\t\toutput information while trades are being executed.\n\n\
\t-m, --median\n\
\t\tAn optional flag that indicates the program should print the current\n\
\t\tmedian match price for each stock.\n\n\
\t-t, --time_travelers\n\
\t\tAn optional flag that requests that, at the end of the day the program\n\
\t\tdeterminet what was the best time to buy (once) and then subsequently sell\n\
\t\t(once) a particular stock during the day to maximize profit, ignoring\n\
\t\tquantity traded.\n\n\
\t-h, --help\n\
\t\tAn optional flag that prints this help message and then exits.\n";


void printHelp() {
    cout << helpText << flush;
} // printHelp()
