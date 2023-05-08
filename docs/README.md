---
layout: spec
title: "Part A Specification"
latex: true
---

<img
  src="https://eecs281staff.github.io/eecs281.org/assets/images/umseal.svg"
  alt="The Seal of the University of Michigan"
  align="right"
  style="padding: 0px"
  width="170px"
  height="170px"
  />

# EECS 281 - Spring 2023 Project 2: Stock Market Simulation
{: .primer-spec-toc-ignore }

***Due Monday, May 22 at 11:59pm***

<div class="primer-spec-callout warning" markdown="1">

**Important Note:** There are two parts to this project. In your IDE, make
a separate "IDE Project" for each part. If you try to create a single
project, you run into a problem of having two copies of `main()`, which
won't compile, etc.

</div>

## Project Overview
{: .primer-spec-toc-ignore }

There are **two** parts to Project 2. Part A is an emulation of an electronic
stock exchange market. Part B requires you to make multiple implementations
of the priority queue abstract data type.

### Part A Goals
{: .primer-spec-toc-ignore }

* Gain experience using a priority queue.
* Become more proficient with object-oriented design.
* Become more proficient using the STL, especially `std::priority_queue<>`.

### Part B Goals
{: .primer-spec-toc-ignore }

* Implement multiple versions of the priority queue and compare their
  performances.
* Learn a data structure (the pairing heap) from a paper. This type of task
  is something that programmers have to do in their careers.
* Gain experience writing templated classes and subclasses.

## Command Line Interface

TODO
Your program market should take the following case-sensitive command-line
options that will determine which types of output to generate. There are no
arguments required or allowed for any of the output options. Details about
each output mode are under the Output Details section. 

* `-v`, `--verbose`

An optional flag that indicates verbose output should be generated

* `-m`, `--median`

An optional flag that indicates median output should be generated

* `-i`, `--trader_info`

An optional flag that indicates that the trader details output should be
generated 

* `-t`, `--time_travelers`

An optional flag that indicates that time travelers' output should be
generated 

### Legal Command Line Examples
{: .primer-spec-toc-ignore }

```
./market < infile.txt > outfile.txt
./market --verbose --trader_info < infile.txt
./market --verbose --median > outfile.txt
./market --time_travelers
./market --trader_info --verbose 
./market -vmit
```

### Illegal Command Line Examples
{: .primer-spec-toc-ignore }

```
./market -v -q
```

We will not be specifically error-checking your command-line handling;
however we expect that your program conforms with the default behavior of
`getopt_long()`. Incorrect command-line handling may lead to a variety of
difficult-to-diagnose problems.

## Market Logic

Your program market will receive a series of "**orders**," or intentions to
buy or sell shares of a certain stock.  An order consists of the following
information:

* Timestamp - the timestamp that this order comes in
* Trader ID - the trader who is issuing the order
* Stock ID - the stock that the trader is interested in
* Buy/Sell Intent - whether the trader wants to buy or sell shares
* Price Limit - the max/min amount the trader is willing to pay/receive per share
* Quantity - the number of shares the trader is interested in

As each order comes in, your program should see if the new order can be
matched with any previous orders. A new order can be matched with a previous
order if:

* Both orders are for the same stock ID
  * Trader ID does not matter; traders are allowed to buy from themselves.
* The buy/sell intentions are different. That is, one trader is buying and
  the other trader is selling.
* The selling order's price limit is less than or equal to the buying order's
  price limit.

A buyer will always try to buy for the lowest price possible, and a seller
will always try to sell for the highest price possible. Functionally, this
means that whenever a possible match exists, it will **always** occur at the
price of the *earlier* order. When trying to match orders, use priority
queues to identify the *lowest-price* seller and the *highest-price* buyer.

<div class="primer-spec-callout warning" markdown="1">
**Important:** For Part A, you should always use `std::priority_queue<>`, not
your templates from Part B.
</div>

If the SELL order arrived first, then the price of the match will be at the
price listed by the seller. If the BUY order arrived first, the match price
will be the price listed by the buyer.

In the event of a tie (e.g. the two cheapest sellers are offering for the
same price), **always match using the order that arrived earliest.**

### Simple Example

Consider the following series of orders:

1. Trader 1 wants to buy 10 shares of stock 2 for up to $100 each
2. Trader 2 wants to sell 20 shares of stock 2 for at least $10 each
3. Trader 3 wants to buy 10 shares of stock 2 for up to $1 each

