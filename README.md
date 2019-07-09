# crawl

given a partial address with k unknown characters, there are 32^k addresses which are possibly valid.

suppose that h represents the number of hosts available to you, t the request timeout (in seconds). setting n = 1/h * 32^k, host r (where each host is indexed from 0 to h-1) should exectute `python crawl.py -d t -r r*n -i n -p xxxxxxxxxxxxxxxx`using the character 0 in place of missing characters. 

e.g. say you have 1024 hosts available to you, as well as the partial address "drips-re--4mj---". then there are 32^6 possible addresses which are valid and so each host has n = 32^4 = 1048576 addresses to scan. using a timeout of 3 seconds, host 2 would execute `python crawl.py -d 3 -r 2097152 -i 1048576 -p drips0re004mj000`. given this configuration, as well as running this process concurrently on each host would allow you to scan the entire space in roughly 36 days. 
