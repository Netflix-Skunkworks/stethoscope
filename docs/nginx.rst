Nginx
=====

Configuration
-------------

For `Nginx`_, the supplied :file:`nginx.conf` sets up the appropriate configuration for running
locally out of the repository directory. Essentially, requests for static files are handled by
`Nginx`_, requests for non-API endpoints are proxied to port 5002 (to be handled by the login
server), and requests for API endpoints are proxied to port 5001 (to be handled by the API server).

Running
-------

.. code:: sh

    nginx -c nginx.conf -p $(pwd)


.. _Nginx: https://www.nginx.com/
