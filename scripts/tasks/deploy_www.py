from scripts import configs
from scripts.services import publish_service


def main():
    publish_service.update_www()
    publish_service.deploy_www(configs.git_deploy_config)


if __name__ == '__main__':
    main()
