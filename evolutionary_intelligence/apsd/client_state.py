class ClientState():
    """
    Client side for web handling

    :param
        clientId (string) - unique client id
        radius (int)      - sensors' radius
        clusterCnt (int)  - cluster count
    """

    def __init__(self, clientId, radius, clusterCnt):
        self.id = clientId
        self.radius = radius
        self.clusterCnt = clusterCnt
        self.clusters = []
        self.controller = None