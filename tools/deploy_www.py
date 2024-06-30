from tools.services import publish_service


def main():
    publish_service.update_www()
    publish_service.deploy_www()


if __name__ == '__main__':
    main()
