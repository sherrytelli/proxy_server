# PROXY_SERVER
This is a proxy server made in python.

The server currently works in http 1.0 and only the GET method is implemented. on all other methods, 501 not implemented will be returned. if the url or the request is not in the correct format 400 bad request will be retuned by the proxy server.

## how to run
you have to specify a port number in the command line when running the program
example usage: python proxy.py 8080

## how to send request to the server
in one terminal run the proxy server. in another terminal send a curl request "curl -x http://localhost:8080 http://example.com".

you can also configure you browser to run send request to the proxy by going into the network settings of yout browser and changing prioxy settings.

# NOTE
The above program is made with linux systems calls and will only work on linux.