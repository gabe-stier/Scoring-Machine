SET sql_notes = 0;
CREATE TABLE IF NOT EXISTS pop3 (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success INTEGER CHECK (
		success = 1
		or success = 0
		or success = 2
	)
);
CREATE TABLE IF NOT EXISTS splunk (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS ecomm (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS ldap (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS smtp (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS dns_windows (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS dns_linux (
	test_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	test_date TEXT,
	success ENUM ('0','1', '2')
);
CREATE TABLE IF NOT EXISTS ldap_info (
	user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	username TEXT NOT NULL,
	password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pop3_info (
	user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	username TEXT NOT NULL,
	password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS smtp_info (
	email_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	to_user TEXT NOT NULL
);
SET sql_notes = 1;