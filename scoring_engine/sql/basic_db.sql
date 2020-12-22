use scoring_engine;
CREATE TABLE IF NOT EXISTS pop3 (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);

CREATE TABLE IF NOT EXISTS splunk (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);
CREATE TABLE IF NOT EXISTS ecomm (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);

CREATE TABLE IF NOT EXISTS ldap (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);
CREATE TABLE IF NOT EXISTS smtp (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);

CREATE TABLE IF NOT EXISTS dns_windows (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);

CREATE TABLE IF NOT EXISTS dns_linux (
    test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    test_date TEXT,
    success ENUM('False', 'True', 'Error')
);

CREATE TABLE IF NOT EXISTS ldap_info (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
