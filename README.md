# Multi-Client Networked Chat App

## Objectives
- Learn Socket Programing in Python
- Implement concurrency using Threads

## Capabilities
- Requesting list of connected clients
- Sending text messages to clients
- Sending text files to clients

## Limitations
- Can only send utf-8 encoded files
- File size is limited by the buffer size on the server's end

## Usage

Start the server
```
python3 server.py -p <port_num>
```

Start the client
```
python3 client.py -p <server_port_num> -u <username>
```

Get the list of online users
```
list
```

Sending message to other users
```
msg <num of users> <user1> <user2> <message>
```