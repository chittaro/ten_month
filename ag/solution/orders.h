// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#pragma once

#include <fstream>
using namespace std;


struct EndOfOrders {};


// What is read in, given to Time Traveler, etc.
struct ReadOrder {
    int timestamp;
    int price;
    int quantity;
    unsigned int id;
    unsigned int equity;
    unsigned int trader;
    bool isBuyOrder;
    static unsigned int currentId;

    //Constructor used for PR input mode
    bool nextReadOrder(istream &is) {
        string buyOrSell;
        char ch;

        if (!(is >> timestamp)) {
            return false;
        } // if

        id = currentId++;

#ifdef CORRECT // Must be <= 30 orders
        if (currentId > 30) {
            cerr << "ERROR: Too many orders placed (must be <= 30)." << endl;
            exit(1);
        } // if
#endif

#ifdef BUG9 // Fails with timestamp >= 1000
        if (timestamp >= 1000)
            exit(1);
#endif

        if (!(is >> buyOrSell >> ch >> trader >> ch >> equity >> ch >> price >> ch >> quantity)) {
            cerr << "Your input file is invalid: missing space, text where there should be a number, etc." << endl;
            cerr << "Error encountered while reading order " << currentId - 1 << endl;
            exit(1);
        } // if

        isBuyOrder = (buyOrSell == "BUY") ? 1 : 0;
        return true;
    } // nextReadOrder()
}; // ReadOrder


// What is actually stored in the PQ
struct StoredOrder {
    int price;
    mutable int quantity;
    unsigned int id;
    unsigned int trader;

    explicit StoredOrder(const ReadOrder &read) : price{ read.price }, quantity{ read.quantity }, id{ read.id }, trader{ read.trader } {}
};
