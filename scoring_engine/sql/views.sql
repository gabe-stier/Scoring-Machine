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