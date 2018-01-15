# coding: utf-8

import socket


def test_request_server_list_url(acmclient):
    assert "8080/diamond-server/diamond" in acmclient.request_server_list_url()


def test_fetch_server_list(acmclient):
    hosts = acmclient.fetch_server_list()
    assert hosts, 'ali server list error'
    for ip in hosts:
        assert socket.inet_aton(ip), 'ip address error'
