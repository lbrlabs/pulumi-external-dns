import pulumi
import pulumi_kubernetes as k8s
import pulumi_kubernetes.helm.v3 as helm
from pulumi_kubernetes.core.v1 import Namespace

config = pulumi.Config()

# Get the outputs from the current stack
# We assume here we always want the reference from the stack we're in
stack = pulumi.get_stack()
cluster_project = config.require("cluster_project")
sr = "jaxxstorm/{}/{}".format(cluster_project, stack)
stack_ref = pulumi.StackReference(sr)
# Get the kubeconfig from the stack
kubeconfig = stack_ref.get_output("kubeConfig")

# Get configuration options
namespace = config.require("namespace")
api_token = config.require_secret("api_token")

# Set up the provider
provider = k8s.Provider(
    "home.lbrlabs",
    kubeconfig=kubeconfig
)

# Create the namespace
ns = Namespace("ns", metadata={
    "name": namespace,
    },
    opts=pulumi.ResourceOptions(provider=provider),

)

# Install the helm chart
helm.Chart("external-dns", helm.ChartOpts(
    chart="external-dns",
    namespace=ns.metadata["name"],
    values={
        "provider": "cloudflare",
        "cloudflare": {
            "apiToken": api_token,
            "proxied": False,
        },
        "sources": [ "service", "ingress" ],
        "logFormat": "json",
        "txtOwnerId": "home.lbrlabs",
    },
    fetch_opts=helm.FetchOpts(
        repo="https://charts.bitnami.com/bitnami"
    ),
    ), pulumi.ResourceOptions(provider=provider) 
)



