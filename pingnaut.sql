CREATE table results (
id int(10) auto_increment NOT NULL,
response_time float(9) NOT NULL,
source varchar(512) NOT NULL,
traceroute text,
url varchar(1024),
response_code int(4),
timestamp TIMESTAMP,
PRIMARY KEY (id)
);
