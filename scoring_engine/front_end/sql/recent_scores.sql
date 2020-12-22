use scoring_engine;
select 	dns_linux.success as DNSL_SUCCESS,
        dns_windows.success as DNSW_SUCCESS,
		ecomm.success as ECOMM_SUCCESS,
        ldap.success as LDAP_SUCCESS,
        splunk.success as SPLUNK_SUCCESS,
        pop3.success as POP3_SUCCESS,
        smtp.success as SMTP_SUCCESS      
from	dns_linux,
		ecomm,
		dns_windows,
		ldap,
		splunk,
		pop3,
		smtp
LIMIT 1;