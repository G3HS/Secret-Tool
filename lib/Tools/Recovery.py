class Recovery:
    def __init__(rom):
        rom.seek(0xAC)
        self.gamecode = rom.read(4)