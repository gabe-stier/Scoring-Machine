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

INSERT INTO dns_windows (test_date, success) VALUES (1,'Error');
INSERT INTO dns_linux (test_date, success) VALUES (1,'Error');
INSERT INTO splunk (test_date, success) VALUES (1,'Error');
INSERT INTO ecomm (test_date, success) VALUES (1,'Error');
INSERT INTO pop3 (test_date, success) VALUES (1,'Error');
INSERT INTO smtp (test_date, success) VALUES (1,'Error');