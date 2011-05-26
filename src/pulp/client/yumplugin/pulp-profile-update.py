#
# Copyright (c) 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#
import os
from yum.plugins import TYPE_CORE
from pulp.client.credentials import Consumer as ConsumerBundle
from pulp.client.api.consumer import ConsumerAPI
from pulp.client.package_profile import get_profile
from pulp.client.server import PulpServer, set_active_server
from pulp.client.config import Config

requires_api_version = '2.5'
plugin_type = (TYPE_CORE,)

def get_consumer():
    """
    Get consumer bundle
    """
    bundle = ConsumerBundle()
    return bundle

def pulpserver():
    """
    Pulp server configuration
    """
    cfg = Config()
    bundle = get_consumer()
    pulp = PulpServer(cfg.server.host, timeout=10)
    pulp.set_ssl_credentials(bundle.crtpath(), bundle.keypath())
    set_active_server(pulp)

def update_consumer_profile(cid):
    """
    Updates consumer package profile information
    @param cid: Consumer ID
    @type cid: str
    """
    pulpserver()
    capi = ConsumerAPI()
    pkginfo = get_profile("rpm").collect()
    capi.profile(cid, pkginfo)

def posttrans_hook(conduit):
    """
    Update Package Profile for available consumer.
    """
    if os.getuid() != 0:
        conduit.info(2, 'Not root, Pulp consumer profile not updated')
        return
    if hasattr(conduit, 'registerPackageName'):
        conduit.registerPackageName("pulp-client")
    try:
        bundle = get_consumer()
        cid = bundle.getid()
        if not cid:
            conduit.info(2, "Consumer Id could not be found. Cannot update consumer profile.")
            return
        update_consumer_profile(cid)
        conduit.info(2, "Profile updated successfully for consumer [%s]" % cid)
    except Exception, e:
        conduit.error(2, str(e))

