import argparse
import yaml


parser = argparse.ArgumentParser(description='Generating a dynamic docker-compose file.')
parser.add_argument('-c', '--count_instance', type=int, required=True, help='Number of instances to run')

args = parser.parse_args()
count_instance = args.count_instance

symbol = 'fact'
coin = 'factorn'
services = {}

for i in range(1, count_instance + 1):
    coind_service_name = f'{symbol}-{i}'
    umbrel_service_name = f'umbrel-bitcoin-{i}'

    # Настройки для btcw сервиса
    services[coind_service_name] = {
        'container_name': f'{symbol}_{i}',
        'command': '-port=30030 -rpcport=8332 -rpcbind=0.0.0.0 -rpcallowip=0.0.0.0/0 -rpcauth=umbrel:5071d8b3ba93e53e414446ff9f1b7d7b$$375e9731abd2cd2c2c44d2327ec19f4f2644256fdeaf4fc5229bf98b778aafec -txindex=1 -server=1',
        'volumes': [f'/{symbol}/node_{i}:/{symbol}/.{coin}'],
        'ports': [f"{30030+i}:30030", f"{8330+i}:8332"],  # Изменим порт на уникальный для каждого экземпляра
        'image': 'grinvest/fact:4.23.69',
        'restart': 'unless-stopped',
        'stop_grace_period': '15m30s',
        'networks': [f'{symbol}_default']
    }

    # Настройки для umbrel-bitcoin сервиса
    services[umbrel_service_name] = {
        'container_name': f'crypto_umbrel_{symbol}_{i}',
        'build': '.',
        'depends_on': [coind_service_name],
        'command': ['npm', 'start'],
        'restart': 'on-failure',
        'deploy': {
            'resources': {
                'limits': {
                    'cpus': '1',
                    'memory': '512m'
                }
            }
        },
        'ports': [f"{3000+i}:3005"],
        'volumes': [
            f'/{symbol}/umbrel_data/app_{i}:/data',
            f'/{symbol}/node_{i}:/bitcoin/.bitcoin'
        ],
        'environment': {
            'PORT': "3005",
            'BITCOIN_HOST': coind_service_name,
            'BITCOIN_P2P_PORT': "30030",
            'BITCOIN_RPC_PORT': '8332',
            'BITCOIN_DEFAULT_NETWORK': 'main',
            'RPC_USER': 'umbrel',
            'RPC_PASSWORD': 'moneyprintergobrrr',
            'DEVICE_DOMAIN_NAME': 'test.local',
            'BITCOIND_IP': f'{symbol}_{i}',
            'JSON_STORE_FILE': f"/data/{coin}-config.json",
            'UMBREL_BITCOIN_CONF_FILE': f"/bitcoin/.bitcoin/umbrel-{coin}.conf",
            'BITCOIN_CONF_FILE': f"/bitcoin/.bitcoin/{coin}.conf",
            'BITCOIN_INITIALIZE_WITH_CLEARNET_OVER_TOR': 1,
        },
        'networks': [f'{symbol}_default']
    }

docker_compose = {
    'version': '3.8',
    'services': services,
    'networks': {
        f'{symbol}_default': {
            'external': True,
            'name': 'crypto_default'
        }
    }
}

with open('docker-compose.yml', 'w') as file:
    yaml.dump(docker_compose, file, default_flow_style=False)
