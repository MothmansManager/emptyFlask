DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    age INTEGER NOT NULL
);

DROP TABLE IF EXISTS userProfile;

CREATE TABLE userProfile
(
    user_id TEXT PRIMARY KEY, 
    icon TEXT NOT NULL,
    first_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    bio TEXT NOT NULL
);

DROP TABLE IF EXISTS subscriptions;

CREATE TABLE subscriptions
(
    pack_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pack_name TEXT NOT NULL,
    pack_price REAL NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO subscriptions (pack_name, pack_price, description)
VALUES
    ('Seedling', 2.99, 'Monthly subscription that supports the creator!'),
    ('Fresh Sprout', 4.99, 'Monthly subscription that supports the creator!'),
    ('Wizened Botanist', 6.99, 'Monthly subscription that supports the creator a hell of a lot!');


DROP TABLE IF EXISTS purchases;

CREATE TABLE purchases
(
    user_id TEXT NOT NULL, 
    purchasedAmount TEXT NOT NULL
);
