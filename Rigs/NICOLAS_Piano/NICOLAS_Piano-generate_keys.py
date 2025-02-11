#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NICOLAS_Piano © 2025 MaelPERON

Description : Instantie les modifiers sur chaque touche pour chaque cible de collision.
Licence : GNU General Public License v3.0

Ce fichier fait partie du Github "Dagda's Cauldron", un répertoire collaboratif
d'outils, fichiers et scripts créés sur mesure, désormais partagés pour
bénéficier à tous (voir https://github.com/MaelPERON/Dagda-s-Cauldron).
"""

import bpy
from bpy.path import clean_name

C = bpy.context
D = bpy.data

rig = D.objects.get("rig")
pressure_listener = D.node_groups.get("PRESSURE_LISTENER")
colliders_targets = [tgt for tgt in D.collections.get("Targets").objects if tgt.name.startswith("collider_target")]
colliders_owners = [own for own in D.collections.get("Collection").objects if own.name.startswith("collider_owner")]

for owner in colliders_owners:
    # Nettoyage des précédents listeners
    for mod in owner.modifiers:
        if mod.node_group.name == "PRESSURE_LISTENER":
            owner.modifiers.remove(mod)

    # Ajouter les listeners
    for tgt in colliders_targets:
        tgt_name = clean_name(tgt.name)
        mod = owner.modifiers.new(tgt_name, "NODES")
        mod.node_group = pressure_listener
        mod["Socket_2"] = True # Clamp Key Pressure
        mod["Socket_3"] = False # +Y
        mod["Socket_4"] = tgt

        # Drivers
        # fc = owner.driver_add(f'modifiers["{tgt_name}"]["Socket_2"]')
        # dv = fc.driver
        # for var in dv.variables:
        #     dv.variables.remove(var)
        # dv.type = "AVERAGE"
        # vars = dv.variables
        # var = vars.new()
        # var.type = "SINGLE_PROP"
        # var.name = 
        # tg = var.targets[0]
        # tg.id = rig
        # tg.data_path = f'pose.bones["target.000"]["clamp"]'