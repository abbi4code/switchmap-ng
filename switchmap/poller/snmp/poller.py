"""SNMP Poller module."""

# Switchmap imports
from switchmap.poller.configuration import ConfigPoller
from switchmap.poller import POLLING_OPTIONS, SNMP, POLL
from . import snmp_info
from . import snmp_manager
from switchmap.core import log


class Poll:
    """Switchmap-NG agent that gathers data.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        populate:
        post:
    """

    def __init__(self, hostname):
        """Initialize the class.

        Args:
            hostname: Hostname to poll

        Returns:
            None

        """
        # *  we take the hostname (like from each device we already sepearted then we just callling )
        # Initialize key variables
        self._server_config = ConfigPoller()
        self._hostname = hostname
        self._snmp_object = None

        print(f"🔧 [POLLER.PY] Initializing SNMP poller for {hostname}")

        # Get snmp configuration information from Switchmap-NG
        validate = snmp_manager.Validate(
            POLLING_OPTIONS(
                hostname=hostname,
                authorizations=self._server_config.snmp_auth(),
            )
        )
        #! here this authorization have all the creds 
        authorization = validate.credentials()

        print(f"🔑 [POLLER.PY] Got SNMP credentials for {hostname}: {bool(authorization)}")

        # Create an SNMP object for querying
        if _do_poll(authorization) is True:
            print(f"✅ [POLLER.PY] Creating SNMP interaction object for {hostname}")
            self._snmp_object = snmp_manager.Interact(
                POLL(
                    hostname=hostname,
                    authorization=authorization,
                )
            )
            print(f"chekcinggggggggggg ❤️, {self._snmp_object}")
        else:
            print(f"❌ [POLLER.PY] Cannot create SNMP object for {hostname}")
            log_message = (
                "Uncontactable or disabled host {}, or no valid SNMP "
                "credentials found for it.".format(self._hostname)
            )
            log.log2info(1081, log_message)

    def query(self):
        """Query all remote hosts for data.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        _data = None

        print(f"📡 [POLLER.PY] Starting query for {self._hostname}")

        # Only query if wise
        if bool(self._snmp_object) is False:
            print(f"❌ [POLLER.PY] No valid SNMP object for {self._hostname}")
            return _data

        # Get data
        log_message = """\
Querying topology data from host {}.""".format(
            self._hostname
        )
        log.log2info(1078, log_message)

        print(f"🔍 [POLLER.PY] Creating snmp_info.Query object for {self._hostname}")
        # Return the data polled from the device
        status = snmp_info.Query(self._snmp_object)
        
        print(f"🚀 [POLLER.PY] Calling everything() to gather all MIB data for {self._hostname}")
        _data = status.everything()
        
        if _data:
            print(f"✅ [POLLER.PY] Query successful for {self._hostname}")
            print(f"📊 [POLLER.PY] Collected data categories: {list(_data.keys())}")
        else:
            print(f"❌ [POLLER.PY] Query failed for {self._hostname}")
        
        return _data


def _do_poll(authorization):
    """Determine whether doing a poll is valid.

    Args:
        authorization: SNMP object

    Returns:
        poll: True if a poll should be done

    """
    # Initialize key variables
    poll = False

    if bool(authorization) is True:
        if isinstance(authorization, SNMP) is True:
            poll = bool(authorization.enabled)

    # Return
    return poll
