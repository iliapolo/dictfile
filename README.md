[![Build Status](https://travis-ci.org/iliapolo/dictfile.svg?branch=release)](https://travis-ci.org/iliapolo/dictfile)
[![Build status](https://ci.appveyor.com/api/projects/status/psflvuie49b5gi71/branch/release?svg=true)](https://ci.appveyor.com/project/iliapolo/dictfile/branch/release)
[![Build Status](https://circleci.com/gh/iliapolo/dictfile/tree/release.svg?style=svg)](https://circleci.com/gh/iliapolo/dictfile/tree/release)
[![Requirements Status](https://requires.io/github/iliapolo/dictfile/requirements.svg?branch=release)](https://requires.io/github/iliapolo/dictfile/requirements/?branch=release)
[![codecov](https://codecov.io/gh/iliapolo/dictfile/branch/release/graph/badge.svg)](https://codecov.io/gh/iliapolo/dictfile)
[![PyPI Version](http://img.shields.io/pypi/v/dictfile.svg)](https://pypi.org/project/dictfile/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/dictfile.svg)](https://pypi.org/project/dictfile/)
[![Is Wheel](https://img.shields.io/pypi/wheel/dictfile.svg?style=flat)](https://pypi.org/project/dictfile/)
[![DictFile release](https://img.shields.io/badge/pyci-release-brightgreen.svg)](https://github.com/iliapolo/pyci)

## The Why

- Have you ever spent more than 5 minutes building a `sed` command to manipulate a simple 
configuration file?

    For example, you have this yaml configuration:
    
    ```yaml
    services:
      elasticsearch:
        cluster: avengers
        addresses:
          - 192.168.2.3:9200
          - 192.158.2.4:9200
    ```
    
    How would you add an elasticsearch address using `sed`? Or any other command line programmatic
    way for that matter? 
    
    If you have to google the answer, its not worth it. Just use `dictfile`:    
    
    Add your configuration file to the `dictfile` repository: (just once)
    
    `dictfile repository add --alias services --file-path services.yaml --fmt yaml`
    
    Then run the following command from anywhere you like:
    
    `dictfile configure services add --key services:elasticsearch:addresses --value 192.168.2.5:9200`
    
    Your file will be as expected: (order and indentation is not currently preserved)
    
    ```yaml
    services:
      elasticsearch:
        addresses:
        - 192.168.2.3:9200
        - 192.158.2.4:9200
        - 192.168.2.5:9200
        cluster: avengers
    ```
    
    **In addition, all standard dictionary operations are supported as well (put, delete, get)**

- Have you ever introduced a syntax error when changing a config file?

    I think we have all been there: You make a small change to the configuration file, only to 
    later realize you made a typo or some other stupid thing. 
    
    With `dictfile`, this wont happen. Given you manipulate the file only with `dictfile`, it simply wont 
    allow you to make any change that breaks the format of the file.

- Have you ever wondered what changes were made to a configuration file on your production server?

    Your system is acting up, though no code changes were pushed to it for a while. What else can
    affect it? Well, configuration obviously.
    
    If multiple changes were made to the configuration file manually, you have no way of knowing 
    what changed and when. However, `dictfile` saves the entire history of changes for you:
       
    `dictfile repository revisions --alias services`
    
    ```text
    +----------+-------------------------+----------------------------+---------+---------------------------------------------------------------+
    |  alias   |           path          |         timestamp          | version |                            message                            |
    +----------+-------------------------+----------------------------+---------+---------------------------------------------------------------+
    | services | /Users/elip/config.yaml | 2018-06-12T17:53:15.886623 |    0    | original version committed automatically upon adding the file |
    | services | /Users/elip/config.yaml | 2018-06-12T17:53:31.213890 |    1    |                  Added an elasticsearch host                  |
    | services | /Users/elip/config.yaml | 2018-06-12T17:54:56.851202 |    2    |               Changed elasticsearch cluster name              |
    +----------+-------------------------+----------------------------+---------+---------------------------------------------------------------+    
    ```

- Have you ever needed to reset a configuration file to a specific point in time?

    Now that you have the history, you can very simple reset to any point in time:
    
    `dictfile repository reset --alias services --version 1`
    
    You can also have a look at each version using:
    
    `dictfile repository show --alias services --version 0`
    
    ```yaml
    services:
      elasticsearch:
        cluster: avengers
        addresses:
          - 192.168.2.3:9200
          - 192.158.2.4:9200
    ```


## The when

*When your configuration files are in one of the following dict based formats:*

- YAML
- INI
- PROPERTIES
- JSON

Building the tool, I saw two main use cases in front of me:

### Build Time

Basically, every time I had to manipulate a configuration file from inside a docker file, it made 
me sad, and I was sad a lot. I found `dictfile` very useful for programmatic editing of these 
configuration files during build time.

### Runtime

Even if you dont edit files at build time, you probably SSH'd into a server to edit
a configuration file more than once in your life. (If not, bravo on the CM setup, I envy you --> 
you probably never worked in a startup)

So, gone are the days of manually editing configuration files on production servers, `dictfile` is a 
much safer and controlled way of doing it.

## The who

Anyone. I dont really have anything to say here, it just seemed fitting to have a *The who* 
section as well.


## The how

`pip install dictfile`

Also, since `dictfile` uses [PyCI](https://github.com/iliapolo/pyci) for releases, you can just 
download a binary executable:

Linux/MacOS:

```bash
sudo curl -L https://github.com/iliapolo/dictfile/releases/download/{version}/dictfile-$(uname -m)-$(uname -s) -o /usr/local/bin/dictfile
```

Windows (PowerShell):

```cmd
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest "https://github.com/iliapolo/dictfile/releases/download/{version}/dictfile-x86-Windows.exe" -UseBasicParsing -OutFile $Env:ProgramFiles\dictfile.exe
```