(see [Input](#input) below for actual input formatting)

Here is an explanation of what should happen:

1. Trader #1 enters the market with the intent to buy 10 shares of stock #2
   for up to $100/share
  * There are no other orders in the market yet, so trader #1 posts his order
    to the stock exchange to wait for a matching order.
2. Trader #2 enters the market with the intent to sell 20 shares of stock #2
   for as low as $10 per share
  * Trader #2 sees the order left by trader #1, and decides to first sell 10
    shares of the stock to trader #1 for $100 each.
  * Even though she would have been happy selling for $10/share, she wants to
    make as much money as possible and takes advantage of the fact that
    trader #1 is willing to pay more.
  * After selling her 10 shares, she still has 10 shares she wants to get rid
    of. So, she now posts an order to sell her 10 leftover shares for $10 per
    share to wait for a matching order.
3. Trader #3 enters the market with the intent to buy 10 shares of stock #2
   for only $1/share.
  * Trader #3 sees the order left by trader #2 to sell for $10 each, but is
    not willing to pay that much.
  * As a result, Trader #3 posts an order to wait for a matching order.

## Input

Input will arrive from standard input (`cin`). There are two input formats,
trade list (TL) and pseudorandom (PR). All numeric values within an input
file will always fit within a 4-byte integer variable (`int`).

### Input File Header

The first four lines of input will always look the same, with no syntax
errors, additions, or omissions, regardless of input format:

```
COMMENT: <COMMENT AS ONE OR MORE CHARACTERS AND/OR SPACES>
MODE: <INPUT_MODE_AS_TWO_CHARACTERS>
NUM_TRADERS: <NUM_TRADERS_AS_A_POSITIVE_INTEGER>
NUM_STOCKS: <NUM_STOCKS_AS_A_POSITIVE_INTEGER>
```
{: data-title="Common header format for all input files" }

**\<COMMENT...\>** is a string terminated by a newline, which should be
ignored. Each input file will have exactly one line of comments. You should
add a meaningful comment your test files to explain their purpose. 

**\<INPUT_MODE...\>** will either be the string "TL" or "PR" (without the
quote marks). TL indicates that the rest of input will be in the trade list
format, and PR indicates that the rest of input will be in pseudo-random
format. Details for these input formats will be explained shortly.

**\<NUM_TRADERS\>** and **\<NUM_STOCKS\>**, respectively, will tell you how
many traders and stocks will exist. These are integers.

### Trade List Input Mode

If \<INPUT_MODE...\> is TL, the rest of the input file will be a series of
lines in the following format:

    <TIMESTAMP> <BUY/SELL> T<TRADER_ID> S<STOCK_NUM> $<PRICE> #<QUANTITY>

Each line represents a unique order. For example, the line:

    0 BUY T1 S2 $100 #50

reads:

_"At timestamp 0, trader 1 is willing to buy 50 shares of stock 2 for up to
$100/share."_

Each line which describes an order will be well-formatted, meaning that it
might have invalid values, but not an unreadable format.  For example, there
will always be a `T` before the `\<TRADER_ID\>`, always be an `S` before the
\<STOCK_NUM\>, etc. The things you expect to be integers will always be
integers (not strings, not floating-point values with a decimal point).

When you want to read a trade, DO NOT `getline()` the entire line, copy it to
a stringstream, then extract what you want one piece at a time: that’s
processing the same input three times. Instead, use `>>` to extract exactly
what you need. Starting out, a trade needs some type of integer (the
timestamp), a string (`BUY` or `SELL`), a char for the `T` before the trader
number, some type of integer for the trader number, another char for the `S`,
etc.

#### TL Input Errors

You will always find a number where you expect to find one (though they might
be invalid values). To avoid unexpected losses of large amounts of money,
you must check for each of the following:

* `<TIMESTAMP>` is non-negative (no one can trade before the market
opens)
* Timestamps are non-decreasing
  * e.g. 0 cannot come after 1, but there can be multiple orders with the
    same timestamp
* `<TRADER_ID>` is in the range `[0, <NUM_TRADERS>)`
  * e.g. if `<NUM_TRADERS>` is 5, then valid trader IDs are 0, 1, 2, 3, 4
* `<STOCK_ID>` is in the range `[0, <NUM_STOCKS>)` 
  * ibid.
* <PRICE> and <QUANTITY> are both positive

If you detect an input error at any time during the program, print a helpful
message to `cerr` and `exit(1)`. You do not need to check for input errors
not explicitly mentioned here.

### Pseudorandom Input Mode

If \<INPUT_MODE\> is PR, the rest of input will consist of these three lines:

```
RANDOM_SEED: <RANDOM_SEED>
NUMBER_OF_ORDERS: <NUM_ORDERS>
ARRIVAL_RATE: <ARRIVAL_RATE>
```
{: data-title="Pseudorandom generator value format for PR input files" }

**\<RANDOM_SEED\>** — A number integer used to initialize the random seed.

**\<NUMBER_OF_ORDERS\>** — The number of orders to generate.

**\<ARRIVAL_RATE\>** — The average number of orders per timestamp.

All three of these values are unsigned integers.

***PR input will always be correctly formatted.***

#### Using P2random.h

In the project folder, we provide a pair of files to generate the orders in
PR mode. This pseudorandom order generator (PROG) is to make sure that the
generation of pseudo-random numbers is consistent across platforms. The class
P2random contains the following function:

```c++
void P2random::PR_init(std::stringstream& ss,    unsigned int seed,
                       unsigned int num_traders, unsigned int num_stocks,
                       unsigned int num_orders,  unsigned int arrival_rate);
```
{: data-title="PR_init() initializes the pseudorandom order generator" }

`P2random::PR_init()` will set the contents of the stringstream argument
(`ss`) so that you can use it just like you would use cin for TL mode.

You may find the following C++ code helpful in reducing code duplication:

```c++
...
  // First read Input File Header (mode, num_traders, num_stocks)
...

  // Create a stringstream object in case the PROG is used
  stringstream ss;
  
  if (mode == "PR") {
    // TODO: Read PR mode values from cin (seed, num_orders, arrival_rate)
    ...
    // Initialize the PROG and populate ss with orders
    P2random::PR_init(ss, seed, num_traders, num_stocks, num_orders, rate);
  }  // if ..mode

  // Call the function with either the stringstream produced by PR_init()
  // or cin
  if (mode == "PR")
    processOrders(ss);  // This is a separate function you must write
  else
    processOrders(cin);

...
}

// TODO: Create a separate function as referenced above, accepting a stream
//       reference variable, to which you will pass cin or a stringstream
//       that is populated by PR_init()
void processOrders(istream &inputStream) {
  // Read orders from inputStream, NOT cin
  while (inputStream >> var1 >> var2 ...) {
    // process orders
    ...
  }  // while ..inputStream
}  // processOrders()

```
{: data-title="Useful code snippet for eliminating duplicate code" }

### Spec Example Inputs

The following two input files are in different modes, but produce the same
buy/sell orders; thus they generate the same output.

```
COMMENT: Spec Example, TL mode generating 12 orders.
MODE: TL
NUM_TRADERS: 3
NUM_STOCKS: 2
0 SELL T1 S0 $100 #44
1 SELL T2 S0 $56 #42
2 BUY T1 S0 $73 #19
2 BUY T2 S0 $34 #50
2 SELL T2 S1 $86 #23
2 SELL T0 S0 $20 #39
2 BUY T1 S1 $49 #24
2 SELL T1 S1 $83 #45
3 SELL T0 S1 $64 #22
3 SELL T2 S1 $6 #19
3 SELL T0 S1 $42 #37
4 SELL T1 S0 $10 #44
```
{: data-title="Spec Example, Transaction List Input Mode:
p2-stocks/spec-input-TL.txt" }

```
COMMENT: Spec Example, PR mode generating the same 12 orders.
MODE: PR
NUM_TRADERS: 3
NUM_STOCKS: 2
RANDOM_SEED: 104
NUMBER_OF_ORDERS: 12
ARRIVAL_RATE: 10
```
{: data-title="Spec Example, Pseudorandom Input Mode:
p2-stocks/spec-input-PR.txt" }

## Output Details

The output generated by your program will depend on the command line options
specified at runtime. With the exception of startup output and the summary
output, all output is optional and should not be generated unless the
corresponding command line option is specified.

### Startup Output

Your program should always print the following line before reading any
deployments:

`Processing orders...`

### Summary Output

After all input has been read and all possible trades completed, the
following output should always be printed without any preceding newlines
before any optional end of day output:

```
---End of Day---
Trades Completed: <TRADES_COMPLETED><NEWLINE>
```

**\<TRADES_COMPLETED\>** is the total number of trades completed over the
course of the trading day. The number of shares traded doesn't matter; any
seller and any buyer making a trade of matched orders adds one to this count.

### Verbose Output

If and only if the `--verbose/-v` option is specified on the command line
(see [Command Line Interface](#command-line-interface)), whenever a trade is
completed you should print on a single line:

`Trader **\<BUYING_TRADER_NUM\>** purchased **\<NUM_SHARES\>** shares of Stock
**\<STOCK_NUM\>** from Trader **\<SELLING_TRADER_NUM\>** for
$**\<PRICE\>**/share`

#### Verbose Output Example
{: .primer-spec-toc-ignore }

Given the following list of orders:

```
0 SELL T1 S0 $125 #10
0 BUY T2 S0 $1 #100
0 SELL T3 S0 $100 #10
0 SELL T4 S0 $80 #10
0 BUY T5 S0 $200 #4
```

**No trades** are possible until the **5**th order comes in. When the 5th
order comes in, you should print:

`Trader 5 purchased 4 shares of Stock 0 from Trader 4 for $80/share`

### Median Output

If and only if the `--median/-m` option is specified on the command line, at
the times detailed in the Market Logic section, your program should print the
current median match price for all stocks in ascending order by stock ID.
**If no trades have been made for a given stock, it does not have a median,
and thus nothing should be printed for that stock’s median.** In the case
that a median does exist, you should print:

`Median match price of Stock <STOCK_ID> at time <TIMESTAMP> is $<MEDPRICE>`

If there are an even number of trades, take the average of the middle-most
and **use integer division** to compute the median. **If a particular
timestamp in the input file produces no new trades, you still print a median
for that timestamp (limited by the rules above);** see [Detailed
Algorithm](#detailed-algorithm).

#### Median Output Example
{: .primer-spec-toc-ignore }

Given the following transactions:

`Trader 5 purchased 4 shares of Stock 9 from Trader 4 for $80/share`  
`Trader 2 purchased 1 shares of Stock 9 from Trader 10 for $50/share`

The median match price for Stock 9 after these two transactions is $(80 + 50
/ 2) or $65. If the timestamp changed and the `--median/-m` option was
specified, you should print:

`Median match price of Stock 9 at time 0 is $65`

The median match price only considers transactions, and does not consider the
quantity traded in each trade. You must keep a running median, and do it
efficiently! Simply sorting the values every time you need the middle
value(s) will take too much time.

### Trader Info Output

If and only if the `--trader_info/-i` option is specified on the command
line, **following the summary output**, you should print the following line
without any preceding newlines.

`---Trader Info---`

This is followed by a line printed for every trader in ascending order (0, 1,
2, etc.):

`Trader <TRADER_ID> bought <NUMBER_BOUGHT> and sold <NUMBER_SOLD> for a net
transfer of $<NET_VALUE_TRADED>(newline)`

These numbers consider orders across all stocks.

#### Trader Info Example
{: .primer-spec-toc-ignore }

```
---Trader Info---
Trader 0 bought 0 and sold 2 for a net transfer of $166
Trader 1 bought 63 and sold 0 for a net transfer of $-5359
Trader 2 bought 24 and sold 85 for a net transfer of $5193
```

The numbers bought and sold, and net value traded include all stocks that the
trader happened to trade in.  The total number bought by all traders should
equal the total number sold by all traders, and the total of all the net
transfers should be 0.  This shows that our simulation is a zero-sum game.

### Time Travelers Output

In time-travel trading, we want to find the ideal times that a time traveler
theoretically could have bought shares of a stock and then later sold that
stock to maximize profit per share.

If and only if the `--time_travelers/-t` option is specified on the command
line, you should print the following line without any preceding newlines:

`---Time Travelers---`

This is followed by time traveler’s output for every stock in ascending order
(0, 1, 2, etc.):

`A time traveler would buy Stock <STOCK_ID> at time <TIMESTAMP1> for
$<PRICE1> and sell it at time <TIMESTAMP2> for $<PRICE2>`

`<TIMESTAMP1>` will correspond to an actual sell order that came in during
the day, and `<TIMESTAMP2>` will correspond to an actual buy order that came
after the sell order that maximizes the time traveler’s profit.

* When calculating the results for time traveler trading, the only factors
  are the time and price of orders that happened throughout the day, quantity
  is not considered.
* If there would be more than one answer that yields the optimal result, you
  should report the buy/sell pair with the lowest `<TIMESTAMP1>` and
  `<TIMESTAMP2>`. This implies the first selection when ties occur for either
  of the buy/sell prices, and the earliest matched pair if multiple matches
  return the same amount of profit.

If there are no valid buy/sell order pairs (none exist, or none result in a
profit) you should print:

`A time traveler could not make a profit on Stock <STOCK_ID>`

#### Time Traveler Output Example
{: .primer-spec-toc-ignore }

Suppose you had these orders:

```
0 SELL T1 S0 $10 #10
0 BUY T2 S0 $20 #10
0 SELL T1 S0 $30 #10
0 BUY T1 S0 $40 #10
```

The most profitable time traveler trades of stock 0 would be to buy
shares for $10, and then later sell them for $40. **Notice that an actual
matched pair of orders need not occur (the $10 shares are no longer available
when the $40 buyer arrives). You should report only the most profitable
*hypothetical* trade, regardless of which trades actually happen.

Your time traveler must work in $$\Theta(n)$$ time ($$\Theta(1)$$ per
buy/sell order), using $$\Theta(1)$$ memory per stock.

## Detailed Algorithm

Following these steps in order will help guarantee that your program prints
the correct output at the proper times. Details of the output options are
be covered in the [Output Details](#output-details) section.

Initialize `CURRENT_TIMESTAMP` to 0, its value is updated throughout the run
of the program, and even though the first order may not arrive at timestamp
0, no valid orders can arrive before that time.

1. Print [Startup Output](#startup-output)
2. Read the next order from input
3. If the new order's `TIMESTAMP != CURRENT_TIMESTAMP`
  a. If the `--median/-m` option is specified, print the median price of all
     stocks that have been traded on at least once by this point in ascending
     order by stock ID ([Median Output](#median-output))
  b. Set `CURRENT_TIMESTAMP` to be the new order's `TIMESTAMP`.
4. Add the new order to the market
5. Make all possible matches in the market that now includes the new order
   (observing the fact that a single incoming order may make matches with
   multiple existing orders)
  a. If a match is made and the `--verbose/-v` option is specified, print
     [Verbose Output](#verbose-output)
  b. Remove any completed orders from the market
  c. Update the share quantity of any partially fulfilled order in the
     market
6. Repeat steps 2-5 until there are no more orders
7. If the `--median/-m` flag is set, output final timestamp median
   information of all stocks that were traded that day 
   ([Median Output](#median-output))
8. Print [Summary Output](#summary-output)
9. If the `--trader_info/-i` flag is set print [Trader Info
   Output](#trader-info-output)
10. If the `--time_travelers/-t` flag is set print [Time Travelers
   Output](#time-travelers-output)

## Full Spec Example

Given the Spec Example input in either format (TL input shown below):

```
COMMENT: Spec example, TL mode generating 12 orders.
MODE: TL
NUM_TRADERS: 3
NUM_STOCKS: 2
0 SELL T1 S0 $100 #44
1 SELL T2 S0 $56 #42
2 BUY T1 S0 $73 #19
2 BUY T2 S0 $34 #50
2 SELL T2 S1 $86 #23
2 SELL T0 S0 $20 #39
2 BUY T1 S1 $49 #24
2 SELL T1 S1 $83 #45
3 SELL T0 S1 $64 #22
3 SELL T2 S1 $6 #19
3 SELL T0 S1 $42 #37
4 SELL T1 S0 $10 #44
```
{: data-title="p2-stocks/spec-input-TL.txt" }

the output when run with command line options: `--verbose`, `--median`,
`--trader_info`, and `--time_travelers` would be:

```
Processing orders...
Trader 1 purchased 19 shares of Stock 0 from Trader 2 for $56/share
Trader 2 purchased 39 shares of Stock 0 from Trader 0 for $34/share
Median match price of Stock 0 at time 2 is $45
Trader 1 purchased 19 shares of Stock 1 from Trader 2 for $49/share
Trader 1 purchased 5 shares of Stock 1 from Trader 0 for $49/share
Median match price of Stock 0 at time 3 is $45
Median match price of Stock 1 at time 3 is $49
Trader 2 purchased 11 shares of Stock 0 from Trader 1 for $34/share
Median match price of Stock 0 at time 4 is $34
Median match price of Stock 1 at time 4 is $49
---End of Day---
Trades Completed: 5
---Trader Info---
Trader 0 bought 0 and sold 44 for a net transfer of $1571
Trader 1 bought 43 and sold 11 for a net transfer of $-1866
Trader 2 bought 50 and sold 38 for a net transfer of $295
---Time Travelers---
A time traveler would buy Stock 0 at time 1 for $56 and sell it at time 2 for $73
A time traveler could not make a profit on Stock 1
```
{: data-title="Full Spec Example Output: p2-stocks/spec-output-all.txt" }

## Part B: Priority Queues

The [Part B Spec](https://eecs281staff.github.io/p2b-priority-queues) is in
a separate document. The solution to Part B will be submitted separately from
Part A, and should be developed separately in your development environment,
with the files from both solutions stored in separate directories.
