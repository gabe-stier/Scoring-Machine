use scoring_engine;
CREATE OR REPLACE VIEW scores AS
    SELECT 
        DNSL.success AS DNSL_SUCCESS,
        DNSW.success AS DNSW_SUCCESS,
        ECOMM.success AS ECOMM_SUCCESS,
        LDAP.success AS LDAP_SUCCESS,
        SPLUNK.success AS SPLUNK_SUCCESS,
        POP3.success AS POP3_SUCCESS,
        SMTP.success AS SMTP_SUCCESS
    FROM
        (SELECT 
            test_id, success
        FROM
            ldap
        ORDER BY test_id DESC
        LIMIT 1) AS LDAP,
        (SELECT 
            test_id, success
        FROM
            dns_linux
        ORDER BY test_id DESC
        LIMIT 1) AS DNSL,
        (SELECT 
            test_id, success
        FROM
            dns_windows
        ORDER BY test_id DESC
        LIMIT 1) AS DNSW,
        (SELECT 
            test_id, success
        FROM
            pop3
        ORDER BY test_id DESC
        LIMIT 1) AS POP3,
        (SELECT 
            test_id, success
        FROM
            splunk
        ORDER BY test_id DESC
        LIMIT 1) AS SPLUNK,
        (SELECT 
            test_id, success
        FROM
            smtp
        ORDER BY test_id DESC
        LIMIT 1) AS SMTP,
        (SELECT 
            test_id, success
        FROM
            ecomm
        ORDER BY test_id DESC
        LIMIT 1) AS ECOMM;
CREATE OR REPLACE VIEW top_5_dnsl AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_linux
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_dnsw AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_windows
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_pop3 AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.pop3
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_smtp AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.smtp
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_splunk AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.splunk
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_ecomm AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ecomm
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_5_ldap AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ldap
    ORDER BY test_id DESC
    LIMIT 5;
CREATE OR REPLACE VIEW top_10_dnsl AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_linux
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_dnsw AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_windows
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_pop3 AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.pop3
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_smtp AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.smtp
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_splunk AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.splunk
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_ecomm AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ecomm
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_10_ldap AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ldap
    ORDER BY test_id DESC
    LIMIT 10;
CREATE OR REPLACE VIEW top_15_dnsl AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_linux
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_dnsw AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_windows
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_pop3 AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.pop3
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_smtp AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.smtp
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_splunk AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.splunk
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_ecomm AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ecomm
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_15_ldap AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ldap
    ORDER BY test_id DESC
    LIMIT 15;
CREATE OR REPLACE VIEW top_20_dnsl AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_linux
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_dnsw AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.dns_windows
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_pop3 AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.pop3
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_smtp AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.smtp
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_splunk AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.splunk
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_ecomm AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ecomm
    ORDER BY test_id DESC
    LIMIT 20;
CREATE OR REPLACE VIEW top_20_ldap AS
    SELECT 
        test_id, success
    FROM
        scoring_engine.ldap
    ORDER BY test_id DESC
    LIMIT 20;