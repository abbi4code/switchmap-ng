"""Module to aggregate query results."""

import time
from collections import defaultdict

from . import iana_enterprise
from . import get_queries


class Query:
    """Class interacts with IfMIB devices.

    Args:
        None

    Returns:
        None

    """

    def __init__(self, snmp_object):
        """Instantiate the class.

        Args:
            snmp_object: SNMP Interact class object from snmp_manager.py

        Returns:
            None

        """
        # Define query object
        self.snmp_object = snmp_object
        print(f"🔧 [SNMP_INFO.PY] Created Query object for {snmp_object.hostname()}")

    def everything(self):
        """Get all information from device.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize key variables
        data = {}
        hostname = self.snmp_object.hostname()

        print(f"🌟 [SNMP_INFO.PY] Starting everything() for {hostname}")

        # Append data
        print(f"📋 [SNMP_INFO.PY] Gathering misc data for {hostname}")
        data["misc"] = self.misc()
        
        print(f"📊 [SNMP_INFO.PY] Gathering layer1 data for {hostname}")
        data["layer1"] = self.layer1()
        
        print(f"🔗 [SNMP_INFO.PY] Gathering layer2 data for {hostname}")
        data["layer2"] = self.layer2()
        
        print(f"🌐 [SNMP_INFO.PY] Gathering layer3 data for {hostname}")
        data["layer3"] = self.layer3()
        
        print(f"🖥️  [SNMP_INFO.PY] Gathering system data for {hostname}")
        data["system"] = self.system()

        print(f"✅ [SNMP_INFO.PY] Completed everything() for {hostname}")
        print(f"📊 [SNMP_INFO.PY] Final data structure: {list(data.keys())}")

        # Return
        return data

    def misc(self):
        """Provide miscellaneous information about device and the poll.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize data
        data = defaultdict(lambda: defaultdict(dict))
        data["timestamp"] = int(time.time())
        data["host"] = self.snmp_object.hostname()

        # Get vendor information
        sysobjectid = self.snmp_object.sysobjectid()
        vendor = iana_enterprise.Query(sysobjectid=sysobjectid)
        data["IANAEnterpriseNumber"] = vendor.enterprise()

        print(f"📝 [SNMP_INFO.PY] Misc data: host={data['host']}, vendor={data['IANAEnterpriseNumber']}")

        # Return
        return data

    def system(self):
        """Get all system information from device.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize data
        data = defaultdict(lambda: defaultdict(dict))
        processed = False
        hostname = self.snmp_object.hostname()

        print(f"🖥️  [SNMP_INFO.PY] Starting system() queries for {hostname}")

        # Get system information from SNMPv2-MIB, ENTITY-MIB, IF-MIB
        # Instantiate a query object for each system query
        system_queries = get_queries("system")
        print(f"🔍 [SNMP_INFO.PY] Found {len(system_queries)} system MIB classes for {hostname}")

        for i, Query in enumerate(system_queries):
            item = Query(self.snmp_object)
            mib_name = item.__class__.__name__
            print(f"  🧪 [SNMP_INFO.PY] Testing MIB {i+1}/{len(system_queries)}: {mib_name} for {hostname}")
            
            if item.supported():
                print(f"  ✅ [SNMP_INFO.PY] MIB {mib_name} is SUPPORTED for {hostname}")
                processed = True
                old_keys = list(data.keys())
                data = _add_system(item, data)
                new_keys = list(data.keys())
                added_keys = set(new_keys) - set(old_keys)
                print(f"  📊 [SNMP_INFO.PY] MIB {mib_name} added: {list(added_keys)}")
            else:
                print(f"  ❌ [SNMP_INFO.PY] MIB {mib_name} is NOT supported for {hostname}")

        # Return
        if processed is True:
            print(f"✅ [SNMP_INFO.PY] System data collected successfully for {hostname}")
            print(f"📊 [SNMP_INFO.PY] System MIBs found: {list(data.keys())}")
            return data
        else:
            print(f"❌ [SNMP_INFO.PY] No system MIBs supported for {hostname}")
            return None

    def layer1(self):
        """Get all layer1 information from device.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize key values
        data = defaultdict(lambda: defaultdict(dict))
        processed = False
        hostname = self.snmp_object.hostname()

        print(f"📊 [SNMP_INFO.PY] Starting layer1() queries for {hostname}")

        # Get information layer1 queries
        layer1_queries = get_queries("layer1")
        print(f"🔍 [SNMP_INFO.PY] Found {len(layer1_queries)} layer1 MIB classes for {hostname}")

        for i, Query in enumerate(layer1_queries):
            item = Query(self.snmp_object)
            mib_name = item.__class__.__name__
            print(f"  🧪 [SNMP_INFO.PY] Testing layer1 MIB {i+1}/{len(layer1_queries)}: {mib_name} for {hostname}")
            
            if item.supported():
                print(f"  ✅ [SNMP_INFO.PY] Layer1 MIB {mib_name} is SUPPORTED for {hostname}")
                processed = True
                data = _add_layer1(item, data)
            else:
                print(f"  ❌ [SNMP_INFO.PY] Layer1 MIB {mib_name} is NOT supported for {hostname}")

        # Return
        if processed is True:
            print(f"✅ [SNMP_INFO.PY] Layer1 data collected successfully for {hostname}")
            return data
        else:
            print(f"❌ [SNMP_INFO.PY] No layer1 MIBs supported for {hostname}")
            return None

    def layer2(self):
        """Get all layer2 information from device.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize key variables
        data = defaultdict(lambda: defaultdict(dict))
        processed = False
        hostname = self.snmp_object.hostname()

        print(f"🔗 [SNMP_INFO.PY] Starting layer2() queries for {hostname}")

        layer2_queries = get_queries("layer2")
        print(f"🔍 [SNMP_INFO.PY] Found {len(layer2_queries)} layer2 MIB classes for {hostname}")

        for i, Query in enumerate(layer2_queries):
            item = Query(self.snmp_object)
            mib_name = item.__class__.__name__
            print(f"  🧪 [SNMP_INFO.PY] Testing layer2 MIB {i+1}/{len(layer2_queries)}: {mib_name} for {hostname}")
            
            if item.supported():
                print(f"  ✅ [SNMP_INFO.PY] Layer2 MIB {mib_name} is SUPPORTED for {hostname}")
                processed = True
                data = _add_layer2(item, data)
            else:
                print(f"  ❌ [SNMP_INFO.PY] Layer2 MIB {mib_name} is NOT supported for {hostname}")

        # Return
        if processed is True:
            print(f"✅ [SNMP_INFO.PY] Layer2 data collected successfully for {hostname}")
            return data
        else:
            print(f"❌ [SNMP_INFO.PY] No layer2 MIBs supported for {hostname}")
            return None

    def layer3(self):
        """Get all layer3 information from device.

        Args:
            None

        Returns:
            data: Aggregated data

        """
        # Initialize key variables
        data = defaultdict(lambda: defaultdict(dict))
        processed = False

        for item in [
            Query(self.snmp_object) for Query in get_queries("layer3")
        ]:
            if item.supported():
                processed = True
                data = _add_layer3(item, data)

        # Return
        if processed is True:
            return data
        else:
            return None


def _add_data(source, target):
    """Add data from source to target dict. Both dicts must have two keys.

    Args:
        source: Source dict
        target: Target dict

    Returns:
        target: Aggregated data

    """
    # Process data
    for primary in source.keys():
        for secondary, value in source[primary].items():
            target[primary][secondary] = value

        # Return
    return target


def _add_layer1(query, original_data):
    """Add data from successful layer1 MIB query to original data provided.

    Args:
        query: MIB query object
        original_data: Two keyed dict of data

    Returns:
        new_data: Aggregated data

    """
    # Process query
    result = query.layer1()
    new_data = _add_data(result, original_data)

    # Return
    return new_data


def _add_layer2(query, original_data):
    """Add data from successful layer2 MIB query to original data provided.

    Args:
        query: MIB query object
        original_data: Two keyed dict of data

    Returns:
        new_data: Aggregated data

    """
    # Process query
    result = query.layer2()
    new_data = _add_data(result, original_data)

    # Return
    return new_data


def _add_layer3(query, original_data):
    """Add data from successful layer3 MIB query to original data provided.

    Args:
        query: MIB query object
        original_data: Two keyed dict of data

    Returns:
        new_data: Aggregated data

    """
    # Process query
    result = query.layer3()
    new_data = _add_data(result, original_data)

    # Return
    return new_data


def _add_system(query, data):
    """Add data from successful system MIB query to original data provided.

    Args:
        query: MIB query object
        data: Three keyed dict of data

    Returns:
        data: Aggregated data

    """
    # Process query
    mib_name = query.__class__.__name__
    print(f"  🔧 [SNMP_INFO.PY] Processing system data from {mib_name}")
    
    result = query.system()

    if result:
        print(f"  📊 [SNMP_INFO.PY] {mib_name} returned system data with keys: {list(result.keys())}")
        
        # Add tag
        for primary in result.keys():
            for secondary in result[primary].keys():
                for tertiary, value in result[primary][secondary].items():
                    data[primary][secondary][tertiary] = value
                    
        print(f"  ✅ [SNMP_INFO.PY] Successfully added {mib_name} system data")
    else:
        print(f"  ❌ [SNMP_INFO.PY] {mib_name} returned no system data")

    # Return
    return data
