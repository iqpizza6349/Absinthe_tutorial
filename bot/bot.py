import sc2
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Unit
from sc2.position import Point2
from sc2.player import Bot, Computer


class CompetitiveBot(BotAI):
    NAME: str = "CompetitiveBot"
    """This bot's name"""
    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        # Initalize inherited class
        sc2.BotAI.__init__(self)


    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gateway()
        await self.build_gas()

        pass

    async def build_workers(self):
        nexus = self.townhalls.ready.random # 완성된 넥서스 중 하나를 가져옴
        if (
                self.can_afford(UnitTypeId.PROBE)
                and nexus.is_idle
                and self.workers.amount < self.townhalls.amount * 22
        ):
            nexus.train(UnitTypeId.PROBE)

    async def build_pylons(self):
        nexus = self.townhalls.ready.random # 완성된 넥서스 중 하나를 가져옴
        pos = nexus.position.towards(self.enemy_start_locations[0], 10)

        if (
                self.supply_left < 3
                and self.already_pending(UnitTypeId.PYLON) == 0
                and self.can_afford(UnitTypeId.PYLON)
        ):
            await self.build(UnitTypeId.PYLON, near=pos)

    async def build_gateway(self):
        if (
                self.structures(UnitTypeId.PYLON).ready
                and self.can_afford(UnitTypeId.GATEWAY)
                and not self.structures(UnitTypeId.GATEWAY)
        ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_gas(self):
        if self.structures(UnitTypeId.GATEWAY):
            for nexus in self.townhalls.ready:
                vespenes = self.vespene_geyser.closer_than(15, nexus)
                for gas in vespenes:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    worker = self.select_build_worker(gas.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, gas):
                        worker.build(UnitTypeId.ASSIMILATOR, gas)
                        worker.stop(queue=True)

    def on_end(self, result):
        print("Game ended.")
        # Do things here after the game ends
