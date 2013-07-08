from twisted.internet import protocol
from twisted.application import service, internet
from twisted.web.client import getPage, HTTPClientFactory
from twisted.web.error import PageRedirect

HTTPClientFactory.noisy = False

import struct
import json

import M2Crypto
import hashlib
import base64

### begin config

SERVER_HOST   = "192.95.39.248"
SERVER_PORT   = 25565

PING_VERSION  = "1.6.2"
PING_PROTOCOL = "74"
PING_MOTD     = "Junction Auth"

AUTH_ADDR     = "http://session.minecraft.net/game/checkserver.jsp?user={user}&serverId={serverId}"
AUTH_TIMEOUT  = 10

API_LOGIN     = "https://junction.at/login.json"
API_ADDR      = "https://junction.at/api/confirm_auth/{user}/{addr}/"
API_TIMEOUT   = 10
API_USERNAME  = "Anathema"
API_PASSWORD  = "7M5GiAKOimuwectX9QON"

### end config

class Crypto:
    rand_bytes = M2Crypto.Rand.rand_bytes

    @classmethod
    def make_keypair(cls):
        return M2Crypto.RSA.gen_key(1024, 257)

    @classmethod
    def make_server_id(cls):
        return "".join("%02x" % ord(c) for c in cls.rand_bytes(10))

    @classmethod
    def make_verify_token(cls):
        return cls.rand_bytes(4)

    @classmethod
    def make_digest(cls, *data):
        sha1 = hashlib.sha1()
        for d in data: sha1.update(d)

        digest = long(sha1.hexdigest(), 16)
        if digest >> 39*4 & 0x8:
            return"-%x" % ((-digest) & (2**(40*4)-1))
        else:
            return "%x" % digest


    @classmethod
    def export_public_key(cls, keypair):
        pem_start = "-----BEGIN PUBLIC KEY-----"
        pem_end = "-----END PUBLIC KEY-----"

        #First extract a PEM file
        bio = M2Crypto.BIO.MemoryBuffer("")
        keypair.save_pub_key_bio(bio)
        d = bio.getvalue()

        #Get just the key data
        s = d.find(pem_start)
        e = d.find(pem_end)
        assert s != -1 and e != -1
        out = d[s+len(pem_start):e]

        #Decode
        return base64.decodestring(out)

    @classmethod
    def decrypt(cls, keypair, data):
        return keypair.private_decrypt(data, M2Crypto.m2.pkcs1_padding)


class Underrun(Exception):
    pass


class Buffer(object):
    def __init__(self):
        self.buff1 = ""
        self.buff2 = ""

    def length(self):
        return len(self.buff1)

    def empty(self):
        return len(self.buff1) == 0

    def add(self, d):
        self.buff1 += d
        self.buff2 = self.buff1

    def restore(self):
        self.buff1 = self.buff2

    def peek(self):
        if len(self.buff1) < 1:
            raise Underrun()
        return ord(self.buff1[0])

    def unpack_raw(self, l):
        if len(self.buff1) < l:
            raise Underrun()
        d, self.buff1 = self.buff1[:l], self.buff1[l:]
        return d

    def unpack(self, ty):
        s = struct.unpack(">"+ty, self.unpack_raw(struct.calcsize(ty)))
        return s[0] if len(ty) == 1 else s

    def unpack_string(self):
        l = self.unpack("h")
        return self.unpack_raw(l*2).decode("utf-16be")

    def unpack_array(self):
        l = self.unpack("h")
        return self.unpack_raw(l)

    @classmethod
    def pack(cls, ty, *data):
        return struct.pack(">"+ty, *data)

    @classmethod
    def pack_string(cls, data):
        return cls.pack("h", len(data)) + data.encode("utf-16be")

    @classmethod
    def pack_array(cls, data):
        return cls.pack("h", len(data)) + data


class AuthProtocol(protocol.Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr
        self.buff = Buffer()

        self.server_id    = Crypto.make_server_id()
        self.verify_token = Crypto.make_verify_token()

    def dataReceived(self, data):
        self.buff.add(data)
        try:
            ident = self.buff.unpack("B")
            if ident == 0xFE:
                self.kick(u"\u0000".join((
                    u"\u00a71",
                    PING_PROTOCOL,
                    PING_VERSION,
                    PING_MOTD,
                    "0", "0"
                )))
            elif ident == 0x02:
                self.buff.unpack("B") #protocol version
                self.username = self.buff.unpack_string()
                self.buff.unpack_string() #host
                self.buff.unpack("I") #port

                self.transport.write(
                    "\xFD" +
                    Buffer.pack_string(self.server_id) +
                    Buffer.pack_array(self.factory.public_key) +
                    Buffer.pack_array(self.verify_token)
                )
            elif ident == 0xFC:
                shared_secret = Crypto.decrypt(self.factory.keypair, self.buff.unpack_array())
                verify_token  = Crypto.decrypt(self.factory.keypair, self.buff.unpack_array())

                if verify_token != self.verify_token:
                    return self.kick("E00 verify token incorrect")

                digest = Crypto.make_digest(self.server_id, shared_secret, self.factory.public_key)

                def auth_ok(data):
                    if data != "YES":
                        return self.kick("E01 name authentication failed")

                    def api_ok(data):
                        return self.kick(u"\u00a7lThanks! \u00a7rPlease continue your registration at"
                                         u"\u00a7l\u00a7e http://junction.at/register/{user}/".format(user=self.username))

                    def api_err(e):
                        print "API AUTH: {0}".format(e.getErrorMessage())
                        return self.kick("E02 API failed")

                    d = getPage(API_ADDR.format(
                        user = self.username,
                        addr = self.addr.host,
                    ), cookies=self.factory.cookies, timeout=API_TIMEOUT)
                    d.addCallbacks(api_ok, api_err)

                def auth_err(e):
                    print "MC.NET: {0}".format(e.getErrorMessage())
                    return self.kick("E03 minecraft.net is down")

                d = getPage(AUTH_ADDR.format(
                    user = self.username,
                    serverId = digest
                ), timeout=AUTH_TIMEOUT)
                d.addCallbacks(auth_ok, auth_err)
            else:
                self.kick("E04 protocol error")
        except Underrun:
            self.buff.restore()

    def kick(self, message):
        self.transport.write("\xFF" + Buffer.pack_string(message))


class AuthFactory(protocol.Factory):
    noisy = False
    def __init__(self):
        self.keypair = Crypto.make_keypair()
        self.public_key = Crypto.export_public_key(self.keypair)
        self.cookies = {}

    def startFactory(self):
        def login_ok(d):
            print "API LOGIN: Failed."
        def login_err(e):
            if e.check(PageRedirect) and e.value.status == "303":
                print "API LOGIN: OK"
            else:
                print "API LOGIN: {0}".format(e.getErrorMessage())

        args = json.dumps({"username": API_USERNAME, "password": API_PASSWORD})
        d = getPage(
            API_LOGIN,
            method="POST",
            cookies=self.cookies,
            followRedirect=False,
            postdata=args,
            headers={'Content-Type': 'application/json'})
        d.addCallbacks(login_ok, login_err)

    def buildProtocol(self, addr):
        return AuthProtocol(self, addr)


application = service.Application("Minecraft Auth Server")
service = internet.TCPServer(SERVER_PORT, AuthFactory(), interface=SERVER_HOST)
service.setServiceParent(application)