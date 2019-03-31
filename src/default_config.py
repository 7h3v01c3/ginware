
# default "public" connections for RPC proxy
dashd_default_connections = [
    {
        "use_ssh_tunnel": False,
        "host": "ginware1.gincoin.io",
        "port": "443",
        "username": "",
        "password": "",
        "use_ssl": True
    },
    {
        "use_ssh_tunnel": False,
        "host": "localhost",
        "port": "10211",
        "username": "rpcuser",
        "password": "674141414141426373564158765a7a7337504b546f52376a5f3555443849576f5362512d3361656e49417243597477734c64495a4443534558635571386f646370535f58505a6e463272304d75475f43674a656957304a67303772665069614b64513d3d",
        "use_ssl": False
    }
]
