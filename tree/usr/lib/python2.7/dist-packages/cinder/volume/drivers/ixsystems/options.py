# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2016 iXsystems

"""Contains configuration options for iXsystems Cinder drivers."""

from oslo_config import cfg

ixsystems_connection_opts = [
    cfg.StrOpt('ixsystems_server_hostname',
               default=None,
               help='Host name for the storage controller'),
    cfg.IntOpt('ixsystems_server_port',
               default=3000,
               help='Port number for the storage controller'),
    cfg.IntOpt('ixsystems_server_iscsi_port',
               default=3260,
               help='ISCSI port number for the storage controller'),
    cfg.StrOpt('ixsystems_api_version',
               default='v1.0',
               help='FREENAS API version'),
    cfg.StrOpt('ixsystems_volume_backend_name',
               default='iXsystems_FREENAS_Storage',
               help='Backend Storage Controller Name'), 
    cfg.StrOpt('ixsystems_vendor_name',
               default='iXsystem',
               help='vendor name on Storage controller'),
    cfg.StrOpt('ixsystems_storage_protocol',
               default='iscsi',
               help='storage protocol on Storage controller'), ]

ixsystems_transport_opts = [
    cfg.StrOpt('ixsystems_transport_type',
               default='http',
               help='Transport type protocol'), ]

ixsystems_basicauth_opts = [
    cfg.StrOpt('ixsystems_login',
               default='root',
               help='User name for the storage controller'),
    cfg.StrOpt('ixsystems_password',
               default='ixsystems',
               help='Password for the storage controller',
               secret=True), ]

ixsystems_provisioning_opts = [
    cfg.StrOpt('ixsystems_datastore_pool',
               default=None,
               help='Storage controller datastore pool name'),
    cfg.IntOpt('ixsystems_reserved_percentage',
               default=0,
               help='Reserved space on Storage controller'),
    cfg.StrOpt('ixsystems_iqn_prefix',
               default='iqn.2005-10.org.freenas.ctl',
               help='Storage controller iSCSI Qualified Name prefix'), 
    cfg.StrOpt('ixsystems_portal_id',
               default=1,
               help='Storage controller iSCSI portal ID'),
    cfg.StrOpt('ixsystems_initiator_id',
               default=1,
               help='Storage controller iSCSI Initiator ID'), ]
