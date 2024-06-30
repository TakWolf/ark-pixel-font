
class GitDeployConfig:
    url: str
    remote_name: str
    branch_name: str

    def __init__(self, url: str, remote_name: str, branch_name: str):
        self.url = url
        self.remote_name = remote_name
        self.branch_name = branch_name
