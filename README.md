# IP_server
A python module to update a dynamic IP address of a server on more clients.

I wrote this program to help a friend that needed to syncronize the IP address of a server on more clients around the country.
One possible solution could be to buy a static IP addres from the provider but for me this was sort of a game to play so I wrote the program.

## Overall concept

### Server side

The idea is to have an application always running on the server that gets the IP address from an online service [https://api.ipify.org/](https://api.ipify.org/) and sends an email to a specified address, once every hour.

### Client side

On the client side there should be a program that the staff can run when a certain condition shous up. I.e. when certain program shows "offline" status most probable reason is that the server is no more reachable thus the IP address changed.

### Security

As you know, your IP is logged on a lot of sites you visit and I do not consider it "higly confidential" indeed I do prefer not to store the history of my IP adresses on my Gmail that is openly harvested for informations by Google.

#### In transit

One observation I made is that if I send an email to myself Google is clever enough for not bouncing all over the world but, seen the header, is clear that uses a loopback IP. In this way therereal "tranmission", the email is sent through SSL connection to Google and that's it.

#### Storage

A IP address is clearly visible and can be identified with a simple regex while scanning through massive amount of data so I thought to sor of "encrypt" it.

##### Encryption

My encryption works in this way:

1. I divide the IP in 4 integer numbers, removing the dots.
2. I sum every cypher of every number until I get a number thet is < 9 (one cipher number). This will be the key cipher.
3. A random encryption factor is generated from a pool starting from -10 up to +10. This myst be known on both sides.
4. Every integer number obtained in point 1 is divided in this way:
    ```
    int * (key * factor)
    ```
5. The key nombers are translated into letters following an array of random letters that must be nown on both sides.
6. At the end of every float will be attached the "key" translated into a letter, and a "padding" letter.

This is an example of what is the aspect of '192.168.0.1' with the following parameters

    alpha = ['o', 'd', 'z', 'm', 't', 'a', 'c', 'i', 'r', 'u']
    paddingPool = 'befghjklnpqsvwxy'
    encryptionFactor = -9.616013867352109

    -5538.823987594815mn-9692.941978290926cq-0.0ox-9.616013867352109db


### Graphics
Because this program is meant to be used by "users" there must be some sort of communication with them and the best way I foun are simple windows.

### Wrapper

Almost every function has a decorator with the purpose of execute that function for n times or until it returns and return its retur value or either fail or return False.
All of this can be controlled by some arguments passed to the decorator.

## TODO

1. Complete docstrings
2. Insert some comment lines
3. Improve this README.md (language and clarity)
3. Clean-up, reshape, improve the graphical part
4. Anything could be done to improve stability and render the code more "pythonic"
5. Add cli arguments parsing like calling the module with the --client or --server arguments
6. Clear or shorten variables names
