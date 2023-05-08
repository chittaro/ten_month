// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#ifndef STOCKS_H
#define STOCKS_H

#include <queue>
#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>
#include <random>
#include <vector>
#include <sstream>
#include "RunningMedian.h"
#include "orders.h"
#include "TimeTraveler.h"
using namespace std;


struct Command {
    bool verbose;
    bool median;
    bool traderInfo;
    bool travelers;
    bool convertPRtoTL;
    Command() : verbose(false), median(false), traderInfo(false), travelers(false), convertPRtoTL(false) {}
}; // Command


struct BuyComparator {
    bool operator() (const StoredOrder &left, const StoredOrder &right) const {
        if (left.price == right.price)
#ifdef BUG1 // buyers compare wrong on equal price
            return right.id > left.id;
#else
            return right.id < left.id;
#endif
        return right.price > left.price;
    } // operator()
}; // BuyComparator


struct SellComparator {
    bool operator() (const StoredOrder &left, const StoredOrder &right) const {
        if (left.price == right.price)
#ifdef BUG2 // sellers compare wrong on equal price
            return right.id > left.id;
#else
            return right.id < left.id;
#endif
        return right.price < left.price;
    } // operator()
}; // SellComparator


struct Orderbook {
    priority_queue<StoredOrder, vector<StoredOrder>, BuyComparator>  buyOrders;
    priority_queue<StoredOrder, vector<StoredOrder>, SellComparator> sellOrders;
    TimeTraveler timeTraveler;
    RunningMedian<int> rm;
    int equity; // Needs to know it for trader info
    static int equityCounter;

    Orderbook() : equity{ equityCounter++ } {}

    bool tradesLeft() const {
        return ((!buyOrders.empty()) && (!sellOrders.empty()))
            && (buyOrders.top().price) >= (sellOrders.top().price);
    } // tradesLeft()
}; // OrderBook


struct Trader {
    long long numBought;
    long long numSold;
    long long netTraded;
    bool exists;
    Trader() : numBought(0), numSold(0), netTraded(0), exists(false) {}
    void updateNet(int amount, int number, bool isBuy) {
        if (isBuy) {
            long long total = static_cast<long long>(amount) * number;
            numBought += number;
            netTraded -= total;
        } // if
        else {
            long long total = static_cast<long long>(amount) * number;
            numSold += number;
            netTraded += total;
        } // else
    } // updateNet()
}; // Trader


void runMarket(Command &line, unsigned int numEquities, unsigned int numTraders, istream &is);


#endif // STOCKS_H
