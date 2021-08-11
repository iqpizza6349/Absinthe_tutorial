import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random


class CompetitiveBot(sc2.BotAI):
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
        await self.build_core()
        await self.build_four_gates()
        await self.train_stalkers()
        await self.chrono()
        await self.warpgate_research()
        await self.attack()
        await self.warp_stalkers()
        await self.mirco_stalkers()
        await self.expand()

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

    async def build_core(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylons = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if (
                            self.can_afford(UnitTypeId.CYBERNETICSCORE)
                            and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                    ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylons)

    async def train_stalkers(self):
        for gate in self.structures(UnitTypeId.GATEWAY).ready:
            if (
                self.can_afford(UnitTypeId.STALKER)
                and gate.is_idle
            ):
                gate.train(UnitTypeId.STALKER)

    async def build_four_gates(self):
        if (
            self.structures(UnitTypeId.PYLON).ready
            and self.can_afford(UnitTypeId.GATEWAY)
            and self.structures(UnitTypeId.GATEWAY).amount < 4
        ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def chrono(self):
        if self.structures(UnitTypeId.PYLON):
            nexus = self.townhalls.ready.random
            if (
                self.structures(UnitTypeId.PYLON).amount > 0
            ):
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

    async def warpgate_research(self):
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.can_afford(AbilityId.RESEARCH_WARPGATE)
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
        ):
            cybercore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            cybercore.research(UpgradeId.WARPGATERESEARCH)

    async def attack(self):
        stalker_count = self.units(UnitTypeId.STALKER).amount
        stalkers = self.units(UnitTypeId.STALKER).ready.idle

        if stalker_count > 3:
            for s in stalkers:
                s.attack(self.find_target())

    async def warp_stalkers(self):
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            if AbilityId.WARPGATETRAIN_STALKER in abilities and self.can_afford(UnitTypeId.STALKER):
                placement = pylon.position.random_on_distance(3)
                warpgate.warp_in(UnitTypeId.STALKER, placement)

    async def mirco_stalkers(self):
        stalkers = self.units(UnitTypeId.STALKER)
        enemy_location = self.enemy_start_locations[0]

        if self.structures(UnitTypeId.PYLON):
            pylon = self.structures(UnitTypeId.PYLON).closest_to(enemy_location)

            for stalker in stalkers:
                if stalker.weapon_cooldown == 0:
                    stalker.attack(enemy_location)
                elif stalker.weapon_cooldown < 0:
                    stalker.move(pylon)
                else:
                    stalker.move(pylon)

    async def expand(self):
        if self.units(UnitTypeId.NEXUS).amount < 3 and self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()

    def find_target(self):
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]

    def on_end(self, result):
        print("Game ended.")
        # Do things here after the game ends
