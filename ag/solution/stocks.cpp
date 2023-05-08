// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#include "stocks.h"
#include <iostream>
#include <string>
#include <cassert>
#include <algorithm>
#include <sstream>
#include <vector>
#include <cmath>
#include <numeric>
using namespace std;


uint32_t ReadOrder::currentId = 0;
int Orderbook::equityCounter = 0;


ostream &operator <<(ostream &os, const ReadOrder& o) {
    os << o.timestamp << (o.isBuyOrder ? "BUY" : "SELL") << " T" << " " << o.trader << " S" << o.equity;
    os << " $" << o.price << " #" << o.quantity;
    return os;
} // operator<<()


void updateTravelers(vector<Orderbook> &orderBooks, const ReadOrder &o) {
    orderBooks[o.equity].timeTraveler.receiveOrder(o);
} // updateTravelers()


void printTraderInfo(const vector<Trader> &traders) {
    long long totalTrades = 0;
    for (size_t i = 0; i < traders.size(); ++i) {
        cout << "Trader " << i << " bought " << traders[i].numBought << " and sold "
             << traders[i].numSold << " for a net transfer of $" << traders[i].netTraded << '\n';
        totalTrades += traders[i].numSold;
    } // for

#ifdef BUG14 // Fail if no trades completed
    if (totalTrades == 0)
        exit(1);
#else
    (void)totalTrades;
#endif
} // printTraderInfo()


void processTransactions(Orderbook &book, Command &commandLineFlags,
                         vector<Trader> &traderInfo, uint32_t &ordersProcessed) {
    while (book.tradesLeft()) {
        const StoredOrder &buyOrder  = book.buyOrders.top();
        const StoredOrder &sellOrder = book.sellOrders.top();
        int minQuantity = min(buyOrder.quantity, sellOrder.quantity);
        int transactionPrice = (buyOrder.id < sellOrder.id) ? buyOrder.price : sellOrder.price;

#ifdef BUG10 // Fail if buyer == seller
        if (buyOrder.trader == sellOrder.trader)
            exit(1);
#endif

#ifdef BUG11 // Fail if buyer price == seller price
        if (buyOrder.price == sellOrder.price)
            exit(1);
#endif

#ifdef BUG12 // Fails if buyer quantity == seller quantity
        if (buyOrder.quantity == sellOrder.quantity)
            exit(1);
#endif

        if (commandLineFlags.verbose) {
            cout << "Trader " << buyOrder.trader << " purchased " << minQuantity << " shares of Stock ";
            cout << book.equity << " from Trader " << sellOrder.trader << " for $" << transactionPrice;
            cout << "/share" << "\n";
        } // if

        if (commandLineFlags.traderInfo) {
            traderInfo[buyOrder.trader].updateNet(transactionPrice, minQuantity, true);
            traderInfo[sellOrder.trader].updateNet(transactionPrice, minQuantity, false);
        } // if

        buyOrder.quantity -= minQuantity;
        sellOrder.quantity -= minQuantity;

        if (commandLineFlags.median)
            book.rm.push(transactionPrice);

#ifndef BUG4 // always remove buy order after one trade
        if (buyOrder.quantity == 0)
#endif
        {
            book.buyOrders.pop();
        } // if
#ifndef BUG5 // always remove sell order after one trade
        if (sellOrder.quantity == 0)
#endif
        {
            book.sellOrders.pop();
        } // if

        ordersProcessed++;
    } // while
} // processTransactions()


void runMarket(Command &commandLineFlags, uint32_t numEquities,
               uint32_t numTraders, istream &is) {
    vector<Orderbook> orderBooks(numEquities);
    vector<Trader> traderInfo;
    int currentTime = 0;
    uint32_t ordersProcessed = 0;

    if (commandLineFlags.traderInfo)
        traderInfo.resize(numTraders);

    cout << "Processing orders..." << "\n";
    ReadOrder nextOrder;
    while (nextOrder.nextReadOrder(is)) {
        // INV: Timestamp must be non-negative integer.
        if (nextOrder.timestamp < 0) {
            cerr << "Negative timestamp for order: " << nextOrder.timestamp << endl;
            exit(1);
        } // if

        // INV: Equity must be in range. No need to check for >= 0, equity is unsigned.
        if (nextOrder.equity >= numEquities) {
            cerr << "Stock not in range: " << nextOrder.equity << endl;
            exit(1);
        } // if

        // INV: Trader ID must be in range. No need to check for >= 0, trader is unsigned.
        if (nextOrder.trader >= numTraders) {
            cerr << "Trader not in range: " << nextOrder.trader << endl;
            exit(1);
        } // if

        // INV: Price must be positive.
        if (nextOrder.price <= 0) {
            cerr << "Price not positive: " << nextOrder.price << endl;
            exit(1);
        } // if

        // INV: Quantity must be positive.
        if (nextOrder.quantity <= 0) {
            cerr << "Quantity not positive: " << nextOrder.quantity << endl;
            exit(1);
        } // if

        // INV: Timestamps must be nondecreasing.
        if (nextOrder.timestamp < currentTime) {
            cerr << "Timestamp didn't strictly increase: " << currentTime << endl;
            exit(1);
        } // if

#ifdef BUG13 // Fail if new order timestamp == last timestamp
        if (currentTime == nextOrder.timestamp)
            exit(1);
#endif

#ifdef BUG15 // Change equity to 0 after reading
        nextOrder.equity = 0;
#endif

        //Print median match price of all equities if new timestamp and median flag set
        if (currentTime != nextOrder.timestamp) {
            if (commandLineFlags.median) {
                for (uint32_t i = 0; i < numEquities; ++i) {
                    //Only print median if there have been trades executed for a given equity
                    if (orderBooks[i].rm.hasMedian() != 0) {
                        cout << "Median match price of Stock " << i << " at time ";
                        cout << currentTime << " is $" << orderBooks[i].rm.median() << "\n";
                    } // if
                } // for
            } // if
            //Update current timestamp
            currentTime = nextOrder.timestamp;
        } // if

        Orderbook &currentOrderBook = orderBooks[nextOrder.equity];

        if (commandLineFlags.travelers)
            updateTravelers(orderBooks, nextOrder);

        if (nextOrder.isBuyOrder)
            currentOrderBook.buyOrders.emplace(nextOrder);
        else
            currentOrderBook.sellOrders.emplace(nextOrder);

        processTransactions(currentOrderBook, commandLineFlags, traderInfo, ordersProcessed);
    } // while

    if (commandLineFlags.median) {
        for (uint32_t i = 0; i < numEquities; ++i) {
            if (orderBooks[i].rm.hasMedian() != 0) {
                cout << "Median match price of Stock " << i << " at time ";
                cout << currentTime << " is $" << orderBooks[i].rm.median() << "\n";
            } // if
        }
    } // if

    cout << "---End of Day---" << "\n";
    cout << "Trades Completed: " << ordersProcessed << "\n";

    if (commandLineFlags.traderInfo) {
        cout << "---Trader Info---" << "\n";
        printTraderInfo(traderInfo);
    } // if

    if (commandLineFlags.travelers) {
        cout << "---Time Travelers---" << "\n";
        for (uint32_t i = 0; i < numEquities; ++i) {
            orderBooks[i].timeTraveler.printTraveler(i);
        } // for
    } // if
} // runMarket()

