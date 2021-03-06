import urllib2, json, time, sys
#from flask import requests
import requests

#sys encoding things to prevent Unicode encoding errors
reload(sys)
sys.setdefaultencoding('utf-8')

def search_api(query):
    temp = requests.get("http://pokeapi.co/api/v2/"+ query, None)
    dic = temp.json()
    return dic

# Returns a dictionary of the pokemon's moves, items, abilities, etc.
def search_poke(pokemon):
    dic = search_api("pokemon/" + pokemon)
    return dic



# ============ STRENGTHS/WEAKNESSES ===============
'''
The final goal is to get a dictionary for the team formated as such:
{
    normal: 1
    fighting: 2
    flying: 0
    poison: -3
    ground: 1
    rock: 0
    bug: 0
    ghost: 0
    steel: 0
    fire: 0
    water: 0
    grass: 0
    electric: 0
    psychic: 0
    ice: 0
    dragon: 0
    dark: 0
}
'''


# Returns a (formated) dictionary with the type effectiveness for the given type
def type_info(type):
    dmg_rel = search_api("type/" + type)["damage_relations"]
    for relation in dmg_rel:
        type_list = []
        for type_entry in dmg_rel[relation]:
            type_list.append( type_entry["name"] )
        dmg_rel[relation] = type_list
    return dmg_rel

# Adds the damage relationships for the individual type to the overall dictionary
# for the team. Must also pass offensive/deffensive
def add_dmg_rel(poketypes, relationship):
    types = {'normal': 0,'fighting': 0,'flying': 0,'poison': 0,'ground': 0,'rock': 0,'bug': 0,'ghost': 0,'steel': 0,'fire': 0,'water': 0,'grass': 0,'electric': 0,'psychic': 0,'ice': 0,'dragon': 0,'dark': 0, 'fairy':0}
    for poketype in poketypes:
        ind_dmg_rel = type_info(poketype)
        if relationship == "offensive":
            for reltype in ind_dmg_rel["half_damage_to"]:
                types[reltype] += .5
            for reltype in ind_dmg_rel["no_damage_to"]:
                types[reltype] -= .5
            for reltype in ind_dmg_rel["double_damage_to"]:
                types[reltype] += 2
        if relationship == "defensive":
            for reltype in ind_dmg_rel["half_damage_from"]:
                types[reltype] -= .5
            for reltype in ind_dmg_rel["no_damage_from"]:
                types[reltype] += 1
            for reltype in ind_dmg_rel["double_damage_from"]:
                types[reltype] -= 2
    return types
                
def keyswithmaxval(d):
    poketypes = list()
    v=d.values()
    maxval = max(v)
    while (maxval in d.values()) :
        v = d.values()
        k = d.keys()
        ptype = k[v.index(max(v))]
        poketypes.append(ptype)
        del d[ptype]
    return poketypes

def keyswithminval(d):
    poketypes = list()
    v=d.values()
    minval = min(v)
    while (minval in d.values()) :
        v = d.values()
        k = d.keys()
        ptype = k[v.index(min(v))]
        poketypes.append(ptype)
        del d[ptype]
    return poketypes
                
# given a list of pokemon, returns a dictionary keyed by type with values equal
# to the offense of the team against that type
def get_sandw(poketypes):
    offensive = add_dmg_rel(poketypes, "offensive")
    defensive = add_dmg_rel(poketypes, "defensive")
    s_off = keyswithmaxval(offensive)
    s_def = keyswithmaxval(defensive)
    strengths = {'offensive': s_off, 'defensive': s_def}
    w_off = keyswithminval(offensive)
    w_def = keyswithminval(defensive)
    weaknesses = {'offensive': w_off, 'defensive': w_def}
    sandw = list()
    sandw.append(strengths)
    sandw.append(weaknesses)
    return sandw


if __name__ == '__main__':
    poketypes = ['electric', 'grass', 'ground']
    print get_stren_and_weak(poketypes)
    # print search_poke("pikachu")
    # print search_api("type/ground")
