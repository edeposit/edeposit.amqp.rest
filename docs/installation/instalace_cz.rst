Proces instalace (cz)
=====================

Nainstalovat balík přes PIP:

    sudo pip install edeposit.amqp.rest

Dál je potřeba vytvořit konfigurák ``~/edeposit/rest.json``, či ``/etc/edeposit/rest.json``, s cestama k ZEO konfiguracím a nastavením webserveru::

    {
        "WEB_ADDR": "localhost",
        "WEB_PORT": 8080,
        "WEB_SERVER": "paste",

        "WEB_CACHE": "/var/edeposit/rest_cache",

        "ZEO_CLIENT_CONF_FILE": "/etc/edeposit/zconf/zeo_client.conf",
        "ZEO_SERVER_CONF_FILE": "/etc/edeposit/zconf/zeo.conf"
    }

Dále vytvořit složku pro databázi, třeba v ``/var/edeposit/zodb/``::

    mkdir /var/edeposit/zodb

A také nastavit správná oprávnění přístupu.

Pokud neexistují ZEO konfiguráky v ``zconf/``, lze je automatizovaně vytvořit použitím scriptu ``zeo_connector_gen_defaults.py``, který se nainstaloval společně s tímto balíkem::

    mkdir /etc/edeposit/zconf
    cd /etc/edeposit/zconf/
    chmod 755 /etc/edeposit/zconf/

    zeo_connector_gen_defaults.py /var/edeposit/zodb

Dále pak vytvořit složku, kam budou ukládány dočasně cacheované soubory, které uživatel nahrál::

    mkdir /var/edeposit/rest_cache

A opět nastavit správná oprávnění přístupu.

Poté ještě přidat do cronu script ``edeposit_rest_cached_uploader.py``, který se bude starat o load balancing komunikace edeposit <-> rest::

    */5 * * * * edeposit_rest_cached_uploader.py

Nyní už je možné server provozovat. K tomu slouží dva scripty:

- ``edeposit_rest_runzeo.py`` pro databázový proces. Nemusí běžet, pokud už běží jiný proces a je správně nakonfigurována databáze v ``zeo_client.conf``.

- ``edeposit_rest_webserver.py`` pro proces webserveru zajišťujícího REST API.

Oba dva doporučuji přidat do `supervisord`_.

.. _supervisord: http://supervisord.org/
