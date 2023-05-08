// Project identifier: 0E04A31E0D60C01986ACB20081C9D8722A1899B6

#pragma once

#include "orders.h"
using namespace std;

class TimeTraveler {
    enum class TimeTravelerStatus {
        JustArrived,
        InitialPosition,
        MadeTransaction,
        PotentialImprovement
    };

    TimeTravelerStatus tts = TimeTravelerStatus::JustArrived;
    int bestBuyPrice, bestBuyTime;
    int bestSellPrice, bestSellTime;
    int newBuyPrice, newBuyTime;

public:
    TimeTraveler() : bestBuyPrice{ -1 }, bestBuyTime{ -1 },
        bestSellPrice{ -1 }, bestSellTime{ -1 },
        newBuyPrice{ -1 }, newBuyTime{ -1 } {}

    int getTimeToBuy()  const { return bestBuyTime;   }
    int getPriceToBuy() const { return bestBuyPrice;  }
    int getTimeToSell()   const { return bestSellTime;  }
    int getPriceToSell()  const { return bestSellPrice; }

    void receiveOrder(const ReadOrder &order) {
        switch (tts) {
        case TimeTravelerStatus::JustArrived:
            if (!order.isBuyOrder) {  // First seller
                bestBuyPrice = order.price;
                bestBuyTime = order.timestamp;
                tts = TimeTravelerStatus::InitialPosition;  // Advance
            }  // if
            break;
        case TimeTravelerStatus::InitialPosition:
            if (order.isBuyOrder) {  // Possible first buyer
#ifndef BUG8 // Time traveler will accept a loss
                if (order.price > bestBuyPrice)
#endif
                {
                    // First valid buyer
                    bestSellPrice = order.price;
                    bestSellTime = order.timestamp;
                    tts = TimeTravelerStatus::MadeTransaction;  // Advance
                }  // if
            }  // if
            else {  // Possible initial position improvement
                if (order.price < bestBuyPrice) {  // Improve initial position
                    bestBuyPrice = order.price;
                    bestBuyTime = order.timestamp;
                }  // if
            }  // else
            break;
        case TimeTravelerStatus::MadeTransaction:
            if (order.isBuyOrder) {  // Possible transaction improvement
                if (order.price > bestSellPrice) {  // Improve TT transaction
                    bestSellPrice = order.price;
                    bestSellTime = order.timestamp;
                }  // if
            }  // if
            else {  // Possible new TT transaction
                if (order.price < bestBuyPrice) {  // Potential initial position
                    newBuyPrice = order.price;
                    newBuyTime = order.timestamp;
                    tts = TimeTravelerStatus::PotentialImprovement;  // Advance
                }  // if
            }  // else
            break;
        case TimeTravelerStatus::PotentialImprovement:
            if (order.isBuyOrder) {  // Possible replacement of current TT transaction
                if (order.price - newBuyPrice > bestSellPrice - bestBuyPrice) {  // Better!
                    bestBuyPrice = newBuyPrice;
                    bestBuyTime = newBuyTime;
                    bestSellPrice = order.price;
                    bestSellTime = order.timestamp;
                    tts = TimeTravelerStatus::MadeTransaction;  // Retreat
                }  // if
            }  // if
            else {  // Possible potential initial position improvement
                if (order.price < newBuyPrice) {  // Improved potential initial
#ifdef BUG16 // Time traveler bug: remember potential sell as actual
                    bestBuyPrice = order.price;
                    bestBuyTime = order.timestamp;
                    tts = TimeTravelerStatus::MadeTransaction;  // Retreat
#else
                    newBuyPrice = order.price;
                    newBuyTime = order.timestamp;
#endif
                }  // if
            }  // else
            break;
        }  // switch
    }  // receiveOrder()


    void printTraveler(uint32_t stockNum) {
#ifdef BUG6 // time traveler prints even if no trade completed
        if (true) {
#else
//        if ((getTimeToSell() != -1) && (getTimeToBuy() != -1)) {
        if (tts == TimeTravelerStatus::MadeTransaction || tts == TimeTravelerStatus::PotentialImprovement) {
#endif

#ifdef BUG7 // Time traveler fails if start/end times same (and not -1)
            if (getTimeToSell() == getTimeToBuy() && getTimeToSell() != -1)
                exit(1);
#endif

            cout << "A time traveler would buy Stock " << stockNum;
            cout << " at time " << getTimeToBuy() << " for $" << getPriceToBuy();
            cout << " and sell it at time " << getTimeToSell();
            cout << " for $" << getPriceToSell() << "\n";
        } // if
        else {
            cout << "A time traveler could not make a profit on Stock " << stockNum << "\n";
        } // else
    } // printTraveler()
}; // class TimeTraveler
