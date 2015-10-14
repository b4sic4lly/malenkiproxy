# Malenki Proxy

This is a really small HTTP-proxy. It is very rudimentary and should
be used for the analysis of HTTP traffic of programs. It is also possible to
replace files live when the proxy receives a request. 

## Usage

In a configfile you can specify address and port of the server as well as the
info for replacing the files. A config file can look like this:

```
[General]
host: localhost
port: 8080

[FileReplace]
some.pdf: someother.pdf
somezip.zip: someotherzip.zip
```

The config is very self-explaining. The FileReplace works as follows: If 
a request is coming e.g. http://www.example.com/some.pdf the proxy will not
respond with the actual pdf but with the `someother.pdf` which is a local file
in the Malenki Proxy folder. 

The `--save-files` switch specifies that it should download all transactions, 
be it HTML or some other file, in a folder `files` in the Malenki Proxy folder. 

```
$ ./malenkiproxy.py -h
usage: malenkiproxy.py [-h] [-c CONFIG] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify config file
  -s, --save-files      if set, proxy saves every transaction in a file
```
