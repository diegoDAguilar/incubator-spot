
# Demo Read the Docs

|Spot Field Name  |Type    |Description                                                           |Original Field Name  |Format      |Spot-ingest       |Spot-ml           |Spot-oa           |Spot-ui           | 
|---------------- |--------|----------------------------------------------------------------------|---------------------|------------|------------------|------------------|------------------|------------------|
| p_date          | string | Date for the connection                                              |        date         | yyyy-mm-dd |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| p_time	      | string | Time for the connection	                                          |        time	        | hh:MM:SS   |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| clientip        | string |IP address of the client sending the request                          |        c-ip	        |ip address	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| host        	  | string |Hostname from the client's request URL	                              |       cs-host	    |   text	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| reqmethod	      | string |Request method used from client to appliance (HTTP Method - GET, POST, CONNECT) |   cs-method | 	text |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| useragent	      | string |Browser Type	                                                      | cs(User-Agent)	    |quoted text |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| resconttype	  | string |Content-type (Ex. text/html, image/xml)	                              |rs(Content-Type)     | text	     |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| duration	      |  int   |Duration of the connection	                                          |time-taken           |numerical	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| username	      |string  |Client Username	                                                      |cs-username	        |text	     |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| authgroup   	  |string  |Client Authentication Group	                                          |cs-auth-group 	    |text	     |:white_check_mark:|	-	           |     -            |       -          |
| exceptionid	  |string  |Identifier of the exception resolved (empty if the transaction has not been terminated) |x-exception-id|text|:white_check_mark:|-              |     -            |       -          |	
| filterresult    |string  |Content filtering result: Denied, Proxied or Observed                 |sc-filter-result     | text       |:white_check_mark:|   -              |     -            |       -          |			
| webcat	      |string  |All content categories of the request URL	                          |cs-categories        |quoted text |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| referer	      |string  |Request header: Referer %S s-sitename The service type used to        |cs(Referer)          | url        |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| respcode	      |string  |Protocol status code from appliance to client (HTTP Response Codes)   |sc-status            | numerical  |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| action	      |string  |What type of action did the Appliance take to process this request; possible values include ALLOWED, DENIED, FAILED, SERVER_ERROR|s-action |text |:white_check_mark:| -| -|-         | 			
| urischeme	      |string  |Scheme of the original URL requested	                              |cs-uri-scheme        |text	     |:white_check_mark:|   -              |     -            |       -          |		
| uriport	      |string  |Port from the original URL requested	                              |cs-uri-port 	        |numerical	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| uripath	      |string  |Path of the original URL requested without query                      |cs-uri-path          |text        |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| uriquery	      |string  |Query from the original URL requested	                              |cs-uri-query	        |text	     |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| uriextension	  |string  |Document extension from the original URL requested                    |cs-uri-extension     |text	     |:white_check_mark:|   -              |     -            |       -          |		
| serverip	      |string  |IP address of the appliance on which the client established its connection|s-ip             |ip address  |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| scbytes	      |int	   |Number of bytes sent from appliance to client                         |sc-bytes             |numerical	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| csbytes	      |int	   |Number of bytes sent from client to appliance                         |cs-bytes 	        |numerical	 |:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:|
| virusid	      |string  |x-virus-id 	                                                          |x-virus-id 	        |text	     |:white_check_mark:|   -              |    -             |       -          |		
| bcappname	      |string  |x-bluecoat-application-name 	                                 |x-bluecoat-application-name|quoted text|:white_check_mark:|   -              |    -             |       -          |			
| bcappoper	      |string  |x-bluecoat-application-operation	         |x-bluecoat-application-operation              |quoted text |:white_check_mark:|   -              |    -             |       -          |			
|fulluri	      |string  |Full URI concatenated from cs-host, cs-uri-path, cs-uri-query fields |it does not exist, it is calculated during ingest|text|:white_check_mark:|:white_check_mark:|:white_check_mark:|:white_check_mark:| 
| word 	          |string  |      -                					                              |           -         |   -        |     -            |   -              |:white_check_mark:|       -          |
| ml_score	      |float   |				-	                                                  |           -         |   -        |     -            |   -              |:white_check_mark:|       -          |
| respcode_name   |string  |IANA translation for the response code column                         |           -         |   -        |     -            |   -              |:white_check_mark:|:white_check_mark:|
| uri_rep	      |string  |Reputation value according to Threat intelligence services            | 	      -         |	-		 |     -            |   -              |:white_check_mark:|:white_check_mark:|
| network_context |string  |User defined value					                                  |           -         |   -        |     -            |   -              |:white_check_mark:|:white_check_mark:|  

