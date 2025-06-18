"""Switchmap-NG poll module.

Updates the database with device SNMP data.

"""

# Standard libraries
from multiprocessing import Pool
from collections import namedtuple
from pprint import pprint
import os

# Import app libraries
from switchmap import API_POLLER_POST_URI
from switchmap.poller.snmp import poller
from switchmap.poller.update import device as udevice
from switchmap.poller.configuration import ConfigPoller
from switchmap.core import log
from switchmap.core import rest
from switchmap.core import files
from switchmap import AGENT_POLLER

_META = namedtuple("_META", "zone hostname config")


def devices(multiprocessing=False):
    """Poll all devices for data using subprocesses and create YAML files.

    Args:
        multiprocessing: Run multiprocessing when True

    Returns:
        None

    """
    # Initialize key variables
    arguments = []

    # Get configuration
    config = ConfigPoller()

    # Get the number of threads to use in the pool
    pool_size = config.agent_subprocesses()

    # Create a list of polling objects
    zones = sorted(config.zones())

    print(f"🚀 [POLL.PY] Starting polling for {len(zones)} zones")

    # Create a list of arguments
    for zone in zones:
        print(f"📍 [POLL.PY] Zone: {zone.name} has {len(zone.hostnames)} hosts")
        arguments.extend(
            _META(zone=zone.name, hostname=_, config=config)
            for _ in zone.hostnames
        )

    print(f"🎯 [POLL.PY] Total devices to poll: {len(arguments)}")

    # Process the data
    if bool(multiprocessing) is False:
        for argument in arguments:
            device(argument)

    else:
        # Create a multiprocessing pool of sub process resources
        with Pool(processes=pool_size) as pool:
            # Create sub processes from the pool
            pool.map(device, arguments)


def device(poll, post=True):
    """Poll single device for data and create YAML files.

    Args:
        poll: _META object
        post: Post the data if True, else just print it.

    Returns:
        None

    """
    # Initialize key variables
    hostname = poll.hostname
    zone = poll.zone
    config = poll.config

    print(f"🔥 [POLL.PY] Starting poll for {hostname} in zone {zone}")

    # Do nothing if the skip file exists
    skip_file = files.skip_file(AGENT_POLLER, config)
    if os.path.isfile(skip_file) is True:
        log_message = """\
Skip file {} found. Aborting poll for {} in zone "{}". A daemon \
shutdown request was probably requested""".format(
            skip_file, hostname, zone
        )
        log.log2debug(1041, log_message)
        return

    # Poll data for obviously valid hostnames (eg. "None" used in installation)
    if bool(hostname) is True:
        if isinstance(hostname, str) is True:
            if hostname.lower() != "none":
                print(f"📡 [POLL.PY] Creating SNMP poller for {hostname}")
                poll = poller.Poll(hostname)
                
                print(f"⚡ [POLL.PY] Querying SNMP data from {hostname}")
                snmp_data = poll.query()

                # Process if we get valid data
                if bool(snmp_data) and isinstance(snmp_data, dict):
                    print(f"✅ [POLL.PY] Got SNMP data from {hostname}")
                    print(f"📊 [POLL.PY] Data keys: {list(snmp_data.keys())}")
                    
                    # Show system info if available
                    if 'system' in snmp_data and snmp_data['system']:
                        if 'SNMPv2-MIB' in snmp_data['system']:
                            sys_data = snmp_data['system']['SNMPv2-MIB']
                            print(f"🖥️  [POLL.PY] System Info for {hostname}:")
                            print(f"    - Name: {sys_data.get('sysName', {}).get(0, 'N/A')}")
                            print(f"    - Description: {sys_data.get('sysDescr', {}).get(0, 'N/A')[:50]}...")
                            print(f"    - Uptime: {sys_data.get('sysUpTime', {}).get(0, 'N/A')}")

                    # Process device data
                    print(f"🔧 [POLL.PY] Processing device data for {hostname}")
                    _device = udevice.Device(snmp_data)
                    data = _device.process()
                    data["misc"]["zone"] = zone

                    print(f"📤 [POLL.PY] Processed data keys: {list(data.keys())}")

                    if bool(post) is True:
                        print(f"🚀 [POLL.PY] Posting data to API for {hostname}")
                        # Update the database tables with polled data
                        rest.post(API_POLLER_POST_URI, data, config)
                        print(f"✅ [POLL.PY] Successfully posted data for {hostname}")
                    else:
                        print(f"📋 [POLL.PY] Printing data for {hostname} (no post)")
                        pprint(data)
                else:
                    print(f"❌ [POLL.PY] No valid data received from {hostname}")
                    log_message = """\
Device {} returns no data. Check your connectivity and/or SNMP configuration\
""".format(
                        hostname
                    )
                    log.log2debug(1025, log_message)


def cli_device(hostname):
    """Poll single device for data and create YAML files.

    Args:
        hostname: Host to poll

    Returns:
        None

    """
    # Initialize key variables
    arguments = []

    # Get configuration
    config = ConfigPoller()

    # Create a list of polling objects
    zones = sorted(config.zones())

    # Create a list of arguments
    for zone in zones:
        for next_hostname in zone.hostnames:
            if next_hostname == hostname:
                arguments.append(
                    _META(zone=zone.name, hostname=hostname, config=config)
                )

    if bool(arguments) is True:
        for argument in arguments:
            device(argument, post=False)
    else:
        log_message = "No hostname {} found in configuration".format(hostname)
        log.log2see(1036, log_message)
