CREATE TABLE Users
(
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(35) NOT NULL UNIQUE,
    password_hash CHAR(32) NOT NULL,
    salt CHAR(16) NOT NULL,
    registration_date DATE NOT NULL
);

CREATE TABLE UsersIcon
(
    uid INTEGER,
    data BLOB,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES Users(uid)
);

CREATE TABLE Accounts
(
    aid INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER,
    creation_date DATE NOT NULL, -- Date when this account was first created
    registration_date DATE NOT NULL, -- Date when this account was added to the database
    last_transaction_date DATE, -- May be null
    currency CHAR(3) NOT NULL,
    name VARCHAR(35) NOT NULL,
    description TEXT,
    FOREIGN KEY (uid) REFERENCES Users(uid)
);

CREATE TABLE Transactions
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account INTEGER,
    uid INTEGER,
    date DATE NOT NULL, -- Date when the transaction was effected
    available_date DATE, -- Date when the transaction take effect (may be null)
    registration_date DATE, -- Date when the transaction was effected
    amount REAL NOT NULL,
    description TEXT,
    FOREIGN KEY (account) REFERENCES Accounts(aid)
);

CREATE TABLE Tags
(
    uid INTEGER,
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(35) NOT NULL,
    description TEXT,
    color CHAR(6), -- 000000
    UNIQUE (uid, name),
    FOREIGN KEY (uid) REFERENCES Users(uid)
);

CREATE TABLE TransactionHasTag
(
    tid INTEGER,
    tag INTEGER,
    PRIMARY KEY (tid, tag),
    FOREIGN KEY (tid) REFERENCES Transactions,
    FOREIGN KEY (tag) REFERENCES Tags
);

CREATE TABLE Budget
(
    bid INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    name VARCHAR(35) NOT NULL,
    interval INTEGER NOT NULL, -- 0:day, 1:month, 2:trimester, 3:semester, 4:year
    FOREIGN KEY (uid) REFERENCES Users(uid)
);

CREATE TABLE BudgetSpendingCategory
(
    bsid INTEGER PRIMARY KEY AUTOINCREMENT,
    bid INTEGER NOT NULL,
    name VARCHAR(35) NOT NULL, 
    matcher TEXT NOT NULL,
    formula TEXT NOT NULL,
    priority INTEGER NOT NULL,
    FOREIGN KEY (bid) REFERENCES Budget,
    UNIQUE (bid, name)
);

CREATE TABLE BudgetIncomeCategory
(
    biid INTEGER PRIMARY KEY AUTOINCREMENT,
    bid INTEGER NOT NULL,
    name VARCHAR(35) NOT NULL,
    matcher TEXT NOT NULL,
    safety_level REAL NOT NULL,
    priority INTEGER NOT NULL,
    FOREIGN KEY (bid) REFERENCES Budget,
    UNIQUE (bid, name)
);

CREATE TABLE Ticket
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    date DATE NOT NULL,
    name VARCHAR(45),
    last_name VARCHAR(45),
    email VARCHAR(60),
    country VARCHAR(40),
    content TEXT,
    FOREIGN KEY (uid) REFERENCES Users(uid)
);
