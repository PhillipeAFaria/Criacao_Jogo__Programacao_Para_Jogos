import os, unittest, copy, random
from unittest.mock import Mock
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
from svz.app import Game
from svz.developer_lab import DeveloperLab
import pygame

class DeveloperLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=Game(integration_preview=True)
        while not cls.app.assets.complete: cls.app.assets.load_next()
    @classmethod
    def tearDownClass(cls): pygame.quit()
    def test_all_units_spawn_and_animate_in_all_scenarios(self):
        app=self.app
        for region in ('city','desert','beach'):
            lab=DeveloperLab(app);lab.region=region;lab.reset()
            for team in ('soldiers','enemies'):
                lab.team=team
                for i,entry in enumerate(lab.entries()):
                    with self.subTest(region=region,unit=entry[0]):
                        lab.reset();lab.index=i;lab.spawn(1,4)
                        lab.animate('move');lab.update(.1)
                        app.developer_lab=lab;app.scene='developer';app.draw()
            lab.close()
    def test_campaign_and_session_untouched(self):
        app=self.app
        campaign=copy.deepcopy(app.save); pending=app.pending_snapshot; battle=app.battle
        state=random.getstate()
        save=Mock();record=Mock()
        original_save=app.session_store.save;original_record=app.score_store.record
        app.session_store.save=save;app.score_store.record=record
        try:
            lab=DeveloperLab(app);app.developer_lab=lab;app.scene='developer'
            lab.spawn(1,2);lab.team='enemies';lab.spawn(1,6)
            lab.paused=False
            for _ in range(180): lab.update(1/60)
            app.checkpoint();app.draw();lab.close()
            save.assert_not_called();record.assert_not_called()
            self.assertEqual(app.save,campaign)
            self.assertIs(app.pending_snapshot,pending)
            self.assertIs(app.battle,battle)
            self.assertEqual(random.getstate(),state)
        finally:
            app.session_store.save=original_save;app.score_store.record=original_record
    def test_catalog_selection_and_unit_controls(self):
        lab=DeveloperLab(self.app)
        lab.action('catalog');lab.action('page_next')
        self.assertLess(lab.index,len(lab.entries()))
        lab.action('pick:0');self.assertFalse(lab.catalog)
        lab.spawn(1,2);unit=lab.selected
        lab.action('damage');self.assertLess(unit.hp,unit.max_hp)
        lab.action('heal');self.assertEqual(unit.hp,unit.max_hp)
        self.assertEqual(unit.ammo,unit.max_ammo)
        lab.action('remove');self.assertFalse(lab.battle.defenders)
        lab.spawn(1,2);lab.action('death');self.assertIsNone(lab.selected)
        lab.action('clear');self.assertTrue(lab.paused)
        self.assertFalse(lab.battle.defenders)
        lab.close()

    def test_step_is_independent_of_speed_and_escape_closes_catalog(self):
        lab=DeveloperLab(self.app);lab.spawn(1,2);lab.animate('idle')
        anim=lab.selected.visual_animation
        anim.update=Mock()
        lab.speed=2;lab.action('step')
        anim.update.assert_called_once_with(1/60)
        self.assertTrue(lab.paused)
        lab.catalog=True;lab.key(pygame.K_ESCAPE)
        self.assertFalse(lab.catalog)
        lab.close()
    def test_demolisher_requires_soldier_within_two_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('bruto')
        lab.spawn(1,6);enemy=lab.selected;b=lab.battle
        for distance,row,hp in ((2*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
            soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
            b.effects.clear();b.enemy_special(enemy)
            self.assertFalse(b.effects)
            self.assertNotEqual(enemy.motion.state,'skill')
        soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+2*CELL_W
        b.enemy_special(enemy)
        self.assertEqual(enemy.motion.state,'skill')
        self.assertFalse(any(e.kind=='ground_slam' for e in b.effects))
        self.assertEqual(soldier.hp,soldier.max_hp)
        delay=enemy.slam_windup
        b.update_enemies(delay-.01)
        self.assertFalse(any(e.kind=='ground_slam' for e in b.effects))
        b.update_enemies(.011)
        self.assertTrue(any(e.kind=='ground_slam' for e in b.effects))
        self.assertLess(soldier.hp,soldier.max_hp)
        lab.close()
    def test_scientist_launches_only_on_release_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('cientista_helix')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        enemy.x=soldier.x+2*CELL_W
        b.enemy_special(enemy)
        self.assertFalse(b.projectiles)
        delay=enemy.acid_windup
        self.assertGreater(delay,0)
        x=enemy.x
        b.update_enemies(delay-.01)
        self.assertFalse(b.projectiles)
        self.assertEqual(enemy.x,x)
        b.update_enemies(.011)
        self.assertEqual(len(b.projectiles),1)
        self.assertEqual(b.projectiles[0].kind,'acid')
        b.update_enemies(.02)
        self.assertEqual(len(b.projectiles),1)
        lab.close()

    def test_commander_fires_only_on_aim_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('policial')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        enemy.x=soldier.x+2*CELL_W
        b.enemy_special(enemy)
        self.assertFalse(b.projectiles)
        delay=enemy.gun_windup
        self.assertGreater(delay,0)
        x=enemy.x
        b.update_enemies(delay-.01)
        self.assertFalse(b.projectiles)
        self.assertEqual(enemy.x,x)
        b.update_enemies(.011)
        self.assertEqual(len(b.projectiles),1)
        self.assertEqual(b.projectiles[0].kind,'enemy_bullet')
        b.update_enemies(.02)
        self.assertEqual(len(b.projectiles),1)
        lab.close()

    def test_scientist_requires_live_target_within_two_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('cientista_helix')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            for distance,row,hp in ((2*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.enemy_special(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.acid_windup,0)
                b.release_enemy_acid(enemy)
                self.assertFalse(b.projectiles)
            soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+2*CELL_W
            b.enemy_special(enemy)
            self.assertEqual(enemy.motion.state,'skill')
            self.assertGreater(enemy.acid_windup,0)
            # Revalidate when the release pose arrives, not only at windup.
            enemy.x+=1
            b.update_enemies(enemy.acid_windup+.001)
            self.assertFalse(b.projectiles)
        finally:
            lab.close()


    def test_commander_requires_live_target_within_two_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('policial')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            for distance,row,hp in ((2*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.enemy_special(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.gun_windup,0)
                b.release_enemy_gun(enemy)
                self.assertFalse(b.projectiles)
            soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+2*CELL_W
            b.enemy_special(enemy)
            self.assertEqual(enemy.motion.state,'skill')
            self.assertGreater(enemy.gun_windup,0)
            # Revalidate when the release pose arrives, not only at windup.
            enemy.x+=1
            b.update_enemies(enemy.gun_windup+.001)
            self.assertFalse(b.projectiles)
        finally:
            lab.close()


    def test_commander_and_quarantine_death_have_no_explosion(self):
        for key in ('policial', 'divisor'):
            with self.subTest(unit=key):
                lab=DeveloperLab(self.app)
                try:
                    lab.team='enemies'
                    lab.index=[k for k,n in lab.entries()].index(key)
                    lab.spawn(1,5);enemy=lab.selected;b=lab.battle
                    b.explosion=Mock()
                    b.kill_enemy(enemy)
                    b.explosion.assert_not_called()
                    self.assertNotIn(enemy,b.enemies)
                    self.assertEqual(len(b.fallen),1)
                    self.assertGreater(b.score,0)
                finally:
                    lab.close()

    def test_director_entrance_stuns_without_special_attack(self):
        from svz.content import BOSSES
        self.assertEqual(BOSSES['bruto_demolidor']['hp'],1250)
        self.assertEqual(BOSSES['bruto_demolidor']['speed'],7.5)
        lab=DeveloperLab(self.app)
        try:
            lab.spawn(1,2);soldier=lab.selected
            lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('bruto_demolidor')
            lab.spawn(1,5);enemy=lab.selected;b=lab.battle
            b.effects.clear();soldier.stun=0
            b.boss_entrance(enemy)
            self.assertEqual(soldier.stun,3.0)
            self.assertNotEqual(enemy.motion.state,'skill')
            self.assertFalse(b.effects)
            soldier.stun=0
            b.boss_skill(enemy)
            self.assertEqual(soldier.stun,0)
            self.assertNotEqual(enemy.motion.state,'skill')
            self.assertFalse(b.effects)
        finally: lab.close()

    def test_isotopic_burst_matches_aim_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('comandante_mortos')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        enemy.x=soldier.x+2*CELL_W
        b.enemy_special(enemy)
        self.assertFalse(b.projectiles)
        delay=enemy.gun_windup
        self.assertGreater(delay,0)
        x=enemy.x
        b.update_enemies(delay-.01)
        self.assertFalse(b.projectiles)
        self.assertEqual(enemy.x,x)
        b.update_enemies(.011)
        self.assertEqual(len(b.projectiles),2)
        self.assertEqual(b.projectiles[0].kind,'enemy_bullet')
        b.update_enemies(.02)
        self.assertEqual(len(b.projectiles),2)
        lab.close()

    def test_isotopic_has_no_red_command_circles(self):
        lab=DeveloperLab(self.app)
        try:
            lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('comandante_mortos')
            lab.spawn(1,5);enemy=lab.selected;b=lab.battle
            b.effects.clear()
            b.boss_entrance(enemy)
            self.assertFalse(any(e.kind=='command_aura' for e in b.effects))
            b.release_isotopic_burst(enemy)
            self.assertFalse(any(e.kind=='command_aura' for e in b.effects))
        finally: lab.close()

    def test_isotopic_only_fires_within_four_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('comandante_mortos')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            b.boss_entrance(enemy)
            self.assertNotEqual(enemy.motion.state,'skill')
            for distance,row,hp in ((4*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.boss_skill(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.gun_windup,0)
                b.release_isotopic_burst(enemy)
                self.assertFalse(b.projectiles)
            soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+4*CELL_W
            b.boss_skill(enemy)
            self.assertEqual(enemy.motion.state,'skill')
            b.update_enemies(enemy.gun_windup+.001)
            self.assertEqual(len(b.projectiles),2)
            b.projectiles.clear()
            b.boss_skill(enemy)
            enemy.x+=1
            b.update_enemies(enemy.gun_windup+.001)
            self.assertFalse(b.projectiles)
        finally: lab.close()

    def test_corrosive_acid_matches_release_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('cuspidor_alfa')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        enemy.x=soldier.x+2*CELL_W
        b.enemy_special(enemy)
        self.assertFalse(b.projectiles)
        delay=enemy.acid_windup
        self.assertGreater(delay,0)
        x=enemy.x
        b.update_enemies(delay-.01)
        self.assertFalse(b.projectiles)
        self.assertEqual(enemy.x,x)
        b.update_enemies(.011)
        self.assertEqual(len(b.projectiles),1)
        self.assertEqual(b.projectiles[0].kind,'acid')
        b.update_enemies(.02)
        self.assertEqual(len(b.projectiles),1)
        lab.close()

    def test_corrosive_only_spits_within_six_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('cuspidor_alfa')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            b.boss_entrance(enemy)
            self.assertNotEqual(enemy.motion.state,'skill')
            for distance,row,hp in ((6*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.boss_skill(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.acid_windup,0)
                b.release_enemy_acid(enemy)
                self.assertFalse(b.projectiles)
            soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+6*CELL_W
            b.boss_skill(enemy)
            self.assertEqual(enemy.motion.state,'skill')
            b.update_enemies(enemy.acid_windup+.001)
            self.assertEqual(len(b.projectiles),1)
            b.projectiles.clear()
            b.boss_skill(enemy)
            enemy.x+=1
            b.update_enemies(enemy.acid_windup+.001)
            self.assertFalse(b.projectiles)
        finally: lab.close()

    def test_catalog_is_grouped_by_map_and_team(self):
        from svz.content import REGION_ROSTERS, REGION_ENEMIES, REGION_SUBBOSSES, REGION_BOSSES
        lab=DeveloperLab(self.app)
        try:
            for region in ('city','desert','beach'):
                lab.index=999
                lab.action(region)
                self.assertEqual(lab.index,0)
                self.assertEqual(lab.battle.region,region)
                lab.team='soldiers'
                self.assertEqual(lab.entries(),list(REGION_ROSTERS[region]))
                lab.action('team')
                self.assertEqual([k for k,n in lab.entries()],list(dict.fromkeys(REGION_ENEMIES[region]+REGION_SUBBOSSES[region]+REGION_BOSSES[region])))
                lab.catalog=True
                lab.action('page_next')
                self.assertLess(lab.index,len(lab.entries()))
        finally: lab.close()

    def test_khepra_bites_only_in_contact_and_at_contact_pose(self):
        lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('desperto_khepra')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            enemy.x=soldier.x+150;enemy.attack_timer=0
            b.update_enemies(.01)
            self.assertEqual(enemy.attack_windup,0)
            self.assertNotEqual(enemy.motion.state,'attack')
            b.enemy_special(enemy)
            self.assertNotEqual(enemy.motion.state,'skill')
            enemy.x=soldier.x+58
            b.update_enemies(.01)
            delay=enemy.attack_windup
            self.assertGreater(delay,0)
            hp=soldier.hp
            b.update_enemies(delay-.001)
            self.assertEqual(soldier.hp,hp)
            b.update_enemies(.002)
            self.assertLess(soldier.hp,hp)
            enemy.attack_timer=0
            b.update_enemies(.01)
            hp=soldier.hp;enemy.x=soldier.x+150
            b.update_enemies(enemy.attack_windup+.001)
            self.assertEqual(soldier.hp,hp)
        finally: lab.close()

    def test_archer_only_fires_within_three_cells(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('arqueiro_necropole')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            self.assertNotEqual(enemy.motion.state,'skill')
            for distance,row,hp in ((3*CELL_W+1,1,100),(CELL_W,2,100),(-CELL_W,1,100),(CELL_W,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.enemy_special(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.gun_windup,0)
                b.release_enemy_gun(enemy)
                self.assertFalse(b.projectiles)
            soldier.row=1;soldier.hp=soldier.max_hp;enemy.x=soldier.x+3*CELL_W
            b.enemy_special(enemy)
            self.assertEqual(enemy.motion.state,'skill')
            b.update_enemies(enemy.gun_windup+.001)
            self.assertEqual(len(b.projectiles),1)
            b.projectiles.clear()
            b.enemy_special(enemy)
            enemy.x+=1
            b.update_enemies(enemy.gun_windup+.001)
            self.assertFalse(b.projectiles)
        finally: lab.close()

    def test_beetle_host_attack_matches_contact(self):
        lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('hospedeiro_escaravelhos')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            enemy.x=soldier.x+150;enemy.attack_timer=0
            b.update_enemies(.01)
            self.assertEqual(enemy.attack_windup,0)
            self.assertNotEqual(enemy.motion.state,'attack')
            b.enemy_special(enemy)
            self.assertNotEqual(enemy.motion.state,'skill')
            enemy.x=soldier.x+58
            b.update_enemies(.01)
            delay=enemy.attack_windup
            self.assertGreater(delay,0)
            hp=soldier.hp
            b.update_enemies(delay-.001)
            self.assertEqual(soldier.hp,hp)
            b.update_enemies(.002)
            self.assertLess(soldier.hp,hp)
            enemy.attack_timer=0
            b.update_enemies(.01)
            hp=soldier.hp;enemy.x=soldier.x+150
            b.update_enemies(enemy.attack_windup+.001)
            self.assertEqual(soldier.hp,hp)
        finally: lab.close()

    def test_beetle_death_effect_requires_nearby_live_target(self):
        from svz.config import CELL_W
        for distance,row,hp,expected in ((CELL_W,1,100,True),(2*CELL_W,1,100,False),(CELL_W,2,100,False),(CELL_W,1,0,False)):
            lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
            lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('hospedeiro_escaravelhos')
            lab.spawn(1,5);enemy=lab.selected;b=lab.battle
            try:
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.explosion=Mock();b.kill_enemy(enemy)
                self.assertEqual(b.explosion.called,expected)
                if expected: self.assertLess(soldier.hp,hp)
                else: self.assertEqual(soldier.hp,hp)
            finally: lab.close()

    def test_looter_steals_only_at_contact_pose_and_range(self):
        lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('saqueador_canopico')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            b.supplies=100
            for distance,row,hp in ((150,1,100),(58,2,100),(-58,1,100),(58,1,0)):
                soldier.row=row;soldier.hp=hp;enemy.x=soldier.x+distance
                b.enemy_special(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.steal_windup,0)
            soldier.row=1;soldier.hp=100;enemy.x=soldier.x+58
            b.enemy_special(enemy);delay=enemy.steal_windup
            self.assertGreater(delay,0)
            b.update_enemies(delay-.001);self.assertEqual(b.supplies,100)
            b.update_enemies(.002);self.assertEqual(b.supplies,82)
            self.assertEqual(enemy.stolen,18)
            b.enemy_special(enemy);enemy.x=soldier.x+150
            b.update_enemies(enemy.steal_windup+.001)
            self.assertEqual(b.supplies,82)
        finally: lab.close()

    def test_blade_has_only_ballistic_resistance(self):
        lab=DeveloperLab(self.app);lab.action('desert');lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('parasita')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            enemy.x=soldier.x+58
            b.enemy_special(enemy)
            self.assertNotEqual(enemy.motion.state,'skill')
            b.resolve_blade_skill(enemy)
            self.assertEqual(soldier.stun,0)
            self.assertEqual(enemy.blade_windup,0)
            hp=enemy.hp;b.take_enemy_damage(enemy,20,source=soldier)
            self.assertAlmostEqual(hp-enemy.hp,4)
            hp=enemy.hp;b.take_enemy_damage(enemy,20,'explosion')
            self.assertAlmostEqual(hp-enemy.hp,20)
            self.assertFalse(enemy.data['counter_keys'])
        finally: lab.close()

    def test_priest_heal_requires_wounded_ally_and_release_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.action('desert');lab.team='enemies'
        lab.index=[k for k,n in lab.entries()].index('desperto_khepra');lab.spawn(1,3);ally=lab.selected
        lab.index=[k for k,n in lab.entries()].index('curandeiro');lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        try:
            for distance,row,hp in ((3*CELL_W,1,100),(CELL_W,2,100),(CELL_W,1,0),(CELL_W,1,ally.max_hp)):
                ally.x=enemy.x-distance;ally.row=row;ally.hp=hp
                b.enemy_special(enemy)
                self.assertNotEqual(enemy.motion.state,'skill')
                self.assertEqual(enemy.heal_windup,0)
            ally.x=enemy.x-CELL_W;ally.row=1;ally.hp=100
            b.enemy_special(enemy);delay=enemy.heal_windup
            self.assertGreater(delay,0)
            b.update_enemies(delay-.001);self.assertEqual(ally.hp,100)
            b.update_enemies(.002);self.assertEqual(ally.hp,142)
            b.enemy_special(enemy);ally.x=enemy.x-3*CELL_W
            b.update_enemies(enemy.heal_windup+.001);self.assertEqual(ally.hp,142)
        finally: lab.close()

    def test_priest_death_has_no_visual_effect(self):
        lab=DeveloperLab(self.app);lab.action('desert');lab.team='enemies'
        lab.index=[k for k,n in lab.entries()].index('curandeiro');lab.spawn(1,5)
        enemy=lab.selected;b=lab.battle
        try:
            b.explosion=Mock();score=b.score;supplies=b.supplies
            b.kill_enemy(enemy)
            b.explosion.assert_not_called()
            self.assertFalse(b.fallen)
            self.assertNotIn(enemy,b.enemies)
            self.assertGreater(b.score,score)
            self.assertGreater(b.supplies,supplies)
        finally: lab.close()

    def test_healing_effect_is_not_clipped_by_lane(self):
        from svz.motion import VisualEffect
        from svz.board import lane_bounds
        lab=DeveloperLab(self.app);lab.action('desert')
        original=self.app.screen
        try:
            top,bottom=lane_bounds('desert',1)
            for kind in ('heal_pulse','heal_receive'):
                effect=VisualEffect(kind,600,top, (154,239,134),1,scale=.76)
                effect.elapsed=.5
                expected=pygame.Surface(original.get_size(),pygame.SRCALPHA)
                actual=pygame.Surface(original.get_size(),pygame.SRCALPHA)
                self.app.screen=expected
                self.app.renderer.draw_linked_skill_effect(effect,600,top,.5)
                self.app.screen=actual;lab.battle.effects=[effect]
                self.app.renderer.draw_visual_effects(lab.battle)
                self.assertEqual(pygame.image.tobytes(actual,'RGBA'),pygame.image.tobytes(expected,'RGBA'),kind)
                self.assertEqual(actual.get_clip(),actual.get_rect())
        finally:
            self.app.screen=original;lab.close()

    def test_damage_preserves_animation_and_flashes_only_silhouette(self):
        lab=DeveloperLab(self.app);lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.spawn(1,5);enemy=lab.selected
        original=self.app.screen
        try:
            for unit,damage in ((soldier,lambda:lab.battle.damage_defender(soldier,1)),(enemy,lambda:lab.battle.take_enemy_damage(enemy,1))):
                unit.motion.trigger('attack',.8)
                unit.visual_animation.play('bite' if unit is enemy else 'shoot',restart=True)
                unit.visual_animation.update(.05)
                state=unit.visual_animation.state;frame=unit.visual_animation.frame_index
                damage()
                self.assertEqual(unit.motion.state,'attack')
                self.assertEqual(unit.visual_animation.state,state)
                self.assertEqual(unit.visual_animation.frame_index,frame)
                self.assertGreater(unit.motion.hit_flash,0)
                sprite=unit.visual_animation.frame
                original_pixels=pygame.image.tobytes(sprite,'RGBA')
                flashed=self.app.renderer.damage_flash_sprite(sprite,unit.motion.hit_flash)
                self.assertTrue((pygame.surfarray.array_alpha(sprite)==pygame.surfarray.array_alpha(flashed)).all())
                self.assertEqual(pygame.image.tobytes(sprite,'RGBA'),original_pixels)
                self.assertNotEqual(pygame.image.tobytes(flashed,'RGBA'),original_pixels)
                probe=pygame.Surface((5,5),pygame.SRCALPHA)
                probe.set_at((2,2),(40,60,80,128))
                tinted=self.app.renderer.damage_flash_sprite(probe,.13)
                self.assertEqual(tinted.get_at((0,0)).a,0)
                self.assertEqual(tinted.get_at((2,2)).a,128)
                self.assertGreater(tinted.get_at((2,2)).r,40)
        finally:
            self.app.screen=original;lab.close()

    def test_executor_range_and_synchronized_release(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region='desert';lab.reset()
        lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('mutante')
        lab.spawn(1,5);enemy=lab.selected;b=lab.battle
        enemy.x=soldier.x+CELL_W*4+1
        b.enemy_special(enemy)
        self.assertEqual(enemy.slam_windup,0)
        self.assertEqual(enemy.gun_windup,0)
        enemy.x=soldier.x+CELL_W*3
        b.enemy_special(enemy)
        self.assertEqual(enemy.slam_windup,0)
        self.assertEqual(enemy.gun_windup,0)
        self.assertNotEqual(enemy.motion.state,"skill")
        enemy.x=soldier.x+CELL_W
        hp=soldier.hp;b.enemy_special(enemy)
        delay=enemy.slam_windup
        self.assertGreater(delay,0)
        self.assertAlmostEqual(delay,enemy.gun_windup)
        self.assertEqual(soldier.hp,hp)
        self.assertFalse(b.projectiles)
        b.update_enemies(delay-.001)
        self.assertEqual(soldier.hp,hp)
        b.update_enemies(.002)
        self.assertLess(soldier.hp,hp)
        self.assertEqual(len(b.projectiles),1)
        self.assertTrue(any(e.kind=='ground_slam' for e in b.effects))
        b.effects.clear();b.projectiles.clear()
        enemy.x=soldier.x+CELL_W*5
        hp=soldier.hp;b.resolve_stomp(enemy);b.release_enemy_gun(enemy)
        self.assertEqual(soldier.hp,hp)
        self.assertFalse(b.effects);self.assertFalse(b.projectiles)
        lab.close()

    def test_anubis_only_strikes_targets_in_range_at_contact(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region='desert';lab.reset()
        lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('mutante_ruinas')
        lab.spawn(1,6);enemy=lab.selected;b=lab.battle
        b.effects.clear();enemy.x=soldier.x+CELL_W*3
        b.boss_skill(enemy)
        self.assertEqual(enemy.slam_windup,0)
        self.assertNotEqual(enemy.motion.state,'skill')
        enemy.x=soldier.x+CELL_W
        hp=soldier.hp;b.boss_skill(enemy);delay=enemy.slam_windup
        self.assertGreater(delay,0);self.assertEqual(soldier.hp,hp)
        b.update_enemies(delay-.001);self.assertEqual(soldier.hp,hp)
        b.update_enemies(.002);self.assertLess(soldier.hp,hp)
        self.assertGreaterEqual(soldier.stun,1.0)
        self.assertTrue(any(e.kind=='ground_slam' for e in b.effects))
        b.effects.clear();hp=soldier.hp;enemy.x=soldier.x+CELL_W*3
        b.release_anubis_slam(enemy)
        self.assertEqual(soldier.hp,hp);self.assertFalse(b.effects)
        lab.close()

    def test_necropolis_command_requires_target_and_releases_once(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region='desert';lab.reset()
        lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('necromante')
        lab.spawn(1,6);enemy=lab.selected;b=lab.battle
        b.effects.clear();enemy.x=soldier.x+CELL_W*4+1
        b.boss_skill(enemy)
        self.assertEqual(enemy.command_windup,0)
        self.assertNotEqual(enemy.motion.state,'skill')
        enemy.x=soldier.x+CELL_W*2
        b.boss_skill(enemy);delay=enemy.command_windup;n=len(b.enemies)
        self.assertGreater(delay,0)
        b.update_enemies(delay-.001);self.assertEqual(len(b.enemies),n)
        b.update_enemies(.002);self.assertEqual(len(b.enemies),n+1)
        self.assertIsNotNone(b.enemies[-1].visual_animation)
        b.update_enemies(.01);self.assertEqual(len(b.enemies),n+1)
        ally=b.enemies[-1];ally.hp-=50;before=ally.hp
        enemy.motion.event_left=0;enemy.motion.state='move'
        b.boss_skill(enemy);delay=enemy.command_windup
        self.assertEqual(ally.hp,before)
        b.update_enemies(delay+.001)
        self.assertEqual(ally.hp,before)
        enemy.necropolis_heal_timer=.01
        b.update_necropolis_combat(enemy,.011)
        self.assertEqual(ally.hp,before+28)
        n+=1
        b.effects.clear();enemy.x=soldier.x+CELL_W*4
        b.release_necropolis_command(enemy)
        self.assertEqual(len(b.enemies),n+1);self.assertFalse(b.effects)
        lab.close()

    def test_necropolis_rifle_three_cells_and_five_second_heal(self):
        from svz.config import CELL_W
        from svz.entities import Enemy
        from svz.content import ENEMIES
        lab=DeveloperLab(self.app);lab.region='desert';lab.reset();lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('necromante');lab.spawn(1,6)
        enemy=lab.selected;b=lab.battle;enemy.motion.event_left=0
        enemy.x=soldier.x+CELL_W*3+1;b.update_necropolis_combat(enemy,0)
        self.assertFalse(b.projectiles)
        enemy.x=soldier.x+CELL_W*3;b.update_necropolis_combat(enemy,0)
        self.assertEqual(len(b.projectiles),1)
        ally=Enemy('necromante_minion',1,ENEMIES['necromante_minion'],'desert',1,x=enemy.x+30)
        b.enemies.append(ally);ally.hp-=60;hp=ally.hp
        enemy.necropolis_heal_timer=5;b.update_necropolis_combat(enemy,4.99)
        self.assertEqual(ally.hp,hp)
        self.assertEqual(len(b.projectiles),1)
        b.update_necropolis_combat(enemy,.011);self.assertEqual(ally.hp,hp+28)
        self.assertEqual(len(b.projectiles),2)
        self.assertEqual(enemy.necropolis_shot_timer,5.0)
        lab.close()

    def test_colossus_waits_for_target_and_release_pose(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region='desert';lab.reset();lab.spawn(1,2);soldier=lab.selected
        lab.team='enemies';lab.index=[k for k,n in lab.entries()].index('colosso_mutante');lab.spawn(1,6)
        enemy=lab.selected;b=lab.battle;enemy.x=soldier.x+CELL_W*4+1
        b.boss_skill(enemy)
        self.assertEqual(enemy.rock_windup,0);self.assertNotEqual(enemy.motion.state,'skill')
        enemy.x=soldier.x+CELL_W*3;b.boss_skill(enemy);delay=enemy.rock_windup
        self.assertGreater(delay,0);self.assertFalse(b.projectiles)
        x=enemy.x;b.update_enemies(delay-.001)
        self.assertFalse(b.projectiles);self.assertEqual(enemy.x,x)
        b.update_enemies(.002);self.assertEqual(len(b.projectiles),1)
        self.assertEqual(b.projectiles[0].kind,'boulder')
        b.projectiles.clear();enemy.x=soldier.x+CELL_W*5
        b.release_colossus_rock(enemy);self.assertFalse(b.projectiles)
        soldier.hp=0;enemy.x=soldier.x+CELL_W
        self.assertFalse(b.colossus_targets(enemy))
        lab.close()

    def test_surfer_dash_requires_target_and_waits_for_pose(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(0, 2)
        soldier = lab.selected
        lab.team = "enemies"
        lab.index = [k for k, n in lab.entries()].index("surfista")
        lab.spawn(0, 6)
        enemy = lab.selected
        enemy.row = soldier.row
        enemy.motion.loop("walk")
        battle = lab.battle
        enemy.x = soldier.x + CELL_W * 4
        battle.enemy_special(enemy)
        self.assertEqual(enemy.dash_windup, 0)
        self.assertNotEqual(enemy.motion.state, "skill")
        enemy.x = soldier.x + CELL_W * 2
        battle.enemy_special(enemy)
        self.assertGreater(enemy.dash_windup, 0)
        self.assertEqual(enemy.rage, 0)
        battle.release_surfer_dash(enemy)
        self.assertGreater(enemy.rage, 0)
        enemy.rage = 0
        soldier.hp = 0
        battle.release_surfer_dash(enemy)
        self.assertEqual(enemy.rage, 0)
        lab.close()


    def test_surfer_dash_moves_visibly_without_crossing_soldier(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(0, 2)
        soldier = lab.selected
        lab.team = "enemies"
        lab.index = [k for k, n in lab.entries()].index("surfista")
        lab.spawn(0, 6)
        enemy = lab.selected
        enemy.row = soldier.row
        enemy.motion.loop("walk")
        enemy.x = soldier.x + CELL_W * 2
        enemy.skill_timer = 0
        start = enemy.x
        lab.battle.update_enemies(.01)
        delay = enemy.dash_windup
        self.assertGreater(delay, 0)
        self.assertEqual(enemy.x, start)
        for _ in range(round(delay * 100) + 25):
            lab.battle.update_enemies(.01)
        self.assertGreater(start - enemy.x, 45)
        self.assertGreaterEqual(enemy.x - soldier.x, 57.5)
        lab.close()

    def test_diver_submersion_torpedo_and_emergence(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("mergulhador")
        lab.spawn(1, 6)
        diver = lab.selected
        diver.row = soldier.row
        diver.x = soldier.x + CELL_W * 2
        diver.motion.loop("walk")
        b = lab.battle
        hp = diver.hp
        self.assertTrue(diver.submerged)
        b.take_enemy_damage(diver, 20, "", soldier)
        b.take_enemy_damage(diver, 20, "explosion", soldier)
        self.assertEqual(diver.hp, hp)
        b.take_enemy_damage(diver, 20, "torpedo", soldier)
        self.assertLess(diver.hp, hp)
        diver.x = soldier.x + CELL_W
        b.update_enemies(.01)
        self.assertFalse(diver.submerged)
        self.assertEqual(diver.motion.state, "skill")
        hp = diver.hp
        b.take_enemy_damage(diver, 20, "", soldier)
        self.assertLess(diver.hp, hp)
        lab.close()

    def test_submerged_diver_is_not_a_bullet_target(self):
        from svz.entities import Defender, Enemy
        from svz.content import DEFENSES, ENEMIES
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        b = lab.battle
        diver = Enemy("mergulhador", 1, dict(ENEMIES["mergulhador"]), "beach", 1)
        other = Enemy("surfista", 1, dict(ENEMIES["surfista"]), "beach", 1)
        for key in ("marinheiro", "atirador_precisao_marinha", "submarino_tatico"):
            d = Defender(key, key, 1, 2, dict(DEFENSES[key]), 0, region="beach")
            b.defenders = [d]
            diver.diver_surfaced = False
            diver.x = d.x + CELL_W * 1.4
            other.x = d.x + CELL_W * 1.6
            b.enemies = [diver]
            if key == "submarino_tatico":
                self.assertIs(b.target_in_range(d), diver)
            else:
                self.assertIsNone(b.target_in_range(d))
                ammo = d.ammo
                b.fire_defender(d, diver)
                self.assertEqual(d.ammo, ammo)
                self.assertFalse(b.projectiles)
                b.enemies.append(other)
                self.assertIs(b.target_in_range(d), other)
            b.enemies = [diver]
            diver.diver_surfaced = True
            self.assertIs(b.target_in_range(d), diver)
        lab.close()

    def test_fisher_net_range_and_release_timing(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("pescador_praga")
        lab.spawn(1, 6)
        enemy = lab.selected
        enemy.row = soldier.row
        enemy.motion.loop("walk")
        b = lab.battle
        enemy.x = soldier.x + CELL_W*4
        b.enemy_special(enemy)
        self.assertEqual(enemy.net_windup, 0)
        enemy.x = soldier.x + CELL_W*2
        b.enemy_special(enemy)
        delay = enemy.net_windup
        self.assertEqual(enemy.skill_timer, 5.0)
        self.assertGreater(delay, 0)
        self.assertEqual(soldier.stun, 0)
        x = enemy.x
        b.update_enemies(delay-.001)
        self.assertEqual(soldier.stun, 0)
        self.assertEqual(enemy.x, x)
        b.update_enemies(.002)
        self.assertEqual(soldier.stun, 2.0)
        self.assertEqual(soldier.attack_timer, 2.0)
        self.assertTrue(any(e.kind == "fisher_net" and e.owner is soldier for e in b.effects))
        soldier.stun = 0
        enemy.x = soldier.x+CELL_W*4
        b.release_fisher_net(enemy)
        self.assertEqual(soldier.stun, 0)
        lab.close()

    def test_puffer_skill_requires_target_and_contact_pose(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("baiacu_mutante")
        lab.spawn(1, 6)
        enemy = lab.selected
        enemy.row = soldier.row
        enemy.motion.loop("walk")
        b = lab.battle
        enemy.x = soldier.x + CELL_W*3
        b.enemy_special(enemy)
        self.assertEqual(enemy.slam_windup, 0)
        enemy.x = soldier.x + CELL_W*1.5
        hp = soldier.hp
        b.enemy_special(enemy)
        delay = enemy.slam_windup
        self.assertGreater(delay, 0)
        b.update_enemies(delay-.001)
        self.assertEqual(soldier.hp, hp)
        b.update_enemies(.002)
        self.assertLess(soldier.hp, hp)
        hp = soldier.hp
        enemy.x = soldier.x+CELL_W*3
        b.resolve_stomp(enemy)
        self.assertEqual(soldier.hp, hp)
        lab.close()

    def test_lifeguard_heals_self_and_nearby_allies_every_five_seconds(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("salva_vidas")
        lab.spawn(1, 6)
        enemy = lab.selected
        lab.spawn(1, 5)
        ally = lab.selected
        lab.spawn(2, 5)
        neighbor = lab.selected
        lab.spawn(1, 1)
        distant = lab.selected
        b = lab.battle
        for unit in (enemy, ally, distant, neighbor):
            unit.hp = unit.max_hp*.5
        enemy.age = 4.99
        b.enemy_special(enemy)
        self.assertAlmostEqual(enemy.hp, enemy.max_hp*.5)
        enemy.age = 5
        b.enemy_special(enemy)
        self.assertAlmostEqual(enemy.hp, enemy.max_hp*.55)
        self.assertAlmostEqual(ally.hp, ally.max_hp*.55)
        self.assertAlmostEqual(distant.hp, distant.max_hp*.5)
        self.assertAlmostEqual(neighbor.hp, neighbor.max_hp*.5)
        self.assertEqual(enemy.skill_timer, 5)
        self.assertEqual(enemy.slam_windup, 0)
        enemy.hp = enemy.max_hp*.99
        ally.hp = 0
        b.enemy_special(enemy)
        self.assertEqual(enemy.hp, enemy.max_hp)
        self.assertEqual(ally.hp, 0)
        lab.close()

    def test_hunter_harpoon_range_impact_dash_and_cancellation(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        soldier.hp = 1000
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("cacador")
        lab.spawn(1, 6)
        enemy = lab.selected
        enemy.motion.loop("walk")
        b = lab.battle
        enemy.x = soldier.x + CELL_W*2+.01
        b.enemy_special(enemy)
        self.assertEqual(enemy.harpoon_phase, "")
        enemy.x = soldier.x + CELL_W*2
        b.enemy_special(enemy)
        self.assertEqual(enemy.harpoon_phase, "windup")
        hp, start = soldier.hp, enemy.x
        b.update_hunter_harpoon(enemy, enemy.harpoon_timer+.001)
        self.assertEqual(enemy.harpoon_phase, "flight")
        self.assertEqual(soldier.hp, hp)
        self.assertEqual(enemy.x, start)
        b.update_hunter_harpoon(enemy, .221)
        self.assertLess(soldier.hp, hp)
        self.assertEqual(enemy.harpoon_phase, "dash")
        b.update_hunter_harpoon(enemy, .1)
        self.assertLess(enemy.x, start)
        b.update_hunter_harpoon(enemy, 1)
        self.assertAlmostEqual(enemy.x, soldier.x+48)
        self.assertEqual(enemy.harpoon_phase, "attached")
        b.update_hunter_harpoon(enemy, .36)
        self.assertEqual(enemy.harpoon_phase, "")
        enemy.motion.event_left = 0
        enemy.x = soldier.x+CELL_W
        b.enemy_special(enemy)
        b.update_hunter_harpoon(enemy, enemy.harpoon_timer+.001)
        hp = soldier.hp
        soldier.row = 2
        self.assertFalse(b.update_hunter_harpoon(enemy, .3))
        self.assertEqual(soldier.hp, hp)
        self.assertEqual(enemy.harpoon_phase, "")
        lab.close()

    def test_hunter_damage_does_not_cancel_harpoon_sequence(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        soldier.hp = 1000
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("cacador")
        lab.spawn(1, 4)
        enemy = lab.selected
        enemy.motion.loop("walk")
        enemy.x = soldier.x + CELL_W*1.8
        b = lab.battle
        b.enemy_special(enemy)
        for phase, dt in (("windup", .01), ("flight", .01), ("dash", .01)):
            self.assertEqual(enemy.harpoon_phase, phase)
            hp = enemy.hp
            b.take_enemy_damage(enemy, 1, source=soldier)
            self.assertLess(enemy.hp, hp)
            self.assertEqual(enemy.stun, 0)
            b.update_enemies(dt)
            self.assertEqual(enemy.harpoon_phase, phase)
            if phase in {"windup", "flight"}:
                b.update_hunter_harpoon(enemy, enemy.harpoon_timer+.001)
        b.update_hunter_harpoon(enemy, 1)
        self.assertEqual(enemy.harpoon_phase, "attached")
        self.assertAlmostEqual(enemy.x, soldier.x+48)
        lab.close()

    def test_hunter_melee_repeats_after_harpoon_and_resumes_on_target_loss(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app)
        lab.region = "beach"
        lab.reset()
        lab.spawn(1, 2)
        soldier = lab.selected
        soldier.hp = 10000
        lab.team = "enemies"
        lab.index = [k for k,n in lab.entries()].index("cacador")
        lab.spawn(1, 4)
        enemy = lab.selected
        enemy.x = soldier.x+CELL_W*1.8
        enemy.motion.loop("walk")
        b = lab.battle
        enemy.skill_timer = 0
        hits = []
        last_hp = soldier.hp
        last_phase = ""
        finished = None
        for frame in range(240):
            b.update_enemies(1/60)
            b.update_production_animations(1/60)
            if last_phase == "attached" and not enemy.harpoon_phase:
                finished = frame/60
                self.assertGreater(enemy.attack_windup, 0)
            last_phase = enemy.harpoon_phase
            if soldier.hp < last_hp:
                hits.append((frame/60, last_hp-soldier.hp))
                last_hp = soldier.hp
        self.assertIsNotNone(finished)
        melee = [h for h in hits if h[0] > finished]
        self.assertGreaterEqual(len(melee), 3)
        self.assertLess(melee[0][0]-finished, .6)
        for before, after in zip(melee, melee[1:]):
            self.assertAlmostEqual(after[0]-before[0], enemy.data["attack"], delta=.035)
            self.assertAlmostEqual(after[1], before[1])
        self.assertEqual(enemy.skill_timer > 0, True)
        x = enemy.x
        soldier.row = 2
        hp = soldier.hp
        for _ in range(30):
            b.update_enemies(1/60)
            b.update_production_animations(1/60)
        self.assertEqual(soldier.hp, hp)
        self.assertLess(enemy.x, x)
        soldier.row = enemy.row
        enemy.x = soldier.x+48
        enemy.attack_timer = 0
        b.update_enemies(.01)
        b.kill_defender(soldier)
        x = enemy.x
        b.update_enemies(.1)
        self.assertLess(enemy.x, x)
        lab.close()

    def test_tide_brute_contact_timing_and_target_escape(self):
        from svz.config import CELL_W
        lab = DeveloperLab(self.app);lab.region = "beach";lab.reset()
        lab.spawn(1,2);victim=lab.selected;victim.hp=10000
        lab.team="enemies";lab.index=[k for k,n in lab.entries()].index("tide_brute");lab.spawn(1,4)
        enemy=lab.selected;b=lab.battle
        enemy.tide_windup=0;enemy.motion.event_left=0;enemy.motion.loop("walk");enemy.skill_timer=999
        enemy.x=victim.x+CELL_W*2
        x=enemy.x;b.update_enemies(.1)
        self.assertLess(enemy.x,x);self.assertEqual(enemy.attack_windup,0)
        enemy.x=victim.x+45;enemy.attack_timer=0;b.update_enemies(.01)
        delay=enemy.attack_windup;hp=victim.hp
        self.assertGreater(delay,0)
        b.update_enemies(delay-.001);self.assertEqual(victim.hp,hp)
        b.update_enemies(.002);self.assertLess(victim.hp,hp)
        hp=victim.hp;b.update_enemies(.02);self.assertEqual(victim.hp,hp)
        enemy.attack_timer=0;b.update_enemies(.01)
        victim.row=2;x=enemy.x;b.update_enemies(.01)
        self.assertEqual(enemy.attack_windup,0);self.assertEqual(victim.hp,hp);self.assertLess(enemy.x,x)
        lab.close()

    def test_tide_brute_skill_delays_effect_and_preserves_rules(self):
        lab=DeveloperLab(self.app);lab.region="beach";lab.reset()
        lab.spawn(1,2);victim=lab.selected;victim.hp=10000
        victim.stats=dict(victim.stats,water_only=True)
        lab.team="enemies";lab.index=[k for k,n in lab.entries()].index("tide_brute");lab.spawn(1,4)
        enemy=lab.selected;b=lab.battle
        enemy.tide_windup=0;enemy.motion.event_left=0;enemy.motion.loop("walk")
        b.effects.clear();hp=victim.hp;b.boss_skill(enemy)
        self.assertAlmostEqual(enemy.skill_timer,14*b.difficulty_data["skill_cooldown"])
        self.assertGreater(enemy.tide_windup,0);self.assertFalse(b.effects)
        delay=enemy.tide_windup;b.update_enemies(delay-.001);self.assertEqual(victim.hp,hp)
        b.update_enemies(.002);self.assertEqual(victim.hp,hp-b.scaled_enemy_damage(enemy,12))
        self.assertTrue(any(e.kind=="tidal_surge" for e in b.effects))
        enemy.motion.event_left=0;b.boss_skill(enemy);hp=victim.hp;victim.row=2
        b.update_enemies(enemy.tide_windup+.001);self.assertEqual(victim.hp,hp)
        enemy.motion.event_left=0;b.boss_skill(enemy);self.assertEqual(enemy.tide_windup,0)
        victim.row=enemy.row;enemy.motion.event_left=0;b.boss_entrance(enemy);hp=victim.hp
        self.assertEqual(enemy.skill_timer,14)
        b.update_enemies(enemy.tide_windup+.001)
        self.assertEqual(victim.hp,hp-b.scaled_enemy_damage(enemy,8))
        lab.close()

    def test_tide_brute_keeps_walking_when_hit_at_increased_speed(self):
        lab=DeveloperLab(self.app);lab.region="beach";lab.reset()
        lab.team="enemies";lab.index=[k for k,n in lab.entries()].index("tide_brute");lab.spawn(1,5)
        enemy=lab.selected;b=lab.battle
        enemy.tide_windup=0;enemy.motion.event_left=0;enemy.motion.loop("walk")
        enemy.skill_timer=999;enemy.age=20;enemy.rage=0
        self.assertAlmostEqual(enemy.data["speed"],6.6)
        b.update_production_animations(.05)
        self.assertAlmostEqual(enemy.visual_animation.playback_rate,1.0)
        first_frame=enemy.visual_animation.frame_index
        for _ in range(5):
            x,hp=enemy.x,enemy.hp
            b.take_enemy_damage(enemy,1)
            self.assertLess(enemy.hp,hp)
            self.assertEqual(enemy.stun,0)
            b.update_enemies(.1);b.update_production_animations(.1)
            self.assertAlmostEqual(x-enemy.x,.66,places=5)
            self.assertEqual(enemy.motion.state,"walk")
        self.assertNotEqual(enemy.visual_animation.frame_index,first_frame)
        enemy.soaked=2
        b.update_production_animations(0)
        self.assertAlmostEqual(enemy.visual_animation.playback_rate,.68)
        enemy.soaked=0
        enemy.stun=1
        x=enemy.x;b.update_enemies(.1)
        self.assertEqual(enemy.x,x)
        lab.close()

    def test_abyss_hunter_contact_skill_and_locomotion(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region="beach";lab.reset()
        lab.spawn(1,2);victim=lab.selected;victim.hp=10000
        lab.team="enemies";lab.index=[k for k,n in lab.entries()].index("cacador_abissal");lab.spawn(1,5)
        enemy=lab.selected;b=lab.battle
        enemy.age=20;enemy.motion.event_left=0;enemy.motion.loop("walk");enemy.skill_timer=999
        enemy.x=victim.x+CELL_W*3
        b.update_enemies(.1);b.update_production_animations(.1)
        self.assertEqual(enemy.motion.state,"walk")
        self.assertAlmostEqual(enemy.visual_animation.playback_rate,1)
        self.assertEqual(len(enemy.visual_animation.animations["move"].frames),8)
        b.boss_skill(enemy);self.assertEqual(enemy.abyss_windup,0)
        enemy.x=victim.x+48;enemy.attack_timer=0
        hp=victim.hp;b.update_enemies(.001)
        self.assertEqual(victim.hp,hp)
        windup=enemy.attack_windup
        self.assertGreater(windup,0)
        b.update_enemies(windup+.001)
        self.assertLess(victim.hp,hp)
        hp=victim.hp;b.update_enemies(.01);self.assertEqual(victim.hp,hp)
        enemy.attack_timer=0;enemy.motion.event_left=0;b.update_enemies(.001)
        victim.row=2;b.update_enemies(.01)
        self.assertEqual(enemy.attack_windup,0);self.assertEqual(victim.hp,hp)
        victim.row=enemy.row;victim.stats=dict(victim.stats,water_only=True)
        enemy.x=victim.x+CELL_W*1.5;enemy.motion.event_left=0;enemy.motion.loop("walk")
        b.boss_skill(enemy);self.assertGreater(enemy.abyss_windup,0)
        hp=victim.hp;windup=enemy.abyss_windup
        b.update_enemies(windup-.01);self.assertEqual(victim.hp,hp)
        b.update_enemies(.011)
        self.assertEqual(victim.hp,hp-b.scaled_enemy_damage(enemy,10))
        self.assertGreater(victim.stun,0)
        enemy.motion.event_left=0;enemy.x=victim.x+CELL_W*1.5;b.boss_skill(enemy)
        hp=victim.hp;victim.row=2;b.update_enemies(enemy.abyss_windup+.001)
        self.assertEqual(victim.hp,hp);self.assertIsNone(enemy.abyss_target)
        lab.close()

    def test_green_colossus_jet_and_contact_gates(self):
        from svz.config import CELL_W
        lab=DeveloperLab(self.app);lab.region="beach";lab.reset()
        lab.spawn(1,2);v=lab.selected;v.hp=10000;v.stats=dict(v.stats,water_only=True)
        lab.team="enemies";lab.index=[k for k,n in lab.entries()].index("leviata");lab.spawn(1,5)
        e=lab.selected;b=lab.battle;e.age=20;e.motion.event_left=0;e.motion.loop("walk");e.skill_timer=999
        e.x=v.x+CELL_W*5;b.boss_skill(e);self.assertEqual(e.jet_windup,0)
        b.update_enemies(.1);b.update_production_animations(.1)
        self.assertEqual(e.motion.state,"walk");self.assertAlmostEqual(e.visual_animation.playback_rate,1)
        e.x=v.x+CELL_W*3;e.motion.event_left=0;b.boss_skill(e)
        self.assertEqual(e.skill_timer,5.0)
        self.assertGreater(e.jet_windup,0);self.assertEqual(len(b.projectiles),0)
        delay=e.jet_windup;b.update_enemies(delay-.01);self.assertEqual(len(b.projectiles),0)
        b.update_enemies(.011);self.assertEqual(len(b.projectiles),1)
        self.assertEqual(b.projectiles[0].kind,"waterjet")
        hp=v.hp;b.update_projectiles(.5);self.assertEqual(v.hp,hp-b.scaled_enemy_damage(e,54))
        e.motion.event_left=0;b.boss_skill(e);v.row=2
        b.update_enemies(e.jet_windup+.001);self.assertEqual(len(b.projectiles),0)
        v.row=e.row;e.motion.event_left=0;e.x=v.x+48;e.attack_timer=0;e.skill_timer=999
        hp=v.hp;b.update_enemies(.001);self.assertGreater(e.attack_windup,0);self.assertEqual(v.hp,hp)
        b.update_enemies(e.attack_windup+.001);self.assertLess(v.hp,hp)
        e.attack_timer=0;e.motion.event_left=0;b.update_enemies(.001)
        hp=v.hp;v.hp=0;b.update_enemies(.01);self.assertEqual(e.attack_windup,0)
        lab.close()
