from stem import CircStatus

def print_tor_circuits(controller):
    """Print built Tor circuits using Stem.
    From https://stem.torproject.org/tutorials/examples/list_circuits.html
    """
    for circ in sorted(controller.get_circuits()):
        if circ.status != CircStatus.BUILT:
            continue

        print("\nCircuit %s (%s)" % (circ.id, circ.purpose))

        for i, entry in enumerate(circ.path):
            div = '+' if (i == len(circ.path) - 1) else '|'
            fingerprint, nickname = entry

            desc = controller.get_network_status(fingerprint, None)
            address = desc.address if desc else 'unknown'

            print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))