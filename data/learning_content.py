"""
Content for the Learning section -- 5 original chapters on stock market
basics, written fresh (not copied from any source), citing well-known
books as further-reading references. Structured as a list so the
Learning page can navigate, download, and (separately) ground a
restricted chatbot in exactly this content.
"""

CHAPTERS = [
    {
        "number": 1,
        "title": "What Is the Stock Market?",
        "content": """
### The Basic Idea

Imagine a company needs money to grow -- to build a new factory, hire more people, or launch a new product. One way to raise that money is to sell small pieces of ownership in the company to the public. Each small piece is called a **share**, or a **stock**. The place where these shares are bought and sold is called the **stock market**.

In the simplest words: the stock market is a big, organized marketplace where people buy and sell tiny ownership pieces of companies. When you buy a share, you literally own a small slice of that business. If the company does well, your slice tends to become more valuable. If it struggles, your slice can lose value.

### Two "Markets" in One

There are actually two stages to how a stock reaches your hands:

1. **The primary market** -- where a company sells shares for the very first time, through an **Initial Public Offering (IPO)**. The money goes directly to the company to fund its growth.
2. **The secondary market** -- what most people mean by "the stock market." Once shares exist, investors trade them among themselves -- you buy from another investor, not the company, and sell to someone else who wants in. Exchanges like the **New York Stock Exchange (NYSE)** or **NASDAQ** are simply the organized places where this happens.

### Why Do Stock Prices Move?

Prices move because of two things mixed together: what a company is actually worth (its profits, growth, debts, and future prospects), and what people currently believe and feel about it (hope, fear, excitement, panic).

Economist Burton Malkiel, in *A Random Walk Down Wall Street*, describes a "random walk" as a path where each new step cannot be predicted from the steps before it. Applied to stocks, this means day-to-day price changes tend to be genuinely unpredictable -- not because the market is chaotic, but because almost everything currently known about a stock is usually already reflected in its price. This makes it very hard to consistently find "secret" bargains just by studying past price charts.

Benjamin Graham, in *The Intelligent Investor*, offers a helpful picture for these swings: imagine the market as a moody business partner nicknamed "Mr. Market." Every day, he shows up offering to buy your shares or sell you more, at a price that depends entirely on his mood -- sometimes wildly optimistic, sometimes gloomy and fearful. You are never obligated to trade with him.

### Why Bother With the Stock Market at All?

For companies, it's a way to raise large sums without taking on debt that must be repaid with interest -- instead, they share ownership (and future profit) with investors.

For ordinary people, it's one of the most effective long-term tools for growing savings. Money sitting in a low-interest savings account often barely keeps pace with rising prices (inflation), while a well-chosen collection of stocks has historically grown meaningfully faster over long periods -- with real ups and downs along the way.

### A Simple Mental Model

Think of the stock market as a giant auction house that almost never closes. Thousands of "goods" -- shares of different companies -- are for sale at once. Buyers and sellers constantly quote prices electronically, and a trade happens the instant a buyer and seller agree on one.

### Chapter Summary

- A share is a small ownership piece of a real company.
- The primary market is where shares are first sold (IPOs); the secondary market is where investors trade them afterward.
- Prices reflect both real business fundamentals and shifting human sentiment ("Mr. Market").
- Short-term price movements are genuinely hard to predict (the "random walk" idea).
- Stocks have historically been a strong long-term tool for growing savings.

**Further Reading:** *A Random Walk Down Wall Street* by Burton G. Malkiel; *The Intelligent Investor* by Benjamin Graham.
""",
    },
    {
        "number": 2,
        "title": "Understanding a Company Before You Buy Its Stock",
        "content": """
Before buying a slice of any business, it helps enormously to understand how that business is actually doing financially. Every public company must regularly publish financial reports, and three documents matter most.

### 1. The Balance Sheet -- A Snapshot of What's Owned and Owed

Picture a photograph of a company's finances on one single day -- that's the balance sheet. It has three parts: **assets** (everything the company owns or is owed), **liabilities** (everything it owes others), and **shareholders' equity** (what would be left for the owners if the company sold everything and paid off every debt).

One simple rule underlies the whole thing: **Assets = Liabilities + Shareholders' Equity**

**Worked example** -- a simplified balance sheet where Cash (20,000) + Accounts Receivable (3,000) + Inventory (60,000) + Prepaid Expenses (11,000) + Property/Equipment (110,000) + Intangible Assets (10,000) = Total Assets of 214,000. On the other side: Accounts Payable (2,000) + Accrued Expenses (1,000) + Bank Loan (100,000) + Common Shares (89,000) + Retained Earnings (11,000) = Total Liabilities & Equity of 214,000. Notice both sides exactly match -- this balance is where the "balance sheet" gets its name.

### 2. The Income Statement -- How Much the Company Made or Lost

While the balance sheet is a single snapshot, the income statement covers a stretch of time (a quarter or a year). It has three parts: **revenue** (total money earned from sales), **expenses** (everything spent to run the business), and **net income** (what's left after subtracting expenses from revenue).

**Worked example:** if a company earns $10,000,000 in revenue and spends $8,000,000 on expenses, its net income is $2,000,000. If it has 1,000,000 shares outstanding, its **Earnings Per Share (EPS)** is $2,000,000 / 1,000,000 = **$2.00 per share**.

### 3. The Cash Flow Statement -- Where the Actual Cash Went

Profit on paper isn't the same as cash in the bank -- a company can report a profit while running low on cash, for example if customers haven't paid their bills yet. The cash flow statement tracks real cash movement across three categories: **operating** (day-to-day business), **investing** (cash spent on or received from long-term assets), and **financing** (borrowing, repaying debt, or paying dividends).

### A Toolkit: Ratios, With Worked Numbers

- **Current ratio** = Current assets / Current liabilities. Example: 94,000 / 3,000 = 31.3. Tells you if a company can pay its short-term bills.
- **Return on equity (ROE)** = Net income / Shareholders' equity. Example: 10,000 / 100,000 = 10%.
- **Price-to-earnings (P/E)** = Share price / EPS. Example: $30 / $2 = 15.
- **Market capitalization** = Share price x Shares outstanding. Example: $30 x 1,000,000 = $30,000,000.
- **Dividend yield** = Annual dividend per share / Share price. Example: $1 / $30 = 3.3%.

### Chapter Summary

- The balance sheet shows what's owned and owed at one moment; assets always equal liabilities plus equity.
- The income statement shows profit over a period of time, and is where EPS comes from.
- The cash flow statement tracks real cash movement, which can differ from reported profit.
- Simple ratios (current ratio, ROE, P/E, market cap, dividend yield) make companies easier to compare.

**Further Reading:** *Financial Statements* by Thomas Ittelson; PwC/CFI, *Basic Understanding of a Company's Financial Statements*.
""",
    },
    {
        "number": 3,
        "title": "The Value Investor's Mindset -- Buying Businesses, Not Tickers",
        "content": """
This chapter is built around Benjamin Graham's ideas in *The Intelligent Investor*, the foundational text of value investing.

### A Stock Is a Piece of a Real Business

Graham's central message: when you buy a share, you are not buying a flickering number on a screen -- you are buying a small ownership stake in a real, operating business. His approach is to always ask "what is this business actually worth?" rather than "what did the price do yesterday?"

### Margin of Safety -- The Central Idea

If there is one idea to take from Graham's work, it is the **margin of safety**: don't pay a price too close to (or above) your honest estimate of what a stock is actually worth. Leave room for being wrong.

Think of an engineer building a bridge. The engineer doesn't design it to hold exactly the maximum expected weight -- they build in extra strength in case their estimates are slightly off. A margin of safety works the same way: buying at a meaningful discount to your estimate of true worth means that even if your estimate turns out to be a bit too optimistic, you're still protected from serious loss.

### What a Cautious, "Defensive" Investor Looks For

Graham distinguished between two broad approaches an ordinary investor can honestly choose between:

- The **defensive investor** wants a simple, low-effort, relatively safe approach -- favoring large, well-established, financially sound companies with a long history of profitability and dividend payments, spreading money across a good number of them, and avoiding speculation on short-term price swings.
- The **enterprising investor** is willing to put in real time and effort -- carefully studying financial statements, hunting for genuine bargains, and being more selective and active.

Graham was clear that the enterprising path only pays off for someone genuinely willing to do the extra work; half-hearted effort in that style tends to produce worse results than simply being a careful, defensive investor. The general spirit behind evaluating a sound defensive holding boils down to a few practical questions: Is this a reasonably large, established business rather than a tiny speculative one? Has it shown a consistent history of profit rather than a run of losses? Is its debt manageable relative to what it owns? Has it paid dividends reliably over many years? None of these questions guarantee a good pick on their own -- but running through them pushes you back toward real numbers rather than buying on excitement alone.

### Price Is What You Pay, Value Is What You Get

Price is simply whatever the market happens to charge today, set by current mood, supply, and demand. Value is what the underlying business is actually worth, based on its earnings, assets, and prospects. A good investment is bought at a price meaningfully below its real value. Speculation, by contrast, means buying purely on the hope that price will rise, with little regard for the underlying value.

### Chapter Summary

- Buying a stock means buying a real stake in a real business.
- The margin of safety means leaving room for error between price and your estimate of true value.
- Defensive investors favor safety and simplicity; enterprising investors put in real extra work.
- Price and value are related but different things.

**Further Reading:** *The Intelligent Investor* by Benjamin Graham.
""",
    },
    {
        "number": 4,
        "title": "Finding Good Stocks -- Practical Lessons, and a Realistic Warning",
        "content": """
This chapter draws on Peter Lynch's *One Up On Wall Street*, balanced with Burton Malkiel's central warning about market efficiency.

### "Invest in What You Know" -- A Starting Point, Not a Finish Line

Peter Lynch, who ran one of the most successful mutual funds in history, built much of his approach around a simple idea: ordinary people often spot good companies in everyday life long before Wall Street professionals notice them. Noticing a good business is only the start -- it should be followed by real homework: is the company actually financially healthy, reasonably priced, and growing sensibly?

### Categorizing Companies

Lynch encouraged investors to think about which broad type of company they are looking at:

- **Slow growers** -- large, mature companies that grow slowly but often pay steady dividends.
- **Stalwarts** -- big, solid companies growing a bit faster, offering some safety with moderate growth.
- **Fast growers** -- smaller, aggressive companies expanding quickly; bigger potential gains, but higher risk.
- **Cyclicals** -- companies whose profits rise and fall with the broader economy (car makers, airlines).
- **Turnarounds** -- struggling companies that may recover.
- **Asset plays** -- companies sitting on valuable assets the market hasn't fully noticed yet.

Knowing the category sets realistic expectations.

### Comparing the P/E Ratio to the Growth Rate

Lynch added a practical rule: for a fairly priced company, its P/E ratio should roughly match its earnings growth rate.

**Worked example:** two companies, both trading at a P/E of 12. Company A grows earnings at 6% a year -- its P/E is twice its growth rate, a warning sign. Company B grows earnings at 12% a year but trades at a P/E of only 6 -- half its growth rate, which looks like a genuine bargain worth investigating.

### Why Beating the Market Is Genuinely Hard

Because so much company information is already public and quickly absorbed into prices, it is extremely difficult -- even for full-time professionals -- to consistently find underpriced stocks and beat the overall market year after year. Long-running studies have found that a large share of professional fund managers fail to outperform a simple, low-cost index fund (a fund that buys a broad slice of the whole market) over long periods.

This doesn't mean individual stock research is worthless -- Lynch's own long track record shows it can be done well. It means beginners should be realistic: picking stocks well takes real, ongoing effort and emotional discipline. For anyone unwilling to put in that consistent effort, steadily investing in a broad, low-cost index fund is a well-supported, time-tested alternative.

### Chapter Summary

- Everyday observation can spark good investment ideas, but it's only a starting point.
- Knowing a company's "type" sets realistic expectations.
- Comparing P/E to growth rate is a useful, practical screening tool.
- Consistently beating the market is genuinely difficult -- index funds are a reasonable alternative for many investors.

**Further Reading:** *One Up On Wall Street* by Peter Lynch; *A Random Walk Down Wall Street* by Burton G. Malkiel.
""",
    },
    {
        "number": 5,
        "title": "The Psychology of Investing -- Behaving Well With Your Money",
        "content": """
This chapter draws on Morgan Housel's *The Psychology of Money*.

### Investing Success Is More About Behavior Than Intelligence

Successful investing has less to do with being brilliant at math or economics, and more to do with behaving sensibly, patiently, and consistently over long stretches of time. Someone with modest financial knowledge but strong habits -- regular saving, patience, emotional control -- will often outperform a highly intelligent person who panics and makes emotional decisions during market swings.

### The Quiet Power of Compounding -- A Real Example

Compounding means your money earns returns, and those returns themselves start earning further returns, snowballing over time.

Warren Buffett started investing seriously around age 10. His long-run annual return has been roughly 22% -- remarkable, but not unprecedented; investor Jim Simons of Renaissance Technologies has compounded money at roughly 66% annually since 1988, a far higher rate. Yet Buffett has ended up dramatically wealthier than Simons overall, because Buffett kept compounding money for around 70+ years, while Simons didn't find his stride until age 50.

A widely-cited thought experiment: what if Buffett had built a smaller base by age 30 (say, $25,000), earned that same 22% annual return, but retired at 60 like most people instead of continuing into his 90s? His estimated net worth today would be around $11.9 million -- excellent on its own, but roughly 99.9% less than his actual fortune. Almost all of Buffett's advantage comes from time, not from having a secretly higher return than everyone else.

### Getting Wealthy vs. Staying Wealthy

Getting wealthy often involves taking chances, optimism, and putting money to work. Staying wealthy requires something closer to the opposite: humility, frugality, and a healthy respect for the possibility of loss. Many investors who make large gains lose them again by failing to switch from a "building" mindset to a "protecting" mindset.

### Everyone Is Playing a Different Game

A common source of bad decisions is copying the behavior of people playing a completely different financial "game" than you are. A short-term trader and a long-term retirement saver can look at the exact same stock chart and reasonably reach opposite conclusions, because their goals, time horizons, and risk tolerance are completely different.

### Your Savings Rate Matters More Than Most People Think

Your savings rate -- simply how much of your income you set aside and invest -- is entirely within your own control, unlike stock market returns, which are not. Building wealth is less about earning a huge income or picking the single best stock, and much more about consistently living below your means and giving your savings time to compound.

### Chapter Summary

- Investing success depends more on behavior than raw intelligence.
- Compounding rewards time above almost everything else.
- Building wealth and keeping wealth require different, sometimes opposite, mindsets.
- Copying investors playing a different "game" than you leads to poor decisions.
- Your savings rate is one of the few things fully within your control.

**Further Reading:** *The Psychology of Money* by Morgan Housel; *A Random Walk Down Wall Street* by Burton G. Malkiel.
""",
    },
]

DISCLAIMER = (
    "This content is for general educational purposes only and does not "
    "constitute financial, investment, or legal advice. It does not "
    "predict future market performance and should not be used as the "
    "sole basis for any investment decision."
)


def get_chapter(number: int) -> dict:
    return next((c for c in CHAPTERS if c["number"] == number), None)


def build_full_document() -> str:
    """Assembles all 5 chapters into one downloadable markdown document."""
    parts = [
        "# Understanding the Stock Market: A 5-Chapter Guide\n",
        f"*{DISCLAIMER}*\n",
    ]
    for c in CHAPTERS:
        parts.append(f"\n---\n\n## Chapter {c['number']}: {c['title']}\n")
        parts.append(c["content"])
    return "\n".join(parts)