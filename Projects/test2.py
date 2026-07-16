"""
A small cloud computing + Python example using OpenStack.

Basics:
- Cloud computing gives you remote compute, storage, and networking resources on demand.
- IaaS (Infrastructure as a Service) is a common cloud model where you request VMs, networks, disks, and manage them.
- OpenStack is an open source IaaS platform that exposes APIs for managing cloud resources.
- Python is a great language for cloud automation because it is easy to read and many cloud SDKs are available.

This script:
1. explains the basics briefly
2. connects to an OpenStack cloud using the OpenStack SDK
3. lists available resources
4. optionally creates a small server if you pass --create-server

Before running:
- install the SDK: pip install openstacksdk
- configure OpenStack credentials with OS_ environment variables or clouds.yaml
  (for example OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME, OS_USER_DOMAIN_NAME)
"""

from __future__ import annotations
import openstack
import argparse
import os
import sys

import openstack
from openstack.connection import Connection


def explain_cloud_python() -> None:
    print("\n=== Cloud computing basics ===")
    print("Cloud computing lets you use compute, storage, and networking through APIs.")
    print("You do not manage the physical servers; the cloud provider runs the datacenter.")
    print("Common services: virtual machines, block storage, load balancers, object storage.")
    print("OpenStack is one open source platform for building IaaS clouds.")
    print("\n=== Python basics for automation ===")
    print("Python is a scripting language often used to automate cloud tasks.")
    print("A Python script can import an SDK, authenticate, then create/list resources.")
    print("Python supports modules, functions, and command-line arguments.")
    print()


def get_connection() -> Connection:
    cloud_name = os.environ.get("OS_CLOUD") or os.environ.get("OPENSTACK_CLOUD") or "default"
    print(f"Connecting to OpenStack cloud: {cloud_name}")
    return openstack.connect(cloud=cloud_name)


def list_resources(conn: Connection) -> None:
    print("\n=== Listing OpenStack resources ===")

    print("\nCompute servers:")
    for server in conn.compute.servers():
        print(f" - {server.name} [{server.status}] id={server.id}")

    print("\nAvailable images:")
    for image in conn.compute.images():
        print(f" - {image.name} id={image.id}")

    print("\nFlavors:")
    for flavor in conn.compute.flavors():
        print(f" - {flavor.name} vcpus={flavor.vcpus} ram={flavor.ram}MB")

    print("\nNetworks:")
    for network in conn.network.networks():
        print(f" - {network.name} id={network.id} status={network.status}")


def create_server(conn: Connection, name: str) -> None:
    print(f"\n=== Creating server '{name}' ===")

    image = conn.compute.find_image("cirros") or conn.compute.find_image("Ubuntu 22.04")
    if image is None:
        raise RuntimeError("Could not find a suitable image named 'cirros' or 'Ubuntu 22.04'.")

    flavor = conn.compute.find_flavor("m1.tiny") or conn.compute.find_flavor("small")
    if flavor is None:
        raise RuntimeError("Could not find a suitable flavor named 'm1.tiny' or 'small'.")

    network = conn.network.find_network("public") or next(conn.network.networks(), None)
    if network is None:
        raise RuntimeError("Could not find any available network.")

    print(f"Using image={image.name} flavor={flavor.name} network={network.name}")

    server = conn.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
    )

    server = conn.compute.wait_for_server(server)
    print(f"Server created: {server.name} id={server.id} status={server.status}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenStack cloud demo script")
    parser.add_argument("--create-server", action="store_true", help="Create a test server")
    parser.add_argument("--server-name", default="demo-python-server", help="Name for the created server")
    return parser.parse_args()


def main() -> None:
    explain_cloud_python()
    args = parse_args()

    conn = get_connection()
    list_resources(conn)

    if args.create_server:
        try:
            create_server(conn, args.server_name)
        except Exception as exc:
            print(f"Error creating server: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
