import innertube

client = innertube.InnerTube("WEB", use_po_token=True, pot_provider_url="[::1]:4416")

data = client.player("jNQXAC9IVRw")

print(data["playabilityStatus"])
